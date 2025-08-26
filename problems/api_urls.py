from django.urls import path
from . import api_views

app_name = 'problems_api'

urlpatterns = [
    path('', api_views.ProblemListCreateAPIView.as_view(), name='problem-list-create'),
    path('<int:pk>/', api_views.ProblemDetailUpdateDeleteAPIView.as_view(), name='problem-detail'),
    

    
    # Test case URLs
    path('<int:problem_id>/testcases/', api_views.TestCaseListCreateAPIView.as_view(), name='testcase-list-create'),
    path('testcases/<int:pk>/', api_views.TestCaseDetailUpdateDeleteAPIView.as_view(), name='testcase-detail'),

    # Bulk create problem with test cases
    path('bulk-create/', api_views.ProblemWithTestCasesAPIView.as_view(), name='problem-bulk-create'),
]