/*
  Photo carousels and the full-screen viewer.
  Without JavaScript every carousel is a native horizontal scroller with snap points and captions,
  and every photo link opens the large file. This script adds: buttons, thumbnails, keyboard,
  mouse dragging with a flick, depth/parallax while swiping, and a viewer that morphs out of the slide.
*/
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
const behavior = (): ScrollBehavior => (reduced.matches ? 'auto' : 'smooth');
const EASE = 'cubic-bezier(0.16, 1, 0.3, 1)';

interface Gallery {
  root: HTMLElement;
  links: HTMLAnchorElement[];
  current: () => number;
  goTo: (index: number, how?: ScrollBehavior) => void;
}

const registry = new WeakMap<HTMLElement, Gallery>();
let suppressClickUntil = 0;

function setupGallery(root: HTMLElement): void {
  const viewport = root.querySelector<HTMLElement>('[data-viewport]');
  const slides = Array.from(root.querySelectorAll<HTMLElement>('[data-slide]'));
  const links = slides.map((slide) => slide.querySelector<HTMLAnchorElement>('a[data-zoom]')).filter((a): a is HTMLAnchorElement => a !== null);
  if (!viewport || slides.length === 0) return;

  // Photos fade in over their average colour instead of popping in.
  root.querySelectorAll<HTMLImageElement>('.gallery-media img').forEach((img) => {
    if (img.complete) return;
    img.dataset.loading = '';
    const done = () => delete img.dataset.loading;
    img.addEventListener('load', done, { once: true });
    img.addEventListener('error', done, { once: true });
  });

  const controls = root.querySelector<HTMLElement>('[data-controls]');
  const prev = root.querySelector<HTMLButtonElement>('[data-prev]');
  const next = root.querySelector<HTMLButtonElement>('[data-next]');
  const status = root.querySelector<HTMLElement>('[data-status]');
  const thumbsWrap = root.querySelector<HTMLElement>('[data-thumbs]');
  const thumbs = Array.from(root.querySelectorAll<HTMLButtonElement>('[data-thumb]'));
  const dots = Array.from(root.querySelectorAll<HTMLElement>('.gallery-dots span'));
  const last = slides.length - 1;
  const clamp = (index: number) => Math.max(0, Math.min(last, index));
  let current = -1;
  let frame = 0;

  const centerOf = (slide: HTMLElement) => slide.offsetLeft + slide.offsetWidth / 2 - viewport.clientWidth / 2;
  const nearest = () => {
    const left = viewport.scrollLeft;
    let best = 0;
    slides.forEach((slide, index) => {
      if (Math.abs(centerOf(slide) - left) < Math.abs(centerOf(slides[best]) - left)) best = index;
    });
    return best;
  };

  const render = (index: number) => {
    if (index === current) return;
    current = index;
    slides.forEach((slide, i) => slide.classList.toggle('is-current', i === index));
    if (status) status.innerHTML = `<b>${index + 1}</b> из ${slides.length}`;
    dots.forEach((dot, i) => dot.classList.toggle('is-current', i === index));
    thumbs.forEach((thumb, i) => thumb.setAttribute('aria-current', String(i === index)));
    const thumb = thumbs[index];
    if (thumbsWrap && thumb) {
      const target = thumb.offsetLeft - thumbsWrap.clientWidth / 2 + thumb.offsetWidth / 2;
      thumbsWrap.scrollTo({ left: target, behavior: behavior() });
    }
  };

  // Each slide gets its distance from the centre: CSS turns it into depth (scale, opacity) and parallax.
  // Frames differ in width (portrait vs landscape), so distance is measured in half-widths of slide plus viewport:
  // 0 when centred, 1 once the slide has fully left the view.
  const update = () => {
    const middle = viewport.scrollLeft + viewport.clientWidth / 2;
    slides.forEach((slide) => {
      const reach = (slide.offsetWidth + viewport.clientWidth) / 2 || 1;
      const off = (slide.offsetLeft + slide.offsetWidth / 2 - middle) / reach;
      const bounded = Math.max(-1.5, Math.min(1.5, off));
      slide.style.setProperty('--off', bounded.toFixed(3));
      slide.style.setProperty('--abs', Math.min(1, Math.abs(off)).toFixed(3));
    });
    render(nearest());
  };

  const goTo = (index: number, how: ScrollBehavior = behavior()) => {
    viewport.scrollTo({ left: centerOf(slides[clamp(index)]), behavior: how });
  };

  viewport.addEventListener(
    'scroll',
    () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(update);
    },
    { passive: true },
  );

  viewport.addEventListener('keydown', (event) => {
    const moves: Record<string, number> = { ArrowRight: current + 1, ArrowLeft: current - 1, Home: 0, End: last };
    if (!(event.key in moves)) return;
    event.preventDefault();
    goTo(moves[event.key]);
  });

  prev?.addEventListener('click', () => goTo(current === 0 ? last : current - 1));
  next?.addEventListener('click', () => goTo(current === last ? 0 : current + 1));
  thumbs.forEach((thumb, index) => thumb.addEventListener('click', () => goTo(index)));

  // Mouse dragging. Touch and trackpads already scroll natively, so only a mouse needs help.
  let drag: { x: number; left: number; start: number; moved: boolean; vx: number; lastX: number; lastT: number } | null = null;
  viewport.addEventListener('pointerdown', (event) => {
    if (event.pointerType !== 'mouse' || event.button !== 0 || slides.length < 2) return;
    drag = { x: event.clientX, left: viewport.scrollLeft, start: current, moved: false, vx: 0, lastX: event.clientX, lastT: event.timeStamp };
  });
  window.addEventListener('pointermove', (event) => {
    if (!drag) return;
    const dx = event.clientX - drag.x;
    if (!drag.moved && Math.abs(dx) > 6) {
      drag.moved = true;
      viewport.classList.add('is-dragging');
    }
    if (!drag.moved) return;
    viewport.scrollLeft = drag.left - dx;
    const dt = event.timeStamp - drag.lastT;
    if (dt > 0) drag.vx = (event.clientX - drag.lastX) / dt;
    drag.lastX = event.clientX;
    drag.lastT = event.timeStamp;
  });
  const endDrag = (event: PointerEvent) => {
    if (!drag) return;
    const state = drag;
    drag = null;
    if (!state.moved) return;
    viewport.classList.remove('is-dragging');
    suppressClickUntil = event.timeStamp + 350;
    const dx = event.clientX - state.x;
    let target = nearest();
    // A flick moves one photo even when the pointer travelled only a little.
    if (target === state.start && (Math.abs(state.vx) > 0.35 || Math.abs(dx) > viewport.clientWidth * 0.12)) {
      target = clamp(state.start + (dx < 0 ? 1 : -1));
    }
    goTo(target);
  };
  window.addEventListener('pointerup', endDrag);
  window.addEventListener('pointercancel', endDrag);
  viewport.addEventListener(
    'click',
    (event) => {
      if (event.timeStamp < suppressClickUntil) {
        event.preventDefault();
        event.stopPropagation();
      }
    },
    true,
  );

  new ResizeObserver(() => {
    viewport.scrollTo({ left: centerOf(slides[Math.max(0, current)]), behavior: 'auto' });
    update();
  }).observe(viewport);

  root.dataset.enhanced = '';
  if (controls) controls.hidden = false;
  if (thumbsWrap) thumbsWrap.hidden = false;
  update();

  registry.set(root, { root, links, current: () => current, goTo });
}

