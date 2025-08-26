from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import Http404


def admin_required(view_func):
    """
    Decorator for views that checks that the user is an admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        
        if not request.user.is_staff:
            raise PermissionDenied("You must be an admin to access this page.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def submission_owner_required(view_func):
    """
    Decorator for views that checks that the user owns the submission.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        
        # Get submission ID from URL kwargs
        submission_id = kwargs.get('pk') or kwargs.get('submission_id')
        if not submission_id:
            raise Http404("Submission not found")
        
        # Import here to avoid circular imports
        from submissions.models import Submission
        
        submission = get_object_or_404(Submission, id=submission_id)
        
        if submission.user != request.user and not request.user.is_staff:
            raise PermissionDenied("You can only view your own submissions.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def can_submit_code(view_func):
    """
    Decorator for views that checks if user can submit code.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        
        # Additional checks can be added here
        # For example: check if user is in a contest, has enough privileges, etc.
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def problem_exists(view_func):
    """
    Decorator for views that checks if the problem exists.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        problem_id = kwargs.get('problem_id')
        if not problem_id:
            raise Http404("Problem not found")
        
        # Import here to avoid circular imports
        from problems.models import Problem
        
        get_object_or_404(Problem, id=problem_id)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

