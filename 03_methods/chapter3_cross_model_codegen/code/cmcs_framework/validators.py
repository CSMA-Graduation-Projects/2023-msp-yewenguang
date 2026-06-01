"""
Code Validation Implementations for CMCS Framework

This module provides concrete implementations of code validators for use in the CMCS framework.
"""

import os
import sys
import importlib.util
import subprocess
import tempfile
import time
from typing import Dict, List, Tuple, Optional, Any
import json

from cmcs_framework.core import CodeValidator, ErrorType


class HumanEvalValidator(CodeValidator):
    """
    Implementation of a code validator for HumanEval dataset.
    """
    
    def __init__(self, execution_module_path: str):
        """
        Initialize the HumanEval validator.
        
        Args:
            execution_module_path: Path to the execution module for HumanEval
        """
        self.execution_module_path = execution_module_path
        self._load_execution_module()
    
    def _load_execution_module(self):
        """Load the execution module dynamically."""
        spec = importlib.util.spec_from_file_location("execution_module", self.execution_module_path)
        self.execution_module = importlib.util.module_from_spec(spec)
        sys.modules["execution_module"] = self.execution_module
        spec.loader.exec_module(self.execution_module)
    
    def validate_code(self, problem: Dict, code: str, timeout: float = 5.0) -> Tuple[bool, str, ErrorType]:
        """
        Validate the generated code against the problem using HumanEval execution module.
        
        Args:
            problem: Problem dictionary with prompt, test, and entry_point
            code: Generated code to validate
            timeout: Timeout for execution in seconds
            
        Returns:
            Tuple of (is_correct, error_message, error_type)
        """
        try:
            # Use the check_correctness function from the execution module
            result = self.execution_module.check_correctness(
                problem=problem,
                completion=code,
                timeout=timeout
            )
            
            if result.get("passed", False):
                return True, "", None
            else:
                # Determine error type based on result
                result_str = result.get("result", "")
                if "timed out" in result_str:
                    error_type = ErrorType.RUNTIME
                    error_message = f"Execution timed out after {timeout} seconds"
                elif "failed:" in result_str and any(err in result_str for err in ["SyntaxError", "NameError", "TypeError"]):
                    error_type = ErrorType.COMPILATION
                    error_message = result_str
                else:
                    error_type = ErrorType.TEST
                    error_message = result_str
                
                return False, error_message, error_type
                
        except Exception as e:
            # Handle exceptions during validation
            error_message = f"Validation error: {str(e)}"
            
            # Determine error type
            if "SyntaxError" in str(e) or "NameError" in str(e) or "TypeError" in str(e):
                error_type = ErrorType.COMPILATION
            else:
                error_type = ErrorType.RUNTIME
                
            return False, error_message, error_type


class HumanEvalPlusValidator(CodeValidator):
    """
    Implementation of a code validator for HumanEval+ dataset.
    """
    
    def __init__(self, execution_module_path: str):
        """
        Initialize the HumanEval+ validator.
        
        Args:
            execution_module_path: Path to the execution module for HumanEval+
        """
        self.execution_module_path = execution_module_path
        self._load_execution_module()
    
    def _load_execution_module(self):
        """Load the execution module dynamically."""
        spec = importlib.util.spec_from_file_location("execution_module_plus", self.execution_module_path)
        self.execution_module = importlib.util.module_from_spec(spec)
        sys.modules["execution_module_plus"] = self.execution_module
        spec.loader.exec_module(self.execution_module)
    
    def validate_code(self, problem: Dict, code: str, timeout: float = 5.0) -> Tuple[bool, str, ErrorType]:
        """
        Validate the generated code against the problem using HumanEval+ execution module.
        
        Args:
            problem: Problem dictionary with prompt, test, and entry_point
            code: Generated code to validate
            timeout: Timeout for execution in seconds
            
        Returns:
            Tuple of (is_correct, error_message, error_type)
        """
        try:
            # Use the check_correctness function from the execution module
            result = self.execution_module.check_correctness(
                problem=problem,
                completion=code,
                timeout=timeout
            )
            
            if result.get("passed", False):
                return True, "", None
            else:
                # Determine error type based on result
                result_str = result.get("result", "")
                if "timed out" in result_str:
                    error_type = ErrorType.RUNTIME
                    error_message = f"Execution timed out after {timeout} seconds"
                elif "failed:" in result_str and any(err in result_str for err in ["SyntaxError", "NameError", "TypeError"]):
                    error_type = ErrorType.COMPILATION
                    error_message = result_str
                else:
                    error_type = ErrorType.TEST
                    error_message = result_str
                
                return False, error_message, error_type
                
        except Exception as e:
            # Handle exceptions during validation
            error_message = f"Validation error: {str(e)}"
            
            # Determine error type
            if "SyntaxError" in str(e) or "NameError" in str(e) or "TypeError" in str(e):
                error_type = ErrorType.COMPILATION
            else:
                error_type = ErrorType.RUNTIME
                
            return False, error_message, error_type


