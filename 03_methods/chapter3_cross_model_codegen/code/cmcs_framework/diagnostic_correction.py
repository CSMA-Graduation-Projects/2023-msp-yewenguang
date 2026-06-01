"""
Diagnostic Correction Mechanism Module

This module implements the diagnostic correction mechanism component of the CMCS framework.
"""

import time
from typing import Dict, List, Tuple, Optional

from cmcs_framework.core import BaseLLMModel, ModelType, CodeGenerationResult, CodeValidator, ErrorType


class DiagnosticCorrectionMechanism:
    """
    Implementation of the diagnostic correction mechanism component.
    
    This component is responsible for:
    1. Validating the initial code generation results
    2. Categorizing errors into compilation, runtime, and test errors
    3. Applying a self-correction loop with feedback
    4. Iteratively fixing errors until the code passes all tests or max attempts are reached
    """
    
    def __init__(self, model_a: BaseLLMModel, model_b: BaseLLMModel, 
                 validator: CodeValidator, max_correction_attempts: int = 5):
        """
        Initialize the diagnostic correction mechanism.
        
        Args:
            model_a: First LLM model
            model_b: Second LLM model
            validator: Code validator
            max_correction_attempts: Maximum number of correction attempts
        """
        self.model_a = model_a
        self.model_b = model_b
        self.validator = validator
        self.max_correction_attempts = max_correction_attempts
    
    def validate_and_categorize_error(self, problem: Dict, code: str) -> Tuple[bool, str, ErrorType]:
        """
        Validate the generated code and categorize any errors.
        
        Args:
            problem: Problem dictionary with prompt, test, and entry_point
            code: Generated code to validate
            
        Returns:
            Tuple of (is_correct, error_message, error_type)
        """
        return self.validator.validate_code(problem, code)
    
    def create_error_feedback_prompt(self, prompt: str, code: str, error_message: str, 
                                   error_type: ErrorType) -> str:
        """
        Create a feedback prompt based on the error type and message.
        
        Args:
            prompt: Original problem prompt
            code: Generated code with errors
            error_message: Error message from validation
            error_type: Type of error
            
        Returns:
            Feedback prompt string
        """
        if error_type == ErrorType.COMPILATION:
            return f"""Assuming you are a professional coding expert.

The following is Python code description and incorrect Python program translation and feedback.
```Python code description
{prompt}
```
```Incorrect Python program translation
{code}
```
```Feedback:
Compilation error: {error_message}
```

You should check the feedback, analyze and explain and correct errors in Incorrect Python program translation based on Python code descriptions and provide the complete modified Python code within triple backticks ```python ``` in the end!"""
        
        elif error_type == ErrorType.RUNTIME:
            return f"""Assuming you are a professional coding expert.

The following is Python code description and incorrect Python program translation and feedback.
```Python code description
{prompt}
```
```Incorrect Python program translation
{code}
```
```Feedback:
Runtime error: {error_message}
```

You should check the feedback, analyze and explain and correct errors in Incorrect Python program translation based on Python code descriptions and provide the complete modified Python code within triple backticks ```python ``` in the end!"""
        
        elif error_type == ErrorType.TEST:
            return f"""Assuming you are a professional coding expert.

The following is Python code description and incorrect Python program translation and feedback.
```Python code description
{prompt}
```
```Incorrect Python program translation
{code}
```
```Feedback:
Test failed: {error_message}
```

You should check the feedback, analyze and explain and correct errors in Incorrect Python program translation based on Python code descriptions and provide the complete modified Python code within triple backticks ```python ``` in the end!"""
        
        else:
            return f"""Assuming you are a professional coding expert.

The following is Python code description and incorrect Python program translation and feedback.
```Python code description
{prompt}
```
```Incorrect Python program translation
{code}
```
```Feedback:
Error: {error_message}
```

You should check the feedback, analyze and explain and correct errors in Incorrect Python program translation based on Python code descriptions and provide the complete modified Python code within triple backticks ```python ``` in the end!"""
    
    def fix_code_with_model(self, model: BaseLLMModel, prompt: str, code: str, 
                           error_message: str, error_type: ErrorType) -> str:
        """
        Fix code using the specified model based on error feedback.
        
        Args:
            model: The model to use for fixing
            prompt: Original problem prompt
            code: Generated code with errors
            error_message: Error message from validation
            error_type: Type of error
            
        Returns:
            Fixed code as a string
        """
        # Create feedback prompt
        feedback_prompt = self.create_error_feedback_prompt(prompt, code, error_message, error_type)
        
        # Generate fixed code
        fixed_code = model.fix_code(prompt, code, error_message)
        
        return fixed_code
    
    def apply_correction_loop(self, task_id: str, problem: Dict, initial_result: CodeGenerationResult) -> CodeGenerationResult:
        """
        Apply the correction loop to fix errors in the generated code.
        
        Args:
            task_id: ID of the task
            problem: Problem dictionary
            initial_result: Initial code generation result
            
        Returns:
            Final result after correction attempts
        """
        # Start with the initial result
        current_result = initial_result
        current_result.add_to_history(initial_result)  # Save initial attempt
        
        # Validate the initial code
        is_correct, error_message, error_type = self.validate_and_categorize_error(
            problem, current_result.generated_code
        )
        
        current_result.is_correct = is_correct
        current_result.error_message = error_message
        current_result.error_type = error_type
        
        # If already correct, no need for correction
        if is_correct:
            return current_result
            
        # Apply correction mechanism
        for attempt in range(1, self.max_correction_attempts + 1):
            # Select the appropriate model for correction
            model = self.model_a if current_result.model_type == ModelType.MODEL_A else self.model_b
            
            # Generate fixed code
            fixed_code = self.fix_code_with_model(
                model, current_result.prompt, current_result.generated_code, 
                current_result.error_message, current_result.error_type
            )
            
            # Create new result for this attempt
            new_result = CodeGenerationResult(
                task_id=task_id,
                prompt=current_result.prompt,
                generated_code=fixed_code,
                model_type=current_result.model_type,
                attempt_count=attempt
            )
            
            # Validate the fixed code
            is_correct, error_message, error_type = self.validate_and_categorize_error(
                problem, fixed_code
            )
            
            new_result.is_correct = is_correct
            new_result.error_message = error_message
            new_result.error_type = error_type
            
            # Add to history
            current_result.add_to_history(new_result)
            
            # Update current result
            current_result = new_result
            
            # If fixed, break the loop
            if is_correct:
                break
                
        return current_result
    
    def correct_results(self, results: Dict[str, CodeGenerationResult], 
                       problems: Dict[str, Dict]) -> Dict[str, CodeGenerationResult]:
        """
        Apply diagnostic correction to all results.
        
        Args:
            results: Initial code generation results
            problems: Original problems
            
        Returns:
            Updated results after correction attempts
        """
        corrected_results = {}
        
        for task_id, result in results.items():
            problem = problems[task_id]
            corrected_result = self.apply_correction_loop(task_id, problem, result)
            corrected_results[task_id] = corrected_result
            
        return corrected_results
    
    def get_correction_statistics(self, results_before: Dict[str, CodeGenerationResult], 
                                 results_after: Dict[str, CodeGenerationResult]) -> Dict[str, any]:
        """
        Get statistics about the correction process.
        
        Args:
            results_before: Results before correction
            results_after: Results after correction
            
        Returns:
            Dictionary of correction statistics
        """
        total = len(results_before)
        correct_before = sum(1 for r in results_before.values() if r.is_correct)
        correct_after = sum(1 for r in results_after.values() if r.is_correct)
        
        # Count by error type
        error_types_before = {}
        error_types_after = {}
        
        for r in results_before.values():
            if not r.is_correct and r.error_type:
                error_type = r.error_type.value
                error_types_before[error_type] = error_types_before.get(error_type, 0) + 1
                
        for r in results_after.values():
            if not r.is_correct and r.error_type:
                error_type = r.error_type.value
                error_types_after[error_type] = error_types_after.get(error_type, 0) + 1
        
        # Count by attempt number
        attempt_counts = {}
        for r in results_after.values():
            attempt = r.attempt_count
            attempt_counts[attempt] = attempt_counts.get(attempt, 0) + 1
        
        return {
            "total_problems": total,
            "correct_before": correct_before,
            "correct_after": correct_after,
            "improvement": correct_after - correct_before,
            "improvement_rate": (correct_after - correct_before) / total if total > 0 else 0,
            "error_types_before": error_types_before,
            "error_types_after": error_types_after,
            "attempt_distribution": attempt_counts
        }