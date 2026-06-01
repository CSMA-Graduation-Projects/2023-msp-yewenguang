"""
Example Script for Using CMCS Framework

This script demonstrates how to use the CMCS framework with HumanEval and HumanEval+ datasets.
"""

import os
import json
import argparse
from typing import Dict, List

# Import CMCS framework components
from cmcs_framework import CMCSFramework, ModelType
from cmcs_framework.models import (
    HuggingFaceModel, OpenAIModel, AnthropicModel, AzureOpenAIModel
)
from cmcs_framework.validators import (
    HumanEvalValidator, HumanEvalPlusValidator,
    APPSValidator, CodeContestValidator,
    MBPPValidator, MBPPPlusValidator
)
from datasets.dataset_processor import DatasetProcessor


def load_human_eval_dataset(data_path: str) -> Dict[str, Dict]:
    """
    Load HumanEval dataset from the specified path.
    
    Args:
        data_path: Path to the HumanEval dataset
        
    Returns:
        Dictionary of problems with task_id as key
    """
    processor = DatasetProcessor("human_eval", data_path)
    dataset = processor.load_dataset()
    
    problems = {}
    for item in dataset:
        task_id = item["task_id"]
        problems[task_id] = {
            "prompt": item["prompt"],
            "test": item["test"],
            "entry_point": item["entry_point"],
            "canonical_solution": item.get("canonical_solution", "")
        }
    
    return problems


def load_human_eval_plus_dataset(data_path: str) -> Dict[str, Dict]:
    """
    Load HumanEval+ dataset from the specified path.
    
    Args:
        data_path: Path to the HumanEval+ dataset
        
    Returns:
        Dictionary of problems with task_id as key
    """
    processor = DatasetProcessor("human_eval_plus", data_path)
    dataset = processor.load_dataset()
    
    problems = {}
    for item in dataset:
        task_id = item["task_id"]
        problems[task_id] = {
            "prompt": item["prompt"],
            "test": item["test"],
            "entry_point": item["entry_point"],
            "canonical_solution": item.get("canonical_solution", "")
        }
    
    return problems


def load_apps_dataset(data_path: str) -> Dict[str, Dict]:
    """
    Load APPS dataset from the specified path.
    
    Args:
        data_path: Path to the APPS dataset
        
    Returns:
        Dictionary of problems with task_id as key
    """
    processor = DatasetProcessor("apps", data_path)
    dataset = processor.load_dataset()
    
    problems = {}
    for idx, item in enumerate(dataset):
        task_id = f"apps_{idx}"
        problems[task_id] = {
            "prompt": item.get("question", ""),
            "starter_code": item.get("starter_code", ""),
            "sample_io": item.get("sample_io", []),
            "test_list": item.get("test_list", [])
        }
    
    return problems


def load_codecontest_dataset(data_path: str) -> Dict[str, Dict]:
    """
    Load CodeContest dataset from the specified path.
    
    Args:
        data_path: Path to the CodeContest dataset
        
    Returns:
        Dictionary of problems with task_id as key
    """
    processor = DatasetProcessor("codecontest", data_path)
    dataset = processor.load_dataset()
    
    problems = {}
    for item in dataset:
        task_id = item["task_id"]
        problems[task_id] = {
            "prompt": item.get("prompt", ""),
            "test_imports": item.get("test_imports", []),
            "test_list": item.get("test_list", [])
        }
    
    return problems


def load_mbpp_dataset(data_path: str) -> Dict[str, Dict]:
    """
    Load MBPP dataset from the specified path.
    
    Args:
        data_path: Path to the MBPP dataset
        
    Returns:
        Dictionary of problems with task_id as key
    """
    processor = DatasetProcessor("mbpp", data_path)
    dataset = processor.load_dataset()
    
    problems = {}
    for item in dataset:
        task_id = item["task_id"]
        problems[task_id] = {
            "prompt": item.get("prompt", ""),
            "test_imports": item.get("test_imports", []),
            "test_list": item.get("test_list", []),
            "canonical_solution": item.get("code", "")
        }
    
    return problems


def load_mbpp_plus_dataset(data_path: str) -> Dict[str, Dict]:
    """
    Load MBPP+ dataset from the specified path.
    
    Args:
        data_path: Path to the MBPP+ dataset
        
    Returns:
        Dictionary of problems with task_id as key
    """
    processor = DatasetProcessor("mbpp_plus", data_path)
    dataset = processor.load_dataset()
    
    problems = {}
    for item in dataset:
        task_id = item["task_id"]
        problems[task_id] = {
            "prompt": item.get("prompt", ""),
            "test_imports": item.get("test_imports", []),
            "test_list": item.get("test_list", []),
            "canonical_solution": item.get("code", "")
        }
    
    return problems


