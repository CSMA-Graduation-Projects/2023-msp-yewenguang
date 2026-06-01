"""
CMCS Framework Core Classes

This module defines the core classes for the Collaborative Multi-model Code Generation Scheme (CMCS) framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional, Union
import random
import time
import json
from enum import Enum

# Import dataset processors
from datasets.dataset_processor import DatasetProcessor


class ErrorType(Enum):
    """Enumeration of different error types in code generation."""
    COMPILATION = "compilation"
    RUNTIME = "runtime"
    TEST = "test"


class ModelType(Enum):
    """Enumeration of model types used in CMCS."""
    MODEL_A = "model_a"
    MODEL_B = "model_b"


class CodeGenerationResult:
    """Class to store the result of code generation attempts."""
    
    def __init__(self, task_id: str, prompt: str, generated_code: str = "", 
                 is_correct: bool = False, error_type: Optional[ErrorType] = None,
                 error_message: str = "", execution_time: float = 0.0,
                 model_type: Optional[ModelType] = None, attempt_count: int = 0):
        self.task_id = task_id
        self.prompt = prompt
        self.generated_code = generated_code
        self.is_correct = is_correct
        self.error_type = error_type
        self.error_message = error_message
        self.execution_time = execution_time
        self.model_type = model_type
        self.attempt_count = attempt_count
        self.history = []  # Store history of attempts
        
    def add_to_history(self, result: 'CodeGenerationResult'):
        """Add a result to the history."""
        self.history.append(result)
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "prompt": self.prompt,
            "generated_code": self.generated_code,
            "is_correct": self.is_correct,
            "error_type": self.error_type.value if self.error_type else None,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
            "model_type": self.model_type.value if self.model_type else None,
            "attempt_count": self.attempt_count,
            "history": [h.to_dict() for h in self.history]
        }


class BaseLLMModel(ABC):
    """Abstract base class for LLM models used in CMCS."""
    
    def __init__(self, model_name: str, model_type: ModelType):
        self.model_name = model_name
        self.model_type = model_type
        
    @abstractmethod
    def generate_code(self, prompt: str, additional_context: str = "") -> str:
        """Generate code based on the given prompt."""
        pass
    
    @abstractmethod
    def fix_code(self, prompt: str, code: str, error_message: str) -> str:
        """Fix code based on error message."""
        pass


class CodeValidator(ABC):
    """Abstract base class for code validation."""
    
    @abstractmethod
    def validate_code(self, problem: Dict, code: str, timeout: float = 5.0) -> Tuple[bool, str, ErrorType]:
        """
        Validate the generated code against the problem.
        
        Returns:
            Tuple of (is_correct, error_message, error_type)
        """
        pass


class CMCSFramework:
    """
    Main class for the Collaborative Multi-model Code Generation Scheme (CMCS) framework.
    
    This class orchestrates the three main components:
    1. Dual-Model Collaborative Code Generation
    2. Diagnostic Correction Mechanism
    3. Cross-Model Collaborative Generation
    """
    
    def __init__(self, model_a: BaseLLMModel, model_b: BaseLLMModel, 
                 validator: CodeValidator, max_correction_attempts: int = 5):
        """
        Initialize the CMCS framework.
        
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
        self.results = {}  # Store results for each task
        
    def partition_problems(self, problems: Dict[str, Dict]) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
        """
        Partition the problems into two disjoint subsets for parallel processing.
        
        Args:
            problems: Dictionary of problems to partition
            
        Returns:
            Tuple of (problems_for_model_a, problems_for_model_b)
        """
        problem_ids = list(problems.keys())
        random.shuffle(problem_ids)
        
        mid = len(problem_ids) // 2
        ids_a = problem_ids[:mid]
        ids_b = problem_ids[mid:]
        
        problems_a = {pid: problems[pid] for pid in ids_a}
        problems_b = {pid: problems[pid] for pid in ids_b}
        
        return problems_a, problems_b
    
    def dual_model_collaborative_generation(self, problems_a: Dict[str, Dict], 
                                           problems_b: Dict[str, Dict]) -> Dict[str, CodeGenerationResult]:
        """
        Perform dual-model collaborative code generation.
        
        Args:
            problems_a: Problems for model A
            problems_b: Problems for model B
            
        Returns:
            Dictionary of task_id to CodeGenerationResult
        """
        results = {}
        
        # Process problems with model A
        for task_id, problem in problems_a.items():
            start_time = time.time()
            generated_code = self.model_a.generate_code(problem["prompt"])
            execution_time = time.time() - start_time
            
            result = CodeGenerationResult(
                task_id=task_id,
                prompt=problem["prompt"],
                generated_code=generated_code,
                model_type=ModelType.MODEL_A,
                execution_time=execution_time
            )
            
            results[task_id] = result
            
        # Process problems with model B
        for task_id, problem in problems_b.items():
            start_time = time.time()
            generated_code = self.model_b.generate_code(problem["prompt"])
            execution_time = time.time() - start_time
            
            result = CodeGenerationResult(
                task_id=task_id,
                prompt=problem["prompt"],
                generated_code=generated_code,
                model_type=ModelType.MODEL_B,
                execution_time=execution_time
            )
            
            results[task_id] = result
            
        return results
    
    def diagnostic_correction_mechanism(self, results: Dict[str, CodeGenerationResult], 
                                      problems: Dict[str, Dict]) -> Dict[str, CodeGenerationResult]:
        """
        Apply diagnostic correction mechanism to fix errors in generated code.
        
        Args:
            results: Initial code generation results
            problems: Original problems
            
        Returns:
            Updated results after correction attempts
        """
        corrected_results = {}
        
        for task_id, result in results.items():
            problem = problems[task_id]
            current_result = result
            current_result.add_to_history(result)  # Save initial attempt
            
            # Validate the initial code
            is_correct, error_message, error_type = self.validator.validate_code(
                problem, current_result.generated_code
            )
            
            current_result.is_correct = is_correct
            current_result.error_message = error_message
            current_result.error_type = error_type
            
            # If already correct, no need for correction
            if is_correct:
                corrected_results[task_id] = current_result
                continue
                
            # Apply correction mechanism
            for attempt in range(1, self.max_correction_attempts + 1):
                # Select the appropriate model for correction
                model = self.model_a if current_result.model_type == ModelType.MODEL_A else self.model_b
                
                # Generate fixed code
                fixed_code = model.fix_code(
                    current_result.prompt, 
                    current_result.generated_code, 
                    current_result.error_message
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
                is_correct, error_message, error_type = self.validator.validate_code(
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
                    
            corrected_results[task_id] = current_result
            
        return corrected_results
    
    def cross_model_collaborative_generation(self, results: Dict[str, CodeGenerationResult], 
                                           problems: Dict[str, Dict]) -> Dict[str, CodeGenerationResult]:
        """
        Apply cross-model collaborative generation for problems that couldn't be fixed.
        
        Args:
            results: Results after diagnostic correction
            problems: Original problems
            
        Returns:
            Final results after cross-model collaboration
        """
        final_results = {}
        
        # Separate successful and failed results
        successful_results = {tid: r for tid, r in results.items() if r.is_correct}
        failed_results = {tid: r for tid, r in results.items() if not r.is_correct}
        
        # Keep successful results as is
        final_results.update(successful_results)
        
        # Group failed results by model type
        failed_by_a = {tid: r for tid, r in failed_results.items() if r.model_type == ModelType.MODEL_A}
        failed_by_b = {tid: r for tid, r in failed_results.items() if r.model_type == ModelType.MODEL_B}
        
        # Process cross-model collaboration
        # Model B fixes problems that Model A couldn't fix
        for task_id, result in failed_by_a.items():
            problem = problems[task_id]
            current_result = result
            current_result.add_to_history(result)  # Save previous attempts
            
            # Try with model B
            for attempt in range(self.max_correction_attempts + 1):
                # Generate code with model B
                if attempt == 0:
                    # First attempt with just the prompt
                    generated_code = self.model_b.generate_code(problem["prompt"])
                else:
                    # Subsequent attempts with error feedback
                    generated_code = self.model_b.fix_code(
                        current_result.prompt,
                        current_result.generated_code,
                        current_result.error_message
                    )
                
                # Create new result for this attempt
                new_result = CodeGenerationResult(
                    task_id=task_id,
                    prompt=current_result.prompt,
                    generated_code=generated_code,
                    model_type=ModelType.MODEL_B,
                    attempt_count=current_result.attempt_count + 1
                )
                
                # Validate the code
                is_correct, error_message, error_type = self.validator.validate_code(
                    problem, generated_code
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
                    
            final_results[task_id] = current_result
            
        # Model A fixes problems that Model B couldn't fix
        for task_id, result in failed_by_b.items():
            problem = problems[task_id]
            current_result = result
            current_result.add_to_history(result)  # Save previous attempts
            
            # Try with model A
            for attempt in range(self.max_correction_attempts + 1):
                # Generate code with model A
                if attempt == 0:
                    # First attempt with just the prompt
                    generated_code = self.model_a.generate_code(problem["prompt"])
                else:
                    # Subsequent attempts with error feedback
                    generated_code = self.model_a.fix_code(
                        current_result.prompt,
                        current_result.generated_code,
                        current_result.error_message
                    )
                
                # Create new result for this attempt
                new_result = CodeGenerationResult(
                    task_id=task_id,
                    prompt=current_result.prompt,
                    generated_code=generated_code,
                    model_type=ModelType.MODEL_A,
                    attempt_count=current_result.attempt_count + 1
                )
                
                # Validate the code
                is_correct, error_message, error_type = self.validator.validate_code(
                    problem, generated_code
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
                    
            final_results[task_id] = current_result
            
        return final_results
    
    def run(self, problems: Dict[str, Dict]) -> Dict[str, CodeGenerationResult]:
        """
        Run the complete CMCS framework on the given problems.
        
        Args:
            problems: Dictionary of problems to solve
            
        Returns:
            Dictionary of task_id to final CodeGenerationResult
        """
        # Step 1: Partition problems for dual-model processing
        problems_a, problems_b = self.partition_problems(problems)
        
        # Step 2: Dual-model collaborative code generation
        initial_results = self.dual_model_collaborative_generation(problems_a, problems_b)
        
        # Step 3: Diagnostic correction mechanism
        corrected_results = self.diagnostic_correction_mechanism(initial_results, problems)
        
        # Step 4: Cross-model collaborative generation
        final_results = self.cross_model_collaborative_generation(corrected_results, problems)
        
        self.results = final_results
        return final_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the code generation process.
        
        Returns:
            Dictionary of statistics
        """
        if not self.results:
            return {}
            
        total = len(self.results)
        correct = sum(1 for r in self.results.values() if r.is_correct)
        incorrect = total - correct
        
        # Statistics by model
        model_a_results = [r for r in self.results.values() if r.model_type == ModelType.MODEL_A]
        model_b_results = [r for r in self.results.values() if r.model_type == ModelType.MODEL_B]
        
        model_a_correct = sum(1 for r in model_a_results if r.is_correct)
        model_b_correct = sum(1 for r in model_b_results if r.is_correct)
        
        # Statistics by error type
        error_types = {}
        for r in self.results.values():
            if not r.is_correct and r.error_type:
                error_type = r.error_type.value
                error_types[error_type] = error_types.get(error_type, 0) + 1
                
        # Average attempts
        avg_attempts = sum(r.attempt_count for r in self.results.values()) / total
        
        return {
            "total_problems": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": correct / total if total > 0 else 0,
            "model_a_stats": {
                "total": len(model_a_results),
                "correct": model_a_correct,
                "accuracy": model_a_correct / len(model_a_results) if model_a_results else 0
            },
            "model_b_stats": {
                "total": len(model_b_results),
                "correct": model_b_correct,
                "accuracy": model_b_correct / len(model_b_results) if model_b_results else 0
            },
            "error_types": error_types,
            "average_attempts": avg_attempts
        }
    
    def save_results(self, output_path: str):
        """Save the results to a JSON file."""
        results_dict = {tid: r.to_dict() for tid, r in self.results.items()}
        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)