"""Build optimized standalone presentation mini-apps for Field and Classifier.

Extracts content from materials ZIP archives, replaces all base64 images with
optimized WebP / SVG assets, adds responsive scaling, top bar with back navigation
and language switching, touch swipe support, and saves them as Astro pages:

  src/pages/ru/presentations/field.astro
  src/pages/ru/presentations/classifier.astro
  src/pages/presentations/field.astro (redirect)
  src/pages/presentations/classifier.astro (redirect)
"""

import base64
import os
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "materials"
PAGES_DIR = ROOT / "src" / "pages"
PUBLIC_DIR = ROOT / "public" / "presentations"

FIELD_ZIP = MATERIALS / "Rocksurv_Field_Presentation_Kit_EN_RU_v13.zip"
CLASSIFIER_ZIP = MATERIALS / "rocksurv_classifier.zip"

# Ensure public directories exist
(PUBLIC_DIR / "field" / "assets").mkdir(parents=True, exist_ok=True)
(PUBLIC_DIR / "classifier").mkdir(parents=True, exist_ok=True)
(PAGES_DIR / "ru" / "presentations").mkdir(parents=True, exist_ok=True)
(PAGES_DIR / "presentations").mkdir(parents=True, exist_ok=True)


def extract_field_svgs():
    with zipfile.ZipFile(FIELD_ZIP) as z:
        for svg_name in ["android.svg", "apple.svg", "flag_gb.svg", "flag_ru.svg", "flag_sa.svg"]:
            raw = z.read(f"rocksurv_field/assets/{svg_name}")
            (PUBLIC_DIR / "field" / "assets" / svg_name).write_bytes(raw)
    print("Field SVGs extracted.")


