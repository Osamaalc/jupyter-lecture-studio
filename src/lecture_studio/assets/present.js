/* Lecture Studio presentation mode. Self-contained; no network access. */
(() => {
  const root = document.querySelector('.lecture-studio.ls-present');
  if (!root) return;
  const labels = window.LECTURE_STUDIO_LABELS || {};
  const slides = [...root.children].filter((el) => el.tagName === 'SECTION');
  if (!slides.length) return;
  const rtl = root.getAttribute('dir') === 'rtl';
  const stepped = root.dataset.fragments === 'true';
  document.documentElement.classList.add('ls-presenting');

  const progress = document.createElement('div');
  progress.className = 'ls-present-progress';
  const ui = document.createElement('nav');
  ui.className = 'ls-present-ui';
  ui.setAttribute('aria-label', 'Slides');
  const button = (text, title, action) => {
    const el = document.createElement('button');
    el.type = 'button';
    el.textContent = text;
    el.title = title || '';
    el.setAttribute('aria-label', title || text);
    el.addEventListener('click', action);
    return el;
  };
  const count = document.createElement('span');
  count.className = 'ls-present-count';
  const notes = document.createElement('aside');
  notes.className = 'ls-present-notes';
  notes.hidden = true;
  ui.append(
    button(rtl ? '→' : '←', labels['present.previous'], () => go(-1)),
    count,
    button(rtl ? '←' : '→', labels['present.next'], () => go(1)),
    button('⛶', labels['present.fullscreen'], fullscreen),
    button('✎', labels['present.notes'], toggleNotes),
  );
  root.append(progress, ui, notes);

  let index = 0;
  let step = 0;
  const steps = (slide) => (stepped ? [...slide.querySelectorAll('.ls-card, .ls-agenda-list > li, .ls-option')] : []);

  function render() {
    slides.forEach((slide, i) => {
      const current = i === index;
      slide.classList.toggle('ls-current', current);
      slide.setAttribute('aria-hidden', String(!current));
      steps(slide).forEach((el, k) => el.classList.toggle('ls-hidden-step', current && k >= step));
    });
    count.textContent = `${index + 1} / ${slides.length}`;
    progress.style.width = `${((index + 1) / slides.length) * 100}%`;
    const text = slides[index].querySelector('.ls-notes');
    notes.innerHTML = '';
    if (text) {
      const title = document.createElement('strong');
      title.textContent = labels['present.notes'] || 'Notes';
      notes.append(title, ...[...text.childNodes].map((n) => n.cloneNode(true)));
    }
    if (!text) notes.hidden = true;
    history.replaceState(null, '', `#${index + 1}`);
    fit();
  }

  function fit() {
    const slide = slides[index];
    root.classList.remove('ls-scroll');
    slide.style.transform = 'translate(-50%, -50%)';
    const width = slide.offsetWidth;
    const height = slide.offsetHeight;
    const scale = Math.min((innerWidth * 0.94) / width, (innerHeight * 0.92) / height, 2.4);
    if (scale < 0.62) {
      // Too tall to read when shrunk: fit the width and let the slide scroll.
      const wide = Math.min((innerWidth * 0.96) / width, 2.4);
      root.classList.add('ls-scroll');
      slide.style.transform = `translate(-50%, 2vh) scale(${wide})`;
      root.scrollTop = 0;
    } else {
      slide.style.transform = `translate(-50%, -50%) scale(${scale})`;
    }
  }

  function go(delta) {
    const total = steps(slides[index]).length;
    if (delta > 0 && step < total) { step += 1; return render(); }
    if (delta < 0 && step > 0 && stepped) { step -= 1; return render(); }
    const next = Math.max(0, Math.min(slides.length - 1, index + delta));
    if (next === index) return;
    index = next;
    step = delta > 0 ? 0 : steps(slides[index]).length;
    render();
  }

  function jump(i) {
    index = Math.max(0, Math.min(slides.length - 1, i));
    step = 0;
    render();
  }

  function fullscreen() {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen?.();
  }

  function toggleNotes() {
    if (notes.childNodes.length) notes.hidden = !notes.hidden;
  }

  document.addEventListener('keydown', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.target.closest && event.target.closest('input, textarea, select, summary, label')) {
      if (event.key !== 'PageDown' && event.key !== 'PageUp') return;
    }
    const forward = rtl ? 'ArrowLeft' : 'ArrowRight';
    const back = rtl ? 'ArrowRight' : 'ArrowLeft';
    const key = event.key;
    if ([forward, 'PageDown', ' ', 'Enter', 'ArrowDown'].includes(key)) go(1);
    else if ([back, 'PageUp', 'Backspace', 'ArrowUp'].includes(key)) go(-1);
    else if (key === 'Home') jump(0);
    else if (key === 'End') jump(slides.length - 1);
    else if (key === 'f' || key === 'F') fullscreen();
    else if (key === 's' || key === 'S') toggleNotes();
    else return;
    event.preventDefault();
  });

  let touch = null;
  root.addEventListener('touchstart', (event) => { touch = event.touches[0]; }, { passive: true });
  root.addEventListener('touchend', (event) => {
    if (!touch) return;
    const dx = event.changedTouches[0].clientX - touch.clientX;
    if (Math.abs(dx) > 50) go((dx < 0) !== rtl ? 1 : -1);
    touch = null;
  });
  addEventListener('resize', fit);
  addEventListener('hashchange', () => jump(parseInt(location.hash.slice(1), 10) - 1 || 0));
  if (document.fonts) document.fonts.ready.then(fit);
  jump(parseInt(location.hash.slice(1), 10) - 1 || 0);
})();
