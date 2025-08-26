from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.views import View
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Submission
from .forms import SubmissionForm
from .judge import judge_submission
from problems.models import Problem
from users.decorators import submission_owner_required, can_submit_code, problem_exists
import threading


class SubmissionHistoryView(LoginRequiredMixin, ListView):
    model = Submission
    template_name = 'submissions/history.html'
    context_object_name = 'submissions'
    paginate_by = 20
    
    def get_queryset(self):
        # Users can only see their own submissions
        return Submission.objects.filter(user=self.request.user).order_by('-submitted_at')

    def get_context_data(self, **kwargs):
        # First, get the base context from the parent class
        context = super().get_context_data(**kwargs)
        
        # Get the full, unpaginated list of the user's submissions
        user_submissions = self.get_queryset()
        
        # Calculate the statistics based on the full list
        context['total_submissions_count'] = user_submissions.count()
        
        # --- THIS IS THE CORRECTED LOGIC ---
        # Count the number of UNIQUE problems that have an 'Accepted' status.
        context['accepted_problems_count'] = user_submissions.filter(status='Accepted').values('problem').distinct().count()
        
        context['pending_submissions_count'] = user_submissions.filter(status='Pending').count()
        
        # Return the updated context to the template
        return context


class SubmissionDetailView(LoginRequiredMixin, DetailView):
    model = Submission
    template_name = 'submissions/detail.html'
    context_object_name = 'submission'
    
    def get_queryset(self):
        # Users can only view their own submissions (unless they're staff)
        if self.request.user.is_staff:
            return Submission.objects.all()
        return Submission.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.get_object()
        context['test_cases_passed'] = submission.test_cases_passed
        context['test_cases_total'] = submission.test_cases_total
        return context


class SubmitCodeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            code = data.get('code')
            language = data.get('language')
            problem_id = self.kwargs.get('problem_id')

            if not all([code, language, problem_id]):
                return JsonResponse({'success': False, 'error': 'Missing required data.'}, status=400)

            problem = get_object_or_404(Problem, pk=problem_id)

            if len(code) > 10000:  # 10KB limit
                return JsonResponse({'success': False, 'error': 'Code is too long. Maximum 10KB allowed.'}, status=400)

            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language,
                status='Pending'
            )

            # Judge the submission synchronously to avoid threading issues
            try:
                judge_submission(submission)
                # If submission failed with timeout error, retry once
                submission.refresh_from_db()
                if submission.status == 'Compilation Error' and 'Timed out' in (submission.error or ''):
                    print(f"Retrying submission {submission.id} due to timeout error...")
                    submission.status = 'Pending'
                    submission.error = ''
                    submission.execution_time = None
                    submission.save()
                    judge_submission(submission)
            except Exception as e:
                # If judging fails, mark submission as system error
                submission.status = 'Runtime Error'
                submission.error = f"Judging system error: {str(e)}"
                submission.save()

            return JsonResponse({'success': True, 'submission_id': submission.id})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)





@login_required
@submission_owner_required
def submission_status_api(request, submission_id):
    """API endpoint to check submission status (for AJAX polling)"""
    try:
        submission = Submission.objects.get(id=submission_id)
        return JsonResponse({
            'status': submission.status,
            'execution_time': submission.execution_time,
            'output': submission.output,
            'error_message': submission.error,
            'passed_test_cases': submission.test_cases_passed,
            'total_test_cases': submission.test_cases_total
        })
    except Submission.DoesNotExist:
        return JsonResponse({'error': 'Submission not found'}, status=404)
