"""Turn the app presentations in materials/ into data and images for the site's presentation mini-apps.

The source decks are single HTML files (28-33 MB) with every screenshot embedded as base64 PNG and fixed
1600x900 slides. This script reads them straight from the ZIP kits, without unpacking into the project, and writes:

  src/data/presentations/<deck>.<lang>.json   slide text and structure, one file per original language
  src/data/presentations/images.json          sizes, variants and placeholder colours of every image
  public/presentations/<deck>/<id>-<w>.webp   web copies without metadata

Android status bar and taskbar are cut from device screenshots, as the Field deck already does for its
landscape captures: they carry the clock, notifications and personal app icons, not the product.
The Russian text of the Classifier deck is a translation kept in src/data/presentations/translations/.

Usage: uv run --python-preference only-managed --with pillow python scripts/build_presentations.py
"""

import base64
import hashlib
import io
import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "src" / "data" / "presentations"
PUBLIC_DIR = ROOT / "public" / "presentations"

DECKS = {
    "field": {
        "zip": "materials/Rocksurv_Field_Presentation_Kit_EN_RU_v13.zip",
        "html": {
            "ru": "rocksurv_field/Rocksurv_Field_Presentation_RU.html",
            "en": "rocksurv_field/Rocksurv_Field_Presentation_EN.html",
        },
    },
    "classifier": {
        "zip": "materials/rocksurv_classifier.zip",
        "html": {"en": "rocksurv_classifier/Rocksurv_Classifier_Presentation_EN.html"},
    },
}

# Android 24 dp status bar and the taskbar, measured on the captures (2.67 px per dp).
SCREEN_CROP = {
    (2560, 1600): (70, 1480),  # the Field deck's own crop for landscape captures
    (1600, 2560): (64, 2456),
}
WIDTHS = {
    "screen-landscape": (800, 1280, 1920),
    "screen-portrait": (600, 1000, 1600),
    "photo": (640, 1280, 1920),
}
ACRONYMS = {"gps": "GPS", "iugs": "IUGS", "qapf": "QAPF", "dem": "DEM", "gis": "GIS"}


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def sentence_case(label):
    """'01 / КАРТЫ ПРОЕКТА' -> 'Карты проекта'; the slide number is shown by the deck itself."""
    label = re.sub(r"^\d+\s*/\s*", "", clean(label)).lower()
    words = [ACRONYMS.get(w.strip(",.&"), w) if w.strip(",.&") in ACRONYMS else w for w in label.split(" ")]
    text = " ".join(words)
    return text[:1].upper() + text[1:]


