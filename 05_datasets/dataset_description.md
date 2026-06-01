# 数据集说明

本文件用于登记本论文涉及的所有数据集。每个数据集都应说明来源、用途、处理方式、公开限制和许可证情况。若数据因版权、体积或隐私原因无法直接提交，应说明完整数据位置、访问条件和联系人。

## 数据集登记表

| 数据集名称 | 来源 | 对应章节 | 用途 | 数据格式 | 是否可公开 | 预处理方式 | 样例位置 | 使用限制 | 许可证情况 |
|---|---|---|---|---|---|---|---|---|---|
| HumanEval | OpenAI, https://github.com/openai/human-eval | 第 3、4、5 章 | 函数级代码生成与修复评测 | JSONL (task_id, prompt, canonical_solution, test, entry_point) | 可公开 | 直接使用原始数据 | `05_datasets/samples/` | 无特殊限制 | MIT License |
| MBPP | Google, https://github.com/google-research/google-research/tree/master/mbpp | 第 3、4、5 章 | 编程题代码生成与测试通过率评测 | JSON (task_id, text, code, test_list) | 可公开 | 使用 sanitized 子集 | `05_datasets/samples/` | 无特殊限制 | Apache 2.0 License |
| HumanEvalPlus | EvalPlus, https://github.com/evalplus/evalplus | 第 3、5 章 | 加强测试场景下的代码生成评测 | JSONL (在 HumanEval 基础上扩展 80 倍测试用例) | 可公开 | 通过 evalplus 工具生成增强测试 | `05_datasets/samples/` | 无特殊限制 | Apache 2.0 License |
| MBPPPlus | EvalPlus, https://github.com/evalplus/evalplus | 第 3、5 章 | 加强测试场景下的代码生成评测 | JSONL (在 MBPP 基础上扩展 35 倍测试用例) | 可公开 | 通过 evalplus 工具生成增强测试 | `05_datasets/samples/` | 无特殊限制 | Apache 2.0 License |
| BigCodeBench | BigCode Project, https://github.com/bigcode-project/bigcodebench | 第 3、5 章 | 更复杂代码生成任务评测（多样函数调用与复杂指令） | JSONL (task_id, complete_prompt, instruct_prompt, canonical_solution, test) | 可公开 | 直接使用 HuggingFace 数据集 | `05_datasets/samples/` | 无特殊限制 | Apache 2.0 License |
| ClassEval | https://github.com/luzh0422/ClassEval | 第 4、5 章 | 类级代码生成与修复评测 | JSON (类定义、方法签名、测试用例) | 可公开 | 直接使用原始数据 | `05_datasets/samples/` | 学术研究用途 | MIT License |
| RepoExec | FSoft-AI4Code, https://github.com/FSoft-AI4Code/RepoExec | 第 6 章 | 仓库级代码生成与修复评测 | JSONL (full/medium/small context 三个子集) | 可公开 | 直接使用 HuggingFace 数据集 | `05_datasets/samples/` | 无特殊限制 | CC0 License |
| EvoCodeBench | https://github.com/NL2Code/EvoCodeBench | 第 6 章 | 演化场景下的仓库级代码生成与修复评测 | JSON (仓库、commit、函数、测试) | 可公开 | 直接使用原始数据 | `05_datasets/samples/` | 无特殊限制 | MIT License |
| APPS | UC Berkeley, https://github.com/hendrycks/apps | 第 3 章 | 编程竞赛级代码生成评测（训练/验证） | JSON (problem_id, question, input_output, starter_code) | 可公开 | 使用 HuggingFace 数据集加载 | `05_datasets/samples/` | 学术研究用途 | CC BY-SA 3.0 License |
| CodeContests | Google DeepMind, https://github.com/google-deepmind/code_contests | 第 3 章 | 竞赛级算法代码生成评测（训练/验证） | Protocol Buffer / Parquet | 可公开 | 使用 HuggingFace 数据集加载 | `05_datasets/samples/` | 无特殊限制 | Apache 2.0 (代码) / CC BY 4.0 (数据) |
| 自建轨迹数据 | 本论文实验生成 | 第 4、7 章 | 运行轨迹分析、自动调试和案例展示 | JSON/JSONL (执行日志、调试轨迹) | 部分可公开 | 从 CMCS/TraceCoder 框架运行生成 | `05_datasets/samples/` | 需脱敏 | 本论文自有数据 |

