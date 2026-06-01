"""
Dual-Model Collaborative Code Generation Module

This module implements the dual-model collaborative code generation component of the CMCS framework.
"""

import random
import time
from typing import Dict, List, Tuple, Optional

from cmcs_framework.core import BaseLLMModel, ModelType, CodeGenerationResult


class DualModelCollaborativeGeneration:
    """
    Implementation of the dual-model collaborative code generation component.
    
    This component is responsible for:
    1. Partitioning the problem set into two disjoint subsets
    2. Distributing the subsets to two different models for parallel processing
    3. Collecting the initial code generation results
    """
    
    def __init__(self, model_a: BaseLLMModel, model_b: BaseLLMModel):
        """
        Initialize the dual-model collaborative generation component.
        
        Args:
            model_a: First LLM model
            model_b: Second LLM model
        """
        self.model_a = model_a
        self.model_b = model_b
    
    def partition_problems(self, problems: Dict[str, Dict], 
                          partition_method: str = "random") -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
        """
        Partition the problems into two disjoint subsets for parallel processing.
        
        Args:
            problems: Dictionary of problems to partition
            partition_method: Method for partitioning ("random", "alternating", "custom")
            
        Returns:
            Tuple of (problems_for_model_a, problems_for_model_b)
        """
        problem_ids = list(problems.keys())
        
        if partition_method == "random":
            # Random partition
            random.shuffle(problem_ids)
            mid = len(problem_ids) // 2
            ids_a = problem_ids[:mid]
            ids_b = problem_ids[mid:]
            
        elif partition_method == "alternating":
            # Alternating partition
            ids_a = problem_ids[::2]  # Even indices
            ids_b = problem_ids[1::2]  # Odd indices
            
        elif partition_method == "custom":
            # Custom partition based on problem difficulty or other criteria
            # For now, just use random partition
            random.shuffle(problem_ids)
            mid = len(problem_ids) // 2
            ids_a = problem_ids[:mid]
            ids_b = problem_ids[mid:]
            
        else:
            raise ValueError(f"Unknown partition method: {partition_method}")
        
        problems_a = {pid: problems[pid] for pid in ids_a}
        problems_b = {pid: problems[pid] for pid in ids_b}
        
        return problems_a, problems_b
    
    def generate_code_for_problems(self, problems: Dict[str, Dict], 
                                 model: BaseLLMModel, model_type: ModelType) -> Dict[str, CodeGenerationResult]:
        """
        Generate code for a set of problems using the specified model.
        
        Args:
            problems: Dictionary of problems to solve
            model: The model to use for generation
            model_type: Type of the model (A or B)
            
        Returns:
            Dictionary of task_id to CodeGenerationResult
        """
        results = {}
        
        for task_id, problem in problems.items():
            start_time = time.time()
            generated_code = model.generate_code(problem["prompt"])
            execution_time = time.time() - start_time
            
            result = CodeGenerationResult(
                task_id=task_id,
                prompt=problem["prompt"],
                generated_code=generated_code,
                model_type=model_type,
                execution_time=execution_time
            )
            
            results[task_id] = result
            
        return results
    
    def generate(self, problems: Dict[str, Dict], 
                partition_method: str = "random") -> Dict[str, CodeGenerationResult]:
        """
        Perform dual-model collaborative code generation.
        
        Args:
            problems: Dictionary of problems to solve
            partition_method: Method for partitioning the problems
            
        Returns:
            Dictionary of task_id to CodeGenerationResult
        """
        # Step 1: Partition problems
        problems_a, problems_b = self.partition_problems(problems, partition_method)
        
        # Step 2: Generate code with model A
        results_a = self.generate_code_for_problems(problems_a, self.model_a, ModelType.MODEL_A)
        
        # Step 3: Generate code with model B
        results_b = self.generate_code_for_problems(problems_b, self.model_b, ModelType.MODEL_B)
        
        # Step 4: Combine results
        all_results = {}
        all_results.update(results_a)
        all_results.update(results_b)
        
        return all_results
    
    def get_load_balance_stats(self, problems: Dict[str, Dict], 
                             partition_method: str = "random") -> Dict[str, any]:
        """
        Get statistics about the load balance between the two models.
        
        Args:
            problems: Dictionary of problems
            partition_method: Method for partitioning
            
        Returns:
            Dictionary of load balance statistics
        """
        problems_a, problems_b = self.partition_problems(problems, partition_method)
        
        # Calculate total characters in prompts for each model
        total_chars_a = sum(len(problem["prompt"]) for problem in problems_a.values())
        total_chars_b = sum(len(problem["prompt"]) for problem in problems_b.values())
        
        return {
            "total_problems": len(problems),
            "model_a_problems": len(problems_a),
            "model_b_problems": len(problems_b),
            "model_a_prompt_chars": total_chars_a,
            "model_b_prompt_chars": total_chars_b,
            "load_balance_ratio": total_chars_a / total_chars_b if total_chars_b > 0 else float('inf')
        }