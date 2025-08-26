import os
import subprocess
import sys
import tempfile
import time

try:
    import docker  # type: ignore
except Exception:  # docker is optional at runtime
    docker = None  # type: ignore


def _get_docker_client():
    # Check if Docker usage is disabled via environment variable
    use_docker = os.environ.get('USE_DOCKER', 'true').lower() == 'true'
    if not use_docker:
        return None
    
    if docker is None:
        return None
    try:
        return docker.from_env()
    except Exception:
        return None


docker_client = _get_docker_client()


class SecureCodeRunner:
    def __init__(self) -> None:
        self.docker_client = docker_client
        venv_python = os.path.join('myenv', 'Scripts', 'python.exe')
        self.python_path = os.path.abspath(venv_python) if os.path.exists(venv_python) else sys.executable

    def _normalize_path_for_docker(self, path: str) -> str:
        return os.path.abspath(path).replace('\\', '/')

    def run(self, language: str, code: str, input_data: str, time_limit: int = 5) -> dict:
        if not input_data.strip():
            return {'success': False, 'error': '⚠️ Invalid Test Case: No input provided', 'error_type': 'invalid_input'}

        temp_dir_obj = None
        try:
            temp_dir_obj = tempfile.TemporaryDirectory()
            temp_dir = temp_dir_obj.name

            if self.docker_client:
                if language == 'python':
                    return self._run_python_docker(code, input_data, temp_dir, time_limit)
                if language == 'cpp':
                    return self._run_cpp_docker(code, input_data, temp_dir, time_limit)
                if language == 'java':
                    return self._run_java_docker(code, input_data, temp_dir, time_limit)
                if language == 'c':
                    return self._run_c_docker(code, input_data, temp_dir, time_limit)
                return {'success': False, 'error': f'Unsupported language: {language}', 'error_type': 'system_error'}
            else: # Non-docker execution
                if language == 'python':
                    return self._run_python(code, input_data, temp_dir, time_limit)
                if language == 'cpp':
                    return self._run_cpp(code, input_data, temp_dir, time_limit)
                if language == 'java':
                    return self._run_java(code, input_data, temp_dir, time_limit)
                if language == 'c':
                    return self._run_c(code, input_data, temp_dir, time_limit)
                return {'success': False, 'error': f'Unsupported language: {language}', 'error_type': 'system_error'}
        except Exception as e:
            # Differentiate between Docker and non-Docker errors if needed, but for now, a general error is fine.
            error_type = 'system_error' if self.docker_client else 'runtime_error'
            return {'success': False, 'error': f'Execution failed: {e}', 'error_type': error_type}
        finally:
            if temp_dir_obj:
                temp_dir_obj.cleanup()

    def _run_python(self, code: str, input_data: str, temp_dir: str, time_limit: int) -> dict:
        try:
            py_file = os.path.join(temp_dir, 'solution.py')
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(code)

            start_time = time.time()
            proc = subprocess.run(
                [self.python_path, py_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=time_limit,
                cwd=temp_dir,
            )
            dt = time.time() - start_time

            if proc.returncode == 0:
                return {
                    'success': True,
                    'output': proc.stdout.strip(),
                    'execution_time': f'{dt:.3f}s',
                }
            else:
                return {
                    'success': False,
                    'error': proc.stderr.strip() or 'Runtime error occurred',
                    'error_type': 'runtime_error',
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'⏰ Time Limit Exceeded: Execution took longer than {time_limit}s',
                'error_type': 'timeout',
            }
        except Exception as e:
            return {'success': False, 'error': f'❌ Runtime Error: {e}', 'error_type': 'runtime_error'}

    def _run_cpp(self, code: str, input_data: str, temp_dir: str, time_limit: int) -> dict:
        try:
            code = self._preprocess_cpp_code(code)
            cpp = os.path.join(temp_dir, 'solution.cpp')
            with open(cpp, 'w', encoding='utf-8') as f:
                f.write(code)
            exe = os.path.join(temp_dir, 'solution.exe')
            compile_proc = subprocess.run(['g++', '-std=c++14', '-O2', '-o', exe, cpp], capture_output=True, text=True, cwd=temp_dir)
            if compile_proc.returncode != 0:
                return {'success': False, 'error': f'🔴 Compilation Error:\n{compile_proc.stderr}', 'error_type': 'compilation_error'}

            start_time = time.time()
            proc = subprocess.run([exe], input=input_data, capture_output=True, text=True, timeout=time_limit, cwd=temp_dir)
            dt = time.time() - start_time
            if proc.returncode == 0:
                return {'success': True, 'output': proc.stdout.strip(), 'execution_time': f'{dt:.3f}s'}
            return {'success': False, 'error': proc.stderr.strip() or 'Runtime error occurred', 'error_type': 'runtime_error'}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': f'⏰ Time Limit Exceeded: Execution took longer than {time_limit}s', 'error_type': 'timeout'}
        except Exception as e:
            return {'success': False, 'error': f'❌ Runtime Error: {e}', 'error_type': 'runtime_error'}

    def _run_java(self, code: str, input_data: str, temp_dir: str, time_limit: int) -> dict:
        try:
            import re
            m = re.search(r'class\s+(\w+)', code)
            if not m:
                return {'success': False, 'error': '🔴 Compilation Error: No class found in Java code', 'error_type': 'compilation_error'}
            cls = m.group(1)
            src = os.path.join(temp_dir, f'{cls}.java')
            with open(src, 'w', encoding='utf-8') as f:
                f.write(code)
            comp = subprocess.run(['javac', src], capture_output=True, text=True, cwd=temp_dir)
            if comp.returncode != 0:
                return {'success': False, 'error': f'🔴 Compilation Error:\n{comp.stderr}', 'error_type': 'compilation_error'}

            start_time = time.time()
            proc = subprocess.run(['java', cls], input=input_data, capture_output=True, text=True, timeout=time_limit, cwd=temp_dir)
            dt = time.time() - start_time
            if proc.returncode == 0:
                return {'success': True, 'output': proc.stdout.strip(), 'execution_time': f'{dt:.3f}s'}
            return {'success': False, 'error': proc.stderr.strip() or 'Runtime error occurred', 'error_type': 'runtime_error'}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': f'⏰ Time Limit Exceeded: Execution took longer than {time_limit}s', 'error_type': 'timeout'}
        except Exception as e:
            return {'success': False, 'error': f'❌ Runtime Error: {e}', 'error_type': 'runtime_error'}

    def _run_c(self, code: str, input_data: str, temp_dir: str, time_limit: int) -> dict:
        try:
            src = os.path.join(temp_dir, 'solution.c')
            with open(src, 'w', encoding='utf-8') as f:
                f.write(code)
            exe = os.path.join(temp_dir, 'solution.exe')
            comp = subprocess.run(['gcc', '-O2', '-o', exe, src], capture_output=True, text=True, cwd=temp_dir)
            if comp.returncode != 0:
                return {'success': False, 'error': f'🔴 Compilation Error:\n{comp.stderr}', 'error_type': 'compilation_error'}

            start_time = time.time()
            proc = subprocess.run([exe], input=input_data, capture_output=True, text=True, timeout=time_limit, cwd=temp_dir)
            dt = time.time() - start_time
            if proc.returncode == 0:
                return {'success': True, 'output': proc.stdout.strip(), 'execution_time': f'{dt:.3f}s'}
            return {'success': False, 'error': proc.stderr.strip() or 'Runtime error occurred', 'error_type': 'runtime_error'}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': f'⏰ Time Limit Exceeded: Execution took longer than {time_limit}s', 'error_type': 'timeout'}
        except Exception as e:
            return {'success': False, 'error': f'❌ Runtime Error: {e}', 'error_type': 'runtime_error'}

    def _preprocess_cpp_code(self, code: str) -> str:
        if '#include<bits/stdc++.h>' in code:
            includes = (
                '#include <iostream>\n'
                '#include <vector>\n'
                '#include <string>\n'
                '#include <algorithm>\n'
                '#include <map>\n'
                '#include <set>\n'
                '#include <queue>\n'
                '#include <stack>\n'
                '#include <cmath>\n'
                '#include <cstring>\n'
                '#include <cstdio>\n'
                '#include <cstdlib>\n'
                '#include <climits>\n'
                '#include <cassert>\n'
                '#include <numeric>\n'
                '#include <unordered_map>\n'
                '#include <unordered_set>\n'
                '#include <bitset>\n'
                '#include <limits>\n'
            )
            return code.replace('#include<bits/stdc++.h>', includes)
        return code

    def _run_python_docker(self, code: str, input_data: str, temp_dir: str, time_limit: int) -> dict:
        try:
            src = os.path.join(temp_dir, 'solution.py')
            with open(src, 'w', encoding='utf-8') as f:
                f.write(code)
            command = f"sh -c \"echo '{input_data}' | python /workspace/solution.py\""
            start_time = time.time()
            normalized_temp_dir = self._normalize_path_for_docker(temp_dir)
            container = self.docker_client.containers.run('python:3.9-slim', command=command, volumes={normalized_temp_dir: {'bind': '/workspace', 'mode': 'rw'}}, working_dir='/workspace', detach=True, mem_limit='512m', network_disabled=True, pids_limit=20)
            try:
                result = container.wait(timeout=time_limit + 2)
                end_time = time.time()
                dt = end_time - start_time

                out = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore').strip()
                err = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore').strip()
                
                if result['StatusCode'] == 0:
                    return {'success': True, 'output': out, 'execution_time': f'{dt:.3f}s'}
                
                # Handle timeout specifically
                if result['StatusCode'] == 137: # Common exit code for killed processes (e.g., by timeout or OOM)
                    return {'success': False, 'error': f'⏰ Time Limit Exceeded: Execution took longer than {time_limit}s', 'error_type': 'timeout'}

                return {'success': False, 'error': err or 'Runtime error occurred', 'error_type': 'runtime_error'}
            finally:
                container.remove(force=True)
        except Exception as e:
            return {'success': False, 'error': str(e), 'error_type': 'runtime_error'}

    def _run_cpp_docker(self, code: str, input_data: str, temp_dir: str, time_limit: int) -> dict:
        try:
            code = self._preprocess_cpp_code(code)
            src = os.path.join(temp_dir, 'solution.cpp')
            with open(src, 'w', encoding='utf-8') as f:
                f.write(code)
            command = f"sh -c \"g++ -std=c++14 -O2 -o /workspace/solution /workspace/solution.cpp && echo '{input_data}' | /workspace/solution\""
            start_time = time.time()
            normalized_temp_dir = self._normalize_path_for_docker(temp_dir)
            container = self.docker_client.containers.run('gcc:latest', command=command, volumes={normalized_temp_dir: {'bind': '/workspace', 'mode': 'rw'}}, working_dir='/workspace', detach=True, mem_limit='512m', network_disabled=True, pids_limit=20)
            try:
                result = container.wait(timeout=time_limit + 2)
                end_time = time.time()
                dt = end_time - start_time

                out = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore').strip()
                err = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore').strip()
                
                if result['StatusCode'] == 0:
                    return {'success': True, 'output': out, 'execution_time': f'{dt:.3f}s'}
                
                # Handle timeout specifically
                if result['StatusCode'] == 137: # Common exit code for killed processes (e.g., by timeout or OOM)
                    return {'success': False, 'error': f'⏰ Time Limit Exceeded: Execution took longer than {time_limit}s', 'error_type': 'timeout'}

                if 'g++' in err or 'compilation' in err.lower():
                    print(f"DEBUG: C++ Compilation Error: {err}", file=sys.stderr) # Add this line
                    return {'success': False, 'error': err, 'error_type': 'compilation_error'}
                return {'success': False, 'error': err or 'Runtime error occurred', 'error_type': 'runtime_error'}
            finally:
                container.remove(force=True)
        except Exception as e:
            return {'success': False, 'error': str(e), 'error_type': 'runtime_error'}

    def _run_java_docker(self, code: str, input_data: str, temp_dir: str, time_limit: int) -> dict:
        try:
            import re
            m = re.search(r'class\s+(\w+)', code)
            if not m:
                return {'success': False, 'error': 'No class found in Java code', 'error_type': 'compilation_error'}
            cls = m.group(1)
            src = os.path.join(temp_dir, f'{cls}.java')
            with open(src, 'w', encoding='utf-8') as f:
                f.write(code)
            command = f"sh -c \"javac {cls}.java && echo '{input_data}' | java {cls}\""
            start_time = time.time()
            normalized_temp_dir = self._normalize_path_for_docker(temp_dir)
            container = self.docker_client.containers.run('openjdk:11-jdk-slim', command=command, volumes={normalized_temp_dir: {'bind': '/workspace', 'mode': 'rw'}}, working_dir='/workspace', detach=True, mem_limit='512m', network_disabled=True, pids_limit=20)
            try:
                result = container.wait(timeout=time_limit + 2)
                end_time = time.time()
                dt = end_time - start_time

                out = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore').strip()
                err = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore').strip()
                if result['StatusCode'] == 0:
                    return {'success': True, 'output': out, 'execution_time': f'{dt:.3f}s'}
                
                # Handle timeout specifically
                if result['StatusCode'] == 137: # Common exit code for killed processes (e.g., by timeout or OOM)
                    return {'success': False, 'error': f'⏰ Time Limit Exceeded: Execution took longer than {time_limit}s', 'error_type': 'timeout'}

                if 'javac' in err or 'compilation' in err.lower():
                    return {'success': False, 'error': err, 'error_type': 'compilation_error'}
                return {'success': False, 'error': err or 'Runtime error occurred', 'error_type': 'runtime_error'}
            finally:
                container.remove(force=True)
        except Exception as e:
            return {'success': False, 'error': str(e), 'error_type': 'runtime_error'}

    def _run_c_docker(self, code: str, input_data: str, temp_dir: str, time_limit: int) -> dict:
        try:
            src = os.path.join(temp_dir, 'solution.c')
            with open(src, 'w', encoding='utf-8') as f:
                f.write(code)
            command = f"sh -c \"gcc -O2 -o /workspace/solution /workspace/solution.c && echo '{input_data}' | /workspace/solution\""
            start_time = time.time()
            normalized_temp_dir = self._normalize_path_for_docker(temp_dir)
            container = self.docker_client.containers.run('gcc:latest', command=command, volumes={normalized_temp_dir: {'bind': '/workspace', 'mode': 'rw'}}, working_dir='/workspace', detach=True, mem_limit='512m', network_disabled=True, pids_limit=20)
            try:
                result = container.wait(timeout=time_limit + 2)
                end_time = time.time()
                dt = end_time - start_time

                out = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore').strip()
                err = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore').strip()
                
                if result['StatusCode'] == 0:
                    return {'success': True, 'output': out, 'execution_time': f'{dt:.3f}s'}
                
                # Handle timeout specifically
                if result['StatusCode'] == 137: # Common exit code for killed processes (e.g., by timeout or OOM)
                    return {'success': False, 'error': f'⏰ Time Limit Exceeded: Execution took longer than {time_limit}s', 'error_type': 'timeout'}

                if 'gcc' in err or 'compilation' in err.lower():
                    return {'success': False, 'error': err, 'error_type': 'compilation_error'}
                return {'success': False, 'error': err or 'Runtime error occurred', 'error_type': 'runtime_error'}
            finally:
                container.remove(force=True)
        except Exception as e:
            return {'success': False, 'error': str(e), 'error_type': 'runtime_error'}


secure_code_runner = SecureCodeRunner()