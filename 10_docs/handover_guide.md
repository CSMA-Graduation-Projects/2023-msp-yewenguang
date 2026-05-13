# 后续交接指南

本指南面向后续学生、导师或项目接收人，说明如何快速理解、检查、复现和扩展本项目。

## 一、如何快速理解项目

1. 先阅读根目录 `README.md`，了解学生信息、论文题目、研究内容和目录结构。
2. 阅读 `10_docs/project_overview.md`，理解四类方法和系统实现之间的关系。
3. 查看 `00_admin/archive_status_table.md` 和 `00_admin/missing_items_todo.md`，确认当前材料完整性。
4. 查看 `tree.txt`，快速掌握实际文件分布。

## 二、如何定位方法代码

- 第 3 章跨模型协同代码生成：进入 `03_methods/chapter3_cross_model_codegen/`。
- 第 4 章轨迹驱动修复：进入 `03_methods/chapter4_trace_driven_repair/`。
- 第 5 章过程对齐测试驱动修复：进入 `03_methods/chapter5_process_aligned_repair/`。
- 第 6 章仓库级代码生成：进入 `03_methods/chapter6_repo_level_codegen/`。
- 共享提示词、公共工具和评测脚本：进入 `03_methods/shared_resources/`。

每个章节目录应优先查看 README、`configs/`、`scripts/` 和 `results/`，再进入 `code/` 阅读实现。

## 三、如何复现实验

1. 阅读 `10_docs/environment_setup.md`，配置 Python、系统依赖和模型接口。
2. 阅读 `05_datasets/dataset_description.md`，准备数据集和样例。
3. 阅读 `10_docs/reproduction_guide.md`，按章节运行实验。
4. 在 `06_experiments/` 中查找对应数据集实验目录。
5. 在 `07_results/` 中核对原始输出、汇总表和最终图表。

复现实验前应确认模型接口、随机种子、数据版本和依赖环境是否与论文实验一致。

## 四、如何扩展系统

系统材料位于 `04_system/`。扩展前建议先完成以下检查：

1. 能否启动后端服务。
2. 能否启动前端页面。
3. 数据库或本地存储是否初始化。
4. 模型接口是否使用示例配置或本地安全配置。
5. 是否有一条最小演示任务可以完整运行。

扩展方向可包括：新增智能体角色、替换模型接口、增加仓库级任务支持、改进轨迹展示、增加补丁比较视图或补充自动评测面板。

## 五、如何检查归档质量

1. 运行 `python3 tools/generate_tree.py` 更新目录树。
2. 运行 `python3 tools/check_missing_items.py` 生成缺失项报告。
3. 检查 `00_admin/generated_missing_report.txt`。
4. 对照 `00_admin/archive_checklist.md` 逐项核对。
5. 更新状态表和版本日志。

## 六、交接记录建议

交接时建议新建或更新一份记录，包含：

- 交接日期。
- 交接人和接收人。
- 当前完成内容。
- 仍需补充的问题。
- 无法复现或无法公开的材料。
- 外部存储位置和权限。
- 下一步维护建议。
