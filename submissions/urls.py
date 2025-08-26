from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    path('', views.SubmissionHistoryView.as_view(), name='history'),
    path('<int:pk>/', views.SubmissionDetailView.as_view(), name='detail'),
    path('submit/<int:problem_id>/', views.SubmitCodeView.as_view(), name='submit'),
    path('api/status/<int:submission_id>/', views.submission_status_api, name='status_api'),
]

