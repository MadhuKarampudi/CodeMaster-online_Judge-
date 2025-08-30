from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import User
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from .serializers import (
    UserListSerializer, UserDetailSerializer, UserCreateSerializer,
    UserUpdateSerializer, UserSelfUpdateSerializer, PasswordChangeSerializer,
    UserPublicSerializer, BulkUserActionSerializer, UserSearchSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


class UserListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating users.
    GET: List all users (admin) or search users (authenticated)
    POST: Create a new user (admin only)
    """
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer
    
    def get_permissions(self):
        """Different permissions for different methods."""
        if self.request.method == 'POST':
            permission_classes = [IsAdminOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Return filtered users based on permissions and search parameters."""
        queryset = User.objects.all().order_by('-date_joined')
        
        # If not admin, only show active users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # Apply search filters
        query = self.request.query_params.get('query')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_staff = self.request.query_params.get('is_staff')
        if is_staff is not None and self.request.user.is_staff:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')
        
        return queryset


class UserDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific user.
    GET: Retrieve user details (owner, admin, or public info)
    PUT/PATCH: Update user (owner or admin)
    DELETE: Delete user (admin only)
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            # Users can only update their own profile with limited fields
            if self.get_object() == self.request.user:
                return UserSelfUpdateSerializer
            return UserUpdateSerializer
        elif self.request.method == 'GET':
            # Show detailed info for owner/admin, public info for others
            if (self.get_object() == self.request.user or 
                self.request.user.is_staff):
                return UserDetailSerializer
            return UserPublicSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        """Different permissions for different methods."""
        if self.request.method == 'DELETE':
            permission_classes = [IsAdminOrReadOnly]
        elif self.request.method in ['PUT', 'PATCH']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:  # GET
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]


