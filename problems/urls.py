from django.urls import path
from . import views

app_name = 'problems'

urlpatterns = [
    path('', views.ProblemListView.as_view(), name='list'),
    path('<int:pk>/', views.ProblemDetailView.as_view(), name='detail'),
    path('<int:pk>/solve/', views.ProblemSolveView.as_view(), name='solve'),
    path('add/', views.add_problem, name='add'),
    path('<int:problem_id>/manage-test-cases/', views.manage_test_cases, name='manage_test_cases'),
]

