import fs from 'node:fs';

fs.mkdirSync('src/pages/en/presentations', { recursive: true });

// 1. field.astro
let field = fs.readFileSync('src/pages/ru/presentations/field.astro', 'utf8');

field = field.replace('<html lang="ru">', '<html lang="en">');
field = field.replace('<title>Rocksurv Field — интерактивная презентация приложения</title>', '<title>Rocksurv Field - Interactive App Presentation</title>');
field = field.replace(
  '<meta name="description" content="Интерактивная презентация Rocksurv Field: офлайн-карта GeoPackage, замеры структур, полевой журнал, DEM и экспорт сессий.">',
  '<meta name="description" content="Interactive presentation of Rocksurv Field: GeoPackage offline maps, structural measurements, field log, DEM and session export.">'
);
field = field.replace('href="/ru/#apps"', 'href="/en/#apps"');
field = field.replace('<span>Назад к резюме</span>', '<span>Back to CV</span>');
field = field.replace('<span class="pres-chip">12 слайдов</span>', '<span class="pres-chip">12 slides</span>');
field = field.replace('aria-label="Язык презентации"', 'aria-label="Presentation language"');
field = field.replace(
  '<button class="lang-btn active" id="btn-lang-ru" data-lang="ru">RU</button>\n        <button class="lang-btn" id="btn-lang-en" data-lang="en">EN</button>',
  '<button class="lang-btn" id="btn-lang-ru" data-lang="ru">RU</button>\n        <button class="lang-btn active" id="btn-lang-en" data-lang="en">EN</button>'
);
field = field.replace('title="На весь экран (F)"', 'title="Full screen (F)"');
field = field.replace('title="Печать / PDF (P)"', 'title="Print / PDF (P)"');
field = field.replace('aria-label="Управление слайдами"', 'aria-label="Slide controls"');
field = field.replace('aria-label="Предыдущий слайд"', 'aria-label="Previous slide"');
field = field.replace('aria-label="Следующий слайд"', 'aria-label="Next slide"');
field = field.replace('<span class="keys-hint">← → или Пробел · F весь экран</span>', '<span class="keys-hint">← → or Space · F full screen</span>');

// Switch default active deck
field = field.replace('<div class="deck active-deck" id="deck-ru">', '<div class="deck" id="deck-ru">');
field = field.replace('<div class="deck" id="deck-en">', '<div class="deck active-deck" id="deck-en">');

// Switch default script lang
field = field.replace("let currentLang = 'ru';", "let currentLang = 'en';");
field = field.replace(
  "if (urlParams.get('lang') === 'en') {\n      setLang('en');\n    }",
  "if (urlParams.get('lang') === 'ru') {\n      setLang('ru');\n    }"
);
field = field.replace("window.location.href = '/ru/#apps';", "window.location.href = '/en/#apps';");

fs.writeFileSync('src/pages/en/presentations/field.astro', field, 'utf8');

// 2. classifier.astro
let classifier = fs.readFileSync('src/pages/ru/presentations/classifier.astro', 'utf8');

classifier = classifier.replace('<html lang="ru">', '<html lang="en">');
classifier = classifier.replace('<title>Rocksurv Classifier — интерактивная презентация приложения</title>', '<title>Rocksurv Classifier - Interactive App Presentation</title>');
classifier = classifier.replace(
  '<meta name="description" content="Интерактивная презентация Rocksurv Classifier: стереонет Шмидта, двойной треугольник QAPF Штрекайзена, расчёт параметров и контроль ошибок.">',
  '<meta name="description" content="Interactive presentation of Rocksurv Classifier: Schmidt stereonet, IUGS Streckeisen QAPF double triangle, parameter calculation and error prevention.">'
);
classifier = classifier.replace('href="/ru/#apps"', 'href="/en/#apps"');
classifier = classifier.replace('<span>Назад к резюме</span>', '<span>Back to CV</span>');
classifier = classifier.replace('<span class="pres-chip">10 слайдов · Карусели</span>', '<span class="pres-chip">10 slides · Carousels</span>');
classifier = classifier.replace('title="На весь экран (F)"', 'title="Full screen (F)"');
classifier = classifier.replace('title="Печать / PDF (P)"', 'title="Print / PDF (P)"');
classifier = classifier.replace('aria-label="Управление слайдами"', 'aria-label="Slide controls"');
classifier = classifier.replace('aria-label="Предыдущий слайд"', 'aria-label="Previous slide"');
classifier = classifier.replace('aria-label="Следующий слайд"', 'aria-label="Next slide"');
classifier = classifier.replace('<span class="keys-hint">← → или Пробел · F весь экран</span>', '<span class="keys-hint">← → or Space · F full screen</span>');
classifier = classifier.replace("window.location.href = '/ru/#apps';", "window.location.href = '/en/#apps';");

fs.writeFileSync('src/pages/en/presentations/classifier.astro', classifier, 'utf8');

console.log('Generated src/pages/en/presentations/field.astro and classifier.astro');