def build_field_presentation():
    with zipfile.ZipFile(FIELD_ZIP) as z:
        ru_raw = z.read("rocksurv_field/Rocksurv_Field_Presentation_RU.html").decode("utf-8")
        en_raw = z.read("rocksurv_field/Rocksurv_Field_Presentation_EN.html").decode("utf-8")

    def process_field_deck(raw_html, lang):
        # Extract main slides section: between <main id="stage"> and </main>
        m_main = re.search(r'<main id="stage">(.*?)</main>', raw_html, re.S)
        if not m_main:
            raise ValueError(f"Could not find <main id='stage'> in Field {lang}")
        slides_html = m_main.group(1)

        # Replace raster images and SVGs
        # Order in Field slides:
        # 1-10: raster 01-10
        # 11: Android SVG
        # 12: iOS SVG
        # 13: GB flag SVG
        # 14: RU flag SVG
        # 15: SA flag SVG
        # 16: raster 11
        img_idx = 0

        def replace_img(match):
            nonlocal img_idx
            img_idx += 1
            tag = match.group(0)
            alt_m = re.search(r'alt="([^"]*)"', tag)
            alt = alt_m.group(1) if alt_m else ""
            cls_m = re.search(r'class="([^"]*)"', tag)
            cls = cls_m.group(1) if cls_m else ""
            cls_attr = f' class="{cls}"' if cls else ""

            if img_idx <= 10:
                img_id = f"{img_idx:02d}"
                if img_idx in (1, 2, 3, 4, 8, 9, 10):
                    src = f"/presentations/field/{img_id}-1920.webp"
                    srcset = f"/presentations/field/{img_id}-800.webp 800w, /presentations/field/{img_id}-1280.webp 1280w, /presentations/field/{img_id}-1920.webp 1920w"
                    sizes = "(max-width: 900px) 90vw, 960px"
                elif img_idx in (5, 6):
                    src = f"/presentations/field/{img_id}-1600.webp"
                    srcset = f"/presentations/field/{img_id}-600.webp 600w, /presentations/field/{img_id}-1000.webp 1000w, /presentations/field/{img_id}-1600.webp 1600w"
                    sizes = "(max-width: 900px) 90vw, 430px"
                else:  # 7
                    src = f"/presentations/field/{img_id}-1280.webp"
                    srcset = f"/presentations/field/{img_id}-640.webp 640w, /presentations/field/{img_id}-1280.webp 1280w"
                    sizes = "(max-width: 900px) 90vw, 960px"
                priority = ' fetchpriority="high" loading="eager"' if img_idx == 1 else ' loading="lazy"'
                return f'<img src="{src}" srcset="{srcset}" sizes="{sizes}" alt="{alt}"{cls_attr}{priority} decoding="async">'
            elif img_idx == 11:
                return f'<img src="/presentations/field/assets/android.svg" alt="Android"{cls_attr} loading="lazy">'
            elif img_idx == 12:
                return f'<img src="/presentations/field/assets/apple.svg" alt="iOS"{cls_attr} loading="lazy">'
            elif img_idx == 13:
                return f'<img src="/presentations/field/assets/flag_gb.svg" alt=""{cls_attr} loading="lazy">'
            elif img_idx == 14:
                return f'<img src="/presentations/field/assets/flag_ru.svg" alt=""{cls_attr} loading="lazy">'
            elif img_idx == 15:
                return f'<img src="/presentations/field/assets/flag_sa.svg" alt=""{cls_attr} loading="lazy">'
            elif img_idx == 16:
                src = "/presentations/field/11-1280.webp"
                srcset = "/presentations/field/11-640.webp 640w, /presentations/field/11-1280.webp 1280w"
                sizes = "(max-width: 900px) 90vw, 960px"
                return f'<img src="{src}" srcset="{srcset}" sizes="{sizes}" alt="{alt}"{cls_attr} loading="lazy" decoding="async">'
            return tag

        slides_html = re.sub(r'<img[^>]+>', replace_img, slides_html)
        return slides_html

    ru_slides = process_field_deck(ru_raw, "ru")
    en_slides = process_field_deck(en_raw, "en")

    page_content = f"""---
// Standalone Presentation Mini-App: Rocksurv Field
---
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Rocksurv Field — интерактивная презентация приложения</title>
  <meta name="description" content="Интерактивная презентация Rocksurv Field: офлайн-карта GeoPackage, замеры структур, полевой журнал, DEM и экспорт сессий.">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <style>
    :root {{
      --paper: #f5f7f2;
      --ink: #12352e;
      --muted: #50645d;
      --mint: #69d4ad;
      --line: #cbd7cd;
      --gold: #d6b879;
      --bg: #0e1714;
      --bar-bg: rgba(16, 39, 31, 0.94);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 100%;
      height: 100%;
      background: var(--bg);
      color: var(--ink);
      font-family: 'Segoe UI', system-ui, -apple-system, Arial, sans-serif;
      overflow: hidden;
      user-select: none;
      -webkit-user-select: none;
    }}
    button {{ font: inherit; color: inherit; cursor: pointer; }}

    /* Top Bar */
    .pres-bar {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 52px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      background: var(--bar-bg);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border-bottom: 1px solid rgba(105, 212, 173, 0.2);
      z-index: 100;
      color: #f5f7f2;
      transition: opacity 0.25s ease, transform 0.25s ease;
    }}
    .pres-bar-left, .pres-bar-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .pres-back {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 6px;
      color: #f5f7f2;
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.2s ease;
    }}
    .pres-back:hover {{
      background: rgba(105, 212, 173, 0.22);
      border-color: var(--mint);
      color: #fff;
    }}
    .pres-title-wrap {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .pres-app-title {{
      font-weight: 700;
      font-size: 15px;
      letter-spacing: -0.01em;
      color: #fff;
    }}
    .pres-chip {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 2px 7px;
      background: rgba(105, 212, 173, 0.16);
      color: var(--mint);
      border-radius: 4px;
      font-weight: 600;
    }}
    .lang-toggle {{
      display: inline-flex;
      background: rgba(0, 0, 0, 0.35);
      border-radius: 6px;
      padding: 2px;
      border: 1px solid rgba(255, 255, 255, 0.12);
    }}
    .lang-btn {{
      border: none;
      background: transparent;
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 4px;
      color: #9ab4a8;
      transition: all 0.18s ease;
    }}
    .lang-btn.active {{
      background: var(--mint);
      color: #0e1714;
    }}
    .tool-btn {{
      border: 1px solid rgba(255, 255, 255, 0.15);
      background: rgba(255, 255, 255, 0.06);
      padding: 6px 10px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }}
    .tool-btn:hover {{
      background: rgba(105, 212, 173, 0.2);
      border-color: var(--mint);
    }}

    /* Main Stage */
    #pres-container {{
      position: absolute;
      top: 52px;
      left: 0;
      right: 0;
      bottom: 0;
      overflow: hidden;
    }}
    #stage {{
      position: absolute;
      left: 50%;
      top: 50%;
      width: 1600px;
      height: 900px;
      transform: translate(-50%, -50%) scale(var(--scale, 1));
      transform-origin: center center;
      transition: transform 0.08s ease-out;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.6);
    }}

    .slide {{
      display: none;
      position: relative;
      width: 1600px;
      height: 900px;
      overflow: hidden;
      background: var(--paper);
      padding: 60px 70px;
    }}
    .slide.active {{ display: block; }}

    .deck {{ display: none; width: 100%; height: 100%; }}
    .deck.active-deck {{ display: block; }}

    /* Typography & Layout */
    .brandline {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 18px;
      font-weight: 650;
      letter-spacing: 2px;
    }}
    .brandline .brand {{
      font-size: 25px;
      letter-spacing: -.5px;
      font-weight: 750;
    }}
    .eyebrow {{ color: var(--muted); }}
    h1, h2, p {{ margin: 0; }}
    h2 {{
      font-weight: 650;
      letter-spacing: -1.8px;
      font-size: 57px;
      line-height: 1.1;
      margin: 30px 0 16px;
      max-width: 1460px;
    }}
    .lead {{
      font-size: 27px;
      line-height: 1.35;
      color: var(--muted);
      max-width: 1450px;
    }}
    .feature-content {{
      position: absolute;
      left: 70px;
      right: 70px;
      top: 258px;
      display: grid;
      grid-template-columns: 420px 960px;
      gap: 80px;
      align-items: start;
    }}
    .copy {{ padding-top: 2px; max-width: 390px; }}
    .point {{
      border-top: 1px solid var(--line);
      padding-top: 18px;
      margin-bottom: 31px;
    }}
    .point h3 {{
      margin: 0 0 9px;
      font-size: 27px;
      font-weight: 650;
      line-height: 1.14;
      letter-spacing: -.5px;
    }}
    .point p {{
      font-size: 24px;
      line-height: 1.35;
      color: var(--muted);
    }}

    .shot {{
      position: relative;
      margin: 0;
      overflow: hidden;
      aspect-ratio: 2560 / 1410;
      background: #dfe9e1;
      outline: 1px solid #b9c9bd;
      box-shadow: 0 15px 28px #17372a12;
      border-radius: 4px;
    }}
    .shot img {{
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      transform: none;
      display: block;
    }}
    .caption {{
      margin-top: 14px;
      font-size: 17px;
      line-height: 1.3;
      color: var(--muted);
    }}
    .footer {{
      position: absolute;
      left: 70px;
      right: 70px;
      bottom: 22px;
      border-top: 1px solid var(--line);
      padding-top: 12px;
      display: flex;
      justify-content: space-between;
      gap: 40px;
      font-size: 16px;
      letter-spacing: .4px;
      color: var(--muted);
    }}

    /* Portrait Slides */
    .portrait-slide h2 {{ max-width: 920px; }}
    .portrait-slide .lead {{ max-width: 850px; }}
    .portrait-slide .feature-content {{ top: 350px; display: block; }}
    .portrait-slide .copy {{ max-width: 760px; }}
    .portrait-slide .point {{ margin-bottom: 31px; }}
    .portrait-slide .portrait-visual {{
      position: absolute;
      right: 70px;
      top: 125px;
      width: 430px;
    }}
    .shot.portrait {{ aspect-ratio: 5 / 8; }}
    .shot.portrait img {{ height: 100%; object-fit: contain; transform: none; }}
    .portrait-slide > .caption {{
      position: absolute;
      left: 70px;
      top: 755px;
      width: 820px;
      margin: 0;
    }}

    /* Cover Slide */
    .cover {{
      background: var(--ink);
      color: var(--paper);
    }}
    .cover .eyebrow, .cover .footer {{ color: #a9c6b7; }}
    .cover .footer {{ border-color: #38584b; }}
    .cover .brandline .brand {{ font-size: 30px; }}
    .cover h1 {{
      font-size: 82px;
      line-height: 1.05;
      letter-spacing: -3px;
      font-weight: 650;
      position: absolute;
      top: 222px;
      left: 70px;
      width: 510px;
    }}
    .cover h1 span {{ display: block; color: var(--mint); }}
    .cover .tagline {{
      position: absolute;
      top: 478px;
      left: 70px;
      width: 452px;
      font-size: 31px;
      line-height: 1.5;
      color: #d5e4db;
    }}
    .cover .hero-shot {{
      position: absolute;
      left: 610px;
      right: 70px;
      top: 249px;
    }}
    .cover .hero-shot .shot {{
      outline: 1px solid #5d7b68;
      box-shadow: 0 22px 45px #0004;
    }}
    .cover .hero-shot .caption {{
      color: #b6cfc0;
      margin-top: 24px;
      font-size: 21px;
    }}
    .cover .cover-tag {{
      position: absolute;
      left: 70px;
      top: 727px;
      width: 420px;
      color: var(--mint);
      font-size: 18px;
      line-height: 1.5;
      letter-spacing: .3px;
    }}

    /* Closing Slide */
    .closing {{ background: #eaf1e7; }}
    .closing .cta {{
      margin-top: 18px;
      font-size: 24px;
      line-height: 1.25;
      font-weight: 650;
      color: #126750;
    }}
    .closing .point {{ margin-bottom: 21px; }}
    .closing .point p {{ font-size: 23px; }}
    .closing .caption {{ max-width: 1000px; }}
    .closing .shot {{ aspect-ratio: 16 / 9; }}
    .closing .shot img {{ height: 100%; object-fit: cover; transform: none; }}

    /* Languages Slide */
    .languages {{
      height: 529px;
      padding: 0;
      background: transparent;
      display: grid;
      grid-template-rows: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }}
    .lang-row {{
      position: relative;
      isolation: isolate;
      overflow: hidden;
      border: 0;
      background: #e5eee5;
      padding: 0 36px;
      gap: 48px;
      display: flex;
      justify-content: flex-start;
      align-items: center;
      min-height: 0;
      border-radius: 8px;
    }}
    .lang-row .flag-background {{
      position: absolute;
      right: 0;
      top: 0;
      width: 310px;
      height: 100%;
      object-fit: contain;
      opacity: .52;
      z-index: -1;
    }}
    .lang-row span {{
      width: 60px;
      flex-shrink: 0;
      font-size: 20px;
      color: #50645d;
      letter-spacing: 2px;
    }}
    .lang-row strong {{
      display: flex;
      align-items: center;
      height: 100%;
      font-size: 62px;
      line-height: 1;
      font-weight: 600;
    }}
    .lang-row strong.ar {{ line-height: 1; font-size: 62px; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; }}
    .platforms {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      margin-top: 12px;
      background: var(--ink);
      border-radius: 8px;
      padding: 16px 0;
    }}
    .platform {{
      height: 94px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      gap: 7px;
      font-size: 21px;
      font-weight: 600;
      letter-spacing: .2px;
      color: var(--paper);
    }}
    .platform + .platform {{ border-left: 1px solid #38584b; }}
    .platform-art {{
      height: 57px;
      width: 76px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .platform-art img {{ width: 68px; height: 68px; object-fit: contain; }}
    .platform-art.ios img {{ width: 39px; height: 47px; }}
    .language-slide .point {{ margin-bottom: 20px; }}
    .language-slide .point p {{ font-size: 23px; }}

    /* Bottom Navigation Controls */
    .controls {{
      position: fixed;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--bar-bg);
      border: 1px solid rgba(105, 212, 173, 0.3);
      padding: 6px 12px;
      border-radius: 30px;
      z-index: 90;
      color: #f5f7f2;
      font-size: 13px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
      transition: opacity .25s ease;
    }}
    .controls.quiet {{ opacity: 0.18; }}
    .controls:hover, .controls:focus-within {{ opacity: 1; }}
    .controls button {{
      color: inherit;
      background: transparent;
      border: 0;
      padding: 6px 14px;
      cursor: pointer;
      border-radius: 20px;
      font-weight: 600;
      transition: background 0.18s ease;
    }}
    .controls button:hover, .controls button:focus-visible {{
      background: #355e4a;
      outline: 1px solid var(--mint);
    }}
    .controls output {{
      min-width: 60px;
      text-align: center;
      font-variant-numeric: tabular-nums;
      font-weight: 600;
      letter-spacing: 0.5px;
    }}

    /* Progress bar */
    .pres-progress {{
      position: fixed;
      top: 52px;
      left: 0;
      height: 3px;
      background: var(--mint);
      width: 0%;
      transition: width 0.25s ease;
      z-index: 101;
    }}

    /* Keyboard help tooltip */
    .keys-hint {{
      font-size: 11px;
      color: #8da59b;
      margin-left: 6px;
      padding-left: 8px;
      border-left: 1px solid rgba(255, 255, 255, 0.15);
    }}

    @media print {{
      @page {{ size: 1600px 900px; margin: 0; }}
      html, body {{
        width: 1600px;
        height: auto;
        background: white;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }}
      .pres-bar, .controls, .pres-progress {{ display: none !important; }}
      #pres-container {{ position: static; display: block; }}
      #stage {{ position: static; transform: none; width: 1600px; height: auto; }}
      .slide, .slide.active {{
        display: block !important;
        break-after: page;
        page-break-after: always;
      }}
      .slide:last-child {{ break-after: auto; page-break-after: auto; }}
    }}
  </style>
</head>
<body>
  <!-- Top Navigation Bar -->
  <header class="pres-bar">
    <div class="pres-bar-left">
      <a href="/ru/#apps" class="pres-back" id="back-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        <span>Назад к резюме</span>
      </a>
      <div class="pres-title-wrap">
        <span class="pres-app-title">Rocksurv Field</span>
        <span class="pres-chip">12 слайдов</span>
      </div>
    </div>
    <div class="pres-bar-right">
      <div class="lang-toggle" role="group" aria-label="Язык презентации">
        <button class="lang-btn active" id="btn-lang-ru" data-lang="ru">RU</button>
        <button class="lang-btn" id="btn-lang-en" data-lang="en">EN</button>
      </div>
      <button class="tool-btn" id="full" title="На весь экран (F)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
      </button>
      <button class="tool-btn" id="print" title="Печать / PDF (P)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 14h12v8H6z"/></svg>
      </button>
    </div>
  </header>

  <div class="pres-progress" id="progress-bar"></div>

  <!-- Stage -->
  <div id="pres-container">
    <main id="stage">
      <div class="deck active-deck" id="deck-ru">
        {ru_slides}
      </div>
      <div class="deck" id="deck-en">
        {en_slides}
      </div>
    </main>
  </div>

  <!-- Bottom Navigation Bar -->
  <nav class="controls" aria-label="Управление слайдами">
    <button id="prev" aria-label="Предыдущий слайд">←</button>
    <output id="counter" aria-live="polite">01 / 12</output>
    <button id="next" aria-label="Следующий слайд">→</button>
    <span class="keys-hint">← → или Пробел · F весь экран</span>
  </nav>

  <script is:inline>
    let currentLang = 'ru';
    const deckRu = document.getElementById('deck-ru');
    const deckEn = document.getElementById('deck-en');
    const btnRu = document.getElementById('btn-lang-ru');
    const btnEn = document.getElementById('btn-lang-en');
    const counter = document.getElementById('counter');
    const bar = document.querySelector('.controls');
    const progressBar = document.getElementById('progress-bar');
    const backLink = document.getElementById('back-link');

    // Smart back: if user arrived from the same site, use history.back()
    if (document.referrer && document.referrer.includes(window.location.host)) {{
      backLink.addEventListener('click', (e) => {{
        e.preventDefault();
        history.back();
      }});
    }}

    function getSlides() {{
      const activeDeck = currentLang === 'ru' ? deckRu : deckEn;
      return [...activeDeck.querySelectorAll('.slide')];
    }}

    let slides = getSlides();
    let index = Math.min(slides.length - 1, Math.max(0, parseInt(location.hash.slice(1) || '1', 10) - 1 || 0));

    function setLang(lang) {{
      currentLang = lang;
      if (lang === 'ru') {{
        deckRu.classList.add('active-deck');
        deckEn.classList.remove('active-deck');
        btnRu.classList.add('active');
        btnEn.classList.remove('active');
        document.documentElement.lang = 'ru';
      }} else {{
        deckRu.classList.remove('active-deck');
        deckEn.classList.add('active-deck');
        btnRu.classList.remove('active');
        btnEn.classList.add('active');
        document.documentElement.lang = 'en';
      }}
      slides = getSlides();
      show(index);
    }}

    btnRu.addEventListener('click', () => setLang('ru'));
    btnEn.addEventListener('click', () => setLang('en'));

    // Check URL query param for lang
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('lang') === 'en') {{
      setLang('en');
    }}

    function show(n) {{
      index = Math.min(slides.length - 1, Math.max(0, n));
      slides.forEach((s, i) => {{
        s.classList.toggle('active', i === index);
        s.setAttribute('aria-hidden', i !== index);
      }});
      const num = String(index + 1).padStart(2, '0');
      const total = String(slides.length).padStart(2, '0');
      counter.textContent = `${{num}} / ${{total}}`;
      if (progressBar) {{
        progressBar.style.width = `${{((index + 1) / slides.length) * 100}}%`;
      }}
      history.replaceState(null, '', `#${{index + 1}}`);
    }}

    function fit() {{
      const headerH = 52;
      const margin = 20;
      const availW = window.innerWidth - margin * 2;
      const availH = window.innerHeight - headerH - margin * 2;
      const scale = Math.min(availW / 1600, availH / 900, 1.25);
      document.documentElement.style.setProperty('--scale', Math.max(scale, 0.2).toString());
    }}
    window.addEventListener('resize', fit);
    fit();
    show(index);

    document.getElementById('prev').onclick = () => show(index - 1);
    document.getElementById('next').onclick = () => show(index + 1);
    document.getElementById('print').onclick = () => window.print();

    async function toggleFullscreen() {{
      try {{
        if (document.fullscreenElement) await document.exitFullscreen();
        else await document.documentElement.requestFullscreen();
      }} catch (e) {{
        console.warn('Fullscreen request failed:', e);
      }}
    }}
    document.getElementById('full').onclick = toggleFullscreen;

    window.addEventListener('keydown', (e) => {{
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      if (['ArrowRight', 'PageDown', ' '].includes(e.key)) {{
        e.preventDefault();
        show(index + 1);
      }}
      if (['ArrowLeft', 'PageUp'].includes(e.key)) {{
        e.preventDefault();
        show(index - 1);
      }}
      if (e.key === 'Home') {{ e.preventDefault(); show(0); }}
      if (e.key === 'End') {{ e.preventDefault(); show(slides.length - 1); }}
      if (e.key.toLowerCase() === 'f') toggleFullscreen();
      if (e.key.toLowerCase() === 'p') window.print();
      if (e.key === 'Escape') {{
        if (!document.fullscreenElement) {{
          window.location.href = '/ru/#apps';
        }}
      }}
    }});

    // Quiet controls on inactivity
    let timer;
    function wake() {{
      bar.classList.remove('quiet');
      clearTimeout(timer);
      timer = setTimeout(() => bar.classList.add('quiet'), 3000);
    }}
    window.addEventListener('pointermove', wake);
    wake();

    // Touch swipe gestures
    let touchStartX = 0;
    let touchStartY = 0;
    window.addEventListener('touchstart', (e) => {{
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }}, {{ passive: true }});
    window.addEventListener('touchend', (e) => {{
      const diffX = e.changedTouches[0].screenX - touchStartX;
      const diffY = e.changedTouches[0].screenY - touchStartY;
      if (Math.abs(diffX) > 40 && Math.abs(diffX) > Math.abs(diffY)) {{
        if (diffX < 0) show(index + 1);
        else show(index - 1);
      }}
    }}, {{ passive: true }});
  </script>
</body>
</html>
"""
    (PAGES_DIR / "ru" / "presentations" / "field.astro").write_text(page_content, encoding="utf-8")
    print("Field Astro presentation written successfully.")


