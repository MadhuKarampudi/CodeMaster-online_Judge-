from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import date, timedelta

class UserProfile(models.Model):
    """Extended user profile to store additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    solved_problems_count = models.IntegerField(default=0)
    total_submissions = models.IntegerField(default=0)
    solved_easy_count = models.IntegerField(default=0)
    solved_medium_count = models.IntegerField(default=0)
    solved_hard_count = models.IntegerField(default=0)
    daily_streak = models.IntegerField(default=0)
    last_submission_date = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500, help_text="User bio")
    location = models.CharField(max_length=100, blank=True, help_text="User location")
    website = models.URLField(blank=True, help_text="User website")
    github_username = models.CharField(max_length=50, blank=True, help_text="GitHub username")
    preferred_language = models.CharField(max_length=20, blank=True, help_text="Preferred programming language")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def recalculate_stats(self):
        """Recalculates aggregate stats for the user."""
        from submissions.models import Submission
        
        self.total_submissions = Submission.objects.filter(user=self.user).count()
        accepted_submissions = Submission.objects.filter(user=self.user, status='Accepted')
        self.solved_problems_count = accepted_submissions.values('problem').distinct().count()
        self.solved_easy_count = accepted_submissions.filter(problem__difficulty='Easy').values('problem').distinct().count()
        self.solved_medium_count = accepted_submissions.filter(problem__difficulty='Medium').values('problem').distinct().count()
        self.solved_hard_count = accepted_submissions.filter(problem__difficulty='Hard').values('problem').distinct().count()
        self.save()

    def update_streak(self, submission):
        """Updates the daily streak based on a new submission."""
        if not submission:
            return
        if submission.status == 'Accepted':
            today = date.today()
            if self.last_submission_date:
                if self.last_submission_date == today - timedelta(days=1):
                    self.daily_streak += 1
                elif self.last_submission_date != today:
                    self.daily_streak = 1
            else:
                self.daily_streak = 1
            self.last_submission_date = today
            self.save()

    def update_stats(self, submission=None):
        """Update all user statistics based on a new submission."""
        self.recalculate_stats()
        if submission:
            self.update_streak(submission)


# Signal to create/save UserProfile when a User is created/saved
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    # Ensure userprofile exists before saving, especially if it was just created
    # This line might cause issues if userprofile is not yet created or if it's already saved
    # For now, let's ensure it's not called if 'created' is True and it was just created
    if not created and hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    elif created:
        pass # Do nothing, it's already saved