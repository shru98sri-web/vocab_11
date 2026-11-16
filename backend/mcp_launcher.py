from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)

    candidates = (
        project_root / ".venv" / "bin" / "python",
        project_root / ".venv" / "Scripts" / "python.exe",
    )
    for python in candidates:
        if python.is_file() and Path(sys.prefix).resolve() != python.parent.parent.resolve():
            os.execv(str(python), [str(python), "-m", "backend.vocabulary_mcp"])

    sys.path.insert(0, str(project_root))
    from backend.vocabulary_mcp import main as run_server

    run_server()


if __name__ == "__main__":
    main()
