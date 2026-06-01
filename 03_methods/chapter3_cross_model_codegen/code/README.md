# CMCS - Cross-Model Collaboration for Enhancing LLM-Based Code Generation

CMCS (Collaborative Multi-model Code Generation Scheme) is a Python framework for collaborative multi-model code generation. The framework achieves efficient code generation through three tightly integrated components: dual-model collaborative code generation, diagnostic correction mechanism, and cross-model collaborative generation.

## Framework Structure

```
CMCS/
├── cmcs_framework/          # CMCS framework core implementation
│   ├── __init__.py         # Package initialization file
│   ├── core.py             # Core classes and interface definitions
│   ├── models.py           # Model implementations (HuggingFace, OpenAI, Anthropic, Azure)
│   ├── validators.py       # Code validators
│   ├── dual_model_generation.py      # Dual-model collaborative code generation module
│   ├── diagnostic_correction.py      # Diagnostic correction mechanism module
│   ├── cross_model_collaboration.py  # Cross-model collaborative generation module
│   └── framework.py        # Main framework integration
├── datasets/               # Dataset processing
│   ├── dataset_processor.py
│   ├── human_eval/         # HumanEval dataset
│   ├── human_eval_plus/    # HumanEval+ dataset
│   ├── APPS/               # APPS dataset
│   ├── CodeContest/        # CodeContest dataset
│   ├── mbpp/               # MBPP dataset
│   └── mbpp_plus/          # MBPP+ dataset
└── CMCS.py                 # CMCS main script
```

## Core Components

### 1. Dual-Model Collaborative Code Generation

Responsible for initial efficient parallel generation, dividing the problem set into two subsets, processed in parallel by two models respectively.

### 2. Diagnostic Correction Mechanism

Responsible for self-reflection and error correction within a single model, improving code pass rate through iterative correction loops.

### 3. Cross-Model Collaborative Generation

As a final safeguard mechanism, it utilizes the complementary advantages of different models to solve "stubborn problems".

## Supported Models

The framework supports multiple model types:

### 1. HuggingFace Models (Local)
- **Description**: Load and run models locally using HuggingFace Transformers
- **Examples**: `deepseek-coder-6.7b-base`, `codellama-7b-instruct`, `codeqwen-7b-chat`
- **Requirements**: GPU recommended, sufficient VRAM

### 2. API Models
- **OpenAI**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- **Azure OpenAI**: Your custom deployment names
- **Requirements**: API key (and endpoint for Azure)

## Built-in Datasets

