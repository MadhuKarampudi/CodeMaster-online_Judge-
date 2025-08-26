from django.core.management.base import BaseCommand, CommandParser
from problems.models import Problem

class Command(BaseCommand):
    help = 'Updates the time limit for a specific problem.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('problem_title', type=str, help='The title of the problem to update.')
        parser.add_argument('new_time_limit', type=float, help='The new time limit in seconds.')

    def handle(self, *args, **options):
        problem_title = options['problem_title']
        new_time_limit = options['new_time_limit']

        try:
            problem = Problem.objects.get(title=problem_title)
            problem.time_limit = new_time_limit
            problem.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated time limit for "{problem_title}" to {new_time_limit}s.'))
        except Problem.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Problem with title "{problem_title}" not found.'))
