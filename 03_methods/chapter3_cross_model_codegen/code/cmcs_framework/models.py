"""
Model Implementations for CMCS Framework

This module provides concrete implementations of LLM models for use in the CMCS framework.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import re
from typing import Dict, List, Tuple, Optional
import time
import os

from cmcs_framework.core import BaseLLMModel, ModelType


class HuggingFaceModel(BaseLLMModel):
    """
    Implementation of a HuggingFace model for CMCS.
    """
    
    def __init__(self, model_name: str, model_type: ModelType, 
                 quantization_config: Optional[Dict] = None,
                 device: Optional[str] = None,
                 max_new_tokens: int = 2048):
        """
        Initialize the HuggingFace model.
        
        Args:
            model_name: Name of the model on HuggingFace Hub
            model_type: Type of model (A or B)
            quantization_config: Configuration for quantization
            device: Device to run the model on
            max_new_tokens: Maximum number of new tokens to generate
        """
        super().__init__(model_name, model_type)
        
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_new_tokens = max_new_tokens
        
        # Default quantization config if not provided
        if quantization_config is None:
            quantization_config = {
                "load_in_4bit": True,
                "bnb_4bit_compute_dtype": torch.float16
            }
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Ensure tokenizer has a pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        # Load model with quantization
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=BitsAndBytesConfig(**quantization_config)
        ).to(self.device)
    
    def generate_code(self, prompt: str, additional_context: str = "") -> str:
        """
        Generate code based on the given prompt.
        
        Args:
            prompt: The programming problem prompt
            additional_context: Additional context to include in the prompt
            
        Returns:
            Generated code as a string
        """
        # Create the full prompt with role setting
        full_prompt = self._create_generation_prompt(prompt, additional_context)
        
        # Generate response
        response = self._generate_response(full_prompt)
        
        # Extract code from response
        _, code = self._extract_python_code(response)
        
        return code
    
    def fix_code(self, prompt: str, code: str, error_message: str) -> str:
        """
        Fix code based on error message.
        
        Args:
            prompt: The original programming problem prompt
            code: The incorrect code
            error_message: The error message from validation
            
        Returns:
            Fixed code as a string
        """
        # Create the error fixing prompt
        fix_prompt = self._create_fix_prompt(prompt, code, error_message)
        
        # Generate response
        response = self._generate_response(fix_prompt)
        
        # Extract code from response
        _, fixed_code = self._extract_python_code(response)
        
        return fixed_code
    
    def _create_generation_prompt(self, prompt: str, additional_context: str = "") -> str:
        """Create a prompt for code generation."""
        return f"""Assuming you are a professional coding expert.

The following is a Python code description:
```
{prompt}
```
{additional_context}

You should generate Python code based on the above Python code description and provide the complete Python code within triple backticks ```python ``` in the end!"""
    
    def _create_fix_prompt(self, prompt: str, code: str, error_message: str) -> str:
        """Create a prompt for code fixing."""
        return f"""Assuming you are a professional coding expert.

The following is Python code description and incorrect Python program translation and feedback.
```Python code description
{prompt}
```
```Incorrect Python program translation
{code}
```
```Feedback:
Got the wrong result: "{error_message}".
```

