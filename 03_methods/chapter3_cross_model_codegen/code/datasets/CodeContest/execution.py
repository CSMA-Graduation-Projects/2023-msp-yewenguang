import torch
import subprocess
import os
import ast

def cleanup_gpu():
    """清理显存缓存"""
    torch.cuda.empty_cache()

def has_input_statements(code: str) -> bool:
    """
    检查代码是否包含用户输入的行为。

    :param code: 待检查的代码字符串
    :return: 如果代码中包含输入行为，返回 True，否则返回 False
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"代码解析失败: {e}")
        return False

    for node in ast.walk(tree):
        # 检查是否有 input() 函数调用
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "input":
            return True

        # 检查是否有访问 sys.stdin
        if isinstance(node, ast.Attribute) and node.attr == "stdin":
            return True

    return False


def extract_function_names(code: str) -> list:
    """
    提取代码中的所有函数名。

    :param code: 待检查的代码字符串
    :return: 包含所有函数名的列表
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"代码解析失败: {e}")
        return []

    function_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_names.append(node.name)
    return function_names


def check_correctness(problem, completion, timeout, completion_id=None, include_private=True):
    """检查代码是否通过测试用例"""
    tests = []  # 存储测试结果的列表
    all_tests_passed = True  # 默认所有测试通过
    errors = []  # 存储失败的测试的错误信息
    code_file_path = "temp_code.py"

    if not has_input_statements(completion):
        function_names = extract_function_names(completion)
        if function_names:
            code = "import ast\n\n" + completion + f"""
if __name__ == "__main__":
    user_input = input()

    try:
        # 使用ast.literal_eval安全地评估输入
        user_input = ast.literal_eval(user_input)
    except (ValueError, SyntaxError):
        # 如果评估失败，保持原样
        pass

    result = {function_names[0]}(user_input)
    print(result)
    """
            print(f"code: {code}")

    # 写入临时代码文件
    with open(code_file_path, "w") as file:
        file.write(completion)

    def run_test(test_in, expected_out):
        """运行单个测试"""
        test_result = {
            'test_in': test_in,
            'expected_out': expected_out,
            'actual_out': None,
            'passed': False  # 默认未通过
        }
        nonlocal all_tests_passed
        try:
            result = subprocess.run(
                ['python3', code_file_path],
                input=test_in,
                text=True,
                capture_output=True,
                timeout=timeout  # 设置超时
            )
            output = result.stdout.strip()
            test_result['actual_out'] = output
            test_result['passed'] = (output == expected_out.strip())
            if not test_result['passed']:
                all_tests_passed = False
                errors.append({'test_in': test_in, 'error': f"Expected: {expected_out}, Got: {output}"})
            if result.stderr.strip():
                test_result['error'] = result.stderr.strip()
                errors.append({'test_in': test_in, 'error': result.stderr.strip()})
        except subprocess.TimeoutExpired:
            all_tests_passed = False
            test_result['error'] = "TimeoutExpired"
            errors.append({'test_in': test_in, 'error': "Execution timed out."})
        except Exception as e:
            all_tests_passed = False
            test_result['error'] = str(e)
            errors.append({'test_in': test_in, 'error': str(e)})
        return test_result

    def run_all_tests(tests_input, tests_output):
        """运行所有测试并记录结果"""
        for test_in, expected_out in zip(tests_input, tests_output):
            tests.append(run_test(test_in, expected_out))

    # 运行公共测试
    run_all_tests(problem['public_tests']['input'], problem['public_tests']['output'])

    # 运行私有测试（如果启用）
    if include_private:
        run_all_tests(problem['private_tests']['input'], problem['private_tests']['output'])

    cleanup_gpu()  # 所有测试完成后清理显存

    # 删除临时代码文件
    if os.path.exists(code_file_path):
        os.remove(code_file_path)

    return {
        'passed': all_tests_passed,
        'tests': tests,
        'errors': errors  # 返回失败测试的错误信息
    }


import ast