class CurrentUserAPIView(generics.RetrieveUpdateAPIView):
    """
    API view for current user's profile.
    GET: Retrieve current user's details
    PUT/PATCH: Update current user's profile
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserSelfUpdateSerializer
        return UserDetailSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    API endpoint for changing user password.
    POST: Change password (authenticated users)
    """
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        new_password = serializer.validated_data['new_password']
        
        # For non-admin users, verify old password
        if not user.is_staff:
            old_password = serializer.validated_data.get('old_password')
            if not old_password or not user.check_password(old_password):
                return Response({
                    'error': 'Old password is required and must be correct'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def reset_user_password(request, pk):
    """
    API endpoint for admin to reset user password.
    POST: Reset user password (admin only)
    """
    user = get_object_or_404(User, pk=pk)
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': f'Password reset successfully for user {user.username}'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """
    API endpoint for users to delete their own account.
    POST: Delete current user's account (requires password confirmation)
    """
    password = request.data.get('password')
    if not password:
        return Response({
            'error': 'Password is required to delete account'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    if not user.check_password(password):
        return Response({
            'error': 'Incorrect password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    username = user.username
    user.delete()
    
    return Response({
        'message': f'Account {username} has been deleted successfully'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def bulk_user_action(request):
    """
    API endpoint for bulk actions on users.
    POST: Perform bulk actions (admin only)
    """
    serializer = BulkUserActionSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user_ids = serializer.validated_data['user_ids']
        action = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')
        
        # Verify all users exist
        users = User.objects.filter(id__in=user_ids)
        if users.count() != len(user_ids):
            return Response({
                'error': 'Some user IDs are invalid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'activate':
            users.update(is_active=True)
            message = f'{users.count()} users activated'
        
        elif action == 'deactivate':
            users.update(is_active=False)
            message = f'{users.count()} users deactivated'
        
        elif action == 'delete':
            count = users.count()
            users.delete()
            message = f'{count} users deleted'
        
        elif action == 'make_staff':
            users.update(is_staff=True)
            message = f'{users.count()} users made staff'
        
        elif action == 'remove_staff':
            users.update(is_staff=False)
            message = f'{users.count()} users removed from staff'
        
        return Response({
            'message': message,
            'reason': reason
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_search(request):
    """
    API endpoint for searching users.
    GET: Search users with various filters
    """
    serializer = UserSearchSerializer(data=request.query_params)
    
    if serializer.is_valid():
        queryset = User.objects.all()
        
        # If not admin, only show active users
        if not request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # Apply filters
        query = serializer.validated_data.get('query')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
        
        is_active = serializer.validated_data.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        is_staff = serializer.validated_data.get('is_staff')
        if is_staff is not None and request.user.is_staff:
            queryset = queryset.filter(is_staff=is_staff)
        
        date_joined_after = serializer.validated_data.get('date_joined_after')
        if date_joined_after:
            queryset = queryset.filter(date_joined__gte=date_joined_after)
        
        date_joined_before = serializer.validated_data.get('date_joined_before')
        if date_joined_before:
            queryset = queryset.filter(date_joined__lte=date_joined_before)
        
        min_problems_solved = serializer.validated_data.get('min_problems_solved')
        if min_problems_solved is not None:
            # Filter users who solved at least min_problems_solved problems
            from submissions.models import Submission
            user_ids = Submission.objects.filter(
                status='Accepted'
            ).values('user').annotate(
                problems_count=Count('problem', distinct=True)
            ).filter(
                problems_count__gte=min_problems_solved
            ).values_list('user', flat=True)
            
            queryset = queryset.filter(id__in=user_ids)
        
        preferred_language = serializer.validated_data.get('preferred_language')
        if preferred_language:
            queryset = queryset.filter(
                userprofile__preferred_language=preferred_language
            )
        
        # Order by relevance (username match first, then by date joined)
        if query:
            queryset = queryset.extra(
                select={
                    'username_match': f"CASE WHEN username ILIKE %s THEN 1 ELSE 2 END"
                },
                select_params=[f'%{query}%']
            ).order_by('username_match', '-date_joined')
        else:
            queryset = queryset.order_by('-date_joined')
        
        # Limit results
        queryset = queryset[:50]
        
        # Use public serializer for non-admin users
        if request.user.is_staff:
            result_serializer = UserListSerializer(queryset, many=True)
        else:
            result_serializer = UserPublicSerializer(queryset, many=True)
        
        return Response(result_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminOrReadOnly])
def user_statistics(request):
    """
    API endpoint for getting user statistics.
    GET: Get system-wide user statistics (admin only)
    """
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # Users joined in the last 30 days
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users_30_days = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Users with submissions
    from submissions.models import Submission
    users_with_submissions = Submission.objects.values('user').distinct().count()
    
    # Top users by problems solved
    top_users = []
    users_with_stats = User.objects.filter(is_active=True)[:10]
    
    for user in users_with_stats:
        problems_solved = Submission.objects.filter(
            user=user, 
            status='Accepted'
        ).values('problem').distinct().count()
        
        if problems_solved > 0:
            top_users.append({
                'user_id': user.id,
                'username': user.username,
                'problems_solved': problems_solved
            })
    
    top_users.sort(key=lambda x: x['problems_solved'], reverse=True)
    top_users = top_users[:10]
    
    return Response({
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'new_users_30_days': new_users_30_days,
        'users_with_submissions': users_with_submissions,
        'top_users': top_users
    })


@api_view(['POST'])
@permission_classes([])
def login_api(request):
    """
    JWT Login API endpoint.
    POST: Authenticate user and return JWT tokens
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=email, password=password)
    
    if user:
        if not user.is_active:
            return Response({
                'error': 'Account is disabled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        
        # Create or get user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': '',
                'location': '',
                'website': '',
                'birth_date': None,
                'avatar': None
            }
        )
        
        # Log the user in for Django session auth with backend
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid email or password'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([])
def signup_api(request):
    """
    JWT Signup API endpoint.
    POST: Create new user and return JWT tokens
    """
    print(f"Signup request data: {request.data}")
    print(f"Request POST: {request.POST}")
    
    # Try both request.data (JSON) and request.POST (form data)
    email = request.data.get('email') or request.POST.get('email')
    password = request.data.get('password') or request.POST.get('password1') or request.POST.get('password')
    first_name = request.data.get('first_name', '') or request.POST.get('first_name', '')
    last_name = request.data.get('last_name', '') or request.POST.get('last_name', '')
    
    print(f"Parsed - email: {email}, password: {'***' if password else None}, first_name: {first_name}, last_name: {last_name}")
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({
            'error': 'User with this email already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Log the user in for Django session auth with backend
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined
            }
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'error': f'Failed to create user: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """
    API endpoint for refreshing JWT tokens.
    POST: Refresh access token using refresh token
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({
            'error': 'Refresh token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        return Response({
            'access': access_token
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activity(request, pk=None):
    """
    API endpoint for getting user activity.
    GET: Get activity for current user or specified user
    """
    if pk:
        if not request.user.is_staff and request.user.id != pk:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=pk)
    else:
        user = request.user
    
    from submissions.models import Submission
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get submissions from the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_submissions = Submission.objects.filter(
        user=user,
        submitted_at__gte=thirty_days_ago
    ).order_by('-submitted_at')
    
    # Group by date
    activity_data = {}
    for submission in recent_submissions:
        date_str = submission.submitted_at.date().isoformat()
        if date_str not in activity_data:
            activity_data[date_str] = {
                'date': date_str,
                'submissions': 0,
                'accepted': 0,
                'problems_attempted': set()
            }
        
        activity_data[date_str]['submissions'] += 1
        if submission.status == 'Accepted':
            activity_data[date_str]['accepted'] += 1
        activity_data[date_str]['problems_attempted'].add(submission.problem.id)
    
    # Convert to list and format
    activity_list = []
    for date_str, data in activity_data.items():
        activity_list.append({
            'date': data['date'],
            'submissions': data['submissions'],
            'accepted': data['accepted'],
            'problems_attempted': len(data['problems_attempted'])
        })
    
    activity_list.sort(key=lambda x: x['date'], reverse=True)
    
    return Response({
        'user_id': user.id,
        'username': user.username,
        'activity': activity_list
    })

