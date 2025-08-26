# Test Cases Management Guide

This guide explains how to add multiple test cases to your online judge problems using various methods.

## Method 1: Using Django Management Command

### 1.1 Add Predefined Test Cases

```bash
# Add predefined test cases for Two Sum problem
python manage.py add_test_cases 1 --source predefined --type two_sum --sample

# Add predefined test cases for Binary Search problem
python manage.py add_test_cases 2 --source predefined --type binary_search --sample

# Add predefined test cases for Fibonacci problem
python manage.py add_test_cases 3 --source predefined --type fibonacci --sample

# Add custom addition test cases
python manage.py add_test_cases 4 --source predefined --type custom --sample
```

### 1.2 Add Test Cases from JSON File

First, create a JSON file with test cases:

```json
[
  {
    "input": "1 2",
    "output": "3"
  },
  {
    "input": "5 3", 
    "output": "8"
  },
  {
    "input": "10 20",
    "output": "30"
  }
]
```

Then add them to a problem:

```bash
python manage.py add_test_cases 1 --source file --file test_cases.json --sample
```

### 1.3 Add Test Cases Manually

```bash
python manage.py add_test_cases 1 --source manual --sample
```

This will prompt you to enter test cases interactively.

## Method 2: Using External Tools

### 2.1 Install online-judge-tools

```bash
pip install online-judge-tools
```

### 2.2 Download Test Cases from External Sources

```bash
# Download from Codeforces
oj d https://codeforces.com/contest/1234/problem/A

# Download from AtCoder
oj d https://atcoder.jp/contests/abc001/tasks/abc001_1

# Download from HackerRank
oj d https://www.hackerrank.com/challenges/simple-array-sum/problem
```

### 2.3 Convert and Import Test Cases

Use the utility script to convert downloaded test cases:

```bash
# Convert downloaded test cases to JSON
python download_test_cases.py convert test/

# Then add to your problem
python manage.py add_test_cases 1 --source file --file test_cases.json --sample
```

## Method 3: Using the Utility Script

### 3.1 Create Sample Test Case Files

```bash
python download_test_cases.py create-samples
```

This creates:
- `two_sum.json` - Test cases for Two Sum problems
- `binary_search.json` - Test cases for Binary Search problems  
- `addition.json` - Test cases for simple addition problems
- `fibonacci.json` - Test cases for Fibonacci problems

### 3.2 Download and Convert in One Step

```bash
# Download from URL and convert to JSON
python download_test_cases.py download https://codeforces.com/contest/1234/problem/A

# Then add to your problem
python manage.py add_test_cases 1 --source file --file test_cases.json --sample
```

## Method 4: Manual Creation via Django Admin

1. Go to Django Admin: `http://127.0.0.1:8000/admin/`
2. Navigate to Problems → Test Cases
3. Click "Add Test Case"
4. Fill in:
   - Problem: Select the problem
   - Input Data: Enter the input
   - Expected Output: Enter the expected output
   - Is Sample: Check if it's a sample test case

## Method 5: Programmatic Creation

You can also create test cases programmatically in Python:

```python
from problems.models import Problem, TestCase

# Get the problem
problem = Problem.objects.get(id=1)

# Create test cases
test_cases = [
    ("1 2", "3"),
    ("5 3", "8"),
    ("10 20", "30"),
    ("0 0", "0"),
    ("100 200", "300")
]

for input_data, expected_output in test_cases:
    TestCase.objects.create(
        problem=problem,
        input_data=input_data,
        expected_output=expected_output,
        is_sample=True  # First one as sample
    )
```

## Available Predefined Test Case Types

### two_sum
- Input format: Array of numbers + target sum
- Output format: Indices of two numbers that sum to target

### binary_search
- Input format: Array size + sorted array + target
- Output format: Index of target or -1 if not found

### fibonacci
- Input format: Single number n
- Output format: nth Fibonacci number

### sorting
- Input format: Array size + array
- Output format: Sorted array

### custom
- Input format: Two numbers
- Output format: Sum of numbers

## Best Practices

1. **Always include sample test cases** - Mark at least one test case as sample
2. **Test edge cases** - Include cases with 0, negative numbers, large numbers
3. **Test invalid inputs** - Test what happens with wrong input formats
4. **Use meaningful test cases** - Test cases should cover different scenarios
5. **Keep test cases reasonable** - Don't make them too large or complex

## Troubleshooting

### Common Issues

1. **Problem ID not found**: Make sure the problem exists in your database
2. **JSON format error**: Ensure your JSON file has the correct format
3. **Permission errors**: Make sure you have write permissions in the directory
4. **online-judge-tools not found**: Install with `pip install online-judge-tools`

### Getting Help

- Check the Django logs for detailed error messages
- Verify the problem ID exists in your database
- Ensure JSON files are properly formatted
- Make sure all required dependencies are installed

## Example Workflow

Here's a complete example of adding test cases to a "Two Sum" problem:

```bash
# 1. Create sample test cases
python download_test_cases.py create-samples

# 2. Add predefined test cases to problem ID 1
python manage.py add_test_cases 1 --source predefined --type two_sum --sample

# 3. Verify test cases were added
python manage.py shell -c "from problems.models import Problem; p = Problem.objects.get(id=1); print(f'Problem: {p.title}'); print(f'Test cases: {p.testcase_set.count()}'); print('Sample test cases:'); [print(f'  Input: {tc.input_data} -> Output: {tc.expected_output}') for tc in p.testcase_set.filter(is_sample=True)]"
```

This will give you a fully functional problem with multiple test cases!