def build_classifier_presentation():
    with zipfile.ZipFile(CLASSIFIER_ZIP) as z:
        raw = z.read("rocksurv_classifier/Rocksurv_Classifier_Presentation_EN.html").decode("utf-8")

    # Extract styles between <style> and </style>
    m_style = re.search(r"<style>(.*?)</style>", raw, re.S)
    if not m_style:
        raise ValueError("Could not find <style> in Classifier HTML")
    style_content = m_style.group(1)

    # Extract main slides section between <main id="stage"> and </main>
    m_main = re.search(r'<main id="stage">(.*?)</main>', raw, re.S)
    if not m_main:
        raise ValueError("Could not find <main id='stage'> in Classifier HTML")
    slides_html = m_main.group(1)

    # Replace all 38 raster images in Classifier
    img_idx = 0

    def replace_img(match):
        nonlocal img_idx
        img_idx += 1
        tag = match.group(0)
        alt_m = re.search(r'alt="([^"]*)"', tag)
        alt = alt_m.group(1) if alt_m else ""
        cls_m = re.search(r'class="([^"]*)"', tag)
        cls = cls_m.group(1) if cls_m else ""
        cls_attr = f' class="{cls}"' if cls else ""

        img_id = f"{img_idx:02d}"
        src = f"/presentations/classifier/{img_id}-1600.webp"
        srcset = f"/presentations/classifier/{img_id}-600.webp 600w, /presentations/classifier/{img_id}-1000.webp 1000w, /presentations/classifier/{img_id}-1600.webp 1600w"
        sizes = "(max-width: 900px) 90vw, 430px"
        priority = ' fetchpriority="high" loading="eager"' if img_idx <= 2 else ' loading="lazy"'
        return f'<img src="{src}" srcset="{srcset}" sizes="{sizes}" alt="{alt}"{cls_attr}{priority} decoding="async">'

    slides_html = re.sub(r'<img[^>]+>', replace_img, slides_html)

    # Enhanced Classifier page
    page_content = f"""---
// Standalone Presentation Mini-App: Rocksurv Classifier
---
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Rocksurv Classifier — Interactive Petrographic & Structural Suite Presentation</title>
  <meta name="description" content="Interactive presentation of Rocksurv Classifier: IUGS QAPF classification, Schmidt stereonet, structural verification, fault rocks and rock catalog.">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <style>
    {style_content}

    /* Custom overrides & Top Bar */
    :root {{
      --bar-bg: rgba(9, 19, 28, 0.94);
      --cyan: #38bdf8;
    }}
    html, body {{
      user-select: none;
      -webkit-user-select: none;
    }}

    .pres-bar {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 52px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      background: var(--bar-bg);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border-bottom: 1px solid rgba(56, 189, 248, 0.2);
      z-index: 100;
      color: #f7fafd;
      transition: opacity 0.25s ease;
    }}
    .pres-bar-left, .pres-bar-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .pres-back {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 6px;
      color: #f7fafd;
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.2s ease;
    }}
    .pres-back:hover {{
      background: rgba(56, 189, 248, 0.22);
      border-color: var(--cyan);
      color: #fff;
    }}
    .pres-title-wrap {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .pres-app-title {{
      font-weight: 700;
      font-size: 15px;
      letter-spacing: -0.01em;
      color: #fff;
    }}
    .pres-chip {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 2px 7px;
      background: rgba(56, 189, 248, 0.16);
      color: var(--cyan);
      border-radius: 4px;
      font-weight: 600;
    }}
    .tool-btn {{
      border: 1px solid rgba(255, 255, 255, 0.15);
      background: rgba(255, 255, 255, 0.06);
      padding: 6px 10px;
      border-radius: 6px;
      color: #f7fafd;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .tool-btn:hover {{
      background: rgba(56, 189, 248, 0.2);
      border-color: var(--cyan);
    }}

    #pres-container {{
      position: absolute;
      top: 52px;
      left: 0;
      right: 0;
      bottom: 0;
      overflow: hidden;
    }}
    #stage {{
      position: absolute;
      left: 50%;
      top: 50%;
      width: 1600px;
      height: 900px;
      transform: translate(-50%, -50%) scale(var(--scale, 1));
      transform-origin: center center;
      transition: transform 0.08s ease-out;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.6);
    }}

    .controls {{
      position: fixed;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--bar-bg);
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 6px 12px;
      border-radius: 30px;
      z-index: 90;
      color: #f7fafd;
      font-size: 13px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
      transition: opacity .25s ease;
    }}
    .controls.quiet {{ opacity: 0.18; }}
    .controls:hover, .controls:focus-within {{ opacity: 1; }}
    .controls button {{
      color: inherit;
      background: transparent;
      border: 0;
      padding: 6px 14px;
      cursor: pointer;
      border-radius: 20px;
      font-weight: 600;
      transition: background 0.18s ease;
    }}
    .controls button:hover, .controls button:focus-visible {{
      background: #0c3350;
      outline: 1px solid var(--cyan);
    }}
    .controls output {{
      min-width: 60px;
      text-align: center;
      font-variant-numeric: tabular-nums;
      font-weight: 600;
      letter-spacing: 0.5px;
    }}

    .pres-progress {{
      position: fixed;
      top: 52px;
      left: 0;
      height: 3px;
      background: var(--cyan);
      width: 0%;
      transition: width 0.25s ease;
      z-index: 101;
    }}
    .keys-hint {{
      font-size: 11px;
      color: #7d9cb3;
      margin-left: 6px;
      padding-left: 8px;
      border-left: 1px solid rgba(255, 255, 255, 0.15);
    }}

    @media print {{
      @page {{ size: 1600px 900px; margin: 0; }}
      html, body {{
        width: 1600px;
        height: auto;
        background: white;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }}
      .pres-bar, .controls, .pres-progress {{ display: none !important; }}
      #pres-container {{ position: static; display: block; }}
      #stage {{ position: static; transform: none; width: 1600px; height: auto; }}
      .slide, .slide.active {{
        display: block !important;
        break-after: page;
        page-break-after: always;
      }}
      .slide:last-child {{ break-after: auto; page-break-after: auto; }}
    }}
  </style>
</head>
<body>
  <!-- Top Navigation Bar -->
  <header class="pres-bar">
    <div class="pres-bar-left">
      <a href="/ru/#apps" class="pres-back" id="back-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        <span>Назад к резюме</span>
      </a>
      <div class="pres-title-wrap">
        <span class="pres-app-title">Rocksurv Classifier</span>
        <span class="pres-chip">10 слайдов · Карусели</span>
      </div>
    </div>
    <div class="pres-bar-right">
      <button class="tool-btn" id="full" title="На весь экран (F)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
      </button>
      <button class="tool-btn" id="print" title="Печать / PDF (P)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 14h12v8H6z"/></svg>
      </button>
    </div>
  </header>

  <div class="pres-progress" id="progress-bar"></div>

  <!-- Stage -->
  <div id="pres-container">
    <main id="stage">
      {slides_html}
    </main>
  </div>

  <!-- Bottom Navigation Bar -->
  <nav class="controls" aria-label="Slide controls">
    <button id="prev" aria-label="Previous slide">←</button>
    <output id="counter" aria-live="polite">01 / 10</output>
    <button id="next" aria-label="Next slide">→</button>
    <span class="keys-hint">← → или Пробел · F весь экран</span>
  </nav>

  <script is:inline>
    const slides = [...document.querySelectorAll('.slide')];
    const counter = document.querySelector('#counter');
    const bar = document.querySelector('.controls');
    const progressBar = document.getElementById('progress-bar');
    const backLink = document.getElementById('back-link');

    if (document.referrer && document.referrer.includes(window.location.host)) {{
      backLink.addEventListener('click', (e) => {{
        e.preventDefault();
        history.back();
      }});
    }}

    let index = Math.min(slides.length - 1, Math.max(0, parseInt(location.hash.slice(1) || '1', 10) - 1 || 0));

    function fit() {{
      const headerH = 52;
      const margin = 20;
      const availW = window.innerWidth - margin * 2;
      const availH = window.innerHeight - headerH - margin * 2;
      const scale = Math.min(availW / 1600, availH / 900, 1.25);
      document.documentElement.style.setProperty('--scale', Math.max(scale, 0.2).toString());
    }}
    window.addEventListener('resize', fit);
    fit();

    // Carousel Management
    class SlideCarousel {{
      constructor(el) {{
        this.el = el;
        this.items = [...el.querySelectorAll('.carousel-item')];
        this.dots = [...el.querySelectorAll('.carousel-dot')];
        this.badgeLabel = el.querySelector('.badge-label');
        this.badgeCount = el.querySelector('.badge-count');
        this.progressBar = el.querySelector('.cycle-progress');
        this.btnPrev = el.querySelector('.carousel-btn.prev');
        this.btnNext = el.querySelector('.carousel-btn.next');

        this.currentIndex = 0;
        this.autoTimer = null;
        this.progressTimer = null;
        this.isAutoPlaying = true;
        this.hasCompletedCycle = false;
        this.durationPerItem = 2800;
        this.progressStartTime = 0;

        this.init();
      }}

      init() {{
        this.updateUI();

        if (this.btnPrev) {{
          this.btnPrev.addEventListener('click', (e) => {{
            e.stopPropagation();
            this.stopAutoPlay();
            this.prev();
          }});
        }}

        if (this.btnNext) {{
          this.btnNext.addEventListener('click', (e) => {{
            e.stopPropagation();
            this.stopAutoPlay();
            this.next();
          }});
        }}

        this.dots.forEach((dot, idx) => {{
          dot.addEventListener('click', (e) => {{
            e.stopPropagation();
            this.stopAutoPlay();
            this.goTo(idx);
          }});
        }});

        this.el.addEventListener('mouseenter', () => {{
          if (this.isAutoPlaying) this.pauseAutoPlay();
        }});

        this.el.addEventListener('mouseleave', () => {{
          if (this.isAutoPlaying && !this.hasCompletedCycle) this.resumeAutoPlay();
        }});
      }}

      startAutoPlay() {{
        this.stopAutoPlay();
        if (this.items.length <= 1) return;
        this.isAutoPlaying = true;
        this.hasCompletedCycle = false;
        this.scheduleNext();
      }}

      stopAutoPlay() {{
        clearTimeout(this.autoTimer);
        cancelAnimationFrame(this.progressTimer);
        this.autoTimer = null;
        this.progressTimer = null;
        if (this.progressBar) this.progressBar.style.width = '0%';
      }}

      pauseAutoPlay() {{
        clearTimeout(this.autoTimer);
        cancelAnimationFrame(this.progressTimer);
      }}

      resumeAutoPlay() {{
        this.scheduleNext();
      }}

      scheduleNext() {{
        this.progressStartTime = performance.now();
        const animateProgress = (now) => {{
          const elapsed = now - this.progressStartTime;
          const progress = Math.min(100, (elapsed / this.durationPerItem) * 100);
          if (this.progressBar) this.progressBar.style.width = progress + '%';
          if (elapsed < this.durationPerItem) {{
            this.progressTimer = requestAnimationFrame(animateProgress);
          }}
        }};
        this.progressTimer = requestAnimationFrame(animateProgress);

        this.autoTimer = setTimeout(() => {{
          if (this.currentIndex === this.items.length - 1) {{
            this.hasCompletedCycle = true;
            this.stopAutoPlay();
          }} else {{
            this.next(true);
          }}
        }}, this.durationPerItem);
      }}

      goTo(idx) {{
        this.items[this.currentIndex].classList.remove('active');
        if (this.dots[this.currentIndex]) this.dots[this.currentIndex].classList.remove('active');

        this.currentIndex = idx;

        this.items[this.currentIndex].classList.add('active');
        if (this.dots[this.currentIndex]) this.dots[this.currentIndex].classList.add('active');

        this.updateUI();
      }}

      next(fromAuto = false) {{
        const nextIdx = (this.currentIndex + 1) % this.items.length;
        this.goTo(nextIdx);
        if (fromAuto && this.isAutoPlaying && !this.hasCompletedCycle) {{
          this.scheduleNext();
        }}
      }}

      prev() {{
        const prevIdx = (this.currentIndex - 1 + this.items.length) % this.items.length;
        this.goTo(prevIdx);
      }}

      updateUI() {{
        const currentItem = this.items[this.currentIndex];
        const title = currentItem ? currentItem.getAttribute('data-title') : '';
        if (this.badgeLabel) this.badgeLabel.textContent = title;
        if (this.badgeCount) this.badgeCount.textContent = (this.currentIndex + 1) + ' / ' + this.items.length;
      }}
    }}

    const carousels = [...document.querySelectorAll('.carousel')].map(el => new SlideCarousel(el));

    function show(newIndex) {{
      index = Math.min(slides.length - 1, Math.max(0, newIndex));
      slides.forEach((s, idx) => {{
        s.classList.toggle('active', idx === index);
      }});
      const num = String(index + 1).padStart(2, '0');
      const total = String(slides.length).padStart(2, '0');
      counter.textContent = `${{num}} / ${{total}}`;
      if (progressBar) {{
        progressBar.style.width = `${{((index + 1) / slides.length) * 100}}%`;
      }}
      history.replaceState(null, '', `#${{index + 1}}`);

      const activeSlide = slides[index];
      const activeCarouselEl = activeSlide ? activeSlide.querySelector('.carousel') : null;
      if (activeCarouselEl) {{
        const carouselInstance = carousels.find(c => c.el === activeCarouselEl);
        if (carouselInstance) {{
          carouselInstance.startAutoPlay();
        }}
      }}
    }}

    document.querySelector('#prev').addEventListener('click', () => show(index - 1));
    document.querySelector('#next').addEventListener('click', () => show(index + 1));
    document.querySelector('#full').addEventListener('click', () => {{
      if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {{}});
      else document.exitFullscreen().catch(() => {{}});
    }});
    document.querySelector('#print').addEventListener('click', () => window.print());

    window.addEventListener('keydown', (e) => {{
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (['ArrowRight', 'PageDown', ' '].includes(e.key)) {{ e.preventDefault(); show(index + 1); }}
      if (['ArrowLeft', 'PageUp'].includes(e.key)) {{ e.preventDefault(); show(index - 1); }}
      if (e.key === 'Home') {{ e.preventDefault(); show(0); }}
      if (e.key === 'End') {{ e.preventDefault(); show(slides.length - 1); }}
      if (e.key === 'f' || e.key === 'F') {{
        if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {{}});
        else document.exitFullscreen().catch(() => {{}});
      }}
      if (e.key === 'p' || e.key === 'P') window.print();
      if (e.key === 'Escape') {{
        if (!document.fullscreenElement) {{
          window.location.href = '/ru/#apps';
        }}
      }}
    }});

    let timer;
    function wake() {{
      bar.classList.remove('quiet');
      clearTimeout(timer);
      timer = setTimeout(() => bar.classList.add('quiet'), 3000);
    }}
    window.addEventListener('pointermove', wake);
    wake();

    // Touch swipe gestures
    let touchStartX = 0;
    let touchStartY = 0;
    window.addEventListener('touchstart', (e) => {{
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }}, {{ passive: true }});
    window.addEventListener('touchend', (e) => {{
      const diffX = e.changedTouches[0].screenX - touchStartX;
      const diffY = e.changedTouches[0].screenY - touchStartY;
      if (Math.abs(diffX) > 40 && Math.abs(diffX) > Math.abs(diffY)) {{
        if (diffX < 0) show(index + 1);
        else show(index - 1);
      }}
    }}, {{ passive: true }});

    show(index);
  </script>
</body>
</html>
"""
    (PAGES_DIR / "ru" / "presentations" / "classifier.astro").write_text(page_content, encoding="utf-8")
    print("Classifier Astro presentation written successfully.")


def create_redirect_pages():
    for name in ["field", "classifier"]:
        redirect_astro = f"""---
// Redirect to localized presentation
---
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=/ru/presentations/{name}/">
  <link rel="canonical" href="/ru/presentations/{name}/">
  <title>Redirecting...</title>
</head>
<body>
  <p>Redirecting to <a href="/ru/presentations/{name}/">/ru/presentations/{name}/</a>...</p>
</body>
</html>
"""
        (PAGES_DIR / "presentations" / f"{name}.astro").write_text(redirect_astro, encoding="utf-8")
    print("Redirect pages written.")


def main():
    extract_field_svgs()
    build_field_presentation()
    build_classifier_presentation()
    create_redirect_pages()
    print("All presentations built.")


if __name__ == "__main__":
    main()
