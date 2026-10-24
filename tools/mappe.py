#!/usr/bin/env python3
"""Druckfertige PDF-Mappe für den Schreiner aus docs/schreiner.md und docs/stueckliste.md.

Aufruf (nach tools/build.py):  python3 tools/mappe.py
Braucht das Python-Paket `markdown` und Node.js mit Playwright/Chromium.
"""

import re
import subprocess
import tempfile
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ZIEL = DOCS / "schreiner-mappe.pdf"

CSS = """
@page { size: A4; margin: 14mm 14mm 16mm 14mm; }
body { font: 10pt/1.45 "Helvetica Neue", Arial, sans-serif; color: #1d1d1b; }
h1 { font-size: 20pt; margin: 0 0 6pt; }
h2 { font-size: 14pt; margin: 16pt 0 6pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 9pt; }
th, td { border: 1px solid #ccc; padding: 3pt 5pt; vertical-align: top; text-align: left; }
th { background: #f3eee6; }
img { max-width: 100%; max-height: 235mm; display: block; margin: 6pt auto; }
blockquote { border-left: 3px solid #c0784a; margin: 6pt 0; padding: 2pt 10pt; color: #333; }
.umbruch { break-before: page; }
h2, h3 { break-after: avoid; }
table, img, blockquote { break-inside: avoid; }
a { color: inherit; text-decoration: none; }
"""

DRUCK_JS = """
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await p.pdf({ path: process.argv[3], format: 'A4', printBackground: true,
                displayHeaderFooter: true, headerTemplate: '<span></span>',
                footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888">'
                  + 'Wohnbank mit Trainingsfunktion – Unterlagen für den Schreiner – Seite <span class="pageNumber"></span>/<span class="totalPages"></span></div>',
                margin: { top: '14mm', bottom: '16mm', left: '14mm', right: '14mm' } });
  await b.close();
})();
"""


def html_aus(md_datei):
    text = (DOCS / md_datei).read_text()
    text = re.sub(r"^> Automatisch erzeugt.*$", "", text, flags=re.M)
    html = markdown.markdown(text, extensions=["tables"])
    # Bildpfade absolut machen, Links auf andere Markdown-Dateien als Text belassen
    html = re.sub(r'src="([^"]+)"', lambda m: f'src="file://{(DOCS / m.group(1)).resolve()}"', html)
    html = re.sub(r'<a href="[^"]+\.md">([^<]+)</a>', r"\1", html)
    # Zeichnungen und Ansichten jeweils auf neuer Seite
    html = re.sub(r"<h3>(Querschnitt|Gleitschienen|Metallteile|Tragwerk|Training)", r'<h3 class="umbruch">\1', html)
    html = html.replace("<h2>Konstruktionsvorgaben</h2>", '<h2 class="umbruch">Konstruktionsvorgaben</h2>')
    return html


def main():
    teile = [html_aus("schreiner.md"), '<div class="umbruch"></div>', html_aus("stueckliste.md")]
    seite = f'<!doctype html><html lang="de"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(teile)}</body></html>'
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "mappe.html"
        js = Path(tmp) / "druck.js"
        html.write_text(seite)
        js.write_text(DRUCK_JS)
        subprocess.run(["node", str(js), str(html), str(ZIEL)], check=True)
    print(f"{ZIEL.relative_to(ROOT)} geschrieben")


if __name__ == "__main__":
    main()