The following datasets are pre-integrated into the framework and can be run directly. You can also add custom datasets following the instructions in the [Extending the Framework](#extending-the-framework) section.

The following datasets are pre-integrated into the framework and can be run directly:

| Dataset | Type | Problems | Description |
|---------|------|----------|-------------|
| **HumanEval** | Classic | 164 | Classic code generation evaluation dataset |
| **HumanEval+** | Enhanced | 164 | Enhanced version with additional test cases |
| **MBPP** | Basic | 257 | Mostly Basic Python Problems |
| **MBPP+** | Enhanced | 257 | Enhanced version with additional test cases |
| **APPS** | Competitive | 150 | Subset from APPS benchmark (from [MapCoder](https://arxiv.org/abs/2405.11403) paper) |
| **CodeContest** | Competitive | 165 | Code contest problems with public/private tests |

## Installation

### 1. Install Base Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Optional Dependencies for API Models

For OpenAI and Azure OpenAI models:
```bash
pip install openai
```

For Anthropic models:
```bash
pip install anthropic
```

For HuggingFace models with quantization:
```bash
pip install transformers accelerate bitsandbytes
```

## Usage

### Quick Start

#### Using HuggingFace Models (Default)

```bash
# Run HumanEval dataset
python CMCS.py --dataset human_eval --model_a deepseek-coder-6.7b-base --model_b codellama-7b-instruct

# Run HumanEval+ dataset
python CMCS.py --dataset human_eval_plus --model_a deepseek-coder-6.7b-base --model_b codellama-7b-instruct

# Run APPS dataset
python CMCS.py --dataset apps --model_a deepseek-coder-6.7b-base --model_b codellama-7b-instruct
```

#### Using OpenAI API

```bash
# Set API key via environment variable
export OPENAI_API_KEY="your-api-key"

# Run with OpenAI models
python CMCS.py \
    --dataset human_eval \
    --model_type openai \
    --model_a gpt-4 \
    --model_b gpt-3.5-turbo

# Or pass API key directly
python CMCS.py \
    --dataset mbpp \
    --model_type openai \
    --model_a gpt-4 \
    --model_b gpt-3.5-turbo \
    --api_key sk-xxx
```

#### Using Anthropic API

```bash
# Set API key via environment variable
export ANTHROPIC_API_KEY="your-api-key"

# Run with Claude models
python CMCS.py \
    --dataset apps \
    --model_type anthropic \
    --model_a claude-3-opus-20240229 \
    --model_b claude-3-sonnet-20240229
```

#### Using Azure OpenAI

```bash
# Set credentials via environment variables
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# Run with Azure deployment
python CMCS.py \
    --dataset codecontest \
    --model_type azure \
    --model_a gpt-4-deployment \
    --model_b gpt-35-turbo-deployment

# Or pass credentials directly
python CMCS.py \
    --dataset mbpp_plus \
    --model_type azure \
    --model_a gpt-4-deployment \
    --model_b gpt-35-turbo-deployment \
    --api_key xxx \
    --azure_endpoint https://your-resource.openai.azure.com/
```

### Command Line Parameters

#### General Parameters

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `--dataset` | Dataset to use | `human_eval` | `human_eval`, `human_eval_plus`, `apps`, `codecontest`, `mbpp`, `mbpp_plus` |
| `--data_path` | Path to datasets directory | `./datasets` | Any valid path |
| `--output` | Path to save results | `./results.json` | Any valid path |
| `--max_correction_attempts` | Max correction attempts | `5` | Integer |

#### Model Parameters

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `--model_type` | Type of model to use | `huggingface` | `huggingface`, `openai`, `anthropic`, `azure` |
| `--model_a` | Model A name/path | `deepseek-coder-6.7b-base` | Depends on model_type |
| `--model_b` | Model B name/path | `codellama-7b-instruct` | Depends on model_type |
| `--max_new_tokens` | Maximum tokens to generate | `2048` | Integer |
| `--temperature` | Sampling temperature (API only) | `0.0` | Float (0.0-2.0) |

#### API Authentication Parameters

| Parameter | Description | Required For |
|-----------|-------------|--------------|
| `--api_key` | API key for authentication | OpenAI, Anthropic, Azure |
| `--azure_endpoint` | Azure OpenAI endpoint URL | Azure only |
| `--api_version` | Azure API version | Azure only (default: `2024-02-15-preview`) |

### Environment Variables

Instead of passing API keys via command line, you can set them as environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-xxx"

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-xxx"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="xxx"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

### Advanced Usage Examples

#### Custom Parameters

```bash
# Custom correction attempts and output path
python CMCS.py \
    --dataset human_eval \
    --max_correction_attempts 3 \
    --output my_results.json

# Custom data path
python CMCS.py \
    --data_path /home/user/datasets \
    --model_a deepseek-coder-6.7b-base \
    --model_b codellama-7b-instruct
```

#### Mixing Different Model Types

Currently, both models must be of the same type. To use different model types (e.g., OpenAI + Anthropic), you would need to modify the code or run two separate instances.

#### Running with All Default Parameters

```bash
python CMCS.py
```

This will run with:
- Dataset: `human_eval`
- Model type: `huggingface`
- Model A: `deepseek-coder-6.7b-base`
- Model B: `codellama-7b-instruct`
- Output: `./results.json`

## Output Format

The framework generates a JSON file with the following structure:

```json
{
  "task_id": {
    "task_id": "string",
    "prompt": "string",
    "generated_code": "string",
    "is_correct": true/false,
    "error_type": "compilation/runtime/test/null",
    "error_message": "string",
    "execution_time": float,
    "model_type": "model_a/model_b",
    "attempt_count": int,
    "history": [...]
  }
}
```

## Extending the Framework

### Adding a New Dataset

1. **Prepare Dataset Structure**
   ```
   datasets/
   └── your_dataset/
       ├── data/
       │   └── your_data.jsonl  # or .parquet, .jsonl.gz
       └── execution.py         # Must contain check_correctness function
   ```

2. **Update `datasets/dataset_processor.py`**
   - Add dataset path in `__init__` method
   - Add loading logic in `load_dataset` method

3. **Update `cmcs_framework/validators.py`**
   - Create a new validator class inheriting from `CodeValidator`

4. **Update `CMCS.py`**
   - Add dataset loading function
   - Add CLI option and main logic

### Adding a New Model Provider

1. **Create model class in `cmcs_framework/models.py`**
   - Inherit from `BaseLLMModel`
   - Implement `generate_code()` and `fix_code()` methods

2. **Update `CMCS.py`**
   - Import the new model class
   - Add model type to `--model_type` choices
   - Add initialization logic in `main()`

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'openai'`
- **Solution**: Install openai package: `pip install openai`

**Issue**: `ModuleNotFoundError: No module named 'anthropic'`
- **Solution**: Install anthropic package: `pip install anthropic`

**Issue**: API key not found
- **Solution**: Set API key via `--api_key` parameter or environment variable

**Issue**: CUDA out of memory (HuggingFace models)
- **Solution**: Use smaller models, enable quantization, or use API models instead

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{cmcs_framework,
  title={CMCS Framework: Cross-Model Collaboration for Enhancing LLM-Based Code Generation},
  author={CMCS Team},
  year={2024}
}
```

## License

This project is licensed under the MIT License.
