from rest_framework import serializers
from .models import Problem, TestCase


class TestCaseSerializer(serializers.ModelSerializer):
    """
    Serializer for TestCase model with full CRUD support.
    Used for admin operations and nested within Problem serializers.
    """
    class Meta:
        model = TestCase
        fields = ['id', 'input_data', 'expected_output', 'is_sample']
        read_only_fields = ['id']

    def validate_input_data(self, value):
        """Validate input data is not empty and within reasonable limits."""
        if not value.strip():
            raise serializers.ValidationError("Input data cannot be empty.")
        if len(value) > 10000:  # 10KB limit
            raise serializers.ValidationError("Input data is too large. Maximum 10KB allowed.")
        return value

    def validate_expected_output(self, value):
        """Validate expected output is not empty and within reasonable limits."""
        if not value.strip():
            raise serializers.ValidationError("Expected output cannot be empty.")
        if len(value) > 10000:  # 10KB limit
            raise serializers.ValidationError("Expected output is too large. Maximum 10KB allowed.")
        return value


class TestCaseCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating TestCase instances.
    Excludes the problem field as it's handled by the nested URL.
    """
    class Meta:
        model = TestCase
        fields = ['input_data', 'expected_output', 'is_sample']

    def validate_input_data(self, value):
        """Validate input data is not empty and within reasonable limits."""
        if not value.strip():
            raise serializers.ValidationError("Input data cannot be empty.")
        if len(value) > 10000:  # 10KB limit
            raise serializers.ValidationError("Input data is too large. Maximum 10KB allowed.")
        return value

    def validate_expected_output(self, value):
        """Validate expected output is not empty and within reasonable limits."""
        if not value.strip():
            raise serializers.ValidationError("Expected output cannot be empty.")
        if len(value) > 10000:  # 10KB limit
            raise serializers.ValidationError("Expected output is too large. Maximum 10KB allowed.")
        return value


class ProblemListSerializer(serializers.ModelSerializer):
    """
    Serializer for Problem list view with essential fields.
    Includes test case count for admin users.
    """
    test_case_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Problem
        fields = ['id', 'title', 'difficulty', 'time_limit', 'memory_limit', 'test_case_count']
        read_only_fields = ['id', 'test_case_count']

    def get_test_case_count(self, obj):
        """Return the number of test cases for this problem."""
        return obj.testcase_set.count()


class ProblemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Problem detail view with all fields.
    Includes sample test cases for regular users and all test cases for admins.
    """
    sample_test_cases = serializers.SerializerMethodField()
    all_test_cases = serializers.SerializerMethodField()
    test_case_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Problem
        fields = ['id', 'title', 'description', 'difficulty', 'time_limit', 
                 'memory_limit', 'sample_test_cases', 'all_test_cases', 'test_case_count']
        read_only_fields = ['id', 'sample_test_cases', 'all_test_cases', 'test_case_count']

    def get_sample_test_cases(self, obj):
        """Return sample test cases for regular users."""
        sample_cases = obj.testcase_set.filter(is_sample=True)
        return TestCaseSerializer(sample_cases, many=True).data

    def get_all_test_cases(self, obj):
        """Return all test cases for admin users only."""
        request = self.context.get('request')
        if request and request.user.is_staff:
            all_cases = obj.testcase_set.all()
            return TestCaseSerializer(all_cases, many=True).data
        return None

    def get_test_case_count(self, obj):
        """Return the total number of test cases."""
        return obj.testcase_set.count()


class ProblemCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Problem instances.
    Includes validation for all fields.
    """
    class Meta:
        model = Problem
        fields = ['title', 'description', 'difficulty', 'time_limit', 'memory_limit']

    def validate_title(self, value):
        """Validate problem title."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Title is too long. Maximum 200 characters allowed.")
        return value.strip()

    def validate_description(self, value):
        """Validate problem description."""
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        if len(value) > 50000:  # 50KB limit
            raise serializers.ValidationError("Description is too long. Maximum 50KB allowed.")
        return value.strip()

    def validate_difficulty(self, value):
        """Validate difficulty level."""
        valid_difficulties = ['Easy', 'Medium', 'Hard']
        if value not in valid_difficulties:
            raise serializers.ValidationError(f"Difficulty must be one of: {', '.join(valid_difficulties)}")
        return value

    def validate_time_limit(self, value):
        """Validate time limit."""
        if value <= 0:
            raise serializers.ValidationError("Time limit must be positive.")
        if value > 60:  # 60 seconds max
            raise serializers.ValidationError("Time limit cannot exceed 60 seconds.")
        return value

    def validate_memory_limit(self, value):
        """Validate memory limit."""
        if value <= 0:
            raise serializers.ValidationError("Memory limit must be positive.")
        if value > 1024:  # 1GB max
            raise serializers.ValidationError("Memory limit cannot exceed 1024 MB.")
        return value


class ProblemWithTestCasesSerializer(serializers.ModelSerializer):
    """
    Serializer for Problem with nested test cases for creation/update.
    Allows creating a problem with test cases in a single request.
    """
    test_cases = TestCaseCreateUpdateSerializer(many=True, required=False)
    
    class Meta:
        model = Problem
        fields = ['id', 'title', 'description', 'difficulty', 'time_limit', 
                 'memory_limit', 'test_cases']
        read_only_fields = ['id']

    def validate_title(self, value):
        """Validate problem title."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Title is too long. Maximum 200 characters allowed.")
        return value.strip()

    def validate_description(self, value):
        """Validate problem description."""
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        if len(value) > 50000:  # 50KB limit
            raise serializers.ValidationError("Description is too long. Maximum 50KB allowed.")
        return value.strip()

    def validate_test_cases(self, value):
        """Validate test cases data."""
        if len(value) > 100:  # Maximum 100 test cases
            raise serializers.ValidationError("Too many test cases. Maximum 100 allowed.")
        
        # Ensure at least one sample test case
        sample_count = sum(1 for tc in value if tc.get('is_sample', False))
        if sample_count == 0:
            raise serializers.ValidationError("At least one test case must be marked as sample.")
        
        return value

    def create(self, validated_data):
        """Create problem with nested test cases."""
        test_cases_data = validated_data.pop('test_cases', [])
        problem = Problem.objects.create(**validated_data)
        
        for test_case_data in test_cases_data:
            TestCase.objects.create(problem=problem, **test_case_data)
        
        return problem

    def update(self, instance, validated_data):
        """Update problem and optionally replace test cases."""
        test_cases_data = validated_data.pop('test_cases', None)
        
        # Update problem fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If test cases data is provided, replace all existing test cases
        if test_cases_data is not None:
            instance.testcase_set.all().delete()
            for test_case_data in test_cases_data:
                TestCase.objects.create(problem=instance, **test_case_data)
        
        return instance

