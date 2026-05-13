# 复现指南模板

本指南用于记录如何复现论文中的主要方法、实验结果和系统演示。学生补充材料时，应将“待填写”部分替换为实际命令、路径和参数。

## 一、环境

- 操作系统：待填写，例如 Ubuntu 22.04、macOS 或服务器系统版本。
- Python 版本：待填写，建议记录精确版本，例如 Python 3.10.13。
- 包管理方式：待填写，例如 `pip`、`conda`、`poetry` 或 `uv`。
- GPU/CPU：待填写，包括显卡型号、显存、CPU 型号和内存。
- 外部服务：待填写，例如模型 API、数据库、队列服务或容器服务。

## 二、依赖

请在对应代码目录提供依赖文件，例如：

- `requirements.txt`
- `environment.yml`
- `pyproject.toml`
- `package.json`
- `Dockerfile`

建议记录安装命令：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

实际依赖文件位置：待填写。

## 三、数据准备

1. 下载或准备数据集，记录来源和版本。
2. 将原始数据放入 `05_datasets/raw/` 或对应章节 `data/`。
3. 运行预处理脚本，生成处理后数据。
4. 将样例、许可证和元数据补充到 `05_datasets/`。

数据准备命令：

```bash
# 待学生填写实际命令
python path/to/preprocess.py --input 05_datasets/raw --output 05_datasets/processed
```

## 四、配置

请提供配置样例，不要提交真实密钥。建议将真实配置放在本地未追踪文件中，将示例配置命名为 `config.example.yaml`。

需要记录的配置项包括：

- 模型名称和接口地址。
- 采样温度、候选数量和最大 token。
- 数据集路径。
- 输出目录。
- 测试命令。
- 日志级别。

配置文件位置：待填写。

## 五、运行命令

### 第 3 章跨模型协同代码生成

```bash
# 待学生填写
python 03_methods/chapter3_cross_model_codegen/scripts/run_experiment.py --config 03_methods/chapter3_cross_model_codegen/configs/example.yaml
```

### 第 4 章轨迹驱动修复

```bash
# 待学生填写
python 03_methods/chapter4_trace_driven_repair/scripts/run_repair.py --config 03_methods/chapter4_trace_driven_repair/configs/example.yaml
```

### 第 5 章过程对齐修复

```bash
# 待学生填写
python 03_methods/chapter5_process_aligned_repair/scripts/run_process_alignment.py --config 03_methods/chapter5_process_aligned_repair/configs/example.yaml
```

### 第 6 章仓库级代码生成

```bash
# 待学生填写
python 03_methods/chapter6_repo_level_codegen/scripts/run_repo_codegen.py --config 03_methods/chapter6_repo_level_codegen/configs/example.yaml
```

### 第 7 章系统演示

```bash
# 待学生填写
python 04_system/backend/run_server.py
```

前端启动命令：待填写。

## 六、输出位置

| 内容 | 建议输出位置 | 说明 |
|---|---|---|
| 原始模型输出 | `07_results/raw_outputs/` | 保留未经人工汇总的输出 |
| 实验日志 | `06_experiments/<dataset>/` | 按数据集和方法归档 |
| 汇总结果 | `07_results/summary_tables/` | 对应论文表格 |
| 最终图表 | `07_results/final_figures/` | 对应论文图号 |
| 案例分析 | `07_results/case_studies/` | 成功与失败案例 |

## 七、日志

每次复现实验应保留运行日志，日志中建议包含：

- 运行日期。
- 代码版本或 commit。
- 配置文件路径。
- 数据集版本。
- 模型名称和参数。
- 错误信息和重试记录。
- 最终输出路径。

## 八、常见报错

| 报错现象 | 可能原因 | 处理方式 |
|---|---|---|
| 模型接口调用失败 | 密钥未配置、网络异常或额度不足 | 检查本地环境变量和接口状态 |
| 测试命令无法运行 | 依赖未安装或路径错误 | 重新安装依赖并检查工作目录 |
| 数据文件找不到 | 数据未下载或配置路径错误 | 核对 `05_datasets/` 和配置文件 |
| 结果与论文不一致 | 模型版本、随机种子或数据版本不同 | 固定配置并记录差异 |
| 仓库级任务构建失败 | 目标仓库依赖复杂或系统依赖缺失 | 按 RepoExec 或 EvoCodeBench 任务记录补齐环境 |

## 九、学生补充位置

- 主要复现入口：待填写。
- 推荐复现实验顺序：待填写。
- 最小复现案例：待填写。
- 完整复现实验预计耗时：待填写。
- 已知无法复现项及原因：待填写。
