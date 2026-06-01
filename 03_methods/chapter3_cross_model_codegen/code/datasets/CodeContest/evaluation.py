import subprocess
import sys
import time
import os
import tempfile
import numpy as np  # Import numpy to check for ndarray type


# Helper function to compare outputs, ignoring leading/trailing whitespace
def compare_outputs(actual_output, expected_output):
    """
    Compares two output strings.
    Standard practice is to strip leading/trailing whitespace before comparing.
    """
    actual_str = str(actual_output) if actual_output is not None else ""
    expected_str = str(expected_output) if expected_output is not None else ""
    return actual_str.strip() == expected_str.strip()


# Function to evaluate the generated code against test cases
def check_correctness(problem_data, generated_python_code, timeout_seconds=10.0):  # Modified signature
    """
    Evaluates generated Python code on a single code_contests problem data.
    Can now handle test cases where inputs/outputs are lists or numpy.ndarrays.
    Includes necessary details (input, expected output, status) in error messages upon failure.
    Implements both a subprocess timeout (passed as a parameter) and a stricter check
    against problem-defined time limits.

    Args:
        problem_data (dict): Dictionary containing all info for a single problem.
        generated_python_code (str): The Python code string to evaluate.
        timeout_seconds (float): The timeout in seconds for each test case execution
                                 in the subprocess. Defaults to 10.0.

    Returns:
        dict: Dictionary containing evaluation results:
              {
                  'passed': bool,
                  'passed_count': int,
                  'failed_count': int,
                  'total_count': int,
                  'result': list[dict] # List with failure details
              }
              May return an error dictionary if problem_data is invalid.
    """
    if not isinstance(problem_data, dict) or 'name' not in problem_data:
        return {"error": "Invalid problem_data input. Expected a dictionary with at least a 'name' field."}

    problem_name = problem_data.get('name', 'Unknown Problem')

    # --- 1. Collect all test cases ---
    all_tests = []
    test_sources = {
        'public': problem_data.get('public_tests'),
        'private': problem_data.get('private_tests'),
        'generated': problem_data.get('generated_tests')
    }

    for test_type, tests in test_sources.items():
        if tests and isinstance(tests, dict):
            inputs_raw = tests.get('input')
            outputs_raw = tests.get('output')

            is_input_valid = isinstance(inputs_raw, (list, np.ndarray))
            is_output_valid = isinstance(outputs_raw, (list, np.ndarray))

            if is_input_valid and is_output_valid:
                if len(inputs_raw) == len(outputs_raw):
                    for i in range(len(inputs_raw)):
                        input_item = inputs_raw[i]
                        output_item = outputs_raw[i]

                        if input_item is not None and output_item is not None:
                            all_tests.append({
                                "input": str(input_item),
                                "expected_output": str(output_item),
                                "type": test_type,
                                "index_in_type": i
                            })
                        else:
                            print(
                                f"Warning [Eval-{problem_name}]: Found None in {test_type} test index {i}. Skipping item.")
                else:
                    print(
                        f"Warning [Eval-{problem_name}]: Mismatched input ({len(inputs_raw)}) / output ({len(outputs_raw)}) count for {test_type} tests. Skipping type.")

    if not all_tests:
        print(f"Warning [Eval-{problem_name}]: No valid test cases could be extracted.")
        return {
            "passed": True,
            "passed_count": 0,
            "failed_count": 0,
            "total_count": 0,
            "result": ["No valid executable tests found."]
        }

    # --- 2. Get problem-specific execution limit (for strict check) ---
    time_limit_dict = problem_data.get('time_limit')
    # problem_time_limit is the strict limit defined for the problem
    problem_time_limit = None

    if time_limit_dict and isinstance(time_limit_dict, dict):
        parsed_time_limit = time_limit_dict.get('seconds', 0) + time_limit_dict.get('nanos', 0) / 1e9
        if parsed_time_limit > 0:
            problem_time_limit = parsed_time_limit
        else:
            # timeout_seconds (parameter) is used for subprocess, this warning is about problem_data
            print(
                f"Warning [Eval-{problem_name}]: Invalid problem-defined time limit ({parsed_time_limit}). Subprocess timeout is {timeout_seconds:.2f}s.")
            # problem_time_limit remains None

    # The `timeout_seconds` parameter is used directly for subprocess.run
    # print(f"Info [Eval-{problem_name}]: Using subprocess timeout: {timeout_seconds:.2f}s. Problem-defined time limit for strict check: {problem_time_limit if problem_time_limit is not None else 'N/A'}s.")

    # --- 3. Prepare execution environment ---
    passed_count = 0
    failed_count = 0
    error_details = []  # Stores details for failed tests only
    tmp_code_file_path = None

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp_code_file:
            tmp_code_file_path = tmp_code_file.name
            tmp_code_file.write(generated_python_code)

        # --- 4. Run test cases ---
        for i, test_spec in enumerate(all_tests):
            input_data = test_spec["input"]
            expected_output = test_spec["expected_output"]
            test_type = test_spec["type"]
            index_in_type = test_spec["index_in_type"]
            test_identifier = f"{problem_name} - {test_type}_test[{index_in_type}] (Overall {i + 1}/{len(all_tests)})"

            status = "Unknown"
            current_test_failure_details = {
                "test_identifier": test_identifier,
                "full_input": input_data,
                "expected_output": expected_output,
            }
            if problem_time_limit is not None:
                current_test_failure_details["problem_defined_time_limit_seconds"] = problem_time_limit

            try:
                start_time = time.monotonic()
                process = subprocess.run(
                    [sys.executable, tmp_code_file_path],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,  # Use the passed-in timeout_seconds
                    encoding='utf-8',
                    errors='replace',
                    check=False
                )
                end_time = time.monotonic()
                duration = end_time - start_time
                current_test_failure_details["duration_seconds"] = duration

                if process.returncode != 0:
                    status = "Runtime Error"
                    current_test_failure_details.update({
                        "stderr": process.stderr.strip() if process.stderr else "N/A",
                        "return_code": process.returncode,
                        "raw_actual_output": process.stdout
                    })
                elif problem_time_limit is not None and duration > problem_time_limit:
                    status = "Time Limit Exceeded"  # Exceeded problem's specific time limit
                    current_test_failure_details.update({
                        "raw_actual_output": process.stdout
                    })
                elif compare_outputs(process.stdout, expected_output):
                    status = "Passed"
                else:
                    status = "Wrong Answer"
                    current_test_failure_details.update({
                        "actual_output": process.stdout,
                    })

            except subprocess.TimeoutExpired:
                status = "Time Limit Exceeded"  # Exceeded subprocess hard timeout
                current_test_failure_details.pop("duration_seconds", None)
                # Report the timeout_seconds value that was actually used for the subprocess
                current_test_failure_details["subprocess_timeout_seconds"] = timeout_seconds

            except Exception as e:
                status = "Evaluation Error"
                current_test_failure_details["error_message"] = str(e)

            if status == "Passed":
                passed_count += 1
            else:
                failed_count += 1
                current_test_failure_details["status"] = status
                error_details.append(current_test_failure_details)

    finally:
        if tmp_code_file_path and os.path.exists(tmp_code_file_path):
            try:
                os.remove(tmp_code_file_path)
            except OSError as e:
                print(f"Warning [Eval-{problem_name}]: Could not remove temp file {tmp_code_file_path}: {e}")

    # --- 5. Assemble overall results ---
    total_count = len(all_tests)
    passed_all_tests = (failed_count == 0 and total_count > 0) if total_count > 0 else True

    return {
        "passed": passed_all_tests,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "total_count": total_count,
        "result": error_details
    }