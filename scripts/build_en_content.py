import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "src" / "content"


def check_no_dashes(obj, path=""):
    if isinstance(obj, str):
        if re.search(r'[\u2013\u2014]', obj):
            raise ValueError(f"En/Em dash in {path}: {obj}")
    elif isinstance(obj, list):
        for i, it in enumerate(obj):
            check_no_dashes(it, f"{path}[{i}]")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            check_no_dashes(v, f"{path}.{k}")


apps_en = [
  {
    "id": "rocksurv-field",
    "kind": "product",
    "slug": "rocksurv-field",
    "order": 1,
    "stage": "Field",
    "title": "Rocksurv Field",
    "area": "Field Operations & Geodata Capture",
    "summary": "Complete offline-first mobile workstation for field geologists: OGC GeoPackage maps, structured observation logs, structural measurements, photo documentation, and embedded QA/QC with zero network reliance.",
    "problem": "Traditional paper notebooks and unlinked spreadsheets result in losing up to 20% of relational links between stations, samples, and photos, while post-season digitizing requires weeks of manual cleanup. Rocksurv Field resolves this: each observation station rigidly binds lithological descriptions, sample IDs ('station-S1'), joint and bedding attitudes, photos with compass bearing and scale bar, sketches, and alteration zones within a unified OGC GeoPackage database. Projects are prepared in ArcGIS Pro, run 100% offline in the field, and export to office deliverables in a single click.",
    "workflow": [
      "In office: prepare cartographic base in ArcGIS Pro and export to standard OGC GeoPackage container (raster pyramids, vector layers, geological symbology, and domain dictionaries).",
      "In field: launch project with zero network - offline map navigation, high-precision GNSS with error ellipse, digital geological compass, and topography from local Copernicus DEM GLO-30.",
      "At outcrop: log observation station with dependent lithological pickers, sample registration, planar and linear structural measurements, alteration zones, and ore mineralization.",
      "Embedded QA/QC: automated strike calculation via Right-Hand Rule (RHR), Wentworth grain-size validation, and mineral association compatibility checks eliminate errors on the spot.",
      "Post-field delivery: 1-click session export - structured multi-sheet Excel workbook (.xlsx), ZIP archive of geo-tagged media, and validation_report.json audit trail for GIS."
    ],
    "highlights": [
      "100% Offline-First: raster pyramids and vector layers inside an open OGC GeoPackage container without internet access or ESRI licenses.",
      "Rigid observation integrity: stations bind lithological descriptions, samples ('station-S1'), structural attitudes, photos with compass bearing and scale bar, and field sketches.",
      "Embedded field QA/QC: Right-Hand Rule (RHR) enforcement, mineral compatibility validation, and grain-size normalization upon data entry.",
      "Expedition-grade fault tolerance: background shadow backups every 5 minutes, draft recovery upon app termination, and PendingPhotoStore for orphaned camera images.",
      "1-click post-field export: session export into a multi-sheet Excel workbook (.xlsx), ZIP media package, and validation_report.json audit log.",
      "Multilingual for international projects: English, Russian, and Arabic (RTL) localization with native KSA-GRF17 coordinate system support."
    ],
    "capabilities": [
      {
        "group": "Mapping & Geodata",
        "items": [
          "Offline raster pyramids and vector layers served directly from GeoPackage.",
          "On-the-fly dynamic reprojection (WGS 84, UTM, Web Mercator, KSA-GRF17).",
          "Geological symbology and layer labelling authored in ArcGIS Pro.",
          "Import of GPS tracks and reference waypoints from KML and KMZ files."
        ]
      },
      {
        "group": "Field Journal & Observations",
        "items": [
          "Observation stations: exposure type, rock color, texture, grain size, stratigraphic unit.",
          "Sample cataloging with automated numbering ('station-S1'), sample type, and mass.",
          "Planar and linear attitude measurements with Right-Hand Rule (RHR) enforcement.",
          "Hydrothermal alteration zones and ore mineralization with intensity grading."
        ]
      },
      {
        "group": "Photography & Navigation",
        "items": [
          "Photos with embedded EXIF: coordinates, compass bearing, and target scale bar.",
          "GNSS positioning with accuracy radius, digital geological compass with magnetic declination control.",
          "Topographic elevation from local Copernicus DEM GLO-30 or GEDTM30 datasets."
        ]
      },
      {
        "group": "Reliability & Data Safety",
        "items": [
          "Auto-save and background shadow project copies every 5 minutes.",
          "Soft-delete Recycle Bin with recovery for accidentally discarded records.",
          "PendingPhotoStore background service rescuing photos saved by camera before database commitment.",
          "FieldTextDraft engine restoring unsaved text field drafts across application crashes."
        ]
      },
      {
        "group": "Post-Field Reporting",
        "items": [
          "Session export to Excel (.xlsx) with dedicated worksheets per entity.",
          "ZIP archive containing geo-referenced photographs, outcrop sketches, and diagrams.",
          "Auditable validation_report.json quality control report for corporate GIS integration."
        ]
      }
    ],
    "stack": "Flutter (Dart), MapLibre GL Native, SQLite / OGC GeoPackage, Copernicus DEM GLO-30, ArcGIS Pro Tools (Python)",
    "specVersion": "1.0.4+ (Clean Architecture & GeoPackage Data Engine)",
    "diagram": "field-flow",
    "pending": [
      "Operational demonstration on industrial rugged field tablets.",
      "Production deployment metrics across mineral exploration projects.",
      "Author contribution: system architecture, core engine development, and field testing."
    ],
    "publicationState": "published",
    "productStatus": "prototype",
    "evidence": { "source": "specification", "reference": "materials/design (2).md, sections 1, 2, 4, and 5", "verified": True }
  },
  {
    "id": "classifier",
    "kind": "product",
    "slug": "classifier",
    "order": 2,
    "stage": "Classification",
    "title": "Rocksurv Classifier",
    "area": "Rock Classification & Structural Analysis",
    "summary": "Pocket petrographic laboratory and structural calculator: rigorous rock classification according to IUGS, Dunham, and Sibson standards, spherical geometry attitude validation, and interactive Schmidt stereonet directly at the outcrop.",
    "problem": "Misidentifications in field rock naming and geometric inconsistencies in structural measurements (such as a lineation pitch plunging steeper than the dip of its host plane) are typically uncovered in the office months after the field season ends, leading to costly drilling errors and redundant re-traverses. Rocksurv Classifier brings office-grade calculation rigor directly to the outcrop: instantly computes modal composition coordinates on the Streckeisen QAPF double triangle, audits structural measurement consistency using spherical trigonometry, classifies fault-rock kinematics, and plots equal-area Schmidt stereonets without drafting paper.",
    "workflow": [
      "Enter modal mineral composition (Q, A, P, F and color index M') or tap directly on the interactive QAPF double triangle.",
      "Instantly receive the IUGS classification field and detailed rock diagnostic card with key microscopic and macroscopic criteria.",
      "For ultramafic and mafic rocks: automatic routing to 4 specialized ternary diagrams (Ol-Opx-Cpx, Ol-Px-Hbl, Plag-Px-Ol, Plag-Opx-Cpx).",
      "Enter structural measurements: dip azimuth and dip angle of planar features, plunge azimuth and plunge angle of lineation or slickensides.",
      "Instant spherical trigonometry audit: verify measurement consistency within 5 deg or 8 deg tolerance, compute rake/pitch angle, and deduce slip kinematics.",
      "Project structures onto an equal-area Schmidt net: great circles, normal poles, lineations, beta-axis intersections, and fold analysis."
    ],
    "highlights": [
      "IUGS, Dunham, and Sibson standards: rigorous classification of igneous (plutonic and volcanic), mafic, siliciclastic (Pettijohn), carbonate, and fault rocks.",
      "Outcrop-level structural geometry audit: spherical trigonometry flags physically impossible structural pairs before database entry.",
      "Interactive Schmidt Stereonet: dynamic projection of Bezier great circles, normal poles, lineations, beta-axes, and fold axis geometry.",
      "Dichotomous macroscopic key & catalog: field identification flow chart and illustrated catalog of 24 reference rock types.",
      "Kotlin Multiplatform architecture: single verified mathematical core shared across native Android and iOS client applications.",
      "100% Offline-First: completely autonomous field operations without network dependency, aligned with Karpinsky Institute and SGS methodology."
    ],
    "capabilities": [
      {
        "group": "Igneous Petrology",
        "items": [
          "Streckeisen QAPF double triangle for plutonic and volcanic rocks incorporating color index M'.",
          "4 ternary diagrams Ol-Opx-Cpx, Ol-Px-Hbl, Plag-Px-Ol, Plag-Opx-Cpx for ultramafic and mafic rocks.",
          "Interactive dichotomous flow chart based on macroscopic field diagnostic criteria.",
          "Illustrated rock catalog featuring search filters, diagnostic criteria, and petrographic formulas."
        ]
      },
      {
        "group": "Structural Geology & Kinematics",
        "items": [
          "Automated conversion between dip direction and Right-Hand Rule (RHR) strike.",
          "Calculation of theoretical lineation plunge and spherical tolerance verification (5 deg or 8 deg).",
          "Calculation of rake / pitch angle and automated deduction of slip mechanism: strike-slip, normal, reverse, oblique.",
          "3D visualization of fault-plane geometry and slip vectors."
        ]
      },
      {
        "group": "Schmidt Stereographic Projection",
        "items": [
          "Lower-hemisphere equal-area Schmidt stereonet rendered with Bezier curves.",
          "Dynamic plotting of great circle arcs, pole points, and rake markers.",
          "Kinematic intersections of intersecting planes (beta-axes) and dihedral angle computation.",
          "Fold analysis mode: simultaneous projection of axial surfaces, fold limbs, hinges, and lineations."
        ]
      },
      {
        "group": "Fault Rocks",
        "items": [
          "Sibson-Wise fault rock classification matrix based on cohesion, matrix percentage, and foliation: cataclasites, mylonites, phyllonites, pseudotachylytes."
        ]
      },
      {
        "group": "Sedimentary & Metamorphic Petrology",
        "items": [
          "Sandstone framework classification on Pettijohn ternary diagram (Q-F-R) with matrix proportion assessment.",
          "Carbonate rocks classified according to Dunham structural-genetic schema (mudstone to boundstone).",
          "Pyroclastic rocks: blocks/bombs - lapilli - ash ternary diagram.",
          "Classifiers for foliated (slates, phyllites, schists, gneisses) and non-foliated metamorphic rocks (quartzites, marbles, skarns, eclogites)."
        ]
      }
    ],
    "stack": "Kotlin Multiplatform (:shared core), Android (Material Design 3, Jetpack Compose), iOS (SwiftUI, NavigationSplitView), Spherical Trigonometry Engine",
    "specVersion": "3.0 (KMP Multiplatform Architecture & Extended Petrology Suite)",
    "diagram": "stereonet",
    "pending": [
      "Final iOS client distribution build via TestFlight.",
      "Field calibration benchmark results against Karpinsky Institute and SGS datasets.",
      "Author contribution: mathematical models, KMP system architecture, and UI/UX design."
    ],
    "publicationState": "published",
    "productStatus": "prototype",
    "evidence": { "source": "specification", "reference": "materials/design.md, sections 1, 2, 3, and 5", "verified": True }
  },
  {
    "id": "vba-log-check",
    "kind": "practice",
    "order": 10,
    "title": "Field Observation Log Validator",
    "area": "VBA & Excel, GMAS Project",
    "summary": "VBA scripts validate geological field observation logs against standardized project lexicons, ensuring multi-team dataset consistency.",
    "publicationState": "published",
    "productStatus": "in-use",
    "evidence": { "source": "cv", "reference": "CV Geologist Pakhalko ENG 2026.docx: validation of geological observation logs against project lexicons", "verified": False }
  },
  {
    "id": "android-gmas",
    "kind": "practice",
    "order": 11,
    "title": "Android Application for Field Data",
    "area": "Kotlin & Android, GMAS Project",
    "summary": "Native Android application compliant with GMAS technical guidelines: mobile field data collection with embedded QA/QC validation checks.",
    "publicationState": "published",
    "productStatus": "unverified",
    "evidence": { "source": "cv", "reference": "CV 2026: designed and developed native Android application based on GMAS guidelines", "verified": False }
  }
]

