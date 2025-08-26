from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    Used for managing extended user information.
    """
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'website', 'github_username', 
                 'preferred_language', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_website(self, value):
        """Validate website URL format."""
        if value and not (value.startswith('http://') or value.startswith('https://')):
            raise serializers.ValidationError("Website URL must start with http:// or https://")
        return value

    def validate_bio(self, value):
        """Validate bio length."""
        if value and len(value) > 500:
            raise serializers.ValidationError("Bio cannot exceed 500 characters.")
        return value


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for User list view with essential fields.
    Used for admin user management and public user listings.
    """
    profile = UserProfileSerializer(read_only=True)
    submission_count = serializers.SerializerMethodField()
    problems_solved = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                 'is_active', 'date_joined', 'last_login', 'profile',
                 'submission_count', 'problems_solved']
        read_only_fields = ['id', 'date_joined', 'last_login', 'submission_count', 'problems_solved']

    def get_submission_count(self, obj):
        """Get total number of submissions by this user."""
        return obj.submission_set.count()

    def get_problems_solved(self, obj):
        """Get number of unique problems solved by this user."""
        return obj.submission_set.filter(status='Accepted').values('problem').distinct().count()


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for User detail view with all fields.
    Used for viewing complete user information.
    """
    profile = UserProfileSerializer(read_only=True)
    submission_stats = serializers.SerializerMethodField()
    recent_submissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                 'is_active', 'is_staff', 'date_joined', 'last_login',
                 'profile', 'submission_stats', 'recent_submissions']
        read_only_fields = ['id', 'date_joined', 'last_login', 'submission_stats', 'recent_submissions']

    def get_submission_stats(self, obj):
        """Get detailed submission statistics for this user."""
        from submissions.models import Submission
        from django.db.models import Count
        
        submissions = Submission.objects.filter(user=obj)
        total_submissions = submissions.count()
        
        if total_submissions == 0:
            return {
                'total_submissions': 0,
                'accepted_submissions': 0,
                'problems_solved': 0,
                'acceptance_rate': 0.0,
                'favorite_language': None
            }
        
        status_counts = submissions.values('status').annotate(count=Count('status'))
        status_dict = {item['status']: item['count'] for item in status_counts}
        
        accepted_submissions = status_dict.get('Accepted', 0)
        acceptance_rate = (accepted_submissions / total_submissions) * 100
        problems_solved = submissions.filter(status='Accepted').values('problem').distinct().count()
        
        # Find favorite language
        language_counts = submissions.values('language').annotate(count=Count('language')).order_by('-count')
        favorite_language = language_counts[0]['language'] if language_counts else None
        
        return {
            'total_submissions': total_submissions,
            'accepted_submissions': accepted_submissions,
            'problems_solved': problems_solved,
            'acceptance_rate': round(acceptance_rate, 2),
            'favorite_language': favorite_language,
            'status_distribution': status_dict
        }

    def get_recent_submissions(self, obj):
        """Get recent submissions by this user."""
        from submissions.models import Submission
        
        recent_submissions = Submission.objects.filter(user=obj).order_by('-submitted_at')[:5]
        return [{
            'id': sub.id,
            'problem_title': sub.problem.title,
            'language': sub.language,
            'status': sub.status,
            'submitted_at': sub.submitted_at
        } for sub in recent_submissions]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    Used by admin users for user management.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                 'password', 'password_confirm', 'is_active', 'is_staff', 'profile']

    def validate_username(self, value):
        """Validate username uniqueness and format."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Username can only contain letters, numbers, hyphens, and underscores.")
        return value

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        """Cross-field validation."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        """Create user with profile."""
        profile_data = validated_data.pop('profile', {})
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create or update profile
        if profile_data:
            UserProfile.objects.update_or_create(user=user, defaults=profile_data)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    Used for both self-updates and admin updates.
    """
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'is_active', 'is_staff', 'profile']

    def validate_email(self, value):
        """Validate email uniqueness (excluding current user)."""
        user = self.instance
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update(self, instance, validated_data):
        """Update user and profile."""
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create profile
        if profile_data is not None:
            UserProfile.objects.update_or_create(
                user=instance, 
                defaults=profile_data
            )
        
        return instance


class UserSelfUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for users updating their own information.
    Excludes admin-only fields like is_staff and is_active.
    """
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile']

    def validate_email(self, value):
        """Validate email uniqueness (excluding current user)."""
        user = self.instance
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update(self, instance, validated_data):
        """Update user and profile."""
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create profile
        if profile_data is not None:
            UserProfile.objects.update_or_create(
                user=instance, 
                defaults=profile_data
            )
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    Used for both self-password change and admin password reset.
    """
    old_password = serializers.CharField(required=False)
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, data):
        """Cross-field validation."""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        return data

    def validate_old_password(self, value):
        """Validate old password for self-password change."""
        user = self.context['request'].user
        if not user.is_staff and not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Serializer for public user information.
    Used for displaying user information to other users.
    """
    profile = UserProfileSerializer(read_only=True)
    submission_count = serializers.SerializerMethodField()
    problems_solved = serializers.SerializerMethodField()
    acceptance_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'date_joined',
                 'profile', 'submission_count', 'problems_solved', 'acceptance_rate']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'date_joined',
                           'submission_count', 'problems_solved', 'acceptance_rate']

    def get_submission_count(self, obj):
        """Get total number of submissions by this user."""
        return obj.submission_set.count()

    def get_problems_solved(self, obj):
        """Get number of unique problems solved by this user."""
        return obj.submission_set.filter(status='Accepted').values('problem').distinct().count()

    def get_acceptance_rate(self, obj):
        """Calculate acceptance rate for this user."""
        total_submissions = obj.submission_set.count()
        if total_submissions == 0:
            return 0.0
        
        accepted_submissions = obj.submission_set.filter(status='Accepted').count()
        return round((accepted_submissions / total_submissions) * 100, 2)


class BulkUserActionSerializer(serializers.Serializer):
    """
    Serializer for bulk actions on users.
    Used by admin users for bulk operations.
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=100
    )
    action = serializers.ChoiceField(choices=['activate', 'deactivate', 'delete', 'make_staff', 'remove_staff'])
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_user_ids(self, value):
        """Validate user IDs."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate user IDs found.")
        return value

    def validate(self, data):
        """Ensure admin users cannot perform certain actions on themselves."""
        request = self.context.get('request')
        if request and request.user.id in data['user_ids']:
            action = data['action']
            if action in ['deactivate', 'delete', 'remove_staff']:
                raise serializers.ValidationError(f"You cannot {action} yourself.")
        return data


class UserSearchSerializer(serializers.Serializer):
    """
    Serializer for user search parameters.
    Used for filtering and searching users.
    """
    query = serializers.CharField(max_length=100, required=False)
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    date_joined_after = serializers.DateTimeField(required=False)
    date_joined_before = serializers.DateTimeField(required=False)
    min_problems_solved = serializers.IntegerField(min_value=0, required=False)
    preferred_language = serializers.CharField(max_length=20, required=False)

    def validate_query(self, value):
        """Validate search query."""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Search query must be at least 2 characters long.")
        return value.strip() if value else None

