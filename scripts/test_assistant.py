"""
Manual test / smoke check for the AI Manager Assistant (demo mode).

Loads data, computes KPIs and the risk register, asks several demo-mode
questions, verifies the response contract, and prints the answers. No API key is
required.

Usage:
    python scripts/test_assistant.py
"""

import os
import sys

# Make the project root importable so 'src' can be found when run directly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.assistant import ANSWER_KEYS, answer_manager_question  # noqa: E402
from src.data_loader import DataLoadingError, load_all_data  # noqa: E402
from src.kpi_engine import calculate_all_kpis  # noqa: E402
from src.risk_engine import create_executive_risk_register  # noqa: E402

DATA_DIR = os.path.join(PROJECT_ROOT, "data")

QUESTIONS = [
    "What are the top 5 risks right now?",
    "Which department needs management attention first?",
    "What is the current financial exposure?",
    "Summarize customer SLA pressure.",
    "Summarize approval bottlenecks.",
    "Prepare a 5-bullet executive briefing.",
]


def main() -> int:
    print("=" * 70)
    print("Enterprise AI Control Tower — AI Manager Assistant Test (demo mode)")
    print("=" * 70)

    try:
        all_data = load_all_data(data_dir=DATA_DIR)
    except DataLoadingError as exc:
        print(f"\n[FAILED] Data loading error: {exc}")
        return 1

    all_kpis = calculate_all_kpis(all_data)
    risk_register = create_executive_risk_register(all_data)

    errors = []
    for question in QUESTIONS:
        result = answer_manager_question(
            question, all_kpis, risk_register, force_demo=True
        )

        for key in ANSWER_KEYS:
            if key not in result:
                errors.append(f"[{question!r}] missing key: {key}")
        if result.get("mode") != "demo":
            errors.append(
                f"[{question!r}] expected mode 'demo', got '{result.get('mode')}'"
            )
        if not (result.get("answer") or "").strip():
            errors.append(f"[{question!r}] answer is empty")

        print(f"\n--- Q: {question} ---")
        print(f"[mode: {result.get('mode')}]")
        print(result.get("answer", ""))

    if os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_MODEL"):
        print(
            "\n[NOTE] OpenAI credentials detected — live mode is available in the "
            "dashboard (not exercised by this test)."
        )
    else:
        print(
            "\n[NOTE] No OpenAI credentials detected — demo mode is the default. "
            "This is expected and fine for the portfolio project."
        )

    print("\n" + "=" * 70)
    if errors:
        print("[FAILED] Assistant verification failed:")
        for err in errors:
            print(f"  - {err}")
        print("=" * 70)
        return 1

    print("[SUCCESS] AI Manager Assistant (demo mode) ran correctly.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
