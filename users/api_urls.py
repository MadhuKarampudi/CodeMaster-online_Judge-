from django.urls import path
from . import api_views

urlpatterns = [
    # User CRUD endpoints
    path('', api_views.UserListCreateAPIView.as_view(), name='user-list-create'),
    path('<int:pk>/', api_views.UserDetailUpdateDeleteAPIView.as_view(), name='user-detail-update-delete'),
    
    # Current user endpoints
    path('me/', api_views.CurrentUserAPIView.as_view(), name='current-user'),
    path('me/delete/', api_views.delete_account, name='delete-account'),
    
    # Password management endpoints
    path('change-password/', api_views.change_password, name='change-password'),
    path('<int:pk>/reset-password/', api_views.reset_user_password, name='reset-user-password'),
    
    # User management endpoints (admin only)
    path('bulk-action/', api_views.bulk_user_action, name='user-bulk-action'),
    path('statistics/', api_views.user_statistics, name='user-statistics'),
    
    # Search and activity endpoints
    path('search/', api_views.user_search, name='user-search'),
    path('activity/', api_views.user_activity, name='user-activity'),
    path('<int:pk>/activity/', api_views.user_activity, name='user-activity-by-id'),
    
    # JWT Authentication endpoints
    path('login/', api_views.login_api, name='login-api'),
    path('signup/', api_views.signup_api, name='signup-api'),
    path('refresh-token/', api_views.refresh_token, name='refresh-token'),
]

