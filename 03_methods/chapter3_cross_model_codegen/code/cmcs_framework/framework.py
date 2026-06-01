"""
Main CMCS Framework Implementation

This module integrates all components of the CMCS framework into a unified system.
"""

import time
from typing import Dict, List, Tuple, Optional, Any

from cmcs_framework.core import (
    BaseLLMModel, ModelType, CodeGenerationResult, CodeValidator, ErrorType
)
from cmcs_framework.dual_model_generation import DualModelCollaborativeGeneration
from cmcs_framework.diagnostic_correction import DiagnosticCorrectionMechanism
from cmcs_framework.cross_model_collaboration import CrossModelCollaborativeGeneration


class CMCSFramework:
    """
    Main implementation of the CMCS (Collaborative Multi-model Code Generation Scheme) framework.
    
    This class integrates all three main components:
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
        
        # Initialize the three main components
        self.dual_model_generation = DualModelCollaborativeGeneration(model_a, model_b)
        self.diagnostic_correction = DiagnosticCorrectionMechanism(
            model_a, model_b, validator, max_correction_attempts
        )
        self.cross_model_collaboration = CrossModelCollaborativeGeneration(
            model_a, model_b, validator, max_correction_attempts
        )
    
    def process_problems(self, problems: Dict[str, Dict], 
                         partition_method: str = "random") -> Dict[str, CodeGenerationResult]:
        """
        Process a set of programming problems using the full CMCS framework.
        
        Args:
            problems: Dictionary of problems with task_id as key
            partition_method: Method for partitioning problems ("random", "alternating", "custom")
            
        Returns:
            Dictionary of final results with task_id as key
        """
        # Step 1: Dual-Model Collaborative Code Generation
        print("Step 1: Dual-Model Collaborative Code Generation")
        start_time = time.time()
        
        # Partition problems between the two models
        problems_a, problems_b = self.dual_model_generation.partition_problems(
            problems, partition_method
        )
        
        # Create partitioned problems dictionary
        partitioned_problems = {
            "model_a": problems_a,
            "model_b": problems_b
        }
        
        # Generate code with both models
        results_a = self.dual_model_generation.generate_code_for_problems(partitioned_problems["model_a"], self.model_a, ModelType.MODEL_A)
        results_b = self.dual_model_generation.generate_code_for_problems(partitioned_problems["model_b"], self.model_b, ModelType.MODEL_B)
        
        # Combine results
        initial_results = {**results_a, **results_b}
        
        dual_model_time = time.time() - start_time
        print(f"Dual-Model Collaborative Code Generation completed in {dual_model_time:.2f} seconds")
        
        # Step 2: Diagnostic Correction Mechanism
        print("\nStep 2: Diagnostic Correction Mechanism")
        start_time = time.time()
        
        # Apply diagnostic correction to results from both models
        corrected_results_a = self.diagnostic_correction.correct_results(results_a, problems)
        corrected_results_b = self.diagnostic_correction.correct_results(results_b, problems)
        
        # Combine corrected results
        corrected_results = {**corrected_results_a, **corrected_results_b}
        
        diagnostic_time = time.time() - start_time
        print(f"Diagnostic Correction Mechanism completed in {diagnostic_time:.2f} seconds")
        
        # Step 3: Cross-Model Collaborative Generation
        print("\nStep 3: Cross-Model Collaborative Generation")
        start_time = time.time()
        
        # Apply cross-model collaboration to handle remaining failures
        final_results = self.cross_model_collaboration.apply_cross_model_collaboration(
            corrected_results_a, corrected_results_b, problems
        )
        
        cross_model_time = time.time() - start_time
        print(f"Cross-Model Collaborative Generation completed in {cross_model_time:.2f} seconds")
        
        # Return final results
        return final_results
    
    def get_framework_statistics(self, problems: Dict[str, Dict], 
                                final_results: Dict[str, CodeGenerationResult]) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the framework execution.
        
        Args:
            problems: Original problems
            final_results: Final results after all processing
            
        Returns:
            Dictionary with comprehensive statistics
        """
        total = len(problems)
        correct = sum(1 for r in final_results.values() if r.is_correct)
        
        # Count by model type
        model_counts = {}
        for r in final_results.values():
            model_type = r.model_type.value
            model_counts[model_type] = model_counts.get(model_type, 0) + 1
        
        # Count by error type
        error_types = {}
        for r in final_results.values():
            if not r.is_correct and r.error_type:
                error_type = r.error_type.value
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Count by attempt number
        attempt_counts = {}
        for r in final_results.values():
            attempt = r.attempt_count
            attempt_counts[attempt] = attempt_counts.get(attempt, 0) + 1
        
        return {
            "total_problems": total,
            "correct_solutions": correct,
            "accuracy": correct / total if total > 0 else 0,
            "model_distribution": model_counts,
            "error_distribution": error_types,
            "attempt_distribution": attempt_counts
        }
    
    def save_results(self, results: Dict[str, CodeGenerationResult], 
                    output_path: str) -> None:
        """
        Save the results to a file.
        
        Args:
            results: Results to save
            output_path: Path to save the results
        """
        import json
        
        # Convert results to a serializable format
        serializable_results = {}
        for task_id, result in results.items():
            serializable_results[task_id] = {
                "task_id": result.task_id,
                "prompt": result.prompt,
                "generated_code": result.generated_code,
                "model_type": result.model_type.value,
                "attempt_count": result.attempt_count,
                "is_correct": result.is_correct,
                "error_message": result.error_message,
                "error_type": result.error_type.value if result.error_type else None,
                "generation_time": result.generation_time
            }
        
        # Save to file
        with open(output_path, "w") as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"Results saved to {output_path}")
    
    def load_results(self, input_path: str) -> Dict[str, CodeGenerationResult]:
        """
        Load results from a file.
        
        Args:
            input_path: Path to load the results from
            
        Returns:
            Dictionary of results
        """
        import json
        
        # Load from file
        with open(input_path, "r") as f:
            serializable_results = json.load(f)
        
        # Convert back to CodeGenerationResult objects
        results = {}
        for task_id, data in serializable_results.items():
            result = CodeGenerationResult(
                task_id=data["task_id"],
                prompt=data["prompt"],
                generated_code=data["generated_code"],
                model_type=ModelType(data["model_type"]),
                attempt_count=data["attempt_count"],
                is_correct=data["is_correct"],
                error_message=data["error_message"],
                error_type=ErrorType(data["error_type"]) if data["error_type"] else None,
                generation_time=data["generation_time"]
            )
            results[task_id] = result
        
        return results