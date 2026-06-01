"""
CMCS Framework Package

This package implements the Collaborative Multi-model Code Generation Scheme (CMCS) framework.
"""

from .framework import CMCSFramework
from .core import BaseLLMModel, CodeValidator, CodeGenerationResult, ErrorType, ModelType

__all__ = [
    "CMCSFramework",
    "BaseLLMModel", 
    "CodeValidator",
    "CodeGenerationResult",
    "ErrorType",
    "ModelType"
]