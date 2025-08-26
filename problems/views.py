from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from submissions.models import Submission
from .models import Problem, TestCase
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import ProblemForm, TestCaseForm
from django.forms import inlineformset_factory
import json

class ProblemListView(LoginRequiredMixin, ListView):
    model = Problem
    template_name = 'problems/list.html'
    context_object_name = 'problems'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by search query
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
            
        # Filter by difficulty
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solved_submissions = Submission.objects.filter(
            user=self.request.user, 
            status='Accepted'
        ).values_list('problem_id', flat=True)
        context['solved_problems'] = set(solved_submissions)
        return context

class ProblemDetailView(LoginRequiredMixin, DetailView):
    model = Problem
    template_name = 'problems/detail.html'
    context_object_name = 'problem'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        problem = self.get_object()
        context['user_solved'] = Submission.objects.filter(
            user=self.request.user, 
            problem=problem, 
            status='Accepted'
        ).exists()
        context['recent_submissions'] = Submission.objects.filter(
            user=self.request.user, 
            problem=problem
        ).order_by('-submitted_at')[:5]
        context['sample_test_cases'] = problem.testcase_set.filter(is_sample=True)
        return context

class ProblemSolveView(LoginRequiredMixin, DetailView):
    model = Problem
    template_name = 'problems/solve.html'
    context_object_name = 'problem'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        problem = self.get_object()

        # Find the user's last accepted submission for this problem
        last_accepted_submission = Submission.objects.filter(
            user=self.request.user,
            problem=problem,
            status='Accepted'
        ).order_by('-submitted_at').first()

        if last_accepted_submission:
            context['accepted_code'] = last_accepted_submission.code
            context['accepted_language'] = last_accepted_submission.language

        # Generate the templates as a dictionary
        template_dict = problem.get_template_dict()
        # Provide both raw dict and a specifically named key used by the template json_script
        context['code_templates'] = template_dict
        context['code_templates_json'] = template_dict
        # Provide sample test cases for the template (visibility on solve page)
        context['sample_test_cases'] = problem.testcase_set.filter(is_sample=True)
        return context

@login_required
def add_problem(request):
    TestCaseFormSet = inlineformset_factory(
        Problem, TestCase, form=TestCaseForm, 
        extra=1, can_delete=True, can_delete_extra=True
    )

    if request.method == 'POST':
        form = ProblemForm(request.POST)
        formset = TestCaseFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            problem = form.save()
            formset.instance = problem
            formset.save()
            messages.success(request, 'Problem and test cases added successfully!')
            return redirect('problems:detail', pk=problem.pk)
    else:
        form = ProblemForm()
        formset = TestCaseFormSet()

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'problems/add_problem.html', context)

@login_required
def manage_test_cases(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    
    if request.method == 'POST':
        if 'delete_test_case' in request.POST:
            test_case_id = request.POST.get('test_case_id')
            test_case_to_delete = get_object_or_404(TestCase, pk=test_case_id)
            if test_case_to_delete.problem == problem:
                test_case_to_delete.delete()
                messages.success(request, 'Test case deleted successfully!')
            return redirect('problems:manage_test_cases', problem_id=problem.id)

        form = TestCaseForm(request.POST)
        if form.is_valid():
            test_case = form.save(commit=False)
            test_case.problem = problem
            test_case.save()
            messages.success(request, 'Test case added successfully!')
            return redirect('problems:manage_test_cases', problem_id=problem.id)

    else:
        form = TestCaseForm()

    test_cases = problem.testcase_set.all()
    context = {
        'problem': problem,
        'test_cases': test_cases,
        'form': form,
    }
    return render(request, 'problems/manage_test_cases.html', context)