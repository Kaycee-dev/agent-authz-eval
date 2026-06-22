"""Build docs/writeup/WRITEUP.pdf from the canonical Markdown writeup.

The build uses pandoc for Markdown rendering and Chrome/Edge headless for the
final print-to-PDF step. This avoids adding a LaTeX dependency while preserving
the D-S4-1 pandoc requirement.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WRITEUP_DIR = ROOT / "docs" / "writeup"
INPUT_MD = WRITEUP_DIR / "WRITEUP.md"
OUTPUT_PDF = WRITEUP_DIR / "WRITEUP.pdf"
TMP_DIR = ROOT / "tmp" / "pdfs"


CSS = """
@page { margin: 0.75in; }
body {
  color: #111827;
  font-family: "Segoe UI", Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.48;
  max-width: 7.1in;
  margin: 0 auto;
}
h1, h2, h3 { color: #0f172a; line-height: 1.2; page-break-after: avoid; }
h1 { font-size: 22pt; margin: 0 0 0.35in; }
h2 { font-size: 15pt; border-bottom: 1px solid #cbd5e1; padding-bottom: 0.05in; margin-top: 0.28in; }
h3 { font-size: 12pt; margin-top: 0.22in; }
p { margin: 0 0 0.12in; }
img {
  display: block;
  max-width: 100%;
  max-height: 6.7in;
  margin: 0.18in auto 0.08in;
  page-break-inside: avoid;
}
code {
  background: #f1f5f9;
  border-radius: 3px;
  padding: 0.01in 0.04in;
}
pre {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 0.12in;
  white-space: pre-wrap;
}
"""


def find_pandoc() -> str:
    if path := shutil.which("pandoc"):
        return path
    try:
        import pypandoc  # type: ignore

        path = pypandoc.get_pandoc_path()
        candidate = Path(path)
        if candidate.exists():
            return str(candidate)
        if candidate.with_suffix(".exe").exists():
            return str(candidate.with_suffix(".exe"))
    except Exception:
        pass
    raise SystemExit(
        "pandoc is required. Install pandoc or install pypandoc with its bundled pandoc binary."
    )


def find_browser() -> str:
    for name in ("chrome", "chrome.exe", "msedge", "msedge.exe"):
        if path := shutil.which(name):
            return path
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise SystemExit("Chrome or Edge is required for the headless PDF print step.")


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    completed = subprocess.run(cmd, cwd=cwd, text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    pandoc = find_pandoc()
    browser = find_browser()
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=TMP_DIR) as tmp:
        tmpdir = Path(tmp)
        html = tmpdir / "WRITEUP.html"
        css = tmpdir / "writeup.css"
        css.write_text(CSS, encoding="utf-8")

        run(
            [
                pandoc,
                "WRITEUP.md",
                "--from=gfm",
                "--to=html5",
                "--standalone",
                "--embed-resources",
                f"--css={css}",
                "--metadata",
                "pagetitle=Do Tool-Using LLM Agents Respect Authorization Boundaries?",
                "--output",
                str(html),
            ],
            cwd=WRITEUP_DIR,
        )

        if OUTPUT_PDF.exists():
            OUTPUT_PDF.unlink()

        run(
            [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-pdf-header-footer",
                "--print-to-pdf-no-header",
                f"--print-to-pdf={OUTPUT_PDF}",
                html.as_uri(),
            ]
        )

    size = OUTPUT_PDF.stat().st_size if OUTPUT_PDF.exists() else 0
    if size < 100_000:
        raise SystemExit(f"PDF output is unexpectedly small: {OUTPUT_PDF} ({size} bytes)")
    print(f"Wrote {OUTPUT_PDF} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