You should check the feedback, analyze and explain and correct errors in Incorrect Python program translation based on Python code descriptions and provide the complete modified Python code within triple backticks ```python ``` in the end!"""
    
    def _generate_response(self, prompt: str) -> str:
        """Generate a response from the model."""
        # Create dialog format
        dialog = [{"role": "user", "content": prompt}]
        
        # Apply chat template
        text = self.tokenizer.apply_chat_template(
            dialog,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        
        # Generate
        with torch.no_grad():
            generated_ids = self.model.generate(
                model_inputs.input_ids,
                max_new_tokens=self.max_new_tokens
            )
        
        # Decode
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # Combine with original prompt
        full_response = prompt + "\n" + response
        
        return full_response
    
    def _extract_python_code(self, text: str) -> Tuple[bool, str]:
        """
        Extract Python code from text.
        
        Args:
            text: Text containing Python code
            
        Returns:
            Tuple of (success, extracted_code)
        """
        # Regular expression to match content between ```python``` tags
        pattern = re.compile(r'```python(.*?)```', re.DOTALL)
        matches = pattern.findall(text)

        if matches:
            # Initialize variables to store the code block with the maximum number of lines
            max_lines = 0
            largest_code_block = ""

            for match in matches:
                code_block = match.strip()
                # Calculate the number of lines in the code block
                lines = code_block.split('\n')
                if len(lines) > max_lines:
                    max_lines = len(lines)
                    largest_code_block = code_block

            # Remove the part after `# Example usage` or `# Test cases`
            example_usage_pattern = re.compile(r'(.*?)# (Example usage|Test cases)', re.DOTALL)
            example_usage_match = example_usage_pattern.match(largest_code_block)

            if example_usage_match:
                cleaned_code = example_usage_match.group(1).strip()
            else:
                cleaned_code = largest_code_block

            return True, cleaned_code
        else:
            return False, ""


class OpenAIModel(BaseLLMModel):
    """
    Implementation of an OpenAI API model for CMCS.
    Supports GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, etc.
    """

    def __init__(self, model_name: str, model_type: ModelType,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 max_new_tokens: int = 2048,
                 temperature: float = 0.0):
        """
        Initialize the OpenAI API model.

        Args:
            model_name: Name of the OpenAI model (e.g., 'gpt-4', 'gpt-3.5-turbo')
            model_type: Type of model (A or B)
            api_key: OpenAI API key (will use OPENAI_API_KEY env var if not provided)
            base_url: Custom API base URL (for proxy or compatible APIs)
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature
        """
        super().__init__(model_name, model_type)

        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package is required for OpenAI models. Install with: pip install openai")

        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key must be provided or set in OPENAI_API_KEY environment variable")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_code(self, prompt: str, additional_context: str = "") -> str:
        """
        Generate code based on the given prompt.

        Args:
            prompt: The programming problem prompt
            additional_context: Additional context to include in the prompt

        Returns:
            Generated code as a string
        """
        full_prompt = self._create_generation_prompt(prompt, additional_context)
        response = self._generate_response(full_prompt)
        _, code = self._extract_python_code(response)
        return code

    def fix_code(self, prompt: str, code: str, error_message: str) -> str:
        """
        Fix code based on error message.

        Args:
            prompt: The original programming problem prompt
            code: The incorrect code
            error_message: The error message from validation

        Returns:
            Fixed code as a string
        """
        fix_prompt = self._create_fix_prompt(prompt, code, error_message)
        response = self._generate_response(fix_prompt)
        _, fixed_code = self._extract_python_code(response)
        return fixed_code

    def _create_generation_prompt(self, prompt: str, additional_context: str = "") -> str:
        """Create a prompt for code generation."""
        return f"""Assuming you are a professional coding expert.

The following is a Python code description:
```
{prompt}
```
{additional_context}

You should generate Python code based on the above Python code description and provide the complete Python code within triple backticks ```python ``` in the end!"""

    def _create_fix_prompt(self, prompt: str, code: str, error_message: str) -> str:
        """Create a prompt for code fixing."""
        return f"""Assuming you are a professional coding expert.

The following is Python code description and incorrect Python program translation and feedback.
```Python code description
{prompt}
```
```Incorrect Python program translation
{code}
```
```Feedback:
Got the wrong result: "{error_message}".
```

