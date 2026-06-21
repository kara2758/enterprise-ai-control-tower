"""
Capture portfolio screenshots of the running dashboard (automation helper).

Drives a headless Chromium browser against the live Streamlit dashboard at
``http://localhost:8501``, interacts with the AI sections (clicks *Generate
Executive Summary*, fills + clicks *Ask Assistant*), and writes cropped PNGs for
each section into ``screenshots/``. It also renders
``reports/weekly_management_report.md`` to ``screenshots/weekly_report.png``.

This is a DEV/TOOLING script, not part of the app runtime. It requires extra
packages that are intentionally NOT in requirements.txt:

    pip install playwright markdown
    python -m playwright install chromium

Prerequisite: the dashboard must already be running:
    streamlit run app.py

Usage:
    python scripts/capture_screenshots.py
"""

from __future__ import annotations

import os
import sys

import markdown as md_lib
from PIL import Image
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "screenshots")
REPORT_MD = os.path.join(PROJECT_ROOT, "reports", "weekly_management_report.md")

URL = "http://localhost:8501"
VIEWPORT_WIDTH = 1440
SCALE = 2  # device_scale_factor -> crisp 2x images
PAD = 14   # CSS px padding around each cropped section

# Hide Streamlit chrome (toolbar / header / footer) for clean portfolio shots.
HIDE_CHROME_CSS = """
header, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], footer { display: none !important; }
[data-testid="stAppViewContainer"] { padding-top: 0 !important; }
"""


def abs_top_of_heading(page, needle: str) -> float | None:
    """Return the document-absolute top (CSS px) of the h3 containing needle."""
    return page.evaluate(
        """(needle) => {
            const els = Array.from(document.querySelectorAll('h1,h2,h3'));
            const el = els.find(e => e.textContent.includes(needle));
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return r.top + window.scrollY;
        }""",
        needle,
    )


def abs_top_of_expander(page) -> float | None:
    """Return the document-absolute top (CSS px) of the Dataset Preview expander."""
    return page.evaluate(
        """() => {
            const el = document.querySelector('[data-testid="stExpander"]');
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return r.top + window.scrollY;
        }"""
    )


def full_page_shot(page, tmp_path: str) -> int:
    """Grow the viewport to fit all content, screenshot full page, return height px.

    Streamlit scrolls inside an inner container, so Playwright's ``full_page`` only
    captures the viewport. We measure the real content height and resize the
    viewport to fit, so the whole dashboard is captured in one image.
    """
    content_h = page.evaluate(
        """() => {
            const cands = [document.body.scrollHeight,
                           document.documentElement.scrollHeight];
            const main = document.querySelector(
                'section.main, [data-testid=\"stMain\"], [data-testid=\"stAppViewContainer\"]');
            if (main) cands.push(main.scrollHeight);
            const vb = document.querySelector('[data-testid=\"stVerticalBlock\"]');
            if (vb) cands.push(Math.ceil(vb.getBoundingClientRect().height) + 200);
            return Math.max(...cands);
        }"""
    )
    page.set_viewport_size(
        {"width": VIEWPORT_WIDTH, "height": int(content_h) + 120}
    )
    page.wait_for_timeout(500)
    page.screenshot(path=tmp_path, full_page=True)
    return Image.open(tmp_path).height


def crop_section(full_path: str, out_name: str, top_css, bottom_css, img_h_px) -> None:
    """Crop a full-page screenshot between two CSS y-coordinates."""
    if top_css is None:
        print(f"  [skip] {out_name}: could not locate top anchor")
        return
    top_px = max(0, int((top_css - PAD) * SCALE))
    if bottom_css is None:
        bottom_px = img_h_px
    else:
        bottom_px = min(img_h_px, int((bottom_css + PAD) * SCALE))
    if bottom_px <= top_px:
        print(
            f"  [warn] {out_name}: bad range top_css={top_css} bottom_css="
            f"{bottom_css} -> top_px={top_px} bottom_px={bottom_px}; skipping"
        )
        return
    img = Image.open(full_path)
    crop = img.crop((0, top_px, img.width, bottom_px))
    out_path = os.path.join(SCREENSHOTS_DIR, out_name)
    crop.save(out_path)
    print(f"  [ok]   {out_name}  ({crop.width}x{crop.height})")


