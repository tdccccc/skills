import subprocess
import sys
from pathlib import Path


def export_report(target: Path) -> subprocess.CompletedProcess[str]:
    cli = Path(__file__).with_name("worker_cli.py")
    return subprocess.run(
        [sys.executable, str(cli), "export", "--format", "json", "--out", str(target)],
        text=True,
        capture_output=True,
        check=False,
    )
