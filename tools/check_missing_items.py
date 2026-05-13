#!/usr/bin/env python3
"""检查归档项目中的关键缺失项，并生成报告。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "00_admin" / "generated_missing_report.txt"

IGNORED_NAMES = {
    ".DS_Store",
    ".gitkeep",
    "__pycache__",
}

REQUIRED_FILES = [
    "README.md",
    "project.yaml",
    "tree.txt",
    ".gitignore",
    "00_admin/archive_checklist.md",
    "00_admin/submission_requirements.md",
    "00_admin/missing_items_todo.md",
    "00_admin/archive_status_table.md",
    "00_admin/version_log.md",
    "00_admin/student_submission_notice.md",
    "03_methods/chapter3_cross_model_codegen/README.md",
    "03_methods/chapter4_trace_driven_repair/README.md",
    "03_methods/chapter5_process_aligned_repair/README.md",
    "03_methods/chapter6_repo_level_codegen/README.md",
    "04_system/README.md",
    "05_datasets/dataset_description.md",
    "06_experiments/experiment_index.md",
    "07_results/result_notes.md",
    "10_docs/project_overview.md",
    "10_docs/reproduction_guide.md",
    "10_docs/environment_setup.md",
    "10_docs/directory_guide.md",
    "10_docs/artifact_description.md",
    "10_docs/archive_rules.md",
    "10_docs/faq.md",
    "10_docs/handover_guide.md",
    "11_weekly_and_process_records/timeline.md",
    "tools/check_missing_items.py",
    "tools/generate_tree.py",
    "tools/README.md",
]

KEY_DIRECTORIES = [
    "01_thesis/thesis_pdf",
    "01_thesis/thesis_source",
    "01_thesis/abstract",
    "01_thesis/figures",
    "01_thesis/tables",
    "01_thesis/review_comments",
    "01_thesis/defense_version",
    "01_thesis/final_version",
    "02_papers/related_papers",
    "02_papers/submitted_versions",
    "02_papers/published_versions",
    "02_papers/rebuttal_or_response",
    "02_papers/manuscript_notes",
    "03_methods/chapter3_cross_model_codegen/code",
    "03_methods/chapter3_cross_model_codegen/data",
    "03_methods/chapter3_cross_model_codegen/configs",
    "03_methods/chapter3_cross_model_codegen/scripts",
    "03_methods/chapter3_cross_model_codegen/results",
    "03_methods/chapter3_cross_model_codegen/figures",
    "03_methods/chapter3_cross_model_codegen/docs",
    "03_methods/chapter4_trace_driven_repair/code",
    "03_methods/chapter4_trace_driven_repair/data",
    "03_methods/chapter4_trace_driven_repair/configs",
    "03_methods/chapter4_trace_driven_repair/scripts",
    "03_methods/chapter4_trace_driven_repair/results",
    "03_methods/chapter4_trace_driven_repair/figures",
    "03_methods/chapter4_trace_driven_repair/docs",
    "03_methods/chapter5_process_aligned_repair/code",
    "03_methods/chapter5_process_aligned_repair/data",
    "03_methods/chapter5_process_aligned_repair/configs",
    "03_methods/chapter5_process_aligned_repair/scripts",
    "03_methods/chapter5_process_aligned_repair/results",
    "03_methods/chapter5_process_aligned_repair/figures",
    "03_methods/chapter5_process_aligned_repair/docs",
    "03_methods/chapter6_repo_level_codegen/code",
    "03_methods/chapter6_repo_level_codegen/data",
    "03_methods/chapter6_repo_level_codegen/configs",
    "03_methods/chapter6_repo_level_codegen/scripts",
    "03_methods/chapter6_repo_level_codegen/results",
    "03_methods/chapter6_repo_level_codegen/figures",
    "03_methods/chapter6_repo_level_codegen/docs",
    "03_methods/shared_resources/prompts",
    "03_methods/shared_resources/common_utils",
    "03_methods/shared_resources/datasets",
    "03_methods/shared_resources/evaluation",
    "03_methods/shared_resources/docs",
    "04_system/frontend",
    "04_system/backend",
    "04_system/deployment",
    "04_system/database",
    "04_system/api_docs",
    "04_system/screenshots",
    "04_system/demo_video",
    "04_system/user_manual",
    "04_system/test_records",
    "05_datasets/raw",
    "05_datasets/processed",
    "05_datasets/samples",
    "05_datasets/licenses",
    "05_datasets/metadata",
    "06_experiments/HumanEval",
    "06_experiments/MBPP",
    "06_experiments/HumanEvalPlus",
    "06_experiments/BigCodeBench",
    "06_experiments/ClassEval",
    "06_experiments/RepoExec",
    "06_experiments/EvoCodeBench",
    "06_experiments/ablation",
    "06_experiments/cost_analysis",
    "07_results/summary_tables",
    "07_results/raw_outputs",
    "07_results/final_figures",
    "07_results/case_studies",
    "08_ppt_and_reports/defense_ppt",
    "08_ppt_and_reports/group_meeting_ppt",
    "08_ppt_and_reports/opening_report",
    "08_ppt_and_reports/midterm_report",
    "08_ppt_and_reports/final_report",
    "08_ppt_and_reports/project_application",
    "08_ppt_and_reports/other_reports",
    "09_review_and_graduation_materials/thesis_review_comments",
    "09_review_and_graduation_materials/revision_explanations",
    "09_review_and_graduation_materials/defense_materials",
    "09_review_and_graduation_materials/graduation_forms",
    "09_review_and_graduation_materials/signatures_and_scans",
    "09_review_and_graduation_materials/archive_scans",
    "09_review_and_graduation_materials/official_documents",
    "11_weekly_and_process_records/weekly_reports",
    "11_weekly_and_process_records/meeting_notes",
    "11_weekly_and_process_records/task_records",
    "11_weekly_and_process_records/progress_snapshots",
]


def has_real_content(directory: Path) -> bool:
    """判断目录中是否存在非占位文件。"""
    if not directory.exists() or not directory.is_dir():
        return False
    for item in directory.rglob("*"):
        if item.name in IGNORED_NAMES:
            continue
        if any(part in IGNORED_NAMES for part in item.parts):
            continue
        if item.is_file():
            return True
    return False


def check_required_files() -> list[str]:
    missing = []
    for relative_path in REQUIRED_FILES:
        path = PROJECT_ROOT / relative_path
        if not path.is_file():
            missing.append(relative_path)
    return missing


def check_empty_directories() -> list[str]:
    empty_or_missing = []
    for relative_path in KEY_DIRECTORIES:
        path = PROJECT_ROOT / relative_path
        if not has_real_content(path):
            empty_or_missing.append(relative_path)
    return empty_or_missing


def build_report() -> str:
    missing_files = check_required_files()
    empty_dirs = check_empty_directories()

    lines = [
        "归档缺失项检查报告",
        "=" * 24,
        f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"项目根目录：{PROJECT_ROOT.name}",
        "",
        "一、关键模板文件检查",
        "-" * 24,
    ]

    if missing_files:
        lines.append(f"缺失关键模板文件数量：{len(missing_files)}")
        for item in missing_files:
            lines.append(f"- 缺失：{item}")
    else:
        lines.append("关键模板文件均已存在。")

    lines.extend([
        "",
        "二、关键材料目录内容检查",
        "-" * 24,
    ])

    if empty_dirs:
        lines.append(f"仍为空或仅包含占位文件的关键目录数量：{len(empty_dirs)}")
        for item in empty_dirs:
            lines.append(f"- 待补充：{item}")
    else:
        lines.append("关键材料目录均已包含实际文件。")

    lines.extend([
        "",
        "三、处理建议",
        "-" * 24,
        "1. 优先补充论文最终版、源文件、图表源文件和答辩材料。",
        "2. 优先补充第 3 至第 6 章方法代码、配置、脚本和实验结果。",
        "3. 优先补充系统前后端、部署说明、截图、演示视频和测试记录。",
        "4. 对无法提交的大文件或受限材料，在对应目录放置说明文件。",
        "5. 补充材料后重新运行本脚本，并更新归档状态总表。",
        "",
        f"报告输出位置：{REPORT_PATH.relative_to(PROJECT_ROOT)}",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    report = build_report()
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
