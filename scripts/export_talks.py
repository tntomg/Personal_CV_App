"""Export the author's presentations from materials/ to PDF for reading on the site (public/talks/).

Presentations are published whole, as standalone files; images are never cut out of them for galleries.
Needs Microsoft PowerPoint (COM). Existing PDFs are skipped, so the script can be re-run safely;
pass --force to rebuild, or a key (e.g. 2022-stone-in-architecture) to export only that file.

    uv run --python-preference only-managed --with pywin32 python scripts/export_talks.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "talks"
SIZES_FILE = ROOT / "src" / "data" / "talk-sizes.json"

# Key = public file name (also referenced from src/content/credentials.json, field "file").
TALKS = {
    "2014-norilsk-sulfur-isotopes": "Sulfur isotopic features of sulfide ores in mafic.pptx",
    "2018-jeju-metallogenic-evolution": "2018-Korea,Jeju Pakhalko A.pptx",
    "2019-mongolia-metallogenic-map": "2019-Mongolia, Pakhalko A.pptx",
    "2019-herlany-vuruchuaivench": "Pakhalko Herlany 2019.pptx",
    "2022-stone-in-architecture": "Презентация Камень в архитектуре.pptx",
    "2025-mining-compass": "Gornyj-kompas-principy-primeneniya-v-geologii.pptx",
}

PP_SAVE_AS_PDF = 32


def write_sizes():
    # File sizes for the "PDF, 6,5 МБ" labels on the site (src/pages/ru/index.astro).
    sizes = {f"/talks/{p.name}": p.stat().st_size for p in sorted(OUT.glob("*.pdf"))}
    SIZES_FILE.parent.mkdir(parents=True, exist_ok=True)
    SIZES_FILE.write_text(json.dumps(sizes, indent=2) + "\n", encoding="utf-8")
    print(f"sizes {len(sizes)} -> {SIZES_FILE.relative_to(ROOT)}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    todo = [k for k in TALKS if (not args or k in args) and (force or not (OUT / f"{k}.pdf").exists())]
    if not todo:
        print("all PDFs exist (use --force to rebuild)")
        write_sizes()
        return
    import win32com.client  # only needed when something has to be exported

    app = win32com.client.DispatchEx("PowerPoint.Application")
    try:
        for key in todo:
            name = TALKS[key]
            target = OUT / f"{key}.pdf"
            source = ROOT / "materials" / name
            deck = app.Presentations.Open(str(source), True, False, False)  # ReadOnly, Untitled, WithWindow
            try:
                # ExportAsFixedFormat fails through pywin32 (PrintRange argument); SaveAs PDF is equivalent.
                deck.SaveAs(str(target), PP_SAVE_AS_PDF)
            finally:
                deck.Close()
            print(f"ok    {target.name} ({target.stat().st_size / 1e6:.1f} MB, {name})")
    finally:
        app.Quit()
    write_sizes()


if __name__ == "__main__":
    main()
