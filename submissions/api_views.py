from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Count, Q, Avg
from django.utils import timezone
from .models import Submission
from .serializers import (
    SubmissionListSerializer, SubmissionDetailSerializer, SubmissionCreateSerializer,
    SubmissionUpdateSerializer, SubmissionRejudgeSerializer, SubmissionStatsSerializer,
    BulkSubmissionActionSerializer, UserSubmissionSummarySerializer, SubmissionCodeSerializer
)
from users.permissions import IsAdminOrReadOnly, IsSubmissionOwner
from .judge import judge_submission
from problems.models import Problem
from problems.code_runner import SecureCodeRunner
import threading


class SubmissionListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating submissions.
    GET: List user's own submissions (authenticated users)
    POST: Create a new submission (authenticated users)
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubmissionCreateSerializer
        return SubmissionListSerializer
    
    def get_queryset(self):
        """Return submissions for the current user, or all if admin."""
        user = self.request.user
        if user.is_staff:
            return Submission.objects.all().order_by('-submitted_at')
        return Submission.objects.filter(user=user).order_by('-submitted_at')
    
    def perform_create(self, serializer):
        """Create submission and trigger judging."""
        submission = serializer.save(user=self.request.user)
        
        # Trigger judging in a separate thread
        def judge_async():
            try:
                judge_submission(submission.id)
            except Exception as e:
                submission.status = 'Runtime Error'
                submission.error = f'Judging failed: {str(e)}'
                submission.save()
        
        thread = threading.Thread(target=judge_async)
        thread.daemon = True
        thread.start()
    
    def create(self, request, *args, **kwargs):
        """Override create to return detailed response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Get the created submission with full details
        from .serializers import SubmissionDetailSerializer
        detail_serializer = SubmissionDetailSerializer(serializer.instance, context={'request': request})
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class SubmissionDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific submission.
    GET: Retrieve submission details (owner or admin)
    PUT/PATCH: Update submission (admin only)
    DELETE: Delete submission (admin only)
    """
    queryset = Submission.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SubmissionUpdateSerializer
        return SubmissionDetailSerializer
    
    def get_permissions(self):
        """Different permissions for different methods."""
        if self.request.method == 'GET':
            permission_classes = [IsAuthenticated, IsSubmissionOwner]
        else:
            permission_classes = [IsAdminOrReadOnly]
        
        return [permission() for permission in permission_classes]
    
    def perform_update(self, serializer):
        """Update submission and set judged_at timestamp."""
        serializer.save(judged_at=timezone.now())


