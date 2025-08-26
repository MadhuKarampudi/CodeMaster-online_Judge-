from django.core.management.base import BaseCommand
from problems.models import Problem, TestCase

class Command(BaseCommand):
    help = 'Add a test case to the first problem'

    def handle(self, *args, **options):
        # Get the first problem
        problem = Problem.objects.first()
        if not problem:
            self.stdout.write(self.style.ERROR('No problems found. Please create a problem first.'))
            return
        
        # Check if test case already exists
        if problem.testcase_set.exists():
            self.stdout.write(f"Problem '{problem.title}' already has {problem.testcase_set.count()} test cases")
            return
        
        # Add a sample test case
        test_case = TestCase.objects.create(
            problem=problem,
            input_data="print('Hello')",
            expected_output="Hello",
            is_sample=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Added test case to problem '{problem.title}':\n"
                f"  Input: {test_case.input_data}\n"
                f"  Expected Output: {test_case.expected_output}"
            )
        ) 