class DeckParser(HTMLParser):
    """Collects slides as structured text plus the embedded images in order of appearance."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides = []
        self.slide = None
        self.text = None  # [tag, classes, buffer, attrs]
        self.point = None
        self.state = None
        self.lang_row = None
        self.platform = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "").split()
        if tag == "section" and "slide" in cls:
            kind = "cover" if "cover" in cls else "closing" if "closing" in cls else "languages" if "language-slide" in cls else "feature"
            self.slide = {"kind": kind, "chapter": "", "title": "", "brand": [], "lead": "", "note": "", "points": [],
                          "caption": "", "cta": "", "media": [], "languages": [], "platforms": []}
            self.slides.append(self.slide)
            return
        if self.slide is None:
            return
        if tag == "br" and self.text:
            self.text[2] += " "
            return
        if tag == "div" and "point" in cls:
            self.point = {"title": "", "text": ""}
            self.slide["points"].append(self.point)
        if tag == "div" and "carousel-item" in cls:
            self.state = clean(a.get("data-title", ""))
        if tag == "div" and "lang-row" in cls:
            self.lang_row = {"code": "", "name": "", "lang": "", "dir": "ltr"}
            self.slide["languages"].append(self.lang_row)
        if tag == "div" and "platform" in cls:
            self.platform = True
        if tag == "img":
            src = a.get("src", "")
            if "flag-background" in cls or "image/svg" in src[:40]:
                return  # flags and platform logos are redrawn by the mini-app
            match = re.match(r"data:image/(png|jpeg);base64,(.*)", src, re.S)
            if match:
                self.slide["media"].append({"raw": base64.b64decode(match.group(2)), "alt": clean(a.get("alt", "")), "state": self.state or ""})
            return
        if tag in ("h1", "h2", "h3", "p", "span", "strong"):
            self.text = [tag, cls, "", a]

    def handle_endtag(self, tag):
        if self.slide is None:
            return
        if tag == "section":
            self.slide = None
            return
        if self.text and tag == self.text[0]:
            kind, cls, buf, attrs = self.text
            value = clean(buf)
            self.text = None
            self.store(kind, cls, value, attrs)

    def store(self, tag, cls, value, attrs):
        s = self.slide
        if not value:
            return
        if tag == "span" and "eyebrow" in cls:
            s["chapter"] = sentence_case(value)
        elif tag == "h1":
            s["title"] = value
        elif tag == "span" and s["kind"] == "cover" and not s["brand"] and s["title"] == "" and value not in ("RS Field", "RS Classifier"):
            s["brand"].append(value)
        elif tag == "h2":
            s["title"] = value
        elif tag == "h3" and self.point is not None:
            self.point["title"] = value
        elif tag == "p" and "lead" in cls or tag == "p" and "tagline" in cls:
            s["lead"] = value
        elif tag == "p" and "cover-tag" in cls:
            s["note"] = value
        elif tag == "p" and ("caption" in cls or "cover-caption" in cls):
            s["caption"] = value
        elif tag == "p" and "cta" in cls:
            s["cta"] = value
        elif tag == "p" and self.point is not None and not self.point["text"]:
            self.point["text"] = value
        elif self.lang_row is not None and tag == "span" and not self.lang_row["code"]:
            self.lang_row["code"] = value
        elif self.lang_row is not None and tag == "strong":
            self.lang_row.update(name=value, lang=attrs.get("lang", ""), dir=attrs.get("dir", "ltr"))
            self.lang_row = None
        elif self.platform and tag == "span":
            s["platforms"].append(value)
            self.platform = False


def finish_slide(slide):
    """Cover h1 is 'Rocksurv' + a span with the product word; keep both for the brand lockup."""
    if slide["kind"] == "cover":
        word = slide["brand"][0] if slide["brand"] else ""
        base = slide["title"].replace(word, "").strip() if word else slide["title"]
        slide["brand"] = [base, word] if word else [slide["title"]]
        slide["title"] = " ".join(slide["brand"])
    else:
        slide.pop("brand")
    slide["points"] = [p for p in slide["points"] if p["title"] or p["text"]]
    return slide


def classify(image):
    if image.size in SCREEN_CROP:
        return "screen-landscape" if image.width > image.height else "screen-portrait"
    return "photo"


def average_color(image):
    r, g, b = image.convert("RGB").resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
    return f"#{r:02x}{g:02x}{b:02x}"


def export_image(raw, deck, image_id):
    with Image.open(io.BytesIO(raw)) as original:
        image = original.convert("RGB")
    kind = classify(image)
    if kind.startswith("screen"):
        top, bottom = SCREEN_CROP[image.size]
        image = image.crop((0, top, image.width, bottom))
    out = PUBLIC_DIR / deck
    variants = []
    for width in WIDTHS[kind]:
        if width > image.width and variants:
            continue
        width = min(width, image.width)
        height = round(image.height * width / image.width)
        resized = image if width == image.width else image.resize((width, height), Image.Resampling.LANCZOS)
        # Screens carry small interface text, so they get a higher quality than photos.
        resized.save(out / f"{image_id}-{width}.webp", "WEBP", quality=86 if kind.startswith("screen") else 80, method=6, exif=b"")
        variants.append(width)
    return {"kind": kind, "width": image.width, "height": image.height, "variants": variants, "color": average_color(image)}


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    images = {}
    for deck, spec in DECKS.items():
        out = PUBLIC_DIR / deck
        out.mkdir(parents=True, exist_ok=True)
        for stale in out.glob("*.webp"):
            stale.unlink()
        known = {}  # sha1 -> image id, shared across the language versions of one deck
        images[deck] = {}
        with zipfile.ZipFile(ROOT / spec["zip"]) as kit:
            for lang, member in spec["html"].items():
                parser = DeckParser()
                parser.feed(kit.read(member).decode("utf-8"))
                slides = [finish_slide(s) for s in parser.slides]
                for slide in slides:
                    for media in slide["media"]:
                        raw = media.pop("raw")
                        digest = hashlib.sha1(raw).hexdigest()
                        if digest not in known:
                            known[digest] = f"{len(known) + 1:02d}"
                            images[deck][known[digest]] = export_image(raw, deck, known[digest])
                        media["image"] = known[digest]
                payload = {"deck": deck, "lang": lang, "source": f"{spec['zip']}: {member}", "slides": slides}
                (DATA_DIR / f"{deck}.{lang}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"{deck}.{lang}: {len(slides)} slides")
    (DATA_DIR / "images.json").write_text(json.dumps(images, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
