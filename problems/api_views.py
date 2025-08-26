from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Problem, TestCase
from .serializers import (
    TestCaseSerializer, ProblemWithTestCasesSerializer,
    ProblemListSerializer, ProblemDetailSerializer
)
from users.permissions import IsAdminOrReadOnly
from .code_runner import SecureCodeRunner

class ProblemListCreateAPIView(generics.ListCreateAPIView):
    queryset = Problem.objects.all().order_by('-id')
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProblemDetailSerializer
        return ProblemListSerializer

class ProblemDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
    
class TestCaseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TestCaseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return TestCase.objects.filter(problem_id=self.kwargs['problem_id'])

    def perform__create(self, serializer):
        problem = Problem.objects.get(pk=self.kwargs['problem_id'])
        serializer.save(problem=problem)

class TestCaseDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer
    permission_classes = [IsAdminOrReadOnly]

class ProblemWithTestCasesAPIView(generics.CreateAPIView):
    serializer_class = ProblemWithTestCasesSerializer
    permission_classes = [IsAdminOrReadOnly]