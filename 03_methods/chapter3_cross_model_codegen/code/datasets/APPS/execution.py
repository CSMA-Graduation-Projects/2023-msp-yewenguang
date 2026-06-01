import json
import signal
import subprocess
import tempfile
from typing import Dict, Optional, List
import torch
import subprocess
import os
import re
import ast

# 定义超时处理函数
def timeout_handler(signum, frame):
    raise TimeoutError("Execution exceeded time limit.")

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


def remove_examples_and_tests(code):
    # Regular expression to match lines with the specified patterns
    pattern = re.compile(r'#\s*(Example|Test|example|test).*')

    # Split code into lines
    lines = code.split('\n')

    # Remove content after the matching patterns
    cleaned_lines = [re.sub(pattern, '', line) for line in lines]

    # Join the cleaned lines back into a single string
    cleaned_code = '\n'.join(cleaned_lines)
    return cleaned_code.strip()

def check_correctness(problem, completion, timeout, completion_id=None, include_private=True):
    """检查代码是否通过测试用例"""
    tests = []  # 存储测试结果的列表
    errors = []  # 存储错误信息的列表
    all_tests_passed = True  # 默认所有测试通过
    code_file_path = "temp_code.py"

    print(f"function_header: {problem['starter_code']}")
    
    code = remove_examples_and_tests(completion)
    if not has_input_statements(completion):
        function_name = extract_function_name(problem['starter_code'])
        if function_name:
            code = "import ast\n\n" + completion + f"""
if __name__ == "__main__":
    user_input = input()

    try:
        # 使用ast.literal_eval安全地评估输入
        user_input = ast.literal_eval(user_input)
    except (ValueError, SyntaxError):
        # 如果评估失败，保持原样
        pass

    result = {function_name}(user_input)
    print(result)
    """
    print(f"code: {code}")

    # 写入临时代码文件
    with open(code_file_path, "w") as file:
        file.write(code)

    def run_test(test_in, expected_out):
        """运行单个测试"""
        nonlocal all_tests_passed  # 声明使用外层作用域的变量
        test_result = {
            'test_in': test_in,
            'expected_out': f'{expected_out[0]}',
            'actual_out': None,
            'passed': False,  # 默认未通过
            'error': None  # 初始化error为None
        }
        try:
            result = subprocess.run(
                ['python3', code_file_path],  # 使用 python 运行临时代码文件
                input=test_in,  # 模拟输入
                text=True,  # 将输入输出当作字符串处理
                capture_output=True,  # 捕获标准输出
                timeout=timeout  # 设置超时
            )
            output = result.stdout.strip()  # 获取执行结果输出
            test_result['actual_out'] = output
            test_result['passed'] = (output == f'{expected_out[0]}')  # 比较期望值和实际值
            if not test_result['passed']:
                all_tests_passed = False  # 发现失败的测试
                test_result['error'] = f"Expected: {expected_out[0]}, Got: {output}"  # 记录错误信息
                errors.append(test_result)  # 将失败的测试添加到errors列表中
            if result.stderr.strip():
                test_result['error'] = result.stderr.strip()  # 捕获错误信息
                errors.append(test_result)  # 将失败的测试添加到errors列表中
        except Exception as e:
            all_tests_passed = False  # 异常情况标记测试失败
            test_result['error'] = str(e)
            errors.append(test_result)  # 将失败的测试添加到errors列表中
        return test_result

    # 遍历每个测试样例
    for sample in problem['sample_io']:
        input_data = sample['input']  # 输入数据 (字符串形式)
        expected_output = sample['output']  # 期望输出
        test_result = run_test(input_data, expected_output)
        tests.append(test_result)

    if include_private:
        for sample in problem['test_list']:
            input_data = sample['input']  # 输入数据 (字符串形式)
            expected_output = sample['output']  # 期望输出
            test_result = run_test(input_data, expected_output)
            tests.append(test_result)

    if os.path.exists(code_file_path):
        os.remove(code_file_path)

    return {
        'passed': all_tests_passed,
        'tests': tests,
        'errors': errors  # 返回所有失败的测试和其错误信息
    }


def extract_function_name(function_header):
    """
    从函数头提取函数名。

    :param function_header: 函数头字符串（如 'def get_score(dice):'）
    :return: 提取的函数名称字符串
    """
    # 正则表达式匹配函数名
    match = re.match(r"def\s+(\w+)\s*\(", function_header.strip())
    if match:
        return match.group(1)
    else:
        return "Invalid function header"