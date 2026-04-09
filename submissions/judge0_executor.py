"""
Judge0 API Integration for Vercel Deployment
Replaces Docker-based code execution with external Judge0 service
"""
import os
import time
import requests
import base64
from django.conf import settings
from django.utils import timezone

class Judge0Executor:
    """
    Executes code submissions using Judge0 RapidAPI service
    Perfect for serverless environments like Vercel
    """
    
    # Judge0 API configuration
    JUDGE0_API_URL = "https://judge0-ce.p.rapidapi.com"
    JUDGE0_API_KEY = os.environ.get('JUDGE0_API_KEY', '')
    
    # Language ID mapping for Judge0
    LANGUAGE_MAP = {
        'python': 71,      # Python 3.8.1
        'cpp': 54,         # C++ 17
        'c': 50,           # C 10
        'java': 62,        # Java 14
    }
    
    HEADERS = {
        'x-rapidapi-key': JUDGE0_API_KEY,
        'x-rapidapi-host': 'judge0-ce.p.rapidapi.com',
        'Content-Type': 'application/json'
    }
    
    def __init__(self, submission):
        self.submission = submission
        self.problem = submission.problem
        self.language = submission.language
        self.language_id = self.LANGUAGE_MAP.get(self.language)
        
        if not self.language_id:
            raise ValueError(f"Unsupported language: {self.language}")
    
    def judge(self):
        """Main judging function - runs all test cases"""
        try:
            test_cases = self.problem.testcase_set.all().order_by('id')
            
            if not test_cases.exists():
                self.submission.status = 'Runtime Error'
                self.submission.error = 'No test cases found for this problem.'
                self.submission.save()
                return
            
            total_time = 0.0
            passed_count = 0
            
            for test_case in test_cases:
                result = self._execute_test_case(test_case)
                
                if result['status'] != 'Accepted':
                    self.submission.status = result['status']
                    self.submission.output = result.get('output', '')
                    self.submission.error = result.get('error', '')
                    self.submission.execution_time = total_time
                    self.submission.test_cases_passed = passed_count
                    self.submission.test_cases_total = test_cases.count()
                    self.submission.judged_at = timezone.now()
                    self.submission.save()
                    return  # Stop on first failure
                
                passed_count += 1
                total_time += result.get('execution_time', 0)
            
            # All tests passed
            self.submission.status = 'Accepted'
            self.submission.execution_time = total_time
            self.submission.test_cases_passed = passed_count
            self.submission.test_cases_total = test_cases.count()
            self.submission.judged_at = timezone.now()
            self.submission.save()
            
            # Update user profile stats
            if hasattr(self.submission.user, 'userprofile'):
                self.submission.user.userprofile.update_stats(self.submission)
        
        except Exception as e:
            self.submission.status = 'Runtime Error'
            self.submission.error = f"Judging error: {str(e)}"
            self.submission.judged_at = timezone.now()
            self.submission.save()
    
    def _execute_test_case(self, test_case):
        """Execute a single test case using Judge0 API"""
        try:
            # Prepare the submission
            payload = {
                'language_id': self.language_id,
                'source_code': base64.b64encode(self.submission.code.encode()).decode(),
                'stdin': base64.b64encode(test_case.input_data.encode()).decode(),
                'expected_output': base64.b64encode(test_case.expected_output.strip().encode()).decode()
            }
            
            # Submit code for execution
            submit_response = requests.post(
                f"{self.JUDGE0_API_URL}/submissions",
                json=payload,
                headers=self.HEADERS,
                timeout=30
            )
            
            if submit_response.status_code != 201:
                return {
                    'status': 'System Error',
                    'error': f"Judge0 submission failed: {submit_response.text}",
                    'output': '',
                    'execution_time': 0
                }
            
            submission_id = submit_response.json()['token']
            
            # Poll for result (max 10 seconds)
            max_attempts = 20
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(0.5)
                
                result_response = requests.get(
                    f"{self.JUDGE0_API_URL}/submissions/{submission_id}",
                    headers=self.HEADERS,
                    timeout=30
                )
                
                if result_response.status_code != 200:
                    attempt += 1
                    continue
                
                result = result_response.json()
                status = result.get('status', {}).get('id')
                
                # Status IDs: 1=In Queue, 2=Processing, 3=Accepted, 4=Wrong Answer, 5=TLE, 6=Compilation Error, 7=Runtime Error, 8=System Error
                if status in [3, 4, 5, 6, 7, 8]:  # Final status
                    return self._parse_judge0_result(result)
                
                attempt += 1
            
            return {
                'status': 'Time Limit Exceeded',
                'error': 'Judge0 processing timeout',
                'output': '',
                'execution_time': 0
            }
        
        except requests.exceptions.Timeout:
            return {
                'status': 'Time Limit Exceeded',
                'error': 'Request timeout',
                'output': '',
                'execution_time': 0
            }
        except Exception as e:
            return {
                'status': 'Runtime Error',
                'error': str(e),
                'output': '',
                'execution_time': 0
            }
    
    def _parse_judge0_result(self, result):
        """Convert Judge0 result to our format"""
        status_map = {
            3: 'Accepted',
            4: 'Wrong Answer',
            5: 'Time Limit Exceeded',
            6: 'Compilation Error',
            7: 'Runtime Error',
            8: 'System Error'
        }
        
        status_id = result.get('status', {}).get('id', 8)
        status = status_map.get(status_id, 'Runtime Error')
        
        execution_time = result.get('time', 0)
        if isinstance(execution_time, str):
            try:
                execution_time = float(execution_time)
            except:
                execution_time = 0
        
        output = result.get('stdout', '')
        if output:
            output = base64.b64decode(output).decode('utf-8', errors='ignore')
        
        error = result.get('stderr', '')
        if error:
            error = base64.b64decode(error).decode('utf-8', errors='ignore')
        
        compile_output = result.get('compile_output', '')
        if compile_output:
            compile_output = base64.b64decode(compile_output).decode('utf-8', errors='ignore')
            if not error:
                error = compile_output
        
        return {
            'status': status,
            'output': output.strip(),
            'error': error.strip(),
            'execution_time': execution_time
        }


# Fallback to DockerJudge if JUDGE0_API_KEY is not set
def get_judge(submission):
    """Factory function to get appropriate judge based on environment"""
    if os.environ.get('JUDGE0_API_KEY'):
        return Judge0Executor(submission)
    else:
        # Fall back to original Docker judge
        from .judge import SecureCodeJudge
        return SecureCodeJudge(submission)
