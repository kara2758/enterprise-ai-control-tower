# GitHub Release Checklist

Run through this checklist before publishing the Enterprise AI Control Tower to
GitHub or sharing it on LinkedIn.

## Security & privacy

- [ ] **`.env` is NOT committed** (it is git-ignored; only `.env.example` is
      tracked).
- [ ] **No real credentials** anywhere (no API keys, passwords, or tokens in
      code, JSON, or docs).
- [ ] **No real customer / company / vendor / employee / personal data** — all
      data is synthetic.
- [ ] **Generated reports are safe** — `reports/weekly_management_report.md`
      contains only synthetic data.
- [ ] **n8n workflow contains placeholders only** — placeholder email addresses
      (`example.com`), no SMTP credentials, no real recipients.
- [ ] `.gitignore` covers `.env`, `__pycache__/`, `.venv/`, etc.

## Functionality

- [ ] **Synthetic data generates:** `python scripts/generate_synthetic_data.py`.
- [ ] **All tests pass:** `python scripts/run_all_tests.py`.
- [ ] **Dashboard runs:** `streamlit run app.py` and loads without errors.
- [ ] **Weekly report generates:**
      `python scripts/generate_weekly_report.py`.
- [ ] Demo mode works **without** an API key (AI summary + assistant).

## Documentation

- [ ] **README is accurate and complete** (install, run, tests, disclaimers).
- [ ] Portfolio disclaimer and "not production-ready" statement are present.
- [ ] Docs cross-links work (architecture, KPI, risk, dashboard, AI, automation).
- [ ] LinkedIn case study / posts reviewed for tone (no overclaiming).

## Presentation

- [ ] **Screenshots captured** (see `screenshots/README.md`) and referenced in
      the README where desired.
- [ ] Repository name, description, and topics/tags set on GitHub.
- [ ] (Optional) Demo video recorded using `docs/demo_video_script.md`.

## Final pass

- [ ] Re-read the README top-to-bottom as if you were a recruiter.
- [ ] Confirm the project runs from a clean clone + fresh virtual environment.
- [ ] Tag a release / write release notes if desired.
