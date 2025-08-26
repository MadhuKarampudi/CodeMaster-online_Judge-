from django.core.management.base import BaseCommand
from problems.models import Problem, TestCase

class Command(BaseCommand):
    help = 'Add test cases to a problem'

    def add_arguments(self, parser):
        parser.add_argument('problem_id', type=int, help='ID of the problem')
        parser.add_argument('--sample', action='store_true', help='Add as sample test case')

    def handle(self, *args, **options):
        try:
            problem = Problem.objects.get(id=options['problem_id'])
            self.stdout.write(f"Adding test cases to problem: {problem.title}")
            
            # Simple test cases for addition problem
            test_cases = [
                ("1 2", "3"),
                ("5 3", "8"),
                ("10 20", "30"),
                ("0 0", "0"),
                ("100 200", "300"),
            ]
            
            for i, (input_data, expected_output) in enumerate(test_cases, 1):
                is_sample = options['sample'] and i == 1  # First test case as sample if --sample flag
                
                test_case = TestCase.objects.create(
                    problem=problem,
                    input_data=input_data,
                    expected_output=expected_output,
                    is_sample=is_sample
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Added test case {i}: Input='{input_data}', Expected='{expected_output}'"
                    )
                )
            
            self.stdout.write(
                self.style.SUCCESS(f"Successfully added {len(test_cases)} test cases to '{problem.title}'")
            )
            
        except Problem.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Problem with ID {options['problem_id']} does not exist")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error adding test cases: {str(e)}")
            ) 