class SubmissionCodeAPIView(generics.RetrieveAPIView):
    """
    API view for retrieving only the code of a submission.
    GET: Retrieve submission code (owner or admin)
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionCodeSerializer
    permission_classes = [IsAuthenticated, IsSubmissionOwner]


@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def rejudge_submission(request, pk):
    """
    API endpoint for rejudging a specific submission.
    POST: Rejudge submission (admin only)
    """
    submission = get_object_or_404(Submission, pk=pk)
    serializer = SubmissionRejudgeSerializer(data=request.data)
    
    if serializer.is_valid():
        reason = serializer.validated_data.get('reason', '')
        
        # Reset submission status
        submission.status = 'Pending'
        submission.execution_time = None
        submission.memory_used = None
        submission.output = ''
        submission.error = ''
        submission.test_cases_passed = 0
        submission.total_test_cases = 0
        submission.save()
        
        # Trigger rejudging in a separate thread
        def rejudge_async():
            judge_submission(submission)
        
        thread = threading.Thread(target=rejudge_async)
        thread.daemon = True
        thread.start()
        
        return Response({
            'message': 'Submission queued for rejudging',
            'submission_id': submission.id,
            'reason': reason
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def bulk_submission_action(request):
    """
    API endpoint for bulk actions on submissions.
    POST: Perform bulk actions (admin only)
    """
    serializer = BulkSubmissionActionSerializer(data=request.data)
    
    if serializer.is_valid():
        submission_ids = serializer.validated_data['submission_ids']
        action = serializer.validated_data['action']
        status = serializer.validated_data.get('status')
        reason = serializer.validated_data.get('reason', '')
        
        # Verify all submissions exist
        submissions = Submission.objects.filter(id__in=submission_ids)
        if submissions.count() != len(submission_ids):
            return Response({
                'error': 'Some submission IDs are invalid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'rejudge':
            # Reset and rejudge submissions
            submissions.update(
                status='Pending',
                execution_time=None,
                memory_used=None,
                output='',
                error='',
                test_cases_passed=0,
                total_test_cases=0
            )
            
            # Trigger rejudging for each submission
            def rejudge_bulk():
                for submission in submissions:
                    judge_submission(submission.id)
            
            thread = threading.Thread(target=rejudge_bulk)
            thread.daemon = True
            thread.start()
            
            return Response({
                'message': f'{submissions.count()} submissions queued for rejudging',
                'reason': reason
            }, status=status.HTTP_200_OK)
        
        elif action == 'delete':
            count = submissions.count()
            submissions.delete()
            return Response({
                'message': f'{count} submissions deleted',
                'reason': reason
            }, status=status.HTTP_200_OK)
        
        elif action == 'update_status':
            submissions.update(status=status, judged_at=timezone.now())
            return Response({
                'message': f'{submissions.count()} submissions updated to {status}',
                'reason': reason
            }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_submission_stats(request, user_id=None):
    """
    API endpoint for getting user submission statistics.
    GET: Get statistics for current user or specified user
    """
    if user_id:
        if not request.user.is_staff and request.user.id != user_id:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=user_id)
    else:
        user = request.user
    
    submissions = Submission.objects.filter(user=user)
    
    # Calculate statistics
    total_submissions = submissions.count()
    if total_submissions == 0:
        return Response({
            'user_id': user.id,
            'username': user.username,
            'total_submissions': 0,
            'accepted_submissions': 0,
            'wrong_answer_submissions': 0,
            'time_limit_exceeded_submissions': 0,
            'memory_limit_exceeded_submissions': 0,
            'runtime_error_submissions': 0,
            'compilation_error_submissions': 0,
            'pending_submissions': 0,
            'acceptance_rate': 0.0,
            'problems_solved': 0,
            'favorite_language': None,
            'average_execution_time': 0.0
        })
    
    status_counts = submissions.values('status').annotate(count=Count('status'))
    status_dict = {item['status']: item['count'] for item in status_counts}
    
    accepted_submissions = status_dict.get('Accepted', 0)
    acceptance_rate = (accepted_submissions / total_submissions) * 100
    
    # Count unique problems solved
    problems_solved = submissions.filter(status='Accepted').values('problem').distinct().count()
    
    # Find favorite language
    language_counts = submissions.values('language').annotate(count=Count('language')).order_by('-count')
    favorite_language = language_counts[0]['language'] if language_counts else None
    
    # Calculate average execution time for accepted submissions
    avg_execution_time = submissions.filter(
        verdict='Accepted',
        execution_time__isnull=False
    ).aggregate(avg_time=Avg('execution_time'))['avg_time'] or 0.0
    
    stats_data = {
        'user_id': user.id,
        'username': user.username,
        'total_submissions': total_submissions,
        'accepted_submissions': status_dict.get('Accepted', 0),
        'wrong_answer_submissions': status_dict.get('Wrong Answer', 0),
        'time_limit_exceeded_submissions': status_dict.get('Time Limit Exceeded', 0),
        'memory_limit_exceeded_submissions': status_dict.get('Memory Limit Exceeded', 0),
        'runtime_error_submissions': status_dict.get('Runtime Error', 0),
        'compilation_error_submissions': status_dict.get('Compilation Error', 0),
        'pending_submissions': status_dict.get('Pending', 0),
        'acceptance_rate': round(acceptance_rate, 2),
        'problems_solved': problems_solved,
        'favorite_language': favorite_language,
        'average_execution_time': round(avg_execution_time, 3)
    }
    
    serializer = SubmissionStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    """
    API endpoint for getting user leaderboard based on problems solved.
    GET: Get leaderboard (authenticated users)
    """
    # Get users with their problem solving statistics
    users_stats = []
    users = User.objects.filter(is_active=True)
    
    for user in users:
        submissions = Submission.objects.filter(user=user)
        total_submissions = submissions.count()
        
        if total_submissions > 0:
            accepted_submissions = submissions.filter(status='Accepted').count()
            problems_solved = submissions.filter(status='Accepted').values('problem').distinct().count()
            acceptance_rate = (accepted_submissions / total_submissions) * 100
            
            # Find favorite language
            language_counts = submissions.values('language').annotate(count=Count('language')).order_by('-count')
            favorite_language = language_counts[0]['language'] if language_counts else None
            
            # Get last submission date
            last_submission = submissions.order_by('-submitted_at').first()
            last_submission_date = last_submission.submitted_at if last_submission else None
            
            users_stats.append({
                'user_id': user.id,
                'username': user.username,
                'total_submissions': total_submissions,
                'accepted_submissions': accepted_submissions,
                'problems_solved': problems_solved,
                'acceptance_rate': round(acceptance_rate, 2),
                'favorite_language': favorite_language,
                'last_submission_date': last_submission_date
            })
    
    # Sort by problems solved (descending), then by acceptance rate (descending)
    users_stats.sort(key=lambda x: (-x['problems_solved'], -x['acceptance_rate']))
    
    # Add rank
    for i, user_stat in enumerate(users_stats, 1):
        user_stat['rank'] = i
    
    # Limit to top 100
    users_stats = users_stats[:100]
    
    serializer = UserSubmissionSummarySerializer(users_stats, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def submission_status(request, pk):
    """
    API endpoint for getting real-time submission status.
    GET: Get current status of a submission (owner or admin)
    """
    submission = get_object_or_404(Submission, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and submission.user != request.user:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    return Response({
        'submission_id': submission.id,
        'status': submission.status,
        'execution_time': submission.execution_time,
        'memory_used': submission.memory_used,
        'test_cases_passed': submission.test_cases_passed,
        'total_test_cases': submission.total_test_cases,
        'submitted_at': submission.submitted_at,
        'judged_at': submission.judged_at
    })


@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def system_stats(request):
    """
    API endpoint for getting system-wide submission statistics.
    GET: Get system statistics (admin only)
    """
    total_submissions = Submission.objects.count()
    
    if total_submissions == 0:
        return Response({
            'total_submissions': 0,
            'status_distribution': {},
            'language_distribution': {},
            'daily_submissions': [],
            'total_users': User.objects.count(),
            'active_users': 0
        })
    
    # Status distribution
    status_counts = Submission.objects.values('status').annotate(count=Count('status'))
    status_distribution = {item['status']: item['count'] for item in status_counts}
    
    # Language distribution
    language_counts = Submission.objects.values('language').annotate(count=Count('language'))
    language_distribution = {item['language']: item['count'] for item in language_counts}
    
    # Daily submissions for the last 30 days
    from datetime import datetime, timedelta
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=29)
    
    daily_submissions = []
    current_date = start_date
    while current_date <= end_date:
        count = Submission.objects.filter(
            submitted_at__date=current_date
        ).count()
        daily_submissions.append({
            'date': current_date.isoformat(),
            'count': count
        })
        current_date += timedelta(days=1)
    
    # Active users (users who submitted in the last 30 days)
    active_users = Submission.objects.filter(
        submitted_at__gte=timezone.now() - timedelta(days=30)
    ).values('user').distinct().count()
    
    return Response({
        'total_submissions': total_submissions,
        'status_distribution': status_distribution,
        'language_distribution': language_distribution,
        'daily_submissions': daily_submissions,
        'total_users': User.objects.count(),
        'active_users': active_users
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_code(request):
    """
    API endpoint for running code with custom input.
    """
    problem_id = request.data.get('problem_id')
    code = request.data.get('code')
    language = request.data.get('language')
    input_data = request.data.get('input', '')

    if not all([problem_id, code, language]):
        return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        problem = Problem.objects.get(pk=problem_id)
    except Problem.DoesNotExist:
        return Response({'error': 'Problem not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Create a fresh code runner instance that respects USE_DOCKER setting
    code_runner = SecureCodeRunner()
    result = code_runner.run(language, code, input_data, time_limit=problem.time_limit)
    
    return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_against_samples(request):
    """
    API endpoint for running code against sample test cases.
    """
    problem_id = request.data.get('problem_id')
    code = request.data.get('code')
    language = request.data.get('language')

    if not all([problem_id, code, language]):
        return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        problem = Problem.objects.get(pk=problem_id)
    except Problem.DoesNotExist:
        return Response({'error': 'Problem not found.'}, status=status.HTTP_404_NOT_FOUND)

    sample_test_cases = problem.testcase_set.filter(is_sample=True)
    if not sample_test_cases.exists():
        return Response({'error': 'No sample test cases found for this problem.'}, status=status.HTTP_404_NOT_FOUND)

    # Create a fresh code runner instance that respects USE_DOCKER setting
    code_runner = SecureCodeRunner()
    
    results = []
    for test_case in sample_test_cases:
        result = code_runner.run(language, code, test_case.input_data, time_limit=problem.time_limit)
        results.append({
            'input_data': test_case.input_data,
            'expected_output': test_case.expected_output,
            'result': result,
        })

    return Response(results)

