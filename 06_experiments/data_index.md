# 实验数据索引

本目录存放论文各章节的实验原始日志与结果。由于原始日志文件总量约 3.5GB，部分单文件超过 300MB，超出 GitHub 单文件限制（100MB），因此原始日志未直接上传至本仓库。本索引页记录所有实验数据的分类、归属章节、文件清单及访问方式。

---

## 数据分类说明

论文涉及两大核心框架，其实验数据在文件命名和存储上有交叉：

| 框架 | 对应章节 | 核心方法 | 使用数据集 | 文件命名特征 |
|---|---|---|---|---|
| **CMCS**（跨模型协同代码生成） | 第 3 章 | 双模型生成 → 跨模型协作 → 诊断修正 | HumanEval, HumanEvalPlus, MBPP, MBPPPlus, APPS, CodeContest | `3step_5repaired`、模型名（gemini/codeqwen） |
| **TraceCoder**（轨迹驱动修复） | 第 4 章 | 轨迹分析 → 修复 → 回滚 | HumanEval, HumanEvalPlus, BigCodeBench, ClassEval | `repair-mid-1`、`self-debugging`、`self-planning`、`COT`、`INTERVENOR` |
| **过程对齐修复** | 第 5 章 | 测试生成 → 仲裁 → 最优选择 | HumanEvalPlus, BigCodeBench | `3step_5repaired`（BigCodeBench）、`COT_5repaired`、`self-debugging_5repaired` |
| **仓库级生成** | 第 6 章 | 上下文记忆 → 检索 → 补丁生成 | RepoExec, EvoCodeBench | 无本地日志（使用公开基准评测） |

### CMCS 与 TraceCoder 数据区分规则

1. **按数据集区分**：
   - **CMCS 专属**：MBPP、MBPPPlus、APPS、CodeContest 数据集上的实验仅属于第 3 章
   - **TraceCoder 专属**：BigCodeBench、ClassEval 数据集上的实验仅属于第 4/5 章
   - **共享数据集**：HumanEval、HumanEvalPlus 上的实验需按方法名进一步区分

2. **按方法名区分（HumanEval/HumanEvalPlus）**：
   - `3step_5repaired` → 第 3 章 CMCS（3 步协同生成 + 5 轮诊断修正）
   - `repair-mid-1_*_3steps` → 第 4 章 TraceCoder（轨迹驱动修复）
   - `self-debugging` → 第 4 章 TraceCoder 基线
   - `self-planning` → 第 4 章 TraceCoder 基线
   - `COT` / `COT+INTERVENOR` → 第 4 章 TraceCoder 基线
   - `INTERVENOR` → 第 4 章 TraceCoder 基线

3. **BigCodeBench 上的 `3step_5repaired`/`COT_5repaired`/`self-debugging_5repaired`** → 第 5 章过程对齐修复

---

## 第 3 章 CMCS 实验数据

### 3.1 HumanEval 跨模型协同生成

| 文件名 | 模型 | 大小 | 说明 |
|---|---|---|---|
| `humaneval_3step_5repaired_gemini.log` | Gemini | 53MB | 3步协同+5轮修正 |
| `humaneval_3step_5repaired_codeqwen.log` | CodeQwen | 28MB | 3步协同+5轮修正 |

### 3.2 HumanEvalPlus 跨模型协同生成

| 文件名 | 模型 | 大小 | 说明 |
|---|---|---|---|
| `humanevalplus_3step_5repaired_gemini.log` | Gemini | 5.0MB | 3步协同+5轮修正 |
| `humanevalplus_3step_5repaired_codeqwen.log` | CodeQwen | 13MB | 3步协同+5轮修正（第1次） |
| `humanevalplus_3step_5repaired_codeqwen2.log` | CodeQwen | 10MB | 3步协同+5轮修正（第2次） |

### 3.3 MBPP / MBPPPlus / APPS / CodeContest

这些数据集的 CMCS 实验结果已整合在 CMCS 代码仓库（`03_methods/chapter3_cross_model_codegen/code/`）中，原始日志未单独存储。