def main():
    """
    Main function to run the CMCS framework example.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run CMCS framework on various datasets")
    parser.add_argument("--dataset", choices=["human_eval", "human_eval_plus", "apps", "codecontest", "mbpp", "mbpp_plus"], default="human_eval",
                        help="Dataset to use")
    parser.add_argument("--data_path", default="./datasets",
                        help="Path to the datasets directory")

    parser.add_argument("--model_type", choices=["huggingface", "openai", "anthropic", "azure"], default="huggingface",
                        help="Type of model to use")
    parser.add_argument("--model_a", default="deepseek-coder-6.7b-base",
                        help="Name or path of model A (for HuggingFace) or model name (for OpenAI/Anthropic/Azure)")
    parser.add_argument("--model_b", default="codellama-7b-instruct",
                        help="Name or path of model B (for HuggingFace) or model name (for OpenAI/Anthropic/Azure)")

    parser.add_argument("--api_key", default=None,
                        help="API key for OpenAI/Anthropic (or set via environment variable)")
    parser.add_argument("--azure_endpoint", default=None,
                        help="Azure OpenAI endpoint (only for Azure models)")
    parser.add_argument("--api_version", default="2024-02-15-preview",
                        help="Azure API version (only for Azure models)")

    parser.add_argument("--max_new_tokens", type=int, default=2048,
                        help="Maximum number of tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Temperature for sampling (API models only)")

    parser.add_argument("--max_correction_attempts", type=int, default=5,
                        help="Maximum number of correction attempts")
    parser.add_argument("--output", default="./results.json",
                        help="Path to save the results")
    
    args = parser.parse_args()
    
    # Load the dataset
    if args.dataset == "human_eval":
        problems = load_human_eval_dataset(args.data_path)
        execution_path = os.path.join(args.data_path, "human_eval", "execution.py")
        validator = HumanEvalValidator(execution_path)
    elif args.dataset == "human_eval_plus":
        problems = load_human_eval_plus_dataset(args.data_path)
        execution_path = os.path.join(args.data_path, "human_eval_plus", "execution.py")
        validator = HumanEvalPlusValidator(execution_path)
    elif args.dataset == "apps":
        problems = load_apps_dataset(args.data_path)
        execution_path = os.path.join(args.data_path, "APPS", "execution.py")
        validator = APPSValidator(execution_path)
    elif args.dataset == "codecontest":
        problems = load_codecontest_dataset(args.data_path)
        execution_path = os.path.join(args.data_path, "CodeContest", "execution.py")
        validator = CodeContestValidator(execution_path)
    elif args.dataset == "mbpp":
        problems = load_mbpp_dataset(args.data_path)
        execution_path = os.path.join(args.data_path, "mbpp", "execution.py")
        validator = MBPPValidator(execution_path)
    elif args.dataset == "mbpp_plus":
        problems = load_mbpp_plus_dataset(args.data_path)
        execution_path = os.path.join(args.data_path, "mbpp_plus", "execution.py")
        validator = MBPPPlusValidator(execution_path)
    
    print(f"Loaded {len(problems)} problems from {args.dataset} dataset")

    # Initialize models based on model type
    print(f"Initializing {args.model_type} models...")

    if args.model_type == "huggingface":
        print(f"Loading model A: {args.model_a}")
        model_a = HuggingFaceModel(
            args.model_a, ModelType.MODEL_A,
            max_new_tokens=args.max_new_tokens
        )
        print(f"Loading model B: {args.model_b}")
        model_b = HuggingFaceModel(
            args.model_b, ModelType.MODEL_B,
            max_new_tokens=args.max_new_tokens
        )
    elif args.model_type == "openai":
        print(f"Loading OpenAI model A: {args.model_a}")
        model_a = OpenAIModel(
            args.model_a, ModelType.MODEL_A,
            api_key=args.api_key,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature
        )
        print(f"Loading OpenAI model B: {args.model_b}")
        model_b = OpenAIModel(
            args.model_b, ModelType.MODEL_B,
            api_key=args.api_key,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature
        )
    elif args.model_type == "anthropic":
        print(f"Loading Anthropic model A: {args.model_a}")
        model_a = AnthropicModel(
            args.model_a, ModelType.MODEL_A,
            api_key=args.api_key,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature
        )
        print(f"Loading Anthropic model B: {args.model_b}")
        model_b = AnthropicModel(
            args.model_b, ModelType.MODEL_B,
            api_key=args.api_key,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature
        )
    elif args.model_type == "azure":
        print(f"Loading Azure model A: {args.model_a}")
        model_a = AzureOpenAIModel(
            args.model_a, ModelType.MODEL_A,
            api_key=args.api_key,
            azure_endpoint=args.azure_endpoint,
            api_version=args.api_version,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature
        )
        print(f"Loading Azure model B: {args.model_b}")
        model_b = AzureOpenAIModel(
            args.model_b, ModelType.MODEL_B,
            api_key=args.api_key,
            azure_endpoint=args.azure_endpoint,
            api_version=args.api_version,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature
        )
    
    # Initialize the CMCS framework
    cmcs = CMCSFramework(model_a, model_b, validator, args.max_correction_attempts)
    
    # Process the problems
    print(f"Processing {len(problems)} problems with CMCS framework...")
    results = cmcs.run(problems)

    # Get statistics
    stats = cmcs.get_statistics()

    # Print statistics
    print("\n===== CMCS Framework Results =====")
    print(f"Total problems: {stats['total_problems']}")
    print(f"Correct solutions: {stats['correct']}")
    print(f"Accuracy: {stats['accuracy']:.2%}")
    print("\nModel distribution:")
    print(f"  model_a: {stats['model_a_stats']['total']}")
    print(f"  model_b: {stats['model_b_stats']['total']}")

    if stats['error_types']:
        print("\nError distribution:")
        for error_type, count in stats['error_types'].items():
            print(f"  {error_type}: {count}")

    print("\nAverage attempts: {:.2f}".format(stats['average_attempts']))

    # Save results
    cmcs.save_results(args.output)
    
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()