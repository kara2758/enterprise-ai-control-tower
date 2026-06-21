"""
Manual test / smoke check for the weekly management report generator.

Generates the weekly report (demo mode), confirms the file exists, and verifies
it contains the required sections. No API key is required.

Usage:
    python scripts/test_weekly_report.py
"""

import os
import sys

# Make the project root importable so 'scripts'/'src' resolve when run directly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.generate_weekly_report import (  # noqa: E402
    REPORT_PATH,
    generate_weekly_report,
)

REQUIRED_SECTIONS = [
    "Weekly Executive Risk Report",
    "Executive KPI Summary",
    "Risk Summary",
    "AI Executive Summary",
    "Top 10 Risk Findings",
    "synthetic data",  # disclaimer keyword (case-insensitive check below)
]


def main() -> int:
    print("=" * 70)
    print("Enterprise AI Control Tower — Weekly Report Generation Test")
    print("=" * 70)

    try:
        path = generate_weekly_report()
    except Exception as exc:  # noqa: BLE001
        print(f"\n[FAILED] Report generation error: {exc}")
        return 1

    print(f"\nReport generated at: {path}")

    if not os.path.exists(REPORT_PATH):
        print(f"\n[FAILED] Expected report not found at: {REPORT_PATH}")
        return 1

    with open(REPORT_PATH, "r", encoding="utf-8") as handle:
        content = handle.read()
    content_lower = content.lower()

    missing = [s for s in REQUIRED_SECTIONS if s.lower() not in content_lower]

    print("\nSection checks:")
    for section in REQUIRED_SECTIONS:
        status = "OK" if section.lower() in content_lower else "MISSING"
        print(f"  [{status}] {section}")

    print("\n" + "=" * 70)
    if missing:
        print(f"[FAILED] Missing required section(s): {missing}")
        print("=" * 70)
        return 1

    print("[SUCCESS] Weekly report generated and contains all required sections.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
