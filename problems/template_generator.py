"""
Template generator for creating LeetCode-style code templates
for different programming languages and problem types.
"""

class TemplateGenerator:
    """
    Generates code templates for different programming languages
    following LeetCode conventions.
    """
    
    @staticmethod
    def generate_python_template(function_name, parameters, return_type, problem_description=""):
        """Generate Python template with class Solution format"""
        # Parse parameters to create proper type hints
        param_list = TemplateGenerator._parse_parameters(parameters, 'python')
        
        template = f'''class Solution:
    def {function_name}(self{", " + param_list if param_list else ""}) -> {return_type}:
        """
        {problem_description}
        """
        # Your code here
        pass'''
        
        return template
    
    @staticmethod
    def generate_cpp_template(function_name, parameters, return_type, problem_description=""):
        """Generate C++ template with class Solution format"""
        param_list = TemplateGenerator._parse_parameters(parameters, 'cpp')
        
        template = f'''class Solution {{
public:
    {return_type} {function_name}({param_list}) {{
        // {problem_description}
        // Your code here
        
    }}
}};'''
        
        return template
    
    @staticmethod
    def generate_java_template(function_name, parameters, return_type, problem_description=""):
        """Generate Java template with class Solution format"""
        param_list = TemplateGenerator._parse_parameters(parameters, 'java')
        
        template = f'''class Solution {{
    public {return_type} {function_name}({param_list}) {{
        // {problem_description}
        // Your code here
        
    }}
}}'''
        
        return template
    
    @staticmethod
    def generate_c_template(function_name, parameters, return_type, problem_description=""):
        """Generate C template with function format"""
        param_list = TemplateGenerator._parse_parameters(parameters, 'c')
        
        template = f'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * {problem_description}
 */
{return_type} {function_name}({param_list}) {{
    // Your code here
    
}}'''
        
        return template
    
    @staticmethod
    def _parse_parameters(parameters, language):
        """Parse parameter string and convert to language-specific format"""
        if not parameters:
            return ""
        
        # Common parameter patterns for different problem types
        type_mappings = {
            'python': {
                'int': 'int',
                'string': 'str',
                'array': 'List[int]',
                'matrix': 'List[List[int]]',
                'list': 'List[int]',
                'boolean': 'bool',
                'float': 'float',
                'double': 'float'
            },
            'cpp': {
                'int': 'int',
                'string': 'string',
                'array': 'vector<int>&',
                'matrix': 'vector<vector<int>>&',
                'list': 'vector<int>&',
                'boolean': 'bool',
                'float': 'float',
                'double': 'double'
            },
            'java': {
                'int': 'int',
                'string': 'String',
                'array': 'int[]',
                'matrix': 'int[][]',
                'list': 'int[]',
                'boolean': 'boolean',
                'float': 'float',
                'double': 'double'
            },
            'c': {
                'int': 'int',
                'string': 'char*',
                'array': 'int*',
                'matrix': 'int**',
                'list': 'int*',
                'boolean': 'int',
                'float': 'float',
                'double': 'double'
            }
        }
        
        # If parameters is already formatted, return as is
        if ',' in parameters or ' ' in parameters:
            return parameters
        
        # Generate common parameter patterns based on problem type
        if language == 'python':
            if 'array' in parameters.lower():
                return 'nums: List[int]'
            elif 'matrix' in parameters.lower():
                return 'matrix: List[List[int]]'
            elif 'string' in parameters.lower():
                return 's: str'
            elif 'target' in parameters.lower():
                return 'nums: List[int], target: int'
            else:
                return 'nums: List[int]'
        
        elif language == 'cpp':
            if 'array' in parameters.lower():
                return 'vector<int>& nums'
            elif 'matrix' in parameters.lower():
                return 'vector<vector<int>>& matrix'
            elif 'string' in parameters.lower():
                return 'string s'
            elif 'target' in parameters.lower():
                return 'vector<int>& nums, int target'
            else:
                return 'vector<int>& nums'
        
        elif language == 'java':
            if 'array' in parameters.lower():
                return 'int[] nums'
            elif 'matrix' in parameters.lower():
                return 'int[][] matrix'
            elif 'string' in parameters.lower():
                return 'String s'
            elif 'target' in parameters.lower():
                return 'int[] nums, int target'
            else:
                return 'int[] nums'
        
        elif language == 'c':
            if 'array' in parameters.lower():
                return 'int* nums, int numsSize'
            elif 'matrix' in parameters.lower():
                return 'int** matrix, int matrixSize, int* matrixColSize'
            elif 'string' in parameters.lower():
                return 'char* s'
            elif 'target' in parameters.lower():
                return 'int* nums, int numsSize, int target'
            else:
                return 'int* nums, int numsSize'
        
        return parameters


class ProblemTemplateUpdater:
    """
    Updates existing problems with proper code templates
    """
    
    @staticmethod
    def update_problem_templates(problem):
        """Update a problem with generated templates for all languages"""
        from .models import Problem
        
        # Generate templates for all supported languages
        problem.template_python = TemplateGenerator.generate_python_template(
            problem.function_name,
            "",  # Will be inferred from problem type
            problem.return_type,
            problem.title
        )
        
        problem.template_cpp = TemplateGenerator.generate_cpp_template(
            problem.function_name,
            "",  # Will be inferred from problem type
            problem.return_type,
            problem.title
        )
        
        problem.template_java = TemplateGenerator.generate_java_template(
            problem.function_name,
            "",  # Will be inferred from problem type
            problem.return_type,
            problem.title
        )
        
        problem.template_c = TemplateGenerator.generate_c_template(
            problem.function_name,
            "",  # Will be inferred from problem type
            problem.return_type,
            problem.title
        )
        
        problem.save()
        return problem


# Predefined templates for common problem types
COMMON_TEMPLATES = {
    'two_sum': {
        'python': '''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        """
        Given an array of integers nums and an integer target,
        return indices of the two numbers such that they add up to target.
        """
        # Your code here
        pass''',
        
        'cpp': '''class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Given an array of integers nums and an integer target,
        // return indices of the two numbers such that they add up to target.
        // Your code here
        
    }
};''',
        
        'java': '''class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Given an array of integers nums and an integer target,
        // return indices of the two numbers such that they add up to target.
        // Your code here
        
    }
}''',
        
        'c': '''#include <stdio.h>
#include <stdlib.h>

/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
int* twoSum(int* nums, int numsSize, int target, int* returnSize) {
    // Given an array of integers nums and an integer target,
    // return indices of the two numbers such that they add up to target.
    // Your code here
    
}'''
    },
    
    'reverse_string': {
        'python': '''class Solution:
    def reverseString(self, s: List[str]) -> None:
        """
        Write a function that reverses a string.
        Do not return anything, modify s in-place instead.
        """
        # Your code here
        pass''',
        
        'cpp': '''class Solution {
public:
    void reverseString(vector<char>& s) {
        // Write a function that reverses a string.
        // Do not return anything, modify s in-place instead.
        // Your code here
        
    }
};''',
        
        'java': '''class Solution {
    public void reverseString(char[] s) {
        // Write a function that reverses a string.
        // Do not return anything, modify s in-place instead.
        // Your code here
        
    }
}''',
        
        'c': '''void reverseString(char* s, int sSize) {
    // Write a function that reverses a string.
    // Do not return anything, modify s in-place instead.
    // Your code here
    
}'''
    }
}

