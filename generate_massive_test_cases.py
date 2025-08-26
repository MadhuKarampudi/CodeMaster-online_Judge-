#!/usr/bin/env python3
"""
Script to generate massive test cases for simple addition problems.
Generates 1000+ test cases with various constraints and edge cases.
"""

import json
import random
import sys
from pathlib import Path

def generate_addition_test_cases(num_cases=1000, max_value=1000000):
    """
    Generate test cases for simple addition of two numbers.
    
    Args:
        num_cases: Number of test cases to generate (default: 1000)
        max_value: Maximum value for individual numbers (default: 1000000)
    
    Returns:
        List of test case dictionaries
    """
    test_cases = []
    
    # Edge cases (always include these)
    edge_cases = [
        (0, 0),           # Both zeros
        (0, 1),           # One zero
        (1, 0),           # One zero
        (-1, 1),          # Negative and positive
        (1, -1),          # Positive and negative
        (-1, -1),         # Both negative
        (max_value, 0),   # Max value with zero
        (0, max_value),   # Zero with max value
        (max_value, max_value),  # Both max values
        (-max_value, max_value), # Min and max
        (max_value, -max_value), # Max and min
    ]
    
    # Add edge cases first
    for a, b in edge_cases:
        test_cases.append({
            "input": f"{a} {b}",
            "output": str(a + b)
        })
    
    # Generate random test cases
    remaining_cases = num_cases - len(edge_cases)
    
    for _ in range(remaining_cases):
        # Different ranges for variety
        if random.random() < 0.3:  # 30% small numbers (0-100)
            a = random.randint(-100, 100)
            b = random.randint(-100, 100)
        elif random.random() < 0.5:  # 20% medium numbers (100-10000)
            a = random.randint(-10000, 10000)
            b = random.randint(-10000, 10000)
        elif random.random() < 0.7:  # 20% large numbers (10000-100000)
            a = random.randint(-100000, 100000)
            b = random.randint(-100000, 100000)
        else:  # 30% very large numbers (100000-max_value)
            a = random.randint(-max_value, max_value)
            b = random.randint(-max_value, max_value)
        
        test_cases.append({
            "input": f"{a} {b}",
            "output": str(a + b)
        })
    
    return test_cases

def generate_constrained_test_cases():
    """
    Generate test cases with specific constraints for competitive programming.
    """
    test_cases = []
    
    # Constraint-based test cases
    constraints = [
        # Small positive numbers
        (1, 100, 50),
        # Small negative numbers
        (-100, -1, 50),
        # Mixed small numbers
        (-50, 50, 100),
        # Medium positive numbers
        (1000, 10000, 100),
        # Medium negative numbers
        (-10000, -1000, 100),
        # Large positive numbers
        (100000, 500000, 100),
        # Large negative numbers
        (-500000, -100000, 100),
        # Very large numbers
        (500000, 1000000, 100),
        # Very large negative numbers
        (-1000000, -500000, 100),
        # Mixed large numbers
        (-1000000, 1000000, 200),
    ]
    
    for min_val, max_val, count in constraints:
        for _ in range(count):
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            test_cases.append({
                "input": f"{a} {b}",
                "output": str(a + b)
            })
    
    return test_cases

def generate_special_patterns():
    """
    Generate test cases with special patterns and edge cases.
    """
    test_cases = []
    
    # Powers of 2
    for i in range(20):
        a = 2 ** i
        b = 2 ** (i + 1)
        test_cases.append({
            "input": f"{a} {b}",
            "output": str(a + b)
        })
    
    # Powers of 10
    for i in range(6):
        a = 10 ** i
        b = 10 ** (i + 1)
        test_cases.append({
            "input": f"{a} {b}",
            "output": str(a + b)
        })
    
    # Fibonacci-like sequences
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]
    for i in range(len(fib) - 1):
        test_cases.append({
            "input": f"{fib[i]} {fib[i+1]}",
            "output": str(fib[i] + fib[i+1])
        })
    
    # Prime numbers
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    for i in range(len(primes) - 1):
        test_cases.append({
            "input": f"{primes[i]} {primes[i+1]}",
            "output": str(primes[i] + primes[i+1])
        })
    
    # Boundary values
    boundary_values = [
        (1, 999999),
        (999999, 1),
        (-1, -999999),
        (-999999, -1),
        (999999, 999999),
        (-999999, -999999),
        (999999, -999999),
        (-999999, 999999),
    ]
    
    for a, b in boundary_values:
        test_cases.append({
            "input": f"{a} {b}",
            "output": str(a + b)
        })
    
    return test_cases

def main():
    """Main function to generate test cases."""
    if len(sys.argv) > 1:
        num_cases = int(sys.argv[1])
    else:
        num_cases = 1000
    
    print(f"Generating {num_cases} test cases for addition problem...")
    
    # Generate different types of test cases
    basic_cases = generate_addition_test_cases(num_cases // 2)
    constrained_cases = generate_constrained_test_cases()
    special_cases = generate_special_patterns()
    
    # Combine all test cases
    all_test_cases = basic_cases + constrained_cases + special_cases
    
    # Shuffle to randomize order
    random.shuffle(all_test_cases)
    
    # Limit to requested number
    all_test_cases = all_test_cases[:num_cases]
    
    # Save to file
    output_file = "massive_addition_test_cases.json"
    with open(output_file, 'w') as f:
        json.dump(all_test_cases, f, indent=2)
    
    print(f"✓ Generated {len(all_test_cases)} test cases")
    print(f"✓ Saved to {output_file}")
    
    # Show some sample test cases
    print("\nSample test cases:")
    for i, test_case in enumerate(all_test_cases[:10]):
        print(f"  {i+1}. Input: {test_case['input']} -> Output: {test_case['output']}")
    
    print(f"\nTo add these to your problem, run:")
    print(f"python manage.py add_test_cases 1 --source file --file {output_file}")

if __name__ == "__main__":
    main()