class APPSValidator(CodeValidator):
    """
    Implementation of a code validator for APPS dataset.
    """
    
    def __init__(self, execution_module_path: str):
        """
        Initialize the APPS validator.
        
        Args:
            execution_module_path: Path to the execution module for APPS
        """
        self.execution_module_path = execution_module_path
        self._load_execution_module()
    
    def _load_execution_module(self):
        """Load the execution module dynamically."""
        spec = importlib.util.spec_from_file_location("execution_module_apps", self.execution_module_path)
        self.execution_module = importlib.util.module_from_spec(spec)
        sys.modules["execution_module_apps"] = self.execution_module
        spec.loader.exec_module(self.execution_module)
    
    def validate_code(self, problem: Dict, code: str, timeout: float = 5.0) -> Tuple[bool, str, ErrorType]:
        """
        Validate the generated code against the problem using APPS execution module.
        
        Args:
            problem: Problem dictionary
            code: Generated code to validate
            timeout: Timeout for execution in seconds
            
        Returns:
            Tuple of (is_correct, error_message, error_type)
        """
        try:
            result = self.execution_module.check_correctness(
                problem=problem,
                completion=code,
                timeout=timeout
            )
            
            if result.get("passed", False):
                return True, "", None
            else:
                result_str = str(result.get("errors", ""))
                if "TimeoutExpired" in result_str or "timed out" in result_str:
                    error_type = ErrorType.RUNTIME
                    error_message = f"Execution timed out after {timeout} seconds"
                elif any(err in result_str for err in ["SyntaxError", "NameError", "TypeError"]):
                    error_type = ErrorType.COMPILATION
                    error_message = result_str
                else:
                    error_type = ErrorType.TEST
                    error_message = result_str
                
                return False, error_message, error_type
                
        except Exception as e:
            error_message = f"Validation error: {str(e)}"
            
            if "SyntaxError" in str(e) or "NameError" in str(e) or "TypeError" in str(e):
                error_type = ErrorType.COMPILATION
            else:
                error_type = ErrorType.RUNTIME
                
            return False, error_message, error_type


class CodeContestValidator(CodeValidator):
    """
    Implementation of a code validator for CodeContest dataset.
    """
    
    def __init__(self, execution_module_path: str):
        """
        Initialize the CodeContest validator.
        
        Args:
            execution_module_path: Path to the execution module for CodeContest
        """
        self.execution_module_path = execution_module_path
        self._load_execution_module()
    
    def _load_execution_module(self):
        """Load the execution module dynamically."""
        spec = importlib.util.spec_from_file_location("execution_module_codecontest", self.execution_module_path)
        self.execution_module = importlib.util.module_from_spec(spec)
        sys.modules["execution_module_codecontest"] = self.execution_module
        spec.loader.exec_module(self.execution_module)
    
    def validate_code(self, problem: Dict, code: str, timeout: float = 5.0) -> Tuple[bool, str, ErrorType]:
        """
        Validate the generated code against the problem using CodeContest execution module.
        
        Args:
            problem: Problem dictionary
            code: Generated code to validate
            timeout: Timeout for execution in seconds
            
        Returns:
            Tuple of (is_correct, error_message, error_type)
        """
        try:
            result = self.execution_module.check_correctness(
                problem=problem,
                code=code,
                timeout=timeout
            )
            
            if result.get("passed", False):
                return True, "", None
            else:
                result_str = result.get("result", "")
                if "timeout" in result_str.lower() or "timed out" in result_str.lower():
                    error_type = ErrorType.RUNTIME
                    error_message = result_str
                elif any(err in result_str for err in ["SyntaxError", "NameError", "TypeError"]):
                    error_type = ErrorType.COMPILATION
                    error_message = result_str
                else:
                    error_type = ErrorType.TEST
                    error_message = result_str
                
                return False, error_message, error_type
                
        except Exception as e:
            error_message = f"Validation error: {str(e)}"
            
            if "SyntaxError" in str(e) or "NameError" in str(e) or "TypeError" in str(e):
                error_type = ErrorType.COMPILATION
            else:
                error_type = ErrorType.RUNTIME
                
            return False, error_message, error_type


