"""
Simple dataset processor for HumanEval and HumanEval+ datasets.
"""

import os
import json
import gzip
from typing import Dict, List


class DatasetProcessor:
    """
    Simple dataset processor for HumanEval and HumanEval+ datasets.
    """
    
    def __init__(self, dataset_type: str, data_path: str):
        """
        Initialize the dataset processor.
        
        Args:
            dataset_type: Type of dataset ('human_eval', 'human_eval_plus', 'apps', 'codecontest', 'mbpp', or 'mbpp_plus')
            data_path: Path to the datasets directory
        """
        self.dataset_type = dataset_type
        self.data_path = data_path
        
        # Set the specific data path based on dataset type
        if dataset_type == "human_eval":
            self.data_file = os.path.join(data_path, "human_eval", "data", "HumanEval.jsonl.gz")
        elif dataset_type == "human_eval_plus":
            self.data_file = os.path.join(data_path, "human_eval_plus", "data", "test-00000-of-00001-5973903632b82d40.parquet")
        elif dataset_type == "apps":
            self.data_file = os.path.join(data_path, "APPS", "data", "selected150.jsonl")
        elif dataset_type == "codecontest":
            self.data_file = os.path.join(data_path, "CodeContest", "data", "test-00000-of-00001-9c49eeff30aacaa8.parquet")
        elif dataset_type == "mbpp":
            self.data_file = os.path.join(data_path, "mbpp", "data", "test-00000-of-00001.parquet")
        elif dataset_type == "mbpp_plus":
            self.data_file = os.path.join(data_path, "mbpp_plus", "data", "test-00000-of-00001.parquet")
        else:
            raise ValueError(f"Unsupported dataset type: {dataset_type}")
    
    def load_dataset(self) -> List[Dict]:
        """
        Load the dataset based on the dataset type.
        
        Returns:
            List of problem dictionaries
        """
        if self.dataset_type == "human_eval":
            return self._load_human_eval()
        elif self.dataset_type == "human_eval_plus":
            return self._load_human_eval_plus()
        elif self.dataset_type == "apps":
            return self._load_apps()
        elif self.dataset_type == "codecontest":
            return self._load_parquet()
        elif self.dataset_type == "mbpp":
            return self._load_parquet()
        elif self.dataset_type == "mbpp_plus":
            return self._load_parquet()
        else:
            raise ValueError(f"Unsupported dataset type: {self.dataset_type}")
    
    def _load_apps(self) -> List[Dict]:
        """
        Load APPS dataset from JSONL file.
        
        Returns:
            List of problem dictionaries
        """
        problems = []
        
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"APPS data file not found at {self.data_file}")
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    problems.append(json.loads(line))
        
        return problems
    
    def _load_parquet(self) -> List[Dict]:
        """
        Load dataset from parquet file (for CodeContest, MBPP, MBPP+).
        
        Returns:
            List of problem dictionaries
        """
        problems = []
        
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found at {self.data_file}")
        
        try:
            import pandas as pd
            df = pd.read_parquet(self.data_file)
            problems = df.to_dict('records')
        except ImportError:
            raise ImportError("pandas is required to read parquet files. Install with: pip install pandas")
        
        return problems
    
    def _load_human_eval(self) -> List[Dict]:
        """
        Load HumanEval dataset from JSONL.gz file.
        
        Returns:
            List of problem dictionaries
        """
        problems = []
        
        if not os.path.exists(self.data_file):
            # Try alternative file paths
            alternative_paths = [
                os.path.join(self.data_path, "human_eval", "data", "example_samples.jsonl"),
                os.path.join(self.data_path, "human_eval", "data", "example_problem.jsonl"),
                os.path.join(self.data_path, "human_eval", "data", "test.jsonl")
            ]
            
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    self.data_file = alt_path
                    break
            else:
                raise FileNotFoundError(f"HumanEval data file not found at {self.data_file} or alternative paths")
        
        # Load based on file extension
        if self.data_file.endswith('.gz'):
            with gzip.open(self.data_file, 'rt', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        problems.append(json.loads(line))
        else:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        problems.append(json.loads(line))
        
        return problems
    
    def _load_human_eval_plus(self) -> List[Dict]:
        """
        Load HumanEval+ dataset from parquet file.
        
        Returns:
            List of problem dictionaries
        """
        problems = []
        
        if not os.path.exists(self.data_file):
            # Try to find a JSONL file instead
            jsonl_path = os.path.join(self.data_path, "human_eval_plus", "data", "data.jsonl")
            if os.path.exists(jsonl_path):
                self.data_file = jsonl_path
            else:
                raise FileNotFoundError(f"HumanEval+ data file not found at {self.data_file}")
        
        # Load based on file extension
        if self.data_file.endswith('.parquet'):
            try:
                import pandas as pd
                df = pd.read_parquet(self.data_file)
                problems = df.to_dict('records')
            except ImportError:
                raise ImportError("pandas is required to read parquet files. Install with: pip install pandas")
        else:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        problems.append(json.loads(line))
        
        return problems