def capture_dashboard(page, tmp_full: str) -> None:
    """Capture all 7 dashboard section screenshots."""
    # --- Full-page snapshot #1: initial state (no interactions) ---
    img_h = full_page_shot(page, tmp_full)
    crop_section(tmp_full, "dashboard_overview.png", 0.0,
                 abs_top_of_heading(page, "AI Executive Summary"), img_h)
    crop_section(tmp_full, "executive_kpis.png",
                 abs_top_of_heading(page, "Executive Overview"),
                 abs_top_of_heading(page, "AI Executive Summary"), img_h)
    crop_section(tmp_full, "risk_charts.png",
                 abs_top_of_heading(page, "Risk & Operational Charts"),
                 abs_top_of_heading(page, "Top Risk Findings"), img_h)
    crop_section(tmp_full, "top_risks_table.png",
                 abs_top_of_heading(page, "Top Risk Findings"),
                 abs_top_of_heading(page, "KPI Details"), img_h)

    # --- AI Executive Summary (after clicking Generate) ---
    page.get_by_role("button", name="Generate Executive Summary").click()
    page.get_by_text("Recommended Actions").first.wait_for(timeout=30000)
    page.wait_for_timeout(500)
    img_h = full_page_shot(page, tmp_full)
    crop_section(tmp_full, "ai_summary.png",
                 abs_top_of_heading(page, "AI Executive Summary"),
                 abs_top_of_heading(page, "AI Manager Assistant"), img_h)

    # --- AI Manager Assistant (after asking a question) ---
    question = "What are the top 5 risks right now?"
    page.get_by_label("Ask a question").fill(question)
    page.get_by_role("button", name="Ask Assistant").click()
    page.get_by_text("Top operational risks").first.wait_for(timeout=30000)
    page.wait_for_timeout(500)
    img_h = full_page_shot(page, tmp_full)
    crop_section(tmp_full, "manager_assistant.png",
                 abs_top_of_heading(page, "AI Manager Assistant"),
                 abs_top_of_heading(page, "Risk Summary"), img_h)

    # --- Dataset Preview (after expanding) ---
    page.get_by_text("Dataset Preview").first.click()
    page.wait_for_timeout(800)
    img_h = full_page_shot(page, tmp_full)
    crop_section(tmp_full, "dataset_preview.png",
                 abs_top_of_expander(page), None, img_h)


def capture_weekly_report(page) -> None:
    """Render the weekly report Markdown to a PNG (no VS Code needed)."""
    if not os.path.exists(REPORT_MD):
        print("  [skip] weekly_report.png: report markdown not found")
        return
    with open(REPORT_MD, "r", encoding="utf-8") as handle:
        md_text = handle.read()
    body = md_lib.markdown(md_text, extensions=["tables"])
    html = f"""<!doctype html><html><head><meta charset="utf-8">
    <style>
      body {{ font-family: -apple-system, Segoe UI, Arial, sans-serif;
              max-width: 900px; margin: 24px auto; padding: 0 24px;
              color: #1a1a1a; line-height: 1.5; }}
      h1 {{ border-bottom: 2px solid #eee; padding-bottom: 8px; }}
      table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
      th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: left; }}
      th {{ background: #f4f4f4; }}
      blockquote {{ color: #555; border-left: 4px solid #ddd; margin: 0;
                    padding: 4px 12px; }}
      code {{ background: #f4f4f4; padding: 1px 4px; border-radius: 3px; }}
    </style></head><body>{body}</body></html>"""
    page.set_content(html)
    page.wait_for_timeout(300)
    out_path = os.path.join(SCREENSHOTS_DIR, "weekly_report.png")
    page.screenshot(path=out_path, full_page=True)
    print(f"  [ok]   weekly_report.png")


def main() -> int:
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    tmp_full = os.path.join(SCREENSHOTS_DIR, "_full_tmp.png")

    print("Capturing dashboard screenshots from", URL)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": VIEWPORT_WIDTH, "height": 1000},
            device_scale_factor=SCALE,
        )
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.get_by_text("Executive Overview").first.wait_for(timeout=60000)
        page.add_style_tag(content=HIDE_CHROME_CSS)
        page.wait_for_timeout(800)

        capture_dashboard(page, tmp_full)

        # Reuse the same page (set_content) for the report render.
        capture_weekly_report(page)

        browser.close()

    if os.path.exists(tmp_full):
        os.remove(tmp_full)

    print("\nDone. Files written to:", SCREENSHOTS_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