---

## 第 4 章 TraceCoder 实验数据

### 4.1 HumanEval 轨迹驱动修复

| 文件名 | 模型 | 大小 | 方法 | 说明 |
|---|---|---|---|---|
| `humaneval-repair-mid-1_deepseek_3steps.log` | DeepSeek | 602KB | repair | 3步修复 |
| `humaneval-repair-mid-1_qwen_3steps.log` | Qwen | 1.6MB | repair | 3步修复 |
| `humaneval-self-debugging-deepseek.log` | DeepSeek | 303KB | self-debugging | 自调试基线 |
| `humaneval-self-debugging-qwen.log` | Qwen | 386KB | self-debugging | 自调试基线 |
| `humaneval-self-planning-mid-1_deepseek.log` | DeepSeek | 612KB | self-planning | 自规划基线 |
| `humaneval-self-planning-mid-1_qwen.log` | Qwen | 843KB | self-planning | 自规划基线 |
| `humaneval-self-planning-mid-1_gemini-2.5-flash.log` | Gemini | — | self-planning | 自规划基线 |
| `humaneval-COT+INTERVENOR-mid-1_deepseek.log` | DeepSeek | 788KB | COT+INTERVENOR | 组合基线 |
| `humaneval-COT+INTERVENOR-mid-1_qwen.log` | Qwen | 864KB | COT+INTERVENOR | 组合基线 |
| `humaneval-COT+INTERVENOR-mid-1_gemini-2.5-flash_3steps.log` | Gemini | — | COT+INTERVENOR | 组合基线 |
| `humaneval_self-debugging_5repaired_gemini2.5flash0417.log` | Gemini | 530KB | self-debugging | 自调试+5轮修正 |

### 4.2 HumanEvalPlus 轨迹驱动修复

| 文件名 | 模型 | 大小 | 方法 | 说明 |
|---|---|---|---|---|
| `humanevalplus-repair-mid-1_deepseek_3steps.log` | DeepSeek | 3.9MB | repair | 3步修复 |
| `humanevalplus-repair-mid-1_qwen_3steps.log` | Qwen | 9.2MB | repair | 3步修复 |
| `humanevalplus-repair-mid-1_codeqwen-2.5-flash_3steps.log` | CodeQwen | 5.8MB | repair | 3步修复 |
| `humanevalplus-self-debugging-deepseek.log` | DeepSeek | 341KB | self-debugging | 自调试基线 |
| `humanevalplus-self-debugging-qwen.log` | Qwen | 421KB | self-debugging | 自调试基线 |
| `humanevalplus-self-debugging-mid-1_gemini-2.5-flash_3steps.log` | Gemini | 632KB | self-debugging | 自调试基线 |
| `humanevalplus-self-planning-mid-1_deepseek.log` | DeepSeek | 619KB | self-planning | 自规划基线 |
| `humanevalplus-self-planning-mid-1_qwen.log` | Qwen | 844KB | self-planning | 自规划基线 |
| `humanevalplus-self-planning-mid-1_gemini-2.5-flash_3steps.log` | Gemini | 792KB | self-planning | 自规划基线 |
| `humanevalplus-COT+INTERVENOR-mid-1_deepseek.log` | DeepSeek | 1.1MB | COT+INTERVENOR | 组合基线 |
| `humanevalplus-COT+INTERVENOR-mid-1_qwen.log` | Qwen | 1.4MB | COT+INTERVENOR | 组合基线 |
| `humanevalplus-COT+INTERVENOR-mid-1_gemini-2.5-flash_3steps.log` | Gemini | 1.5MB | COT+INTERVENOR | 组合基线 |

### 4.3 BigCodeBench 轨迹驱动修复