class MBPPValidator(CodeValidator):
    """
    Implementation of a code validator for MBPP dataset.
    """
    
    def __init__(self, execution_module_path: str):
        """
        Initialize the MBPP validator.
        
        Args:
            execution_module_path: Path to the execution module for MBPP
        """
        self.execution_module_path = execution_module_path
        self._load_execution_module()
    
    def _load_execution_module(self):
        """Load the execution module dynamically."""
        spec = importlib.util.spec_from_file_location("execution_module_mbpp", self.execution_module_path)
        self.execution_module = importlib.util.module_from_spec(spec)
        sys.modules["execution_module_mbpp"] = self.execution_module
        spec.loader.exec_module(self.execution_module)
    
    def validate_code(self, problem: Dict, code: str, timeout: float = 5.0) -> Tuple[bool, str, ErrorType]:
        """
        Validate the generated code against the problem using MBPP execution module.
        
        Args:
            problem: Problem dictionary
            code: Generated code to validate
            timeout: Timeout for execution in seconds
            
        Returns:
            Tuple of (is_correct, error_message, error_type)
        """
        try:
            result = self.execution_module.check_correctness(
                problem=problem,
                code=code,
                timeout=timeout
            )
            
            if result.get("passed", False):
                return True, "", None
            else:
                result_str = result.get("result", "")
                if "timeout" in result_str.lower() or "timed out" in result_str.lower():
                    error_type = ErrorType.RUNTIME
                    error_message = result_str
                elif any(err in result_str for err in ["SyntaxError", "NameError", "TypeError"]):
                    error_type = ErrorType.COMPILATION
                    error_message = result_str
                else:
                    error_type = ErrorType.TEST
                    error_message = result_str
                
                return False, error_message, error_type
                
        except Exception as e:
            error_message = f"Validation error: {str(e)}"
            
            if "SyntaxError" in str(e) or "NameError" in str(e) or "TypeError" in str(e):
                error_type = ErrorType.COMPILATION
            else:
                error_type = ErrorType.RUNTIME
                
            return False, error_message, error_type


class MBPPPlusValidator(CodeValidator):
    """
    Implementation of a code validator for MBPP+ dataset.
    """
    
    def __init__(self, execution_module_path: str):
        """
        Initialize the MBPP+ validator.
        
        Args:
            execution_module_path: Path to the execution module for MBPP+
        """
        self.execution_module_path = execution_module_path
        self._load_execution_module()
    
    def _load_execution_module(self):
        """Load the execution module dynamically."""
        spec = importlib.util.spec_from_file_location("execution_module_mbpp_plus", self.execution_module_path)
        self.execution_module = importlib.util.module_from_spec(spec)
        sys.modules["execution_module_mbpp_plus"] = self.execution_module
        spec.loader.exec_module(self.execution_module)
    
    def validate_code(self, problem: Dict, code: str, timeout: float = 5.0) -> Tuple[bool, str, ErrorType]:
        """
        Validate the generated code against the problem using MBPP+ execution module.
        
        Args:
            problem: Problem dictionary
            code: Generated code to validate
            timeout: Timeout for execution in seconds
            
        Returns:
            Tuple of (is_correct, error_message, error_type)
        """
        try:
            result = self.execution_module.check_correctness(
                problem=problem,
                code=code,
                timeout=timeout
            )
            
            if result.get("passed", False):
                return True, "", None
            else:
                result_str = result.get("result", "")
                if "timeout" in result_str.lower() or "timed out" in result_str.lower():
                    error_type = ErrorType.RUNTIME
                    error_message = result_str
                elif any(err in result_str for err in ["SyntaxError", "NameError", "TypeError"]):
                    error_type = ErrorType.COMPILATION
                    error_message = result_str
                else:
                    error_type = ErrorType.TEST
                    error_message = result_str
                
                return False, error_message, error_type
                
        except Exception as e:
            error_message = f"Validation error: {str(e)}"
            
            if "SyntaxError" in str(e) or "NameError" in str(e) or "TypeError" in str(e):
                error_type = ErrorType.COMPILATION
            else:
                error_type = ErrorType.RUNTIME
                
            return False, error_message, error_type


class SimpleValidator(CodeValidator):
    """
    Simple implementation of a code validator for testing purposes.
    """
    
    def validate_code(self, problem: Dict, code: str, timeout: float = 5.0) -> Tuple[bool, str, ErrorType]:
        """
        Simple validation that checks for basic syntax errors.
        
        Args:
            problem: Problem dictionary with prompt, test, and entry_point
            code: Generated code to validate
            timeout: Timeout for execution in seconds
            
        Returns:
            Tuple of (is_correct, error_message, error_type)
        """
        try:
            # Try to compile the code
            compile(code, '<string>', 'exec')
            
            # For simple validation, we'll just check if it compiles
            # In a real implementation, you would run the actual tests
            return True, "", None
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}", ErrorType.COMPILATION
        except Exception as e:
            return False, f"Error: {str(e)}", ErrorType.RUNTIME