## 数据集详细说明

### HumanEval

- **来源**: OpenAI 发布，GitHub 仓库 https://github.com/openai/human-eval，HuggingFace: `openai_humaneval`
- **论文**: "Evaluating Large Language Models Trained on Code" (arXiv:2107.03374)
- **对应章节**: 第 3 章（跨模型协同代码生成）、第 4 章（轨迹驱动代码修复）、第 5 章（实验评测）
- **用途**: 函数级代码生成与修复的基准评测，计算 pass@k 指标
- **数据格式**: JSONL 格式，包含 164 个 Python 编程问题，每个问题包含 task_id、prompt（函数签名+docstring）、canonical_solution（参考解答）、test（单元测试）、entry_point（入口函数名）
- **是否可公开**: 可公开
- **预处理方式**: 直接使用原始数据，无需额外处理
- **样例位置**: `05_datasets/samples/humaneval/`
- **使用限制**: 无特殊限制，可用于学术研究和商用
- **许可证情况**: MIT License

### MBPP (Mostly Basic Python Problems)

- **来源**: Google 发布，GitHub: https://github.com/google-research/google-research/tree/master/mbpp，HuggingFace: `mbpp`
- **论文**: "Program Synthesis with Large Language Models" (arXiv:2108.07732)
- **对应章节**: 第 3 章（跨模型协同代码生成）、第 4 章（轨迹驱动代码修复）、第 5 章（实验评测）
- **用途**: 编程题代码生成与测试通过率评测
- **数据格式**: JSON 格式，包含约 1000 个 Python 编程问题，每个问题包含 task_id、text（问题描述）、code（参考解答）、test_list（测试用例列表）。实验中使用 sanitized 子集（经人工验证的 399 题）
- **是否可公开**: 可公开
- **预处理方式**: 使用 sanitized 子集（hand-verified subset）
- **样例位置**: `05_datasets/samples/mbpp/`
- **使用限制**: 无特殊限制
- **许可证情况**: Apache 2.0 License

### HumanEvalPlus

- **来源**: EvalPlus 框架，GitHub: https://github.com/evalplus/evalplus，HuggingFace: `evalplus/humanevalplus`
- **论文**: "EvalPlus: Programming Benchmarks for Large Language Models" (NeurIPS 2023, arXiv:2305.14257)
- **对应章节**: 第 3 章（跨模型协同代码生成）、第 5 章（实验评测）
- **用途**: 在 HumanEval 基础上扩展 80 倍测试用例，进行更严格的代码生成评测
- **数据格式**: JSONL 格式，结构与 HumanEval 相同，但 test 字段包含更多增强测试用例
- **是否可公开**: 可公开
- **预处理方式**: 通过 `evalplus` 工具包生成增强测试用例
- **样例位置**: `05_datasets/samples/humanevalplus/`
- **使用限制**: 无特殊限制
- **许可证情况**: Apache 2.0 License

### MBPPPlus

- **来源**: EvalPlus 框架，GitHub: https://github.com/evalplus/evalplus，HuggingFace: `evalplus/mbppplus`
- **论文**: "EvalPlus: Programming Benchmarks for Large Language Models" (NeurIPS 2023, arXiv:2305.14257)
- **对应章节**: 第 3 章（跨模型协同代码生成）、第 5 章（实验评测）
- **用途**: 在 MBPP 基础上扩展 35 倍测试用例，进行更严格的代码生成评测
- **数据格式**: JSONL 格式，结构与 MBPP 相同，但 test_list 字段包含更多增强测试用例
- **是否可公开**: 可公开
- **预处理方式**: 通过 `evalplus` 工具包生成增强测试用例
- **样例位置**: `05_datasets/samples/mbppplus/`
- **使用限制**: 无特殊限制
- **许可证情况**: Apache 2.0 License