| 文件名 | 模型 | 大小 | 方法 | 说明 |
|---|---|---|---|---|
| `bigcodebench-repair-mid-1_deepseek_3steps.log` | DeepSeek | 67MB | repair | 3步修复 |
| `bigcodebench-repair-mid-1_deepseek.log` | DeepSeek | 19MB | repair | 单步修复 |
| `bigcodebench-repair-mid-1_qwen_3steps.log` | Qwen | 332MB | repair | 3步修复 |
| `bigcodebench-repair-mid-1_gemini-2.5-flash_3steps22.log` | Gemini | 137MB | repair | 3步修复 |
| `bigcodebench_instruct-repair-mid-1_deepseek_3steps.log` | DeepSeek | 102MB | repair | instruct模式3步修复 |
| `bigcodebench_instruct-repair-mid-1_qwen_3steps.log` | Qwen | 251MB | repair | instruct模式3步修复 |
| `bigcodebench_instruct-repair-mid-1_gemini-2.5-flash_3steps23.log` | Gemini | 60MB | repair | instruct模式3步修复 |
| `bigcodebench-COT-mid-1_deepseek.log` | DeepSeek | 31MB | COT | COT基线 |
| `bigcodebench-COT-mid-1_qwen.log` | Qwen | 69MB | COT | COT基线 |
| `bigcodebench_instruct-COT-mid-1_deepseek.log` | DeepSeek | 40MB | COT | instruct模式COT基线 |
| `bigcodebench_instruct-COT-mid-1_qwen.log` | Qwen | 78MB | COT | instruct模式COT基线 |
| `bigcodebench-self-planning-mid-1_deepseek.log` | DeepSeek | 8.3MB | self-planning | 自规划基线 |
| `bigcodebench-self-planning-mid-1_qwen.log` | Qwen | 11.6MB | self-planning | 自规划基线 |
| `bigcodebench-self-planning-mid-1_gemini-2.5-flash.log` | Gemini | 10MB | self-planning | 自规划基线 |
| `bigcodebench_instruct-self-planning-mid-1_deepseek.log` | DeepSeek | 7.7MB | self-planning | instruct模式自规划基线 |
| `bigcodebench_instruct-self-planning-mid-1_qwen.log` | Qwen | 10MB | self-planning | instruct模式自规划基线 |
| `bigcodebench_intruct-self-planning-mid-1_gemini-2.5-flash.log` | Gemini | 9.2MB | self-planning | instruct模式自规划基线 |
| `bigcodebench-self-debugging-mid-1_qwen.log` | Qwen | 33MB | self-debugging | 自调试基线 |
| `bigcodebench_instruct_self_debugging-repair-mid-1_qwen.log` | Qwen | 38MB | self-debugging+repair | 自调试+修复 |
| `bigcodebench_instruct_self_debugging-repair-mid-1_deepseek.log` | DeepSeek | 18MB | self-debugging+repair | 自调试+修复 |

### 4.4 ClassEval 轨迹驱动修复

| 文件名 | 模型 | 大小 | 方法 | 说明 |
|---|---|---|---|---|
| `classeval-repair-mid-1_deepseek_3steps.log` | DeepSeek | 13MB | repair | 3步修复 |
| `classeval-repair-mid-1_qwen-plus_3steps.log` | Qwen-Plus | 89MB | repair | 3步修复 |
| `classeval-repair-mid-1_gemini-2.5-flash_3steps2.log` | Gemini | 18MB | repair | 3步修复 |
| `classeval-COT-mid-1_deepseek.log` | DeepSeek | 6.9MB | COT | COT基线 |
| `classeval-INTERVENOR-mid-1_qwen-plus.log` | Qwen-Plus | 8.7MB | INTERVENOR | INTERVENOR基线 |
| `classeval-self-debugging-mid-1_deepseek.log` | DeepSeek | 3.9MB | self-debugging | 自调试基线 |
| `classeval-self-debugging-mid-1_qwen-plus.log` | Qwen-Plus | 5.3MB | self-debugging | 自调试基线 |
| `classeval-self-planning-mid-1_deepseek.log` | DeepSeek | 1.4MB | self-planning | 自规划基线 |
| `classeval-self-planning-mid-1_qwen-plus.log` | Qwen-Plus | 2.7MB | self-planning | 自规划基线 |

