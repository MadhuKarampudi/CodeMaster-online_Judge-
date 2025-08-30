from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from problems.models import Problem


class Submission(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Wrong Answer", "Wrong Answer"),
        ("Time Limit Exceeded", "Time Limit Exceeded"),
        ("Runtime Error", "Runtime Error"),
        ("Compilation Error", "Compilation Error"),
        ("Memory Limit Exceeded", "Memory Limit Exceeded"),
    ]

    LANGUAGE_CHOICES = [
        ("python", "Python"),
        ("cpp", "C++"),
        ("java", "Java"),
        ("c", "C"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="Pending")
    output = models.TextField(blank=True, help_text="Program output or error messages")
    error = models.TextField(blank=True, help_text="Compilation or runtime errors")
    execution_time = models.FloatField(null=True, blank=True, help_text="Execution time in seconds")
    memory_used = models.IntegerField(null=True, blank=True, help_text="Memory used in KB")
    test_cases_passed = models.IntegerField(default=0, help_text="Number of test cases passed")
    test_cases_total = models.IntegerField(default=0, help_text="Total number of test cases")
    judged_at = models.DateTimeField(null=True, blank=True, help_text="When the submission was judged")

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} ({self.status})"

    def is_accepted(self):
        return self.status == "Accepted"

    def get_status_color(self):
        """Return CSS class for status color"""
        status_colors = {
            "Pending": "warning",
            "Accepted": "success",
            "Wrong Answer": "danger",
            "Time Limit Exceeded": "warning",
            "Runtime Error": "danger",
            "Compilation Error": "danger",
            "Memory Limit Exceeded": "warning",
        }
        return status_colors.get(self.status, "secondary")


# Signal to update user stats when a submission is accepted
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender='submissions.Submission')
def update_user_stats_on_submission(sender, instance, created, **kwargs):
    """
    Update user statistics when a submission is saved.
    Only update if the submission is accepted and it's the first accepted submission for this problem by this user.
    """
    if instance.status == 'Accepted':
        # Get all accepted submissions for this user and problem
        accepted_submissions = sender.objects.filter(
            user=instance.user,
            problem=instance.problem,
            status='Accepted'
        ).order_by('submitted_at')
        
        # If this is the first accepted submission (earliest submitted_at), update stats
        if accepted_submissions.first().id == instance.id:
            if hasattr(instance.user, 'userprofile'):
                instance.user.userprofile.update_stats(instance)


