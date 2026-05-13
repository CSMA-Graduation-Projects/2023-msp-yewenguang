#!/usr/bin/env python3
"""生成当前归档项目目录树到 tree.txt。"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "tree.txt"

IGNORE_NAMES = {
    ".git",
    "__pycache__",
    ".DS_Store",
}


def should_ignore(path: Path) -> bool:
    return path.name in IGNORE_NAMES


def sorted_children(path: Path) -> list[Path]:
    children = [child for child in path.iterdir() if not should_ignore(child)]
    return sorted(children, key=lambda item: (not item.is_dir(), item.name.lower()))


def build_tree(path: Path, prefix: str = "") -> list[str]:
    lines: list[str] = []
    children = sorted_children(path)
    for index, child in enumerate(children):
        connector = "└── " if index == len(children) - 1 else "├── "
        lines.append(f"{prefix}{connector}{child.name}")
        if child.is_dir():
            extension = "    " if index == len(children) - 1 else "│   "
            lines.extend(build_tree(child, prefix + extension))
    return lines


def main() -> None:
    lines = [f"{PROJECT_ROOT.name}/"]
    lines.extend(build_tree(PROJECT_ROOT))
    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已生成目录树：{OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
