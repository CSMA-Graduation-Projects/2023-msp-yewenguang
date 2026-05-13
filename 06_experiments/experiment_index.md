# 实验索引

本文件用于统一登记论文涉及的所有实验。每条实验记录应能对应到数据、配置、脚本、原始输出、结果表和论文中的图表或结论。

当前预填充实验目录包括 HumanEval、MBPP、HumanEvalPlus、BigCodeBench、ClassEval、RepoExec、EvoCodeBench、ablation 和 cost_analysis。其中第 6 章仓库级实验数据包括 RepoExec 和 EvoCodeBench。

| 实验名称 | 对应章节 | 数据集 | 评价指标 | 基线方法 | 结果文件位置 | 是否完成归档 |
|---|---|---|---|---|---|---|
| HumanEval 跨模型协同代码生成实验 | 第 3 章 | HumanEval | Pass@1、Pass@k、编译通过率、成本 | 单模型生成、重采样、简单投票 | `06_experiments/HumanEval/`、`07_results/summary_tables/` | 否 |
| MBPP 跨模型协同代码生成实验 | 第 3 章 | MBPP | Pass@1、Pass@k、测试通过率、成本 | 单模型生成、重采样、简单投票 | `06_experiments/MBPP/`、`07_results/summary_tables/` | 否 |
| HumanEvalPlus 增强测试评测 | 第 3、5 章 | HumanEvalPlus | 增强测试通过率、失败类型、修复轮次 | 单轮生成、无过程对齐方法 | `06_experiments/HumanEvalPlus/` | 否 |
| BigCodeBench 复杂任务代码生成实验 | 第 3、5 章 | BigCodeBench | 任务通过率、代码质量、运行成本 | 单模型、无仲裁方法 | `06_experiments/BigCodeBench/` | 否 |
| ClassEval 类级代码生成与修复实验 | 第 4、5 章 | ClassEval | 类级测试通过率、修复成功率、平均轮次 | 无轨迹修复、无测试生成方法 | `06_experiments/ClassEval/` | 否 |
| RepoExec 仓库级代码生成实验 | 第 6 章 | RepoExec | 仓库任务通过率、补丁正确率、上下文长度、平均轮次 | 无上下文记忆、简单检索、单轮补丁 | `06_experiments/RepoExec/` | 否 |
| EvoCodeBench 仓库级代码生成实验 | 第 6 章 | EvoCodeBench | 仓库任务通过率、补丁正确率、上下文命中率、平均轮次 | 无上下文记忆、简单检索、单轮补丁 | `06_experiments/EvoCodeBench/` | 否 |
| 运行轨迹驱动修复消融实验 | 第 4 章 | HumanEval、ClassEval 或自建轨迹数据 | 修复成功率、回滚次数、失败分类 | 去除插桩、去除分析、去除历史经验、去除回滚 | `06_experiments/ablation/` | 否 |
| 过程对齐消融实验 | 第 5 章 | HumanEvalPlus、BigCodeBench | 测试通过率、过拟合率、最优解命中率 | 去除测试生成、去除仲裁、去除最优选择 | `06_experiments/ablation/` | 否 |
| 结构化记忆消融实验 | 第 6 章 | RepoExec、EvoCodeBench | 任务通过率、平均轮次、上下文命中率 | 无记忆、固定上下文、仅最近轮次记忆 | `06_experiments/ablation/` | 否 |
| 成本分析 | 第 3 至第 7 章 | 全部主要实验 | token 数、调用次数、运行时间、费用估计、机器资源 | 不同方法和基线对比 | `06_experiments/cost_analysis/` | 否 |

## 实验归档最小要求

每个实验目录应至少包含：

1. 实验配置文件。
2. 运行命令或脚本。
3. 原始日志和模型输出。
4. 结果统计脚本。
5. 结果汇总表。
6. 与论文图表对应的说明。
7. 失败样例或异常记录。

## 更新要求

学生补充材料后，应将“是否完成归档”更新为“待确认”或“是”，并在 `00_admin/archive_status_table.md` 中同步更新对应模块状态。
