"""Create public web copies of selected photos and the downloadable CV; originals stay untouched.

Experience photos are listed in src/content/experience.json (photos[].source) and come from photo/ only.
Presentations are not cut into gallery images: they are published whole as PDFs by scripts/export_talks.py.
Capture dates (photos[].date) are checked against the stage years by the content schema at build time.

The one agreed exception: the thin section in the rotating microscope circle next to the portrait is read
straight from the Herlany 2019 presentation (slide 8, altered gabbronorite, crossed polars). No copy of it is
kept in the project, only the public web versions.
"""

import json
from io import BytesIO
from pathlib import Path
from shutil import copy2
from zipfile import ZipFile

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "public" / "images"
EXPERIENCE_IMAGES = IMAGES / "experience"
SIZES_FILE = ROOT / "src" / "data" / "photo-sizes.json"
PORTRAIT = ROOT / "photo" / "Personal" / "Летний сад-62.jpg"
SCOPE_SOURCE = (ROOT / "materials" / "Pakhalko Herlany 2019.pptx", "ppt/media/image11.jpeg")
CV_SOURCE = ROOT / "CV" / "CV Geologist Pakhalko RUS 2026.docx"
CV_SOURCE_EN = ROOT / "CV" / "CV Geologist Pakhalko ENG 2026.docx"


def open_rgb(path):
    with Image.open(path) as original:
        return ImageOps.exif_transpose(original).convert("RGB")


def open_from_pptx(pptx, member):
    with ZipFile(pptx) as deck, Image.open(BytesIO(deck.read(member))) as original:
        return original.convert("RGB")


def fit(image, box):
    if image.width <= box and image.height <= box:
        return image.copy()
    return ImageOps.contain(image, (box, box), Image.Resampling.LANCZOS)


def save_webp(image, output, quality=78):
    # An empty exif block keeps camera data and GPS coordinates out of public files.
    image.save(output, "WEBP", quality=quality, method=6, exif=b"")
    return image.size


def average_color(image):
    # Placeholder colour for the slide while the photo is still loading.
    r, g, b = image.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
    return f"#{r:02x}{g:02x}{b:02x}"


def main():
    EXPERIENCE_IMAGES.mkdir(parents=True, exist_ok=True)
    for stale in EXPERIENCE_IMAGES.glob("*.webp"):
        stale.unlink()

    entries = json.loads((ROOT / "src" / "content" / "experience.json").read_text(encoding="utf-8"))
    sizes = {}
    for entry in entries:
        for photo in entry.get("photos", []):
            slug = photo["slug"]
            if slug in sizes:
                raise SystemExit(f"Duplicate photo slug: {slug}")
            if not photo["source"].startswith("photo/"):
                raise SystemExit(f"{slug}: gallery photos come from photo/ only, got {photo['source']}")
            image = open_rgb(ROOT / photo["source"])
            save_webp(fit(image, 160), EXPERIENCE_IMAGES / f"{slug}-160.webp", quality=70)
            small = save_webp(fit(image, 640), EXPERIENCE_IMAGES / f"{slug}-640.webp")
            large = save_webp(fit(image, 1280), EXPERIENCE_IMAGES / f"{slug}-1280.webp", quality=80)
            size = {"width": large[0], "height": large[1], "smallWidth": small[0], "color": average_color(image)}
            # The full-screen viewer fills large displays: keep a bigger copy when the original has the pixels.
            if max(image.size) > 1536:
                full = save_webp(fit(image, 1920), EXPERIENCE_IMAGES / f"{slug}-1920.webp", quality=78)
                size.update(fullWidth=full[0], fullHeight=full[1])
            sizes[slug] = size
            print(f"{slug}: {large[0]}x{large[1]}")

    SIZES_FILE.parent.mkdir(parents=True, exist_ok=True)
    SIZES_FILE.write_text(json.dumps(sizes, indent=2) + "\n", encoding="utf-8")

    portrait = open_rgb(PORTRAIT)
    for width in (480, 960):
        height = round(portrait.height * width / portrait.width)
        resized = portrait.resize((width, height), Image.Resampling.LANCZOS)
        save_webp(resized, IMAGES / f"portrait-{width}.webp", quality=76)

    scope = open_from_pptx(*SCOPE_SOURCE)
    for box in (480, 960):
        size = save_webp(fit(scope, box), IMAGES / f"scope-gabbronorite-{box}.webp", quality=82)
        print(f"scope-gabbronorite-{box}: {size[0]}x{size[1]}")

    cv_dir = ROOT / "public" / "cv"
    cv_dir.mkdir(parents=True, exist_ok=True)
    copy2(CV_SOURCE, cv_dir / "Alexey-Pakhalko-CV-RU-2026.docx")
    copy2(CV_SOURCE_EN, cv_dir / "Alexey-Pakhalko-CV-EN-2026.docx")
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        try:
            for src, dst_name in [(CV_SOURCE, "Alexey-Pakhalko-CV-RU-2026.pdf"), (CV_SOURCE_EN, "Alexey-Pakhalko-CV-EN-2026.pdf")]:
                doc = word.Documents.Open(str(src.resolve()))
                doc.SaveAs2(str((cv_dir / dst_name).resolve()), FileFormat=17)
                doc.Close()
        finally:
            word.Quit()
    except Exception as e:
        print(f"Warning: could not export PDF via Word COM: {e}")
    print(f"{len(sizes)} experience photos ready; review CV personal data before public deployment")


if __name__ == "__main__":
    main()
