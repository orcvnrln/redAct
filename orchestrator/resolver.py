"""
Tool Resolver — üç mənbədən axtarır:
1) repo/tools/bin   (özünü idarə edən quraşdırma)
2) ~/.vibeshield/tools (Windows installer varisi)
3) sistem PATH
"""

import shutil
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIRS = [
    REPO_ROOT / "tools" / "bin",
    Path.home() / ".vibeshield" / "tools",
]


def resolve(tool_name: str) -> Optional[str]:
    """Tool-un real yolunu qaytarır; tapılmadıqda None (SKIPPED səbəbi)."""
    for d in TOOLS_DIRS:
        cand = d / tool_name
        if cand.is_file() and cand.stat().st_mode & 0o111:
            return str(cand)
    found = shutil.which(tool_name)
    return found


def resolved_all(names) -> dict:
    return {n: resolve(n) for n in names}
