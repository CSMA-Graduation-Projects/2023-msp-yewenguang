"""
Cross-Model Collaborative Generation Module

This module implements the cross-model collaborative generation component of the CMCS framework.
"""

import time
from typing import Dict, List, Tuple, Optional

from cmcs_framework.core import BaseLLMModel, ModelType, CodeGenerationResult, CodeValidator, ErrorType
from cmcs_framework.diagnostic_correction import DiagnosticCorrectionMechanism


class CrossModelCollaborativeGeneration:
    """
    Implementation of the cross-model collaborative generation component.
    
    This component is responsible for:
    1. Analyzing the results from the dual-model collaborative generation
    2. Identifying failed problems that need cross-model collaboration
    3. Exchanging failed problems between models
    4. Applying diagnostic correction to the cross-model attempts
    5. Selecting the best solutions from all attempts
    """
    
    def __init__(self, model_a: BaseLLMModel, model_b: BaseLLMModel, 
                 validator: CodeValidator, max_correction_attempts: int = 5):
        """
        Initialize the cross-model collaborative generation.
        
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
        self.diagnostic_correction = DiagnosticCorrectionMechanism(
            model_a, model_b, validator, max_correction_attempts
        )
    
    def analyze_results(self, results_a: Dict[str, CodeGenerationResult], 
                       results_b: Dict[str, CodeGenerationResult]) -> Dict[str, any]:
        """
        Analyze the results from both models to determine the collaboration strategy.
        
        Args:
            results_a: Results from model A
            results_b: Results from model B
            
        Returns:
            Dictionary with analysis results and failed tasks for exchange
        """
        # Get all task IDs
        all_task_ids = set(results_a.keys()).union(set(results_b.keys()))
        
        # Categorize tasks
        a_success_b_success = []
        a_success_b_failure = []
        a_failure_b_success = []
        a_failure_b_failure = []
        
        for task_id in all_task_ids:
            a_result = results_a.get(task_id)
            b_result = results_b.get(task_id)
            
            a_success = a_result and a_result.is_correct
            b_success = b_result and b_result.is_correct
            
            if a_success and b_success:
                a_success_b_success.append(task_id)
            elif a_success and not b_success:
                a_success_b_failure.append(task_id)
            elif not a_success and b_success:
                a_failure_b_success.append(task_id)
            else:
                a_failure_b_failure.append(task_id)
        
        return {
            "a_success_b_success": a_success_b_success,
            "a_success_b_failure": a_success_b_failure,
            "a_failure_b_success": a_failure_b_success,
            "a_failure_b_failure": a_failure_b_failure,
            "total_tasks": len(all_task_ids),
            "a_success_count": len([tid for tid in all_task_ids if results_a.get(tid) and results_a[tid].is_correct]),
            "b_success_count": len([tid for tid in all_task_ids if results_b.get(tid) and results_b[tid].is_correct])
        }
    
    def exchange_failed_tasks(self, analysis: Dict[str, any], 
                             results_a: Dict[str, CodeGenerationResult],
                             results_b: Dict[str, CodeGenerationResult],
                             problems: Dict[str, Dict]) -> Dict[str, CodeGenerationResult]:
        """
        Exchange failed tasks between models and apply diagnostic correction.
        
        Args:
            analysis: Analysis results from analyze_results
            results_a: Results from model A
            results_b: Results from model B
            problems: Original problems
            
        Returns:
            Dictionary with cross-model collaborative results
        """
        # Initialize results with existing successful results
        collaborative_results = {}
        
        # Add successful results from both models
        for task_id, result in results_a.items():
            if result.is_correct:
                collaborative_results[task_id] = result
                
        for task_id, result in results_b.items():
            if result.is_correct:
                collaborative_results[task_id] = result
        
        # Case 1: A success, B failure - A fixes B's failures
        for task_id in analysis["a_success_b_failure"]:
            if task_id not in collaborative_results:  # Not already handled
                # Get the problem
                problem = problems[task_id]
                
                # Generate new code with model A
                prompt = problem.get("prompt", "")
                new_code = self.model_a.generate_code(prompt)
                
                # Create new result
                new_result = CodeGenerationResult(
                    task_id=task_id,
                    prompt=prompt,
                    generated_code=new_code,
                    model_type=ModelType.MODEL_A,
                    attempt_count=1
                )
                
                # Apply diagnostic correction
                corrected_result = self.diagnostic_correction.apply_correction_loop(
                    task_id, problem, new_result
                )
                
                collaborative_results[task_id] = corrected_result
        
        # Case 2: A failure, B success - B fixes A's failures
        for task_id in analysis["a_failure_b_success"]:
            if task_id not in collaborative_results:  # Not already handled
                # Get the problem
                problem = problems[task_id]
                
                # Generate new code with model B
                prompt = problem.get("prompt", "")
                new_code = self.model_b.generate_code(prompt)
                
                # Create new result
                new_result = CodeGenerationResult(
                    task_id=task_id,
                    prompt=prompt,
                    generated_code=new_code,
                    model_type=ModelType.MODEL_B,
                    attempt_count=1
                )
                
                # Apply diagnostic correction
                corrected_result = self.diagnostic_correction.apply_correction_loop(
                    task_id, problem, new_result
                )
                
                collaborative_results[task_id] = corrected_result
        
        # Case 3: Both failed - exchange tasks
        for task_id in analysis["a_failure_b_failure"]:
            if task_id not in collaborative_results:  # Not already handled
                # Get the problem
                problem = problems[task_id]
                
                # Determine which model originally handled this task
                # For simplicity, we'll assume tasks were evenly split
                # In a real implementation, this would be tracked during the initial split
                original_model = ModelType.MODEL_A if hash(task_id) % 2 == 0 else ModelType.MODEL_B
                
                # Use the opposite model for cross-model collaboration
                cross_model = self.model_b if original_model == ModelType.MODEL_A else self.model_a
                cross_model_type = ModelType.MODEL_B if original_model == ModelType.MODEL_A else ModelType.MODEL_A
                
                # Generate new code with the opposite model
                prompt = problem.get("prompt", "")
                new_code = cross_model.generate_code(prompt)
                
                # Create new result
                new_result = CodeGenerationResult(
                    task_id=task_id,
                    prompt=prompt,
                    generated_code=new_code,
                    model_type=cross_model_type,
                    attempt_count=1
                )
                
                # Apply diagnostic correction
                corrected_result = self.diagnostic_correction.apply_correction_loop(
                    task_id, problem, new_result
                )
                
                collaborative_results[task_id] = corrected_result
        
        return collaborative_results
    
    def select_best_solutions(self, results_a: Dict[str, CodeGenerationResult],
                             results_b: Dict[str, CodeGenerationResult],
                             collaborative_results: Dict[str, CodeGenerationResult]) -> Dict[str, CodeGenerationResult]:
        """
        Select the best solutions from all available results.
        
        Args:
            results_a: Results from model A
            results_b: Results from model B
            collaborative_results: Results from cross-model collaboration
            
        Returns:
            Dictionary with the best solution for each task
        """
        final_results = {}
        
        # Get all task IDs
        all_task_ids = set(results_a.keys()).union(set(results_b.keys())).union(set(collaborative_results.keys()))
        
        for task_id in all_task_ids:
            # Collect all results for this task
            all_results = []
            
            if task_id in results_a:
                all_results.append(results_a[task_id])
                
            if task_id in results_b:
                all_results.append(results_b[task_id])
                
            if task_id in collaborative_results:
                all_results.append(collaborative_results[task_id])
            
            # Select the best result (correct with least attempts)
            correct_results = [r for r in all_results if r.is_correct]
            
            if correct_results:
                # Among correct results, choose the one with the least attempts
                best_result = min(correct_results, key=lambda r: r.attempt_count)
            else:
                # If none are correct, choose the one with the least attempts
                best_result = min(all_results, key=lambda r: r.attempt_count)
            
            final_results[task_id] = best_result
        
        return final_results
    
    def apply_cross_model_collaboration(self, results_a: Dict[str, CodeGenerationResult],
                                       results_b: Dict[str, CodeGenerationResult],
                                       problems: Dict[str, Dict]) -> Dict[str, CodeGenerationResult]:
        """
        Apply the cross-model collaborative generation process.
        
        Args:
            results_a: Results from model A
            results_b: Results from model B
            problems: Original problems
            
        Returns:
            Final results after cross-model collaboration
        """
        # Analyze the results to determine the collaboration strategy
        analysis = self.analyze_results(results_a, results_b)
        
        # Exchange failed tasks between models and apply diagnostic correction
        collaborative_results = self.exchange_failed_tasks(
            analysis, results_a, results_b, problems
        )
        
        # Select the best solutions from all available results
        final_results = self.select_best_solutions(
            results_a, results_b, collaborative_results
        )
        
        return final_results
    
    def get_collaboration_statistics(self, results_before: Dict[str, CodeGenerationResult],
                                    results_after: Dict[str, CodeGenerationResult]) -> Dict[str, any]:
        """
        Get statistics about the cross-model collaboration process.
        
        Args:
            results_before: Results before cross-model collaboration
            results_after: Results after cross-model collaboration
            
        Returns:
            Dictionary of collaboration statistics
        """
        total = len(results_after)
        correct_before = sum(1 for r in results_before.values() if r.is_correct)
        correct_after = sum(1 for r in results_after.values() if r.is_correct)
        
        # Count by model type
        model_counts_before = {}
        model_counts_after = {}
        
        for r in results_before.values():
            model_type = r.model_type.value
            model_counts_before[model_type] = model_counts_before.get(model_type, 0) + 1
                
        for r in results_after.values():
            model_type = r.model_type.value
            model_counts_after[model_type] = model_counts_after.get(model_type, 0) + 1
        
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
        
        return {
            "total_problems": total,
            "correct_before": correct_before,
            "correct_after": correct_after,
            "improvement": correct_after - correct_before,
            "improvement_rate": (correct_after - correct_before) / total if total > 0 else 0,
            "model_distribution_before": model_counts_before,
            "model_distribution_after": model_counts_after,
            "error_types_before": error_types_before,
            "error_types_after": error_types_after
        }