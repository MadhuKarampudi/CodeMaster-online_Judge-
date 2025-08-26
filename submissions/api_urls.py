from django.urls import path
from . import api_views

app_name = 'submissions_api'

urlpatterns = [
    # Submission CRUD endpoints
    path('', api_views.SubmissionListCreateAPIView.as_view(), name='submission-list-create'),
    path('<int:pk>/', api_views.SubmissionDetailUpdateDeleteAPIView.as_view(), name='submission-detail-update-delete'),
    path('<int:pk>/code/', api_views.SubmissionCodeAPIView.as_view(), name='submission-code'),
    path('<int:pk>/status/', api_views.submission_status, name='submission-status'),
    
    # Submission management endpoints (admin only)
    path('<int:pk>/rejudge/', api_views.rejudge_submission, name='submission-rejudge'),
    path('bulk-action/', api_views.bulk_submission_action, name='submission-bulk-action'),
    
    # Statistics and analytics endpoints
    path('stats/', api_views.user_submission_stats, name='user-submission-stats'),
    path('stats/<int:user_id>/', api_views.user_submission_stats, name='user-submission-stats-by-id'),
    path('leaderboard/', api_views.leaderboard, name='submission-leaderboard'),
    path('system-stats/', api_views.system_stats, name='submission-system-stats'),

    # Code execution endpoints
    path('run-code/', api_views.run_code, name='run-code'),
    path('run-against-samples/', api_views.run_against_samples, name='run-against-samples'),
]