You should check the feedback, analyze and explain and correct errors in Incorrect Python program translation based on Python code descriptions and provide the complete modified Python code within triple backticks ```python ``` in the end!"""

    def _generate_response(self, prompt: str) -> str:
        """Generate a response from the OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_new_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def _extract_python_code(self, text: str) -> Tuple[bool, str]:
        """Extract Python code from text."""
        pattern = re.compile(r'```python(.*?)```', re.DOTALL)
        matches = pattern.findall(text)

        if matches:
            max_lines = 0
            largest_code_block = ""

            for match in matches:
                code_block = match.strip()
                lines = code_block.split('\n')
                if len(lines) > max_lines:
                    max_lines = len(lines)
                    largest_code_block = code_block

            example_usage_pattern = re.compile(r'(.*?)# (Example usage|Test cases)', re.DOTALL)
            example_usage_match = example_usage_pattern.match(largest_code_block)

            if example_usage_match:
                cleaned_code = example_usage_match.group(1).strip()
            else:
                cleaned_code = largest_code_block

            return True, cleaned_code
        else:
            return False, ""


class AnthropicModel(BaseLLMModel):
    """
    Implementation of an Anthropic API model for CMCS.
    Supports Claude-3-Opus, Claude-3-Sonnet, Claude-3-Haiku, etc.
    """

    def __init__(self, model_name: str, model_type: ModelType,
                 api_key: Optional[str] = None,
                 max_new_tokens: int = 2048,
                 temperature: float = 0.0):
        """
        Initialize the Anthropic API model.

        Args:
            model_name: Name of the Anthropic model (e.g., 'claude-3-opus-20240229')
            model_type: Type of model (A or B)
            api_key: Anthropic API key (will use ANTHROPIC_API_KEY env var if not provided)
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature
        """
        super().__init__(model_name, model_type)

        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package is required for Anthropic models. Install with: pip install anthropic")

        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("API key must be provided or set in ANTHROPIC_API_KEY environment variable")

        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_code(self, prompt: str, additional_context: str = "") -> str:
        """Generate code based on the given prompt."""
        full_prompt = self._create_generation_prompt(prompt, additional_context)
        response = self._generate_response(full_prompt)
        _, code = self._extract_python_code(response)
        return code

    def fix_code(self, prompt: str, code: str, error_message: str) -> str:
        """Fix code based on error message."""
        fix_prompt = self._create_fix_prompt(prompt, code, error_message)
        response = self._generate_response(fix_prompt)
        _, fixed_code = self._extract_python_code(response)
        return fixed_code

    def _create_generation_prompt(self, prompt: str, additional_context: str = "") -> str:
        """Create a prompt for code generation."""
        return f"""Assuming you are a professional coding expert.

The following is a Python code description:
```
{prompt}
```
{additional_context}

You should generate Python code based on the above Python code description and provide the complete Python code within triple backticks ```python ``` in the end!"""

    def _create_fix_prompt(self, prompt: str, code: str, error_message: str) -> str:
        """Create a prompt for code fixing."""
        return f"""Assuming you are a professional coding expert.

The following is Python code description and incorrect Python program translation and feedback.
```Python code description
{prompt}
```
```Incorrect Python program translation
{code}
```
```Feedback:
Got the wrong result: "{error_message}".
```

You should check the feedback, analyze and explain and correct errors in Incorrect Python program translation based on Python code descriptions and provide the complete modified Python code within triple backticks ```python ``` in the end!"""

    def _generate_response(self, prompt: str) -> str:
        """Generate a response from the Anthropic API."""
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=self.max_new_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _extract_python_code(self, text: str) -> Tuple[bool, str]:
        """Extract Python code from text."""
        pattern = re.compile(r'```python(.*?)```', re.DOTALL)
        matches = pattern.findall(text)

        if matches:
            max_lines = 0
            largest_code_block = ""

            for match in matches:
                code_block = match.strip()
                lines = code_block.split('\n')
                if len(lines) > max_lines:
                    max_lines = len(lines)
                    largest_code_block = code_block

            example_usage_pattern = re.compile(r'(.*?)# (Example usage|Test cases)', re.DOTALL)
            example_usage_match = example_usage_pattern.match(largest_code_block)

            if example_usage_match:
                cleaned_code = example_usage_match.group(1).strip()
            else:
                cleaned_code = largest_code_block

            return True, cleaned_code
        else:
            return False, ""