function setupLightbox(): void {
  const dialog = document.querySelector<HTMLDialogElement>('[data-lightbox]');
  const stage = dialog?.querySelector<HTMLElement>('[data-lb-stage]');
  const caption = dialog?.querySelector<HTMLElement>('[data-lb-caption]');
  const count = dialog?.querySelector<HTMLElement>('[data-lb-count]');
  const prev = dialog?.querySelector<HTMLButtonElement>('[data-lb-prev]');
  const next = dialog?.querySelector<HTMLButtonElement>('[data-lb-next]');
  const close = dialog?.querySelector<HTMLButtonElement>('[data-lb-close]');
  if (!dialog || !stage || !caption || !count || !prev || !next || !close || typeof dialog.showModal !== 'function') return;

  let gallery: Gallery | null = null;
  let index = 0;
  let image: HTMLImageElement | null = null;
  const canMorph = () => typeof document.startViewTransition === 'function' && !reduced.matches;
  const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

  const build = (link: HTMLAnchorElement) => {
    const img = new Image();
    const width = Number(link.dataset.width) || 1280;
    const height = Number(link.dataset.height) || 960;
    const ratio = width / height;
    img.width = width;
    img.height = height;
    // CSS sizes the photo from this ratio and the free stage, so it always fits the screen whole.
    img.style.setProperty('--r', ratio.toFixed(4));
    if (link.dataset.srcset) {
      // The photo fills the screen, so large displays get the bigger copy when one exists.
      img.srcset = link.dataset.srcset;
      img.sizes = `${Math.ceil(Math.min(window.innerWidth, window.innerHeight * ratio))}px`;
    }
    img.src = link.href;
    img.alt = link.dataset.alt ?? '';
    img.decoding = 'async';
    img.draggable = false;
    return img;
  };
  const preload = (i: number) => {
    const link = gallery?.links[(i + gallery.links.length) % gallery.links.length];
    if (link) build(link);
  };

  // dir: 1 = next, -1 = previous, 0 = no slide animation. fromX keeps a swipe continuous.
  const show = (i: number, dir = 0, fromX = 0) => {
    if (!gallery) return;
    const total = gallery.links.length;
    index = (i + total) % total;
    const link = gallery.links[index];
    const incoming = build(link);
    const outgoing = image;
    image = incoming;
    stage.append(incoming);
    caption.textContent = link.dataset.caption ?? '';
    count.innerHTML = `<b>${index + 1}</b> из ${total}`;
    prev.hidden = next.hidden = total < 2;
    if (outgoing) {
      if (dir === 0 || reduced.matches) {
        outgoing.remove();
      } else {
        outgoing
          .animate([{ transform: `translateX(${fromX}px)`, opacity: 1 }, { transform: `translateX(${-dir * 9}%) scale(0.96)`, opacity: 0 }], { duration: 420, easing: EASE })
          .finished.then(() => outgoing.remove(), () => outgoing.remove());
        incoming.animate([{ transform: `translateX(${dir * 12}%) scale(0.96)`, opacity: 0 }, { transform: 'none', opacity: 1 }], { duration: 560, easing: EASE });
      }
    }
    preload(index + 1);
    preload(index - 1);
  };

  const open = (target: Gallery, i: number, link: HTMLAnchorElement) => {
    gallery = target;
    const thumb = link.querySelector('img');
    const reveal = async () => {
      show(i);
      dialog.showModal();
      await Promise.race([image?.decode().catch(() => undefined), wait(400)]);
    };
    if (canMorph() && thumb) {
      thumb.style.viewTransitionName = 'lb-photo';
      const transition = document.startViewTransition(async () => {
        thumb.style.viewTransitionName = '';
        await reveal();
        if (image) image.style.viewTransitionName = 'lb-photo';
      });
      transition.finished.finally(() => {
        if (image) image.style.viewTransitionName = '';
      });
    } else {
      void reveal();
      if (!reduced.matches) dialog.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 260, easing: EASE });
    }
  };

  const shut = () => {
    if (!dialog.open) return;
    const target = gallery;
    // The carousel follows the viewer, so closing lands on the photo you were looking at.
    if (target && target.current() !== index) target.goTo(index, 'auto');
    const thumb = target?.links[index]?.querySelector('img');
    if (canMorph() && image && thumb) {
      image.style.viewTransitionName = 'lb-photo';
      const transition = document.startViewTransition(() => {
        if (image) image.style.viewTransitionName = '';
        dialog.close();
        thumb.style.viewTransitionName = 'lb-photo';
      });
      transition.finished.finally(() => {
        thumb.style.viewTransitionName = '';
      });
    } else {
      dialog.close();
    }
  };

  document.addEventListener('click', (event) => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = (event.target as Element | null)?.closest<HTMLAnchorElement>('a[data-zoom]');
    const root = link?.closest<HTMLElement>('[data-gallery]');
    const target = root ? registry.get(root) : undefined;
    if (!link || !target) return;
    event.preventDefault();
    open(target, Number(link.dataset.index) || 0, link);
  });

  prev.addEventListener('click', () => show(index - 1, -1));
  next.addEventListener('click', () => show(index + 1, 1));
  close.addEventListener('click', shut);
  dialog.addEventListener('cancel', (event) => {
    event.preventDefault();
    shut();
  });
  dialog.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight') show(index + 1, 1);
    if (event.key === 'ArrowLeft') show(index - 1, -1);
  });
  dialog.addEventListener('click', (event) => {
    if (!(event.target as Element).closest('img, button')) shut();
  });
  dialog.addEventListener('close', () => {
    stage.querySelectorAll('img').forEach((img) => img.remove());
    image = null;
    gallery?.links[index]?.focus({ preventScroll: true });
  });

  // Swipe between photos: the picture follows the finger, a short flick is enough.
  let swipe: { x: number; y: number; dx: number; t: number } | null = null;
  stage.addEventListener('pointerdown', (event) => {
    if ((event.target as Element).closest('button') || !image) return;
    swipe = { x: event.clientX, y: event.clientY, dx: 0, t: event.timeStamp };
  });
  stage.addEventListener('pointermove', (event) => {
    if (!swipe || !image) return;
    swipe.dx = event.clientX - swipe.x;
    if (Math.abs(swipe.dx) > Math.abs(event.clientY - swipe.y)) image.style.transform = `translateX(${swipe.dx}px)`;
  });
  const endSwipe = (event: PointerEvent) => {
    if (!swipe || !image) return;
    const { dx, t } = swipe;
    swipe = null;
    const fast = Math.abs(dx) / Math.max(1, event.timeStamp - t) > 0.5;
    if (Math.abs(dx) > 70 || (fast && Math.abs(dx) > 24)) {
      image.style.transform = '';
      show(index + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1, dx);
    } else if (dx !== 0) {
      const img = image;
      img.animate([{ transform: `translateX(${dx}px)` }, { transform: 'none' }], { duration: 300, easing: EASE });
      img.style.transform = '';
    }
    if (Math.abs(dx) > 8) suppressClickUntil = event.timeStamp + 300;
  };
  stage.addEventListener('pointerup', endSwipe);
  stage.addEventListener('pointercancel', endSwipe);
  stage.addEventListener(
    'click',
    (event) => {
      if (event.timeStamp < suppressClickUntil) event.stopPropagation();
    },
    true,
  );
}

document.querySelectorAll<HTMLElement>('[data-gallery]').forEach(setupGallery);
setupLightbox();
