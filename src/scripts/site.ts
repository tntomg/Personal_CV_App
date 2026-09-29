/*
  Page-level behaviour: scroll reveals, header state, section and stratigraphic-column highlighting,
  and the header switching to night while it sits over the applications block.
  Everything uses IntersectionObserver; there are no window scroll listeners.
*/
import './gallery';

const header = document.querySelector<HTMLElement>('[data-header]');
const hasIO = 'IntersectionObserver' in window;

// Reveals. Content is visible by default; the hidden start state exists only under html.js (see global.css).
const revealables = document.querySelectorAll<HTMLElement>('[data-reveal]');
if (hasIO) {
  const reveal = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        reveal.unobserve(entry.target);
      });
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.12 },
  );
  revealables.forEach((node) => reveal.observe(node));
} else {
  revealables.forEach((node) => node.classList.add('is-visible'));
}

if (header && hasIO) {
  // Hairline under the header once the page has moved.
  const sentinel = document.createElement('div');
  sentinel.setAttribute('aria-hidden', 'true');
  sentinel.style.cssText = 'position:absolute;top:0;left:0;width:1px;height:8px;pointer-events:none';
  document.body.prepend(sentinel);
  new IntersectionObserver(([entry]) => header.classList.toggle('is-scrolled', !entry.isIntersecting)).observe(sentinel);

  // Night header over the applications block.
  const night = document.querySelector<HTMLElement>('[data-scene-night]');
  if (night) {
    let observer: IntersectionObserver | null = null;
    const watch = () => {
      observer?.disconnect();
      const line = Math.round(header.offsetHeight / 2);
      observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) header.dataset.scene = 'night';
          else delete header.dataset.scene;
        },
        { rootMargin: `-${line}px 0px -${Math.max(0, window.innerHeight - line - 2)}px 0px` },
      );
      observer.observe(night);
    };
    watch();
    let resizeTimer = 0;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(watch, 150);
    });
  }
}

// Current section in the main navigation (home page only).
const navLinks = new Map(Array.from(document.querySelectorAll<HTMLAnchorElement>('[data-nav]')).map((link) => [link.dataset.nav ?? '', link]));
const sections = Array.from(document.querySelectorAll<HTMLElement>('main section[id]')).filter((section) => navLinks.has(section.id));
if (hasIO && sections.length > 0 && (location.pathname === '/ru/' || location.pathname === '/en/')) {
  const spy = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((link, id) => {
          if (id === entry.target.id) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    },
    { rootMargin: '-45% 0px -50% 0px' },
  );
  sections.forEach((section) => spy.observe(section));
}

// Stratigraphic column: the layer of the stage you are reading lights up.
const layers = new Map(Array.from(document.querySelectorAll<HTMLAnchorElement>('[data-layer]')).map((link) => [link.dataset.layer ?? '', link]));
const stages = Array.from(document.querySelectorAll<HTMLElement>('[data-stage]'));
if (hasIO && layers.size > 0) {
  const column = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const id = (entry.target as HTMLElement).dataset.stage;
        layers.forEach((link, key) => {
          const active = key === id;
          link.classList.toggle('is-active', active);
          if (active) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    },
    { rootMargin: '-35% 0px -60% 0px' },
  );
  stages.forEach((stage) => column.observe(stage));
}

// Remember language choice when clicking language switch
document.querySelectorAll<HTMLAnchorElement>('.lang-switch a[hreflang]').forEach((link) => {
  link.addEventListener('click', () => {
    const lang = link.getAttribute('hreflang');
    if (lang) {
      try {
        localStorage.setItem('preferred-lang', lang);
      } catch {}
    }
  });
});