experience_en = [
  {
    "id": "gmas",
    "order": 1,
    "period": "2025 - present",
    "place": "Saudi Arabia",
    "short": "Arabian Shield",
    "pattern": "granite",
    "title": "Arabian Shield Geological Mapping",
    "organization": "GMAS Project, Karpinsky Institute",
    "role": "Field Party Leader, Field Geologist",
    "summary": "1:100,000-scale geological mapping. I lead the field party and ensure field data quality and integrity across field teams.",
    "highlights": [
      "Conducted lithological, structural, and metallogenic observations along traverses, measured planar and linear attitudes, and organized systematic sampling.",
      "Planned traverse routes, assigned field crew tasks, validated observations, and trained personnel in digital geological tools.",
      "Authored VBA scripts for Excel to validate observation logs against project dictionaries, ensuring multi-party data consistency.",
      "Designed and built a native Android application in Kotlin compliant with GMAS guidelines: mobile field data entry with embedded QA/QC checks.",
      "Conducted spatial analysis in ArcGIS, integrating field-team observations with formal reporting deliverables."
    ],
    "materials": [
      "Certificate of Appreciation from the Karpinsky Institute to key project contributors, April 3, 2026.",
      "Professional Accreditation as Geologist in Saudi Arabia, 2026."
    ],
    "photoNote": "Month and year are derived from file metadata. Uncompressed messaging copies lack embedded capture timestamps.",
    "photos": [
      { "slug": "gmas-tablet", "source": "photo/Saudi/photo_2026-09-23_07-05-14.jpg", "alt": "Geologist in a wide-brimmed hat reviews data on a rugged field tablet near a rocky slope with an off-road vehicle behind", "caption": "Fieldwork on granite outcrops, map sheet 3922-1 As Sulaym, Saudi Arabia" },
      { "slug": "gmas-maps", "source": "photo/Saudi/photo_2026-09-23_06-39-50.jpg", "alt": "Four geologists discuss geological maps mounted on a field office wall", "caption": "Traverse and geological planning, map sheet 3824-4 Jabal Radwa, Saudi Arabia" },
      { "slug": "gmas-umbrella", "source": "photo/Saudi/photo_2026-09-23_07-05-45.jpg", "alt": "Four geologists walk across a rocky desert plain, one holding a sun umbrella", "caption": "Field reconnaissance traverse, map sheet 3922-1 As Sulaym, Saudi Arabia" },
      { "slug": "gmas-roadside", "source": "photo/Saudi/photo_2026-09-23_07-09-25.jpg", "alt": "Three geologists in field hats stand by a desert roadside", "caption": "Joint traverse with project managers Ashraf Al-Qubsani and Ji Wenhua, Saudi Arabia" },
      { "slug": "gmas-mountains", "source": "photo/Saudi/IMG_20250824_073702.jpg", "date": "2025-08", "alt": "Man in a blue hoodie against the backdrop of rugged mountain ranges", "caption": "Mountainous topography near Bilasmar, Western Escarpment, Saudi Arabia" },
      { "slug": "gmas-hat", "source": "photo/Saudi/IMG_20250416_080107.jpg", "date": "2025-04", "alt": "Man in a wide-brimmed hat by a rock outcrop gives a thumbs-up gesture", "caption": "Typical traverse during a dust storm, Saudi Arabia" },
      { "slug": "gmas-vehicle", "source": "photo/Saudi/IMG_20250411_112731.jpg", "date": "2025-04", "alt": "Man stands beside an expedition pickup truck on an urban street", "caption": "The GMAS project workhorse, Saudi Arabia" }
    ],
    "publicationState": "published",
    "evidence": [
      { "source": "cv", "reference": "CV Geologist Pakhalko RUS/ENG 2026.docx; CV_Pakhalko_Chief_Geologist_2026_EN.docx, work experience", "verified": False },
      { "source": "document", "reference": "certificate/photo_2026-09-23_06-44-25.jpg, Karpinsky Institute appreciation of 03.04.2026; certificate/QVP 2026.pdf", "verified": True },
      { "source": "photo-folder", "reference": "photo/Saudi", "verified": True }
    ]
  },
  {
    "id": "vsegei",
    "order": 2,
    "period": "2012 - present",
    "place": "Saint Petersburg",
    "short": "Karpinsky Institute",
    "pattern": "shale",
    "title": "Karpinsky Institute",
    "organization": "Karpinsky Institute (VSEGEI)",
    "role": "Lead Engineer / Thematic Project Manager",
    "summary": "Metallogenic analysis of Asian ore belts, petrographic and isotopic research, GIS compilation, and international collaboration.",
    "highlights": [
      "Participated in the international project 'Metallogenic Map of Northern, Central, and Eastern Asia at 1:2,500,000 scale': GIS integration, ore deposit database, and metallogenic analysis.",
      "Delivered presentations on metallogeny in Ulaanbaatar (Mongolia, 2019) and Jeju (South Korea, 2018).",
      "Co-authored publications on the geodynamics of the Arctic Ocean (Journal of Geodynamics, 2019) and the basement of the Trans-Urals (2022).",
      "Completed international field excursions: ancient Archean granites of Baijianfen (~3.8 Ga) and mineral deposits of China."
    ],
    "photoNote": "Mongolia, 2019: conference talk, field traverses, and delegates meeting in Ulaanbaatar. China: field trips in 2014 and 2017. Presentation slide decks are available in the Credentials section.",
    "photos": [
      { "slug": "vsegei-talk-mongolia", "source": "photo/IMG_8887.JPG", "date": "2019-08", "alt": "Alexey speaking at the conference lectern beside a slide explaining metallogenic analysis methods", "caption": "Presentation on the Metallogenic Map of Asia: methodology for analyzing spatio-temporal distribution of SEDEX, MVT, porphyry, and epithermal deposits. Ulaanbaatar, Mongolia" },
      { "slug": "mongolia-meeting", "source": "photo/mongolia/DSC_0568_2019_17-е УланБатор.JPG", "date": "2019", "alt": "Group photo of dozens of international conference delegates at the hotel entrance", "caption": "Participants of the international working session in Ulaanbaatar, Mongolia." },
      { "slug": "mongolia-steppe", "source": "photo/mongolia/IMG-20190809-WA0020.jpg", "date": "2019-08", "alt": "Three geologists walk across open steppe with an expedition vehicle in the distance", "caption": "Investigation of gold occurrences in the Ikh-Khairkhan area, Mongolia" },
      { "slug": "mongolia-site", "source": "photo/mongolia/IMG-20190809-WA0023.jpg", "date": "2019-08", "alt": "Group of geologists in hard hats at an industrial mining platform near a hillside", "caption": "Field excursion to a chromite mine, Mongolia" },
      { "slug": "mongolia-outcrop", "source": "photo/mongolia/gLpKhOfy0Ae323aM5KAsqUiGzWjfCLvTVzTd6Hg2y4Ms7c3B7oqpbUFd_RrOMu96z9tYKqYOXSkoU94EHtlDNL8b.jpg", "alt": "Two geologists scramble up a steep rocky outcrop, one holding an umbrella", "caption": "Rocky outcrop, Mongolia" },
      { "slug": "china-baijianfen", "source": "photo/china/00060_Baijianfen-гранит-3.8млрд лет-Wang Yusheng.JPG", "date": "2017-10", "alt": "Four geologists examine a rock outcrop on a vegetated hillside", "caption": "Ancient Baijianfen granites, approximately 3.8 Ga, China" },
      { "slug": "china-granite-block", "source": "photo/china/_DSC0530.JPG", "date": "2014-02", "alt": "Man in a winter jacket stands next to a large quarried granite block showing blast-hole traces", "caption": "Granite quarry block with drill-hole traces, China" }
    ],
    "publicationState": "published",
    "evidence": [
      { "source": "cv", "reference": "CV Geologist Pakhalko RUS/ENG 2026.docx, work experience", "verified": False },
      { "source": "presentation", "reference": "materials/2019-Mongolia, Pakhalko A.pptx; materials/2018-Korea,Jeju Pakhalko A.pptx", "verified": True },
      { "source": "photo-folder", "reference": "photo/mongolia; photo/china", "verified": True }
    ]
  },
  {
    "id": "field-practice",
    "order": 3,
    "period": "2015-2025",
    "place": "Saint Petersburg, Arkhangelsk",
    "short": "Geological Field Practice",
    "pattern": "sand",
    "title": "Geological Field Training & Practice",
    "organization": "Saint Petersburg Mining University",
    "role": "Instructor / Field Training Assistant",
    "summary": "Training students in field geological methods: mapping, compass traverse navigation, lithological logging, and structural measurements.",
    "highlights": [
      "Taught field mapping techniques, compass navigation, and structural attitude measurements for Mining University undergraduate students.",
      "Supervised field traverses on Precambrian crystalline rocks of the Baltic Shield (Karelia) and Phanerozoic sedimentary strata (Leningrad region).",
      "Conducted a master class and lecture on the geological compass at the All-Russian Youth Geological Festival (GeolFest 2025 in Arkhangelsk)."
    ],
    "pending": ["Role in student practice and supervising department."],
    "photos": [
      { "slug": "practice-route", "source": "photo/geo practice mining institute/2022.06.15028 Геологические маршруты (78).jpg", "date": "2022-06", "alt": "Group of students studies porphyritic rapakivi granite outcrops above a lake surrounded by pine trees", "caption": "Study of porphyritic rapakivi granites near Monrepos Park, Vyborg, Karelia." },
      { "slug": "practice-bridge", "source": "photo/geo practice mining institute/a4hMAkXo7m802tWI65i5v7Q5LJPiMlOkf7gXTOOP-nnypPZWN4NxgtH1lsZGc70EpYUX7tDv66E8T3V7GwRH4aXQ.jpg", "alt": "Group of students with backpacks descends a metal staircase toward a river to inspect Phanerozoic sedimentary rocks", "caption": "Investigation of Phanerozoic sedimentary rock exposures near Sablino station, Leningrad region." },
      { "slug": "practice-geolfest", "source": "photo/geo practice mining institute/Геофест1день17.jpg", "date": "2025-09", "alt": "Alexey speaks with a microphone at GeolFest before a presentation slide on the geological compass", "caption": "Lecture on the geological compass at GeolFest, 2025" }
    ],
    "photoNote": "Photographs from student field practice and GeolFest are dated by file metadata (2022 and 2025).",
    "publicationState": "published",
    "evidence": [
      { "source": "cv", "reference": "CV Geologist Pakhalko RUS/ENG 2026.docx, work experience", "verified": False },
      { "source": "presentation", "reference": "materials/Gornyj-kompas-principy-primeneniya-v-geologii.pptx", "verified": True },
      { "source": "photo-folder", "reference": "photo/geo practice mining institute", "verified": True }
    ]
  },
  {
    "id": "china",
    "order": 4,
    "period": "2011-2012",
    "place": "China",
    "short": "China",
    "pattern": "basalt",
    "title": "Traverses and Mining Operations in China",
    "organization": "Field traverses, mining operations, and professional exchange",
    "role": "Field Geologist, Geological Translator",
    "summary": "Field trips to major ore deposits, underground mine inspections, and technical translation of geological literature.",
    "highlights": [
      "Inspected underground workings and geological structure of the Linglong gold deposit, Shandong province.",
      "Participated in geological field excursions to the giant Panzhihua vanadium-titanomagnetite deposit, Sichuan province.",
      "Translated geological and mining technical papers between Russian and English.",
      "Passed the HSK Level 3 Chinese Language Proficiency examination (2018)."
    ],
    "photoNote": "Panzhihua photo is dated November 2011 from file metadata. Second photo lacks embedded timestamp. 2014 and 2017 visits are documented under the Karpinsky Institute stage.",
    "photos": [
      { "slug": "china-emeishan", "source": "photo/emeishan/P1000295.JPG", "date": "2011-11", "alt": "Alexey beside an inscribed stone monument during a field excursion to the Panzhihua iron-titanium deposit", "caption": "Field excursion to the Panzhihua iron-titanium deposit, China" },
      { "slug": "china-gear", "source": "photo/china/fkardYVw7vW9Lo47hPmOxlAp0aQCSor0cF4Hj7DYDoUHWtD2CIYPMNDXW9isQIXUVGTblaHo.jpg", "alt": "Alexey in red protective overalls and hard hat prepared for descent into the underground mine at the Linglong deposit", "caption": "Preparation for descent into the underground mine at the Linglong deposit, China." }
    ],
    "publicationState": "published",
    "evidence": [
      { "source": "legacy-cv", "reference": "2012 CV: China trip, November 2011; 2018 HSK 3 certificate", "verified": False },
      { "source": "photo-folder", "reference": "photo/emeishan; photo/china", "verified": True }
    ]
  },
  {
    "id": "gold-core",
    "order": 5,
    "period": "2010-2011",
    "place": "Magadan Region, Buryatia",
    "short": "Pavlik, Zun-Kholba",
    "pattern": "quartz",
    "title": "Gold of Pavlik and Zun-Kholba",
    "organization": "CJSC RJC Group",
    "role": "Geologist",
    "summary": "Core logging and geological quality control for exploration drilling on primary gold deposits.",
    "highlights": [
      "Logged drill core and delineated gold-bearing ore intervals.",
      "Conducted mineralogical observations and gold sampling in accordance with strict QA/QC standards for primary exploration data.",
      "Prepared accompanying technical drill-hole documentation and cross-sections."
    ],
    "photoNote": "Underground workings at the Zun-Kholba deposit. First photo dated by file metadata; second photo lacks embedded timestamp.",
    "photos": [
      { "slug": "zunkholba-gallery", "source": "photo/zun-holba/Изображение2 236.jpg", "date": "2010-12", "alt": "Geologist in hard hat and protective gear stands in an illuminated underground mine gallery", "caption": "Work in the underground mine at the Zun-Kholba deposit, Republic of Buryatia" },
      { "slug": "zunkholba-team", "source": "photo/zun-holba/w_533e30c9.jpg", "alt": "Three geologists in hard hats with headlamps underground", "caption": "Joint geological investigations in the underground workings with chief mine geologists at the Zun-Kholba deposit, Republic of Buryatia." }
    ],
    "publicationState": "published",
    "evidence": [
      { "source": "cv", "reference": "2026 CV, work experience", "verified": False },
      { "source": "legacy-cv", "reference": "2011 and 2012 CVs: RJC-group, November 2010 - April 2011", "verified": False },
      { "source": "photo-folder", "reference": "photo/zun-holba", "verified": True }
    ]
  },
  {
    "id": "monchegorsk",
    "order": 6,
    "period": "2009-2013",
    "place": "Kola Peninsula",
    "short": "Monchegorsk Pluton",
    "pattern": "gabbro",
    "title": "Monchegorsk Layered Pluton",
    "organization": "Geological Institute of KSC RAS (2009), followed by independent research",
    "role": "Geological Technician, Field Geologist",
    "summary": "Mapping and petrographic study of platinum-group element (PGE) mineralization in a layered mafic-ultramafic intrusion.",
    "highlights": [
      "2009: Russian-Chinese field excursion on PGE-bearing targets of the Monchegorsk pluton. Conducted traverse observations, collected rock and ore samples, sketched outcrops, and drafted local geological maps.",
      "2010: Defended engineering diploma thesis with honors on exploration for platinum-metal mineralization within the Plast-330 reef area of Mt. Sopcha.",
      "Detailed geological mapping, traverse planning, petrographic thin-section preparation, and geochemical assay interpretation.",
      "Vuruchuaivench massif (with S. V. Kashin): determined that ore-bearing rocks are invariably metasomatized, but not all metasomatites carry ore. Identified metasomatic stages: chlorite-zoisite propylitization, two stages of amphibolization, and quartz-sericite alteration. PGE minerals (palladoarsenide, sperrylite, kotulskite) and electrum are closely associated with sulfides. Published conference presentation in 2019, journal article in 2022."
    ],
    "photoNote": "2009 field season. Month is noted where present in file metadata. Thin sections and geological sketches are featured in the 2019 presentation in the Credentials section.",
    "photos": [
      { "slug": "monche-map", "source": "photo/monchegorsk/P1010455.JPG", "date": "2009", "alt": "Three geologists examine a field map laid out on rocks in open boreal woodland", "caption": "Reviewing the geological map of the Moroshkovoe ore occurrence, Monchegorsk pluton." },
      { "slug": "monche-sampling", "source": "photo/monchegorsk/P1010449.JPG", "date": "2009", "alt": "Geologist in a hooded jacket crouches with a rock hammer at a light-colored rock outcrop", "caption": "Sample collection for analysis at the Moroshkovoe ore occurrence, Monchegorsk pluton." },
      { "slug": "monche-boulders", "source": "photo/monchegorsk/P7240628.JPG", "date": "2009-07", "alt": "Geologist with a rock hammer stands on dark boulder scree with a lake and mountain behind", "caption": "Detailing the stratigraphic section of the Plast-330 platinum-metal target, Mt. Sopcha, Monchegorsk pluton." },
      { "slug": "monche-group", "source": "photo/monchegorsk/IMG_2189.JPG", "date": "2009-07", "alt": "Five young geologists rest on a rocky outcrop against a mountain panorama", "caption": "Team of geologists at the Plast-330 platinum-metal target, Mt. Sopcha, Monchegorsk pluton." }
    ],
    "publicationState": "published",
    "evidence": [
      { "source": "cv", "reference": "2026 CV, additional field experience", "verified": False },
      { "source": "legacy-cv", "reference": "2011 and 2012 CVs: Geological Institute of KSC RAS, June - August 2009; diploma topic", "verified": False },
      { "source": "presentation", "reference": "materials/Pakhalko Herlany 2019.pptx, slides 6, 8, 13-18", "verified": True },
      { "source": "photo-folder", "reference": "photo/monchegorsk", "verified": True }
    ]
  },
  {
    "id": "kichany",
    "order": 7,
    "period": "2008",
    "place": "Karelia",
    "short": "Kichany",
    "pattern": "gneiss",
    "title": "Uranium of the Kichany Target",
    "organization": "Karpinsky Institute (VSEGEI), Russian-French joint expedition",
    "role": "Category 1 Geologist",
    "summary": "Exploration for unconformity-related and vein uranium mineralization in Karelia.",
    "highlights": [
      "Detailed geological mapping and ground verification of radiometric uranium anomalies.",
      "Traverse navigation, radiometric surveying, systematic sample collection, and local geological schematic drafting.",
      "Communicated and collaborated in English with French expedition geologists."
    ],
    "publicationState": "published",
    "evidence": [
      { "source": "cv", "reference": "2026 CV, additional field experience", "verified": False },
      { "source": "legacy-cv", "reference": "2011 and 2012 CVs: Karpinsky Institute (VSEGEI), June - August 2008; English communication with French geologists", "verified": False }
    ]
  }
]

