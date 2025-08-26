from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Submission
from problems.models import Problem
from problems.serializers import ProblemListSerializer


class SubmissionListSerializer(serializers.ModelSerializer):
    """
    Serializer for Submission list view with essential fields.
    Used for displaying submissions in lists and admin views.
    """
    problem_title = serializers.CharField(source='problem.title', read_only=True)
    problem_difficulty = serializers.CharField(source='problem.difficulty', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'problem_title', 'problem_difficulty', 'username', 
                 'language', 'status', 'submitted_at', 'judged_at',
                 'execution_time', 'memory_used', 'test_cases_passed', 'test_cases_total']
        read_only_fields = ['id', 'submitted_at', 'judged_at', 'execution_time', 
                           'memory_used', 'test_cases_passed', 'test_cases_total']


class SubmissionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Submission detail view with all fields.
    Used for viewing complete submission information.
    """
    problem = ProblemListSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'user', 'username', 'problem', 'code', 'language', 
                 'submitted_at', 'judged_at', 'status', 'output',
                 'execution_time', 'memory_used',
                 'test_cases_passed', 'test_cases_total']
        read_only_fields = ['id', 'user', 'submitted_at', 'judged_at', 'output', 
                           'execution_time', 'memory_used',
                           'test_cases_passed', 'test_cases_total']


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new submissions.
    Used when users submit code for problems.
    """
    class Meta:
        model = Submission
        fields = ['problem', 'code', 'language']

    def validate_code(self, value):
        """Validate code is not empty and within reasonable limits."""
        if not value or not value.strip():
            raise serializers.ValidationError("Code cannot be empty.")
        
        if len(value) > 10240:  # 10KB limit
            raise serializers.ValidationError("Code cannot exceed 10KB.")
        
        return value.strip()

    def validate_problem(self, value):
        """Validate problem exists and is accessible."""
        if not value:
            raise serializers.ValidationError("Problem is required.")
        return value

    def create(self, validated_data):
        """Create submission with current user."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class SubmissionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating submissions.
    Used by admin users for managing submissions.
    """
    class Meta:
        model = Submission
        fields = ['status', 'output', 'execution_time', 
                 'memory_used', 'test_cases_passed', 'test_cases_total']

    def validate_status(self, value):
        """Validate status is a valid choice."""
        valid_statuses = [choice[0] for choice in Submission.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        return value

    def validate_execution_time(self, value):
        """Validate execution time is positive."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Execution time cannot be negative.")
        return value

    def validate_memory_used(self, value):
        """Validate memory usage is positive."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Memory usage cannot be negative.")
        return value


class SubmissionCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving only the code of a submission.
    Used for viewing submission code without other details.
    """
    class Meta:
        model = Submission
        fields = ['id', 'code', 'language']
        read_only_fields = ['id', 'language']


class SubmissionRejudgeSerializer(serializers.Serializer):
    """
    Serializer for rejudging submissions.
    Used by admin users to trigger rejudging.
    """
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_reason(self, value):
        """Validate reason for rejudging."""
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Reason must be at least 5 characters long.")
        return value.strip() if value else ""


class BulkSubmissionActionSerializer(serializers.Serializer):
    """
    Serializer for bulk actions on submissions.
    Used by admin users for bulk operations.
    """
    submission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=100
    )
    action = serializers.ChoiceField(choices=['rejudge', 'delete', 'update_status'])
    status = serializers.ChoiceField(
        choices=Submission.STATUS_CHOICES,
        required=False
    )
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_submission_ids(self, value):
        """Validate submission IDs."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate submission IDs found.")
        return value

    def validate(self, data):
        """Cross-field validation."""
        action = data.get('action')
        if action == 'update_status' and not data.get('status'):
            raise serializers.ValidationError("Status is required for update_status action.")
        return data


class SubmissionStatsSerializer(serializers.Serializer):
    """
    Serializer for submission statistics.
    Used for displaying user statistics and analytics.
    """
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    total_submissions = serializers.IntegerField()
    accepted_submissions = serializers.IntegerField()
    wrong_answer_submissions = serializers.IntegerField()
    time_limit_exceeded_submissions = serializers.IntegerField()
    memory_limit_exceeded_submissions = serializers.IntegerField()
    runtime_error_submissions = serializers.IntegerField()
    compilation_error_submissions = serializers.IntegerField()
    pending_submissions = serializers.IntegerField()
    acceptance_rate = serializers.FloatField()
    problems_solved = serializers.IntegerField()
    favorite_language = serializers.CharField(allow_null=True)
    average_execution_time = serializers.FloatField()


class UserSubmissionSummarySerializer(serializers.Serializer):
    """
    Serializer for user submission summary in leaderboard.
    Used for displaying user rankings and achievements.
    """
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    total_submissions = serializers.IntegerField()
    accepted_submissions = serializers.IntegerField()
    problems_solved = serializers.IntegerField()
    acceptance_rate = serializers.FloatField()
    favorite_language = serializers.CharField(allow_null=True)
    last_submission_date = serializers.DateTimeField(allow_null=True)