---

## 第 5 章 过程对齐修复实验数据

### 5.1 BigCodeBench 过程对齐修复

| 文件名 | 模型 | 大小 | 方法 | 说明 |
|---|---|---|---|---|
| `bigcodebench_3steps_5repaired_gemini2.5flash0417.log` | Gemini | 228MB | 3step+5repaired | 过程对齐3步+5轮修正 |
| `bigcodebench_instruct_3steps_5repaired_gemini2.5flash0417.log` | Gemini | 154MB | 3step+5repaired | instruct模式过程对齐 |
| `bigcodebench_COT_5repaired_gemini2.5flash0417.log` | Gemini | 56MB | COT+5repaired | COT基线+5轮修正 |
| `bigcodebench_instruct_COT_5repaired_gemini2.5flash0417.log` | Gemini | 72MB | COT+5repaired | instruct模式COT+5轮修正 |
| `bigcodebench_self-debugging_5repaired_gemini2.5flash0417.log` | Gemini | 35MB | self-debugging+5repaired | 自调试+5轮修正 |
| `bigcodebench_instruct_self-debugging_5repaired_gemini2.5flash0417.log` | Gemini | 38MB | self-debugging+5repaired | instruct模式自调试+5轮修正 |

---

## 消融实验（第 4/5 章）

| 文件名 | 模型 | 大小 | 消融项 | 说明 |
|---|---|---|---|---|
| `bigcodebench-repair-mid-1_gemini-2.5-flash_3steps_no_HLLM.log` | Gemini | 73MB | 去除高层语言模型 | 验证HLLM贡献 |
| `bigcodebench-repair-mid-1_gemini-2.5-flash_3steps_no_RM.log` | Gemini | 3.7MB | 去除回滚机制 | 验证回滚贡献 |
| `bigcodebench-repair-mid-1_gemini-2.5-flash_3steps_no_HLLM_RM.log` | Gemini | 3.5MB | 去除HLLM和回滚 | 验证联合贡献 |
| `bigcodebench-repair-mid-1_gemini-2.5-flash_3steps_3.log` | Gemini | 17MB | 完整模型（对照） | 消融对照实验 |
| `bigcodebench-repair-mid-1_gemini-2.5-flash_3steps_23.log` | Gemini | 59MB | 完整模型（对照） | 消融对照实验 |

---

## 参数影响实验（第 4/5 章）

| 文件名 | 模型 | 大小 | 参数设置 | 说明 |
|---|---|---|---|---|
| `bigcodebench_gemini_noimprove_1_attempts_1-5.log` | Gemini | 14MB | 不改进阈值=1, 尝试1-5 | 阈值敏感性 |
| `bigcodebench_gemini_noimprove_1_attempts_1-10.log` | Gemini | 8.4MB | 不改进阈值=1, 尝试1-10 | 阈值敏感性 |
| `bigcodebench_gemini_noimprove_2_attempts_1-5.log` | Gemini | 20MB | 不改进阈值=2, 尝试1-5 | 阈值敏感性 |
| `bigcodebench_gemini_noimprove_3_attempts_1-5.log` | Gemini | 23MB | 不改进阈值=3, 尝试1-5 | 阈值敏感性 |
| `bigcodebench_gemini_noimprove_3_attempts_1-10.log` | Gemini | 8.1MB | 不改进阈值=3, 尝试1-10 | 阈值敏感性 |
| `bigcodebench_gemini_noimprove_4_attempts_1-5.log` | Gemini | 26MB | 不改进阈值=4, 尝试1-5 | 阈值敏感性 |
| `bigcodebench_gemini_noimprove_5_attempts_1-5.log` | Gemini | 28MB | 不改进阈值=5, 尝试1-5 | 阈值敏感性 |
| `bigcodebench_gemini_noimprove_5_attempts_1-10.log` | Gemini | 5.3KB | 不改进阈值=5, 尝试1-10 | 阈值敏感性（未完成） |

