from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone

class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=10,
        choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]
    )
    time_limit = models.FloatField(default=1.0, help_text="Time limit in seconds")
    memory_limit = models.IntegerField(default=128, help_text="Memory limit in MB")
    function_name = models.CharField(max_length=100, default='solve', help_text="e.g., isPalindrome")
    parameters = models.CharField(max_length=200, blank=True, help_text="e.g., x: int or nums: List[int], target: int")
    return_type = models.CharField(max_length=50, default='int', help_text="e.g., bool or List[int]")
    constraints = models.TextField(blank=True, help_text="Problem constraints")

    def __str__(self):
        return self.title

    def get_template_dict(self):
        """Generates a dictionary of code templates for all languages."""
        templates = {
            'python': 'print("Hello, World!")',
            'cpp': '''#include <bits/stdc++.h>
using namespace std;

int main() {
    cout << "Hello World!" << endl;
    return 0;
}''',
            'java': '''public class Solution {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}''',
            'c': '''#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}'''
        }
        return templates

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='testcase_set')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False, help_text="Is this a sample test case visible to users?")

    def __str__(self):
        return f"Test Case for {self.problem.title}"