### BigCodeBench

- **来源**: BigCode Project，GitHub: https://github.com/bigcode-project/bigcodebench，HuggingFace: `bigcode/bigcodebench`
- **论文**: "BigCodeBench: Benchmarking Code Generation with Diverse Function Calls and Complex Instructions" (ICLR 2025 Oral, arXiv:2406.15877)
- **对应章节**: 第 3 章（跨模型协同代码生成）、第 5 章（实验评测）
- **用途**: 评估 LLM 在多样函数调用和复杂指令下的代码生成能力，包含 1140 个任务，涉及 139 个库的 7500+ API 调用
- **数据格式**: JSONL 格式，包含 task_id、complete_prompt（完整提示）、instruct_prompt（指令提示）、canonical_solution（参考解答）、test（单元测试）
- **是否可公开**: 可公开
- **预处理方式**: 直接使用 HuggingFace 数据集，无需额外处理
- **样例位置**: `05_datasets/samples/bigcodebench/`
- **使用限制**: 无特殊限制
- **许可证情况**: Apache 2.0 License

### ClassEval

- **来源**: GitHub: https://github.com/luzh0422/ClassEval，HuggingFace: `luzh0422/ClassEval`
- **论文**: "ClassEval: A Manually-Crafted Benchmark for Evaluating LLMs on Class-Level Code Generation" (ICSE 2024, arXiv:2308.01861)
- **对应章节**: 第 4 章（轨迹驱动代码修复）、第 5 章（实验评测）
- **用途**: 类级代码生成与修复评测，包含 100 个手工编写的 Python 类级编程任务
- **数据格式**: JSON 格式，包含类定义、方法签名、docstring、测试用例等
- **是否可公开**: 可公开
- **预处理方式**: 直接使用原始数据
- **样例位置**: `05_datasets/samples/classeval/`
- **使用限制**: 学术研究用途
- **许可证情况**: MIT License

### RepoExec

- **来源**: FSoft-AI4Code，GitHub: https://github.com/FSoft-AI4Code/RepoExec，HuggingFace: `Fsoft-AIC/RepoExec`
- **论文**: "RepoExec: Evaluate Code Generation with a Repository-Level Executable Benchmark" (arXiv:2406.11927)
- **对应章节**: 第 6 章（仓库级代码生成与修复）
- **用途**: 仓库级代码生成评测，关注可执行性、功能正确性和跨文件上下文依赖
- **数据格式**: JSONL 格式，包含 full_context、medium_context、small_context 三个子集，每个样本包含任务描述、跨文件依赖、目标函数签名、测试用例等
- **是否可公开**: 可公开
- **预处理方式**: 直接使用 HuggingFace 数据集
- **样例位置**: `05_datasets/samples/repoexec/`
- **使用限制**: 无特殊限制
- **许可证情况**: CC0 License

### EvoCodeBench

- **来源**: NL2Code，GitHub: https://github.com/NL2Code/EvoCodeBench，HuggingFace: `NL2Code/EvoCodeBench`
- **论文**: "EvoCodeBench: An Evolving Code Benchmark with Real-World Code Repositories" (arXiv:2402.12871)
- **对应章节**: 第 6 章（仓库级代码生成与修复）
- **用途**: 演化场景下的仓库级代码生成评测，基于真实 GitHub 仓库的 commit 历史构建
- **数据格式**: JSON 格式，包含仓库信息、commit 哈希、目标函数、测试用例、依赖上下文等
- **是否可公开**: 可公开
- **预处理方式**: 直接使用原始数据
- **样例位置**: `05_datasets/samples/evocodebench/`
- **使用限制**: 无特殊限制
- **许可证情况**: MIT License