---

## 成本分析实验

| 文件名 | 数据集 | 模型 | 大小 | 方法 | 说明 |
|---|---|---|---|---|---|
| `classeval_gemini_3step.log` | ClassEval | Gemini | 8.3MB | 3step | 3步修复成本 |
| `classeval_gemini_cot.log` | ClassEval | Gemini | 1.2MB | COT | COT基线成本 |
| `classeval_gemini_cot_interventor.log` | ClassEval | Gemini | 2.0MB | COT+INTERVENOR | 组合基线成本 |
| `classeval_gemini_interventor.log` | ClassEval | Gemini | 16MB | INTERVENOR | INTERVENOR基线成本 |
| `classeval_gemini_planning.log` | ClassEval | Gemini | 1.8MB | self-planning | 自规划基线成本 |
| `classeval_gemini_self_debugging.log` | ClassEval | Gemini | 21MB | self-debugging | 自调试基线成本 |
| `humanevalplus_gemini_3step.log` | HumanEvalPlus | Gemini | 6.0MB | 3step | 3步修复成本 |
| `humanevalplus_gemini_cot_interventor.log` | HumanEvalPlus | Gemini | 1.6MB | COT+INTERVENOR | 组合基线成本 |
| `humanevalplus_gemini_planning.log` | HumanEvalPlus | Gemini | 805KB | self-planning | 自规划基线成本 |
| `humanevalplus_gemini_self_debugging.log` | HumanEvalPlus | Gemini | 638KB | self-debugging | 自调试基线成本 |

---

## 错误分析实验

| 文件名 | 数据集 | 大小 | 说明 |
|---|---|---|---|
| `classeval.log` | ClassEval | — | ClassEval错误分析 |
| `bigcodebench.log` | BigCodeBench | 127MB | BigCodeBench错误分析 |
| `bigcodebench-complete_prompt.log` | BigCodeBench | 159MB | BigCodeBench完整提示错误分析 |

---

## 原始数据访问方式

由于原始日志文件总量约 3.5GB，部分单文件超过 300MB，无法直接上传至 GitHub。可通过以下方式获取：

1. **本地路径**：`/home/speedaye/work/材料/数据/实验数据/`
2. **按需提取**：可根据上述索引表中的文件名，从本地路径复制所需日志
3. **结果摘要**：各实验的关键结果已整理在 `07_results/summary_tables/` 目录下

### 目录结构

```
实验数据/
├── humaneval/                    # HumanEval 实验（CMCS + TraceCoder）
├── humanevalplus/                # HumanEvalPlus 实验（CMCS + TraceCoder）
├── bigcodebench/                 # BigCodeBench 实验（第5章过程对齐）
├── deepseek/                     # DeepSeek 模型实验
│   ├── humaneval/
│   ├── humanevalplus/
│   ├── bigcodebench/
│   └── classeval/
├── qwen/                         # Qwen 模型实验
│   ├── humaneval/
│   ├── humanevalplus/
│   ├── bigcodebench/
│   └── classeval/
├── xiaorong/                     # 消融实验
├── parameter_Impact/             # 参数影响实验
├── cost_analysis/                # 成本分析
├── error_analysis/               # 错误分析
└── experiments2/                 # 第二轮补充实验
    ├── humaneval/
    ├── humanevalplus/
    ├── bigcodebench/
    ├── deepseek/
    └── qwen/
```

---

## 实验数据统计

| 类别 | 文件数 | 总大小 |
|---|---|---|
| 第 3 章 CMCS 实验 | 5 | ~50MB |
| 第 4 章 TraceCoder 实验 | ~50 | ~2.0GB |
| 第 5 章过程对齐实验 | 6 | ~580MB |
| 消融实验 | 5 | ~155MB |
| 参数影响实验 | 8 | ~128MB |
| 成本分析 | 10 | ~58MB |
| 错误分析 | 3 | ~286MB |
| 第二轮补充实验 | 14 | ~730MB |
| **合计** | **~103** | **~3.5GB** |
