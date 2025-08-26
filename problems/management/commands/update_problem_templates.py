from django.core.management.base import BaseCommand
from problems.models import Problem
from problems.template_generator import TemplateGenerator


class Command(BaseCommand):
    help = 'Update existing problems with LeetCode-style code templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--problem-id',
            type=int,
            help='Update specific problem by ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Update all problems',
        )

    def handle(self, *args, **options):
        if options['problem_id']:
            try:
                problem = Problem.objects.get(id=options['problem_id'])
                self.update_problem_templates(problem)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated problem {problem.id}: {problem.title}')
                )
            except Problem.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Problem with ID {options["problem_id"]} does not exist')
                )
        elif options['all']:
            problems = Problem.objects.all()
            updated_count = 0
            for problem in problems:
                self.update_problem_templates(problem)
                updated_count += 1
                self.stdout.write(f'Updated problem {problem.id}: {problem.title}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} problems')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --problem-id or --all')
            )

    def update_problem_templates(self, problem):
        """Update a single problem with generated templates"""
        # Set default values if not set
        if not problem.function_name:
            problem.function_name = self.infer_function_name(problem.title)
        
        if not problem.return_type:
            problem.return_type = 'int'  # Default return type
        
        # Generate templates
        problem.template_python = TemplateGenerator.generate_python_template(
            problem.function_name,
            self.infer_parameters(problem.title),
            problem.return_type,
            problem.title
        )
        
        problem.template_cpp = TemplateGenerator.generate_cpp_template(
            problem.function_name,
            self.infer_parameters(problem.title),
            problem.return_type,
            problem.title
        )
        
        problem.template_java = TemplateGenerator.generate_java_template(
            problem.function_name,
            self.infer_parameters(problem.title),
            problem.return_type,
            problem.title
        )
        
        problem.template_c = TemplateGenerator.generate_c_template(
            problem.function_name,
            self.infer_parameters(problem.title),
            problem.return_type,
            problem.title
        )
        
        problem.save()

    def infer_function_name(self, title):
        """Infer function name from problem title"""
        # Convert title to camelCase function name
        words = title.lower().replace('-', ' ').replace('_', ' ').split()
        if not words:
            return 'solve'
        
        # Common function name mappings
        function_mappings = {
            'two sum': 'twoSum',
            'add two numbers': 'addTwoNumbers',
            'longest substring': 'lengthOfLongestSubstring',
            'median of two sorted arrays': 'findMedianSortedArrays',
            'reverse string': 'reverseString',
            'palindrome number': 'isPalindrome',
            'roman to integer': 'romanToInt',
            'valid parentheses': 'isValid',
            'merge two sorted lists': 'mergeTwoLists',
            'remove duplicates': 'removeDuplicates',
            'fizzbuzz': 'fizzBuzz',
            'factorial': 'factorial'
        }
        
        title_lower = title.lower()
        for key, func_name in function_mappings.items():
            if key in title_lower:
                return func_name
        
        # Default: convert to camelCase
        function_name = words[0]
        for word in words[1:]:
            function_name += word.capitalize()
        
        return function_name

    def infer_parameters(self, title):
        """Infer parameters from problem title"""
        title_lower = title.lower()
        
        if 'two sum' in title_lower:
            return 'array,target'
        elif 'string' in title_lower:
            return 'string'
        elif 'array' in title_lower or 'list' in title_lower:
            return 'array'
        elif 'matrix' in title_lower:
            return 'matrix'
        elif 'number' in title_lower:
            return 'int'
        else:
            return 'array'  # Default

