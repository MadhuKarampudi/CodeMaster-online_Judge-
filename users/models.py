from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import date, timedelta

class UserManager(BaseUserManager):
    def create_user(self, email, first_name='', last_name='', password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name='', last_name='', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, first_name, last_name, password, **extra_fields)

class User(AbstractUser):
    """Custom user model"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    # Fix reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    def __str__(self):
        return self.email

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


# Signal to create UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)