### APPS (Automated Programming Progress Standard)

- **来源**: UC Berkeley，GitHub: https://github.com/hendrycks/apps，HuggingFace: `codeparrot/apps`
- **论文**: "Measuring Coding Challenge Competence With APPS" (NeurIPS 2021, arXiv:2105.09938)
- **对应章节**: 第 3 章（跨模型协同代码生成，用于训练或辅助评测）
- **用途**: 编程竞赛级代码生成评测，包含 10000 个不同难度的编程问题
- **数据格式**: JSON 格式，包含 problem_id、question（问题描述）、input_output（输入输出测试用例）、starter_code（起始代码）
- **是否可公开**: 可公开
- **预处理方式**: 使用 HuggingFace 数据集加载，按难度分为 introductory/interview/competition 三个级别
- **样例位置**: `05_datasets/samples/apps/`
- **使用限制**: 学术研究用途
- **许可证情况**: CC BY-SA 3.0 License

### CodeContests

- **来源**: Google DeepMind，GitHub: https://github.com/google-deepmind/code_contests，HuggingFace: `deepmind/code_contests`
- **论文**: "Competition-Level Code Generation with AlphaCode" (Science 2022, arXiv:2203.07814)
- **对应章节**: 第 3 章（跨模型协同代码生成，用于训练或辅助评测）
- **用途**: 竞赛级算法代码生成评测，包含来自 Codeforces、AtCoder 等平台的编程竞赛题目
- **数据格式**: Protocol Buffer / Parquet 格式，包含 problem 描述、测试用例、参考解答等。分为 train (13328)、valid (117)、test (165) 三个 split
- **是否可公开**: 可公开
- **预处理方式**: 使用 HuggingFace 数据集加载
- **样例位置**: `05_datasets/samples/codecontests/`
- **使用限制**: 无特殊限制
- **许可证情况**: Apache 2.0 License (代码) / CC BY 4.0 International License (数据)

### 自建轨迹数据

- **来源**: 本论文实验过程中通过 CMCS 和 TraceCoder 框架运行生成
- **对应章节**: 第 4 章（轨迹驱动代码修复）、第 7 章（总结与展望中的案例分析）
- **用途**: 运行轨迹分析、自动调试过程展示、修复案例研究
- **数据格式**: JSON/JSONL 格式，包含执行日志、调试轨迹、中间状态、修复建议等
- **是否可公开**: 部分可公开（需脱敏处理）
- **预处理方式**: 从 CMCS/TraceCoder 框架运行过程中采集，经过脱敏和格式化处理
- **样例位置**: `05_datasets/samples/trajectories/`
- **使用限制**: 仅限学术研究，不可商用
- **许可证情况**: 本论文自有数据，遵循论文开源协议

## 第 6 章数据集说明

第 6 章"基于上下文感知与记忆增强的仓库级代码生成方法"的实验数据包括 RepoExec 和 EvoCodeBench。两个数据集的说明如下：

### RepoExec（第 6 章）

- **任务来源**: 从真实 GitHub 仓库中抽取，经过可执行性验证和测试用例自动生成
- **仓库版本**: 使用 HuggingFace 数据集 `Fsoft-AIC/RepoExec` 的固定版本
- **测试命令**: 基于 `unittest` 框架执行生成的测试用例
- **评价指标**: pass@1、pass@10、可执行率、上下文依赖正确率
- **结果文件位置**: `06_experiments/chapter6_repo_level/`
- **许可证情况**: CC0 License

### EvoCodeBench（第 6 章）

- **任务来源**: 基于真实 GitHub 仓库的 commit 历史构建
- **仓库版本**: 使用 HuggingFace 数据集 `NL2Code/EvoCodeBench` 的固定版本
- **测试命令**: 基于仓库自带的测试框架执行
- **评价指标**: pass@1、pass@10、演化场景下的性能变化
- **结果文件位置**: `06_experiments/chapter6_repo_level/`
- **许可证情况**: MIT License