class AzureOpenAIModel(BaseLLMModel):
    """
    Implementation of an Azure OpenAI API model for CMCS.
    """

    def __init__(self, model_name: str, model_type: ModelType,
                 api_key: Optional[str] = None,
                 azure_endpoint: Optional[str] = None,
                 api_version: str = "2024-02-15-preview",
                 max_new_tokens: int = 2048,
                 temperature: float = 0.0):
        """
        Initialize the Azure OpenAI API model.

        Args:
            model_name: Name of the deployment (e.g., 'gpt-4')
            model_type: Type of model (A or B)
            api_key: Azure API key (will use AZURE_OPENAI_API_KEY env var if not provided)
            azure_endpoint: Azure endpoint URL
            api_version: Azure API version
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature
        """
        super().__init__(model_name, model_type)

        try:
            from openai import AzureOpenAI
        except ImportError:
            raise ImportError("openai package is required for Azure OpenAI models. Install with: pip install openai")

        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.api_version = api_version

        api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key must be provided or set in AZURE_OPENAI_API_KEY environment variable")

        if not azure_endpoint:
            azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            if not azure_endpoint:
                raise ValueError("Azure endpoint must be provided or set in AZURE_OPENAI_ENDPOINT environment variable")

        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version
        )

    def generate_code(self, prompt: str, additional_context: str = "") -> str:
        """Generate code based on the given prompt."""
        full_prompt = self._create_generation_prompt(prompt, additional_context)
        response = self._generate_response(full_prompt)
        _, code = self._extract_python_code(response)
        return code

    def fix_code(self, prompt: str, code: str, error_message: str) -> str:
        """Fix code based on error message."""
        fix_prompt = self._create_fix_prompt(prompt, code, error_message)
        response = self._generate_response(fix_prompt)
        _, fixed_code = self._extract_python_code(response)
        return fixed_code

    def _create_generation_prompt(self, prompt: str, additional_context: str = "") -> str:
        """Create a prompt for code generation."""
        return f"""Assuming you are a professional coding expert.

The following is a Python code description:
```
{prompt}
```
{additional_context}

You should generate Python code based on the above Python code description and provide the complete Python code within triple backticks ```python ``` in the end!"""

    def _create_fix_prompt(self, prompt: str, code: str, error_message: str) -> str:
        """Create a prompt for code fixing."""
        return f"""Assuming you are a professional coding expert.

The following is Python code description and incorrect Python program translation and feedback.
```Python code description
{prompt}
```
```Incorrect Python program translation
{code}
```
```Feedback:
Got the wrong result: "{error_message}".
```

You should check the feedback, analyze and explain and correct errors in Incorrect Python program translation based on Python code descriptions and provide the complete modified Python code within triple backticks ```python ``` in the end!"""

    def _generate_response(self, prompt: str) -> str:
        """Generate a response from the Azure OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_new_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def _extract_python_code(self, text: str) -> Tuple[bool, str]:
        """Extract Python code from text."""
        pattern = re.compile(r'```python(.*?)```', re.DOTALL)
        matches = pattern.findall(text)

        if matches:
            max_lines = 0
            largest_code_block = ""

            for match in matches:
                code_block = match.strip()
                lines = code_block.split('\n')
                if len(lines) > max_lines:
                    max_lines = len(lines)
                    largest_code_block = code_block

            example_usage_pattern = re.compile(r'(.*?)# (Example usage|Test cases)', re.DOTALL)
            example_usage_match = example_usage_pattern.match(largest_code_block)

            if example_usage_match:
                cleaned_code = example_usage_match.group(1).strip()
            else:
                cleaned_code = largest_code_block

            return True, cleaned_code
        else:
            return False, ""