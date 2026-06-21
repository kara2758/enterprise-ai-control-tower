"""
Manual test / smoke check for the AI executive summary (demo mode).

Loads data, computes KPIs and the risk register, generates a summary with
``force_demo=True`` (so no API key is required), verifies the output contract,
and prints the result. If OpenAI credentials happen to be configured, it notes
that live mode is available — but live mode is NOT required to pass.

Usage:
    python scripts/test_ai_summary.py
"""

import os
import sys

# Make the project root importable so 'src' can be found when run directly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ai_summary import (  # noqa: E402
    SUMMARY_KEYS,
    format_summary_for_display,
    generate_executive_summary,
)
from src.data_loader import DataLoadingError, load_all_data  # noqa: E402
from src.kpi_engine import calculate_all_kpis  # noqa: E402
from src.risk_engine import create_executive_risk_register  # noqa: E402

DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def main() -> int:
    print("=" * 70)
    print("Enterprise AI Control Tower — AI Executive Summary Test (demo mode)")
    print("=" * 70)

    try:
        all_data = load_all_data(data_dir=DATA_DIR)
    except DataLoadingError as exc:
        print(f"\n[FAILED] Data loading error: {exc}")
        return 1

    all_kpis = calculate_all_kpis(all_data)
    risk_register = create_executive_risk_register(all_data)

    summary = generate_executive_summary(all_kpis, risk_register, force_demo=True)

    # ---- Verification ----
    errors = []
    for key in SUMMARY_KEYS:
        if key not in summary:
            errors.append(f"Missing key: {key}")

    if summary.get("mode") != "demo":
        errors.append(f"Expected mode 'demo', got '{summary.get('mode')}'")
    if not summary.get("key_risks"):
        errors.append("key_risks is empty")
    if not summary.get("recommended_actions"):
        errors.append("recommended_actions is empty")

    # ---- Output ----
    print("\n--- Generated Summary (markdown) ---\n")
    print(format_summary_for_display(summary))

    # Note availability of live mode without requiring it.
    if os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_MODEL"):
        print(
            "\n[NOTE] OPENAI_API_KEY and OPENAI_MODEL are set — live mode is "
            "available in the dashboard (not exercised by this test)."
        )
    else:
        print(
            "\n[NOTE] No OpenAI credentials detected — demo mode is the default. "
            "This is expected and fine for the portfolio project."
        )

    print("\n" + "=" * 70)
    if errors:
        print("[FAILED] AI summary verification failed:")
        for err in errors:
            print(f"  - {err}")
        print("=" * 70)
        return 1

    print("[SUCCESS] AI executive summary (demo mode) ran correctly.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
