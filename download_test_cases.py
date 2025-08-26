#!/usr/bin/env python3
"""
Utility script to download and convert test cases from external sources.
This script helps integrate with online-judge-tools and other sources.
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def download_with_oj_tools(url, output_dir="test_cases"):
    """
    Download test cases using online-judge-tools
    Requires: pip install online-judge-tools
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Run oj download command
        result = subprocess.run(
            ['oj', 'd', url, '-d', output_dir],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ Downloaded test cases to {output_dir}")
        return output_dir
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading test cases: {e}")
        print(f"Make sure you have online-judge-tools installed: pip install online-judge-tools")
        return None
    except FileNotFoundError:
        print("❌ online-judge-tools not found. Install with: pip install online-judge-tools")
        return None

def convert_oj_test_cases(test_dir, output_file="test_cases.json"):
    """
    Convert online-judge-tools test cases to JSON format
    """
    test_cases = []
    
    # Find all .in files
    in_files = list(Path(test_dir).glob("*.in"))
    
    for in_file in in_files:
        # Get corresponding .out file
        out_file = in_file.with_suffix('.out')
        
        if out_file.exists():
            # Read input and output
            with open(in_file, 'r') as f:
                input_data = f.read().strip()
            
            with open(out_file, 'r') as f:
                output_data = f.read().strip()
            
            test_cases.append({
                'input': input_data,
                'output': output_data,
                'name': in_file.stem
            })
    
    # Save to JSON file
    with open(output_file, 'w') as f:
        json.dump(test_cases, f, indent=2)
    
    print(f"✓ Converted {len(test_cases)} test cases to {output_file}")
    return output_file

def create_sample_test_cases():
    """
    Create sample test case files for common problem types
    """
    samples = {
        "two_sum.json": [
            {"input": "2 7 11 15\n9", "output": "0 1"},
            {"input": "3 2 4\n6", "output": "1 2"},
            {"input": "3 3\n6", "output": "0 1"},
            {"input": "1 2 3 4 5\n9", "output": "3 4"},
            {"input": "10 20 30 40 50\n60", "output": "2 3"}
        ],
        "binary_search.json": [
            {"input": "5\n1 3 5 7 9\n3", "output": "1"},
            {"input": "5\n1 3 5 7 9\n10", "output": "-1"},
            {"input": "3\n1 2 3\n2", "output": "1"},
            {"input": "1\n5\n5", "output": "0"},
            {"input": "4\n1 2 3 4\n1", "output": "0"}
        ],
        "addition.json": [
            {"input": "1 2", "output": "3"},
            {"input": "5 3", "output": "8"},
            {"input": "10 20", "output": "30"},
            {"input": "0 0", "output": "0"},
            {"input": "100 200", "output": "300"}
        ],
        "fibonacci.json": [
            {"input": "0", "output": "0"},
            {"input": "1", "output": "1"},
            {"input": "2", "output": "1"},
            {"input": "3", "output": "2"},
            {"input": "4", "output": "3"},
            {"input": "5", "output": "5"},
            {"input": "6", "output": "8"},
            {"input": "7", "output": "13"}
        ]
    }
    
    for filename, test_cases in samples.items():
        with open(filename, 'w') as f:
            json.dump(test_cases, f, indent=2)
        print(f"✓ Created {filename} with {len(test_cases)} test cases")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python download_test_cases.py download <url>")
        print("  python download_test_cases.py convert <test_dir>")
        print("  python download_test_cases.py create-samples")
        return
    
    command = sys.argv[1]
    
    if command == "download":
        if len(sys.argv) < 3:
            print("❌ Please provide a URL")
            return
        
        url = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "test_cases"
        
        print(f"Downloading test cases from: {url}")
        test_dir = download_with_oj_tools(url, output_dir)
        
        if test_dir:
            convert_oj_test_cases(test_dir)
    
    elif command == "convert":
        if len(sys.argv) < 3:
            print("❌ Please provide a test directory")
            return
        
        test_dir = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else "test_cases.json"
        
        print(f"Converting test cases from: {test_dir}")
        convert_oj_test_cases(test_dir, output_file)
    
    elif command == "create-samples":
        print("Creating sample test case files...")
        create_sample_test_cases()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
