# 工具脚本说明

本目录保存归档辅助脚本，用于生成目录树和检查缺失项。脚本均使用 Python 3 编写，应从项目根目录直接运行。

## `generate_tree.py`

用途：生成当前项目目录树，并写入根目录 `tree.txt`。

运行方式：

```bash
python3 tools/generate_tree.py
```

忽略内容：

- `.git`
- `__pycache__`
- `.DS_Store`

建议在新增、删除或移动材料后运行该脚本，确保 `tree.txt` 反映实际目录状态。

## `check_missing_items.py`

用途：检查关键模板文件是否存在，并递归检查关键材料目录是否为空。检查结果写入 `00_admin/generated_missing_report.txt`。

运行方式：

```bash
python3 tools/check_missing_items.py
```

检查说明：

1. 模板文件缺失会列为“缺失”。
2. 只包含 `.gitkeep` 的目录会被视为仍需补充。
3. 报告用于阶段检查和学生补交材料跟踪。
4. 每次补充材料后建议重新运行，并同步更新 `00_admin/archive_status_table.md`。
