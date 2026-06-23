"""
Deploy the dashboard to a Hugging Face Space (dev/tooling script).

Creates (or reuses) a Streamlit Space and uploads the files needed to run the
app: app.py, requirements.txt, src/, data/, plus a Space README with the
required YAML config header. Reads the cached HF token (from `huggingface-cli`/
`login()`); the token is never printed.

Requires `huggingface_hub` (already a transitive dependency of the dev tooling).
NOT part of the app runtime.

Usage:
    python scripts/deploy_hf_space.py
"""

import os

from huggingface_hub import HfApi

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ID = "kara2758/enterprise-ai-control-tower"

SPACE_README = """---
title: Enterprise AI Control Tower
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 🛡️ Enterprise AI Control Tower

AI-powered business process intelligence, risk monitoring, and executive
decision support — built on 100% synthetic data. Demo mode runs with no API key.

Full source, documentation, and the LinkedIn case study:
https://github.com/kara2758/enterprise-ai-control-tower

> Synthetic data only. A professional prototype, not a production system.
"""


def main() -> None:
    api = HfApi()
    print("Authenticated as:", api.whoami()["name"])

    api.create_repo(
        repo_id=REPO_ID, repo_type="space", space_sdk="docker", exist_ok=True
    )
    print("Space ready:", REPO_ID)

    # Space README with the required config header.
    readme_path = os.path.join(PROJECT_ROOT, "_space_readme_tmp.md")
    with open(readme_path, "w", encoding="utf-8") as handle:
        handle.write(SPACE_README)

    api.upload_file(
        path_or_fileobj=readme_path, path_in_repo="README.md",
        repo_id=REPO_ID, repo_type="space",
    )
    for fname in ("app.py", "requirements.txt", "Dockerfile"):
        api.upload_file(
            path_or_fileobj=os.path.join(PROJECT_ROOT, fname),
            path_in_repo=fname, repo_id=REPO_ID, repo_type="space",
        )
    for folder in ("src", "data"):
        api.upload_folder(
            folder_path=os.path.join(PROJECT_ROOT, folder),
            path_in_repo=folder, repo_id=REPO_ID, repo_type="space",
            ignore_patterns=["__pycache__/*", "*.pyc"],
        )

    os.remove(readme_path)
    print("DONE -> https://huggingface.co/spaces/" + REPO_ID)


if __name__ == "__main__":
    main()
