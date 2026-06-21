"""
Run all smoke-test scripts in sequence and print a clean summary.

Each test is executed as a subprocess with the same Python interpreter. The run
stops at the first failure (fail-fast) and reports which test failed. All tests
run offline in demo mode and do NOT require an OpenAI API key.

Usage:
    python scripts/run_all_tests.py
"""

import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TESTS = [
    "test_data_loader.py",
    "test_kpi_engine.py",
    "test_risk_engine.py",
    "test_dashboard_imports.py",
    "test_ai_summary.py",
    "test_assistant.py",
    "test_weekly_report.py",
]


def main() -> int:
    print("=" * 70)
    print("Enterprise AI Control Tower — Running All Tests")
    print("=" * 70)

    passed = []
    for test in TESTS:
        test_path = os.path.join(SCRIPT_DIR, test)
        print(f"\n>>> Running {test} ...")
        result = subprocess.run(
            [sys.executable, test_path],
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            print("\n" + "=" * 70)
            print(f"[FAILED] {test} returned exit code {result.returncode}.")
            print(f"Passed before failure: {passed}")
            print("=" * 70)
            return 1
        passed.append(test)

    print("\n" + "=" * 70)
    print(f"[SUCCESS] All {len(passed)} test scripts passed:")
    for test in passed:
        print(f"  - {test}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
