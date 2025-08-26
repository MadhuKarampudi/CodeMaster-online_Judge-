import os
import tempfile
import time
import subprocess
import sys
from django.conf import settings

try:
    import docker
except ImportError:
    docker = None
from .models import Submission
from django.utils import timezone
from problems.code_runner import SecureCodeRunner

# Initialize Docker client
try:
    # Check if Docker usage is disabled via environment variable
    use_docker = os.environ.get('USE_DOCKER', 'true').lower() == 'true'
    if not use_docker:
        docker_client = None
        print("Docker execution disabled via USE_DOCKER environment variable")
    elif docker:
        docker_client = docker.from_env()
        # Check if Docker is running
        docker_client.ping()
    else:
        docker_client = None
except Exception as e:
    print(f"Warning: Docker not available or not running: {e}")
    docker_client = None

class SecureCodeJudge:
    """
    Handles the secure execution and judging of code submissions using Docker containers.
    """
    LANGUAGE_CONFIGS = {
        'python': {'filename': 'solution.py', 'compiled': False},
        'cpp': {'filename': 'solution.cpp', 'compiled': True},
        'c': {'filename': 'solution.c', 'compiled': True},
        'java': {'filename': 'Solution.java', 'compiled': True},
    }
    
    def __init__(self, submission):
        self.submission = submission
        self.problem = submission.problem
        self.language = submission.language
        self.config = self.LANGUAGE_CONFIGS.get(self.language)
        if not self.config:
            raise ValueError(f"Unsupported language: {self.language}")
        
    def judge(self):
        try:
            print(f"DEBUG: Starting to judge submission {self.submission.id}")
            with tempfile.TemporaryDirectory() as temp_dir:
                self._run_all_test_cases(temp_dir)
        except Exception as e:
            print(f"DEBUG: Exception in judge: {str(e)}")
            self.submission.status = 'Runtime Error'
            self.submission.error = f"An unexpected judging system error occurred: {str(e)}"
        finally:
            self.submission.judged_at = timezone.now()
            self.submission.save()
            print(f"DEBUG: Finished judging submission {self.submission.id}, status: {self.submission.status}")
    
    def _run_all_test_cases(self, temp_dir):
        test_cases = self.problem.testcase_set.all().order_by('id')
        print(f"DEBUG: Found {test_cases.count()} test cases for problem {self.problem.id}")
        if not test_cases.exists():
            print(f"DEBUG: No test cases found for problem {self.problem.title}")
            self.submission.status = 'Runtime Error'
            self.submission.error = 'No test cases found for this problem.'
            return

        total_time = 0.0
        max_memory = 0
        passed_count = 0

        for test_case in test_cases:
            result = self._run_single_test_case(temp_dir, self.submission.code, test_case.input_data)

            # Parse execution time from string format (e.g., "0.077s") to float
            execution_time_str = result.get('execution_time', '0.000s')
            try:
                execution_time_float = float(execution_time_str.replace('s', '')) if isinstance(execution_time_str, str) else execution_time_str
            except (ValueError, AttributeError):
                execution_time_float = 0.0
            
            total_time += execution_time_float
            max_memory = max(max_memory, result.get('memory_used', 0))

            # Normalize output by removing trailing whitespace
            expected_output = test_case.expected_output.strip()
            actual_output = result.get('output', '').strip()

            if result['status'] == 'Accepted' and actual_output == expected_output:
                passed_count += 1
            else:
                # If the code was accepted but output is wrong, it's a Wrong Answer
                status = 'Wrong Answer' if result['status'] == 'Accepted' else result['status']
                self.submission.status = status
                self.submission.output = actual_output
                self.submission.error = result.get('error', '')
                self.submission.execution_time = total_time
                self.submission.memory_used = max_memory
                self.submission.test_cases_passed = passed_count
                self.submission.test_cases_total = test_cases.count()
                return # Stop on first failed test case
        
        # All test cases passed
        self.submission.status = 'Accepted'
        self.submission.execution_time = total_time
        self.submission.memory_used = max_memory
        self.submission.test_cases_passed = passed_count
        self.submission.test_cases_total = test_cases.count()

        # Update user profile stats (FIXED: passing self.submission)
        if hasattr(self.submission.user, 'userprofile'):
            user_profile = self.submission.user.userprofile
            print(f"--- DEBUG: Judging submission {self.submission.id} ---")
            print(f"--- DEBUG: User: {self.submission.user.username} ---")
            print(f"--- DEBUG: UserProfile object: {user_profile} ---")
            print(f"--- DEBUG: Type of user_profile: {type(user_profile)} ---")
            print(f"--- DEBUG: Calling update_stats with submission: {self.submission} ---")
            try:
                user_profile.update_stats(self.submission)
                print(f"--- DEBUG: update_stats called successfully ---")
            except Exception as e:
                print(f"--- DEBUG: Error calling update_stats: {e} ---")
                raise e

    def _run_single_test_case(self, temp_dir, code, input_data):
        self._create_solution_file(temp_dir, self.config['filename'], code)

        # Always use non-Docker execution when docker_client is None
        if not docker_client:
            # Fallback to non-Docker execution using SecureCodeRunner
            # Create fresh code runner instance
            code_runner = SecureCodeRunner()
            result = code_runner.run(
                language=self.language,
                code=code,
                input_data=input_data,
                time_limit=self.problem.time_limit
            )
            
            if result.get('success'):
                execution_time = result.get('execution_time', '0.000s')
                # Parse execution time to float for comparison
                try:
                    time_value = float(execution_time.replace('s', ''))
                except (ValueError, AttributeError):
                    time_value = 0.0
                
                return {
                    'status': 'Accepted',
                    'output': result.get('output', ''),
                    'error': '',
                    'execution_time': execution_time,
                    'memory_used': 0  # Not measured in non-docker version
                }
            else:
                error_type_map = {
                    'compilation_error': 'Compilation Error',
                    'runtime_error': 'Runtime Error',
                    'timeout_error': 'Time Limit Exceeded',
                    'timeout': 'Time Limit Exceeded',
                    'system_error': 'System Error',
                    'invalid_input': 'Invalid Input'
                }
                
                error_type = result.get('error_type', 'runtime_error')
                status = error_type_map.get(error_type, 'Runtime Error')
                
                return {
                    'status': status,
                    'output': result.get('output', ''),
                    'error': result.get('error', 'Unknown error'),
                    'execution_time': '0.000s',
                    'memory_used': 0
                }

        # Original Docker execution path (only when docker_client is available)
        runner_method_name = f'_run_{self.language}_docker'
        runner_method = getattr(self, runner_method_name, None)

        if runner_method:
            return runner_method(temp_dir, input_data)
        else:
            return {
                'status': 'System Error',
                'output': '',
                'error': f'Unsupported language: {self.language}',
                'execution_time': '0.000s',
                'memory_used': 0
            }

    def _create_solution_file(self, directory, filename, code):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        return filepath

    # --- Docker Execution Methods (FIXED: Added all missing methods) ---

    def _run_container(self, image_name, command, temp_dir, stdin_data=None):
        try:
            container = docker_client.containers.run(
                image=image_name,
                command=command,
                volumes={temp_dir: {'bind': '/app', 'mode': 'rw'}},
                working_dir='/app',
                stdin_open=True,
                detach=True,
                mem_limit="256m",
                network_disabled=True # Security: disable network access
            )

            # Send input data to container's stdin if provided
            if stdin_data:
                socket = container.attach_socket(params={'stdin': 1, 'stream': 1})
                socket._sock.sendall(stdin_data.encode('utf-8'))
                socket.close()

            # Wait for container to finish with a timeout
            result = container.wait(timeout=self.problem.time_limit)
            
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', 'ignore')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', 'ignore')

            container.remove() # Clean up the container

            if result['StatusCode'] == 0 and not stderr:
                return {'status': 'Accepted', 'output': stdout, 'error': stderr}
            else:
                return {'status': 'Runtime Error', 'output': stdout, 'error': stderr}

        except docker.errors.ContainerError as e:
            try: container.remove()
            except: pass
            return {'status': 'Runtime Error', 'error': e.stderr.decode('utf-8', 'ignore')}
        except docker.errors.ImageNotFound:
            return {'status': 'Runtime Error', 'error': f'Docker image not found: {image_name}. Please run "docker pull {image_name}".'}
        except Exception: # Catches timeout from container.wait()
            try: container.stop(); container.remove()
            except: pass
            return {'status': 'Time Limit Exceeded', 'error': f'Timed out after {self.problem.time_limit}s'}

    def _run_python_docker(self, temp_dir, input_data):
        command = ["python", self.config['filename']]
        return self._run_container("python:3.11-slim", command, temp_dir, stdin_data=input_data)

    def _run_cpp_docker(self, temp_dir, input_data):
        # Step 1: Compile the code
        compiler_image = "gcc:latest"
        compile_command = ["g++", "-std=c++14", "-O2", "-o", "solution", self.config['filename']]
        
        compile_result = self._run_container(compiler_image, compile_command, temp_dir)
        if compile_result['status'] != 'Accepted':
            compile_result['status'] = 'Compilation Error' # Rename status
            return compile_result

        # Step 2: Run the compiled code in a minimal container
        runner_image = "ubuntu:latest" # Using a minimal base image
        run_command = ["./solution"]
        return self._run_container(runner_image, run_command, temp_dir, stdin_data=input_data)

    def _run_c_docker(self, temp_dir, input_data):
        # Step 1: Compile
        compiler_image = "gcc:latest"
        compile_command = ["gcc", "-O2", "-o", "solution", self.config['filename']]
        compile_result = self._run_container(compiler_image, compile_command, temp_dir)
        if compile_result['status'] != 'Accepted':
            compile_result['status'] = 'Compilation Error'
            return compile_result

        # Step 2: Run
        runner_image = "ubuntu:latest"
        run_command = ["./solution"]
        return self._run_container(runner_image, run_command, temp_dir, stdin_data=input_data)
        
    def _run_java_docker(self, temp_dir, input_data):
        # Step 1: Compile
        compiler_image = "openjdk:17-jdk-slim"
        compile_command = ["javac", self.config['filename']]
        compile_result = self._run_container(compiler_image, compile_command, temp_dir)
        if compile_result['status'] != 'Accepted':
            compile_result['status'] = 'Compilation Error'
            return compile_result

        # Step 2: Run
        runner_image = "openjdk:17-jdk-slim" # Can use the same image to run
        run_command = ["java", "Solution"]
        return self._run_container(runner_image, run_command, temp_dir, stdin_data=input_data)

# This function is called from your views.py in a separate thread
def judge_submission(submission):
    """
    Judges a submission. This function is designed to be called from a thread.
    """
    try:
        judge = SecureCodeJudge(submission)
        judge.judge()
    except Exception as e:
        print(f"FATAL Error judging submission {submission.id}: {e}")
        submission.status = 'Runtime Error'
        submission.error = f"A fatal error occurred in the judging system: {str(e)}"
        submission.judged_at = timezone.now()
        submission.save()