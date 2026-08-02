from pathlib import Path

from service import export_report


def handle_export() -> tuple[int, str]:
    result = export_report(Path("report.json"))
    if result.returncode != 0:
        return 502, result.stderr.strip()
    return 200, result.stdout.strip()