credentials_en = [
  {
    "id": "vsegei-gratitude-2026",
    "kind": "award",
    "title": "Certificate of Appreciation for Organizing and Executing Geological Mapping in the Project 'Detailed Geological Mapping of the Arabian Shield, 1:100,000 Scale Maps'",
    "organization": "Karpinsky Institute, team of principal contributors",
    "year": "2026",
    "detail": "April 3, 2026.",
    "publicationState": "published",
    "evidence": { "source": "document", "reference": "certificate/photo_2026-09-23_06-44-25.jpg, 03.04.2026", "verified": True }
  },
  {
    "id": "saudi-professional-accreditation",
    "kind": "award",
    "title": "Professional Accreditation as Geologist",
    "organization": "Ministry of Human Resources and Social Development, Kingdom of Saudi Arabia",
    "year": "2026",
    "detail": "Professional qualification verified and accredited in accordance with national industry standards.",
    "publicationState": "published",
    "evidence": { "source": "document", "reference": "certificate/QVP 2026.pdf", "verified": True }
  },
  {
    "id": "mnr-gratitude",
    "kind": "award",
    "title": "Certificate of Appreciation, Ministry of Natural Resources of the Russian Federation",
    "organization": "From CV; document and year unverified",
    "year": "",
    "publicationState": "draft",
    "evidence": { "source": "cv", "reference": "CV_Pakhalko_Chief_Geologist_2026_EN.docx, certifications and recognition", "verified": False }
  },
  {
    "id": "gmas-digital-recognition",
    "kind": "award",
    "title": "Recognition for Digital Workflow Innovation within GMAS Field Operations",
    "organization": "From CV; document unverified",
    "year": "2025",
    "publicationState": "draft",
    "evidence": { "source": "cv", "reference": "CV 2026, awards and recognition", "verified": False }
  },
  {
    "id": "gmas-internal-training",
    "kind": "certificate",
    "title": "Internal GMAS Training: Field Data Standards and Digital Workflow Protocols",
    "organization": "GMAS Project; document unverified",
    "year": "",
    "publicationState": "draft",
    "evidence": { "source": "cv", "reference": "CV_Pakhalko_Chief_Geologist_2026_EN.docx, certifications and recognition", "verified": False }
  },
  {
    "id": "yandex-qa",
    "kind": "certificate",
    "title": "QA Engineer Professional Retraining (250 hours)",
    "organization": "Yandex Practicum",
    "year": "2023",
    "detail": "Test analysis and design, web/mobile application and API testing, database foundations and test automation, capstone project.",
    "publicationState": "published",
    "evidence": { "source": "document", "reference": "certificate/Яндекс Инженер по тестированию 2023 (1), (2).jpg; diploma dated 18.03.2023", "verified": True }
  },
  {
    "id": "hsk-3",
    "kind": "certificate",
    "title": "HSK Level 3, Chinese Language Proficiency Certificate",
    "organization": "Confucius Institute Headquarters (Hanban), Beijing",
    "year": "2018",
    "publicationState": "published",
    "evidence": { "source": "document", "reference": "certificate/HSK-3 2018.jpg, exam date 18.02.2018", "verified": True }
  },
  {
    "id": "esri-geodatabases",
    "kind": "certificate",
    "title": "Geodatabases Course",
    "organization": "GIS Centre, Karpinsky Institute (VSEGEI) on behalf of Esri",
    "year": "2015",
    "publicationState": "published",
    "evidence": { "source": "document", "reference": "certificate/КПК Алексей(2).jpg, 08.04.2015", "verified": True }
  },
  {
    "id": "esri-arcgis-desktop",
    "kind": "certificate",
    "title": "ArcGIS Desktop 10 Course, Parts I, II, and III",
    "organization": "GIS Centre, Karpinsky Institute (VSEGEI) on behalf of Esri",
    "year": "2015",
    "publicationState": "published",
    "evidence": { "source": "document", "reference": "certificate/КПК Алексей(1).jpg, 31.03.2015", "verified": True }
  },
  {
    "id": "mining-engineer",
    "kind": "education",
    "title": "Mining Engineer Diploma, Specialization: Applied Geochemistry, Petrology, Mineralogy",
    "organization": "Saint Petersburg State Mining Institute named after G.V. Plekhanov (Mining University)",
    "year": "2010",
    "detail": "Diploma thesis on exploration for platinum-metal mineralization within the Plast-330 reef area of the Monchegorsk pluton, defended with honors (A grade).",
    "publicationState": "published",
    "evidence": { "source": "document", "reference": "certificate/Диплом Горный 2010 (1).jpg; diploma topic from 2011 and 2012 CVs", "verified": True }
  },
  {
    "id": "postgraduate",
    "kind": "education",
    "title": "Postgraduate Studies in Geology",
    "organization": "Karpinsky Institute (VSEGEI)",
    "year": "2010-2014",
    "detail": "Geological surveying, prospecting and exploration of mineral deposits, minerageny.",
    "publicationState": "published",
    "evidence": { "source": "cv", "reference": "CV 2026, education", "verified": False }
  },
  {
    "id": "paper-vuruchuaivench-2022",
    "kind": "publication",
    "title": "Metasomatic assemblages of mafic rocks in the Vuruchuaivench massif, Monchegorsk pluton",
    "authors": "Pahalko A. G., Kashin S. V.",
    "organization": "Regional Geology and Metallogeny, no. 90, pp. 15-25",
    "year": "2022",
    "url": "https://doi.org/10.52349/0869-7892_2022_90_15-25",
    "publicationState": "published",
    "evidence": { "source": "cv", "reference": "CV 2026, publications", "verified": False }
  },
  {
    "id": "paper-trans-urals-2022",
    "kind": "publication",
    "title": "Features of the geological structure of the basement of the Trans-Urals and the age of the rhyolites of the Turin series",
    "authors": "Bochkarev V. S., Ivanov K. S., Pahalko A. G., Sergeev S. A.",
    "organization": "Uralian Geological Journal, no. 6, pp. 55-74",
    "year": "2022",
    "publicationState": "published",
    "evidence": { "source": "cv", "reference": "CV 2026, publications", "verified": False }
  },
  {
    "id": "paper-lomonosov-2019",
    "kind": "publication",
    "title": "Basement segmentation and tectonic structure of the Lomonosov Ridge, Arctic Ocean: Insights from bedrock geochronology",
    "authors": "Rekant P., Sobolev N., Portnov A., Belyatsky B., Dipre G., Pakhalko A., Kaban’kov V., Andreeva I.",
    "organization": "Journal of Geodynamics, vol. 128, pp. 38-54",
    "year": "2019",
    "url": "https://doi.org/10.1016/j.jog.2019.05.001",
    "publicationState": "published",
    "evidence": { "source": "cv", "reference": "CV Geologist Pakhalko ENG 2026.docx, publications", "verified": False }
  },
  {
    "id": "talk-compass-2025",
    "kind": "talk",
    "title": "The Geological Compass: Principles and Field Application in Geology",
    "organization": "Educational Workshop Presentation",
    "place": "GeolFest, Arkhangelsk",
    "year": "2025",
    "detail": "All-Russian Youth Geological Festival: master class on geological compass operations, strike and dip measurements, and traverse navigation.",
    "file": "/talks/2025-mining-compass.pdf",
    "publicationState": "published",
    "evidence": { "source": "presentation", "reference": "materials/Gornyj-kompas-principy-primeneniya-v-geologii.pptx", "verified": True }
  },
  {
    "id": "talk-stone-2022",
    "kind": "talk",
    "title": "Natural Stone in the Architecture of Saint Petersburg",
    "organization": "Popular Science Lecture",
    "place": "Karpinsky Institute (VSEGEI), Saint Petersburg",
    "year": "2022",
    "detail": "Dimension and decorative stones in urban facades, architectural styles, and weathering preservation of stone monuments.",
    "file": "/talks/2022-stone-in-architecture.pdf",
    "publicationState": "published",
    "evidence": { "source": "presentation", "reference": "materials/Презентация Камень в архитектуре.pptx", "verified": True }
  },
  {
    "id": "talk-vuruchuaivench-2019",
    "kind": "talk",
    "title": "The role of metasomatism in PGE-bearing rocks formation of the Vuruchuaivench massif, Monchegorsk Complex (Kola Peninsula, Russia)",
    "authors": "Pakhalko A., Kashin S.",
    "organization": "Presentation on behalf of Karpinsky Institute (VSEGEI)",
    "year": "2019",
    "file": "/talks/2019-herlany-vuruchuaivench.pdf",
    "publicationState": "published",
    "evidence": { "source": "presentation", "reference": "materials/Pakhalko Herlany 2019.pptx", "verified": True }
  },
  {
    "id": "talk-metallogenic-map-2019",
    "kind": "talk",
    "title": "General results of work on Metallogenic map of Northern, Central, and Eastern Asia",
    "authors": "Pakhalko A. G., Pinsky E. M., Shatkov G. A.",
    "organization": "Conference Presentation",
    "place": "Mongolia",
    "year": "2019",
    "file": "/talks/2019-mongolia-metallogenic-map.pdf",
    "publicationState": "published",
    "evidence": { "source": "presentation", "reference": "materials/2019-Mongolia, Pakhalko A.pptx", "verified": True }
  },
  {
    "id": "talk-metallogenic-evolution-2018",
    "kind": "talk",
    "title": "Metallogenic evolution of Northern, Central, and Eastern Asia",
    "authors": "Pakhalko A. G., Shatkov G. A., Pinsky E. M., Chen Tingyu, Babin G. A., Kuznetsov V. A., Kutyreva M. E.",
    "organization": "Conference Presentation",
    "place": "Jeju, Republic of Korea",
    "year": "2018",
    "file": "/talks/2018-jeju-metallogenic-evolution.pdf",
    "publicationState": "published",
    "evidence": { "source": "presentation", "reference": "materials/2018-Korea,Jeju Pakhalko A.pptx", "verified": True }
  },
  {
    "id": "talk-norilsk-2014",
    "kind": "talk",
    "title": "Sulfur isotopic features of sulfide ores in mafic intrusions of Norilsk region",
    "authors": "Pakhalko A. G.",
    "organization": "Presentation on behalf of Karpinsky Institute (VSEGEI)",
    "year": "2014",
    "detail": "Ore-bearing intrusions exhibit delta 34S of 11-12 permil, while weakly mineralized intrusions show 5-7 permil.",
    "file": "/talks/2014-norilsk-sulfur-isotopes.pdf",
    "publicationState": "published",
    "evidence": { "source": "presentation", "reference": "materials/Sulfur isotopic features of sulfide ores in mafic.pptx", "verified": True }
  }
]


def main():
    check_no_dashes(apps_en, "apps_en")
    check_no_dashes(experience_en, "experience_en")
    check_no_dashes(credentials_en, "credentials_en")

    with open(CONTENT / "apps.en.json", "w", encoding="utf-8") as f:
        json.dump(apps_en, f, ensure_ascii=False, indent=2)

    with open(CONTENT / "experience.en.json", "w", encoding="utf-8") as f:
        json.dump(experience_en, f, ensure_ascii=False, indent=2)

    with open(CONTENT / "credentials.en.json", "w", encoding="utf-8") as f:
        json.dump(credentials_en, f, ensure_ascii=False, indent=2)

    print("SUCCESS: Written apps.en.json, experience.en.json, credentials.en.json")


if __name__ == "__main__":
    main()
