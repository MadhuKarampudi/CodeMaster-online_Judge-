from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow access to the owner of the object
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions are only allowed to admin users
        return request.user.is_authenticated and request.user.is_staff


class IsSubmissionOwner(permissions.BasePermission):
    """
    Custom permission for submission objects.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow access to the submission owner or admin
        return obj.user == request.user or request.user.is_staff


class CanSubmitCode(permissions.BasePermission):
    """
    Custom permission to check if user can submit code.
    """

    def has_permission(self, request, view):
        # User must be authenticated to submit code
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Additional checks can be added here (e.g., contest participation)
        return True


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow owners or admins to access/modify objects.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access to the owner or admin users
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        # For User objects, check if it's the same user or admin
        elif hasattr(obj, 'username'):  # User object
            return obj == request.user or request.user.is_staff
        return request.user.is_staff


class IsAdminOrOwnerReadOnly(permissions.BasePermission):
    """
    Custom permission to allow admins full access and owners read-only access.
    """

    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff:
            return True
        
        # Owners have read-only access
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'user'):
                return obj.user == request.user
            elif hasattr(obj, 'username'):  # User object
                return obj == request.user
        
        return False


class IsActiveUser(permissions.BasePermission):
    """
    Custom permission to only allow active users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active


class CanViewUserProfile(permissions.BasePermission):
    """
    Custom permission for viewing user profiles.
    Users can view their own profile, admins can view any profile,
    and authenticated users can view public profiles.
    """

    def has_object_permission(self, request, view, obj):
        # Admin users can view any profile
        if request.user.is_staff:
            return True
        
        # Users can view their own profile
        if obj == request.user:
            return True
        
        # Authenticated users can view public profiles (active users only)
        if request.user.is_authenticated and obj.is_active:
            return True
        
        return False

