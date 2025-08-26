from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Recalculate user statistics for all users'

    def handle(self, *args, **options):
        self.stdout.write('Starting user statistics recalculation...')
        
        users_processed = 0
        for user in User.objects.all():
            if hasattr(user, 'userprofile'):
                user.userprofile.recalculate_stats()
                users_processed += 1
                self.stdout.write(f'Updated stats for user: {user.username}')
            else:
                # Create UserProfile if it doesn't exist
                UserProfile.objects.create(user=user)
                user.userprofile.recalculate_stats()
                users_processed += 1
                self.stdout.write(f'Created and updated stats for user: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {users_processed} users'
            )
        ) 