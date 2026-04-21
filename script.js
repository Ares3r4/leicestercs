'use strict';

// ─── NAVBAR ───────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

// ─── HAMBURGER ────────────────────────────────
let menuOpen = false;
const ham = document.getElementById('hamburger');
const mob = document.getElementById('mobileMenu');

ham.addEventListener('click', () => {
  menuOpen = !menuOpen;
  mob.classList.toggle('open', menuOpen);
  const [a, b, c] = ham.querySelectorAll('span');
  if (menuOpen) {
    a.style.transform = 'rotate(45deg) translate(4.5px, 4.5px)';
    b.style.opacity = '0';
    c.style.transform = 'rotate(-45deg) translate(4.5px, -4.5px)';
  } else {
    [a, b, c].forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
  }
});

document.querySelectorAll('.mm-link').forEach(l => l.addEventListener('click', () => {
  menuOpen = false;
  mob.classList.remove('open');
  ham.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
}));

// ─── SMOOTH SCROLL ────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const t = document.querySelector(a.getAttribute('href'));
    if (t) {
      e.preventDefault();
      window.scrollTo({ top: t.getBoundingClientRect().top + window.scrollY - 68, behavior: 'smooth' });
    }
  });
});

// ─── TEAM CARD FLIP ───────────────────────────
// Flip is triggered ONLY by the FLIP button — LinkedIn link is separate and always clickable
document.querySelectorAll('.tc-flip-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const cardId = btn.dataset.card;
    const card = document.getElementById(cardId);
    if (!card) return;
    const flipped = card.classList.toggle('flipped');
    btn.textContent = flipped ? 'BACK ↺' : 'FLIP ↺';
    btn.classList.toggle('active', flipped);
  });
});

// ─── STAT COUNTERS ────────────────────────────
function countUp(el, target) {
  const dur = 1200, start = performance.now();
  const tick = now => {
    const p = Math.min((now - start) / dur, 1);
    const e = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.floor(e * target) + (target >= 100 ? '+' : '');
    if (p < 1) requestAnimationFrame(tick);
    else el.textContent = target + (target >= 100 ? '+' : '');
  };
  requestAnimationFrame(tick);
}

const obs = new IntersectionObserver(entries => {
  entries.forEach(en => {
    if (!en.isIntersecting) return;
    countUp(en.target, parseInt(en.target.dataset.target));
    obs.unobserve(en.target);
  });
}, { threshold: 0.6 });
document.querySelectorAll('[data-target]').forEach(el => obs.observe(el));

// ─── ACTIVE NAV ───────────────────────────────
const navAs = document.querySelectorAll('.nav-links a');
document.querySelectorAll('section[id]').forEach(sec => {
  new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      navAs.forEach(a => {
        a.style.color = a.getAttribute('href') === '#' + en.target.id ? 'var(--teal)' : '';
        a.style.textShadow = a.getAttribute('href') === '#' + en.target.id ? 'var(--glow-t-sm)' : '';
      });
    });
  }, { threshold: 0.35 }).observe(sec);
});

// ─── IDEA FORM ────────────────────────────────
document.getElementById('ideaForm')?.addEventListener('submit', function(e) {
  e.preventDefault();
  const btn = document.getElementById('ideaBtn');
  btn.textContent = 'SENDING...';
  btn.disabled = true;
  setTimeout(() => {
    this.style.display = 'none';
    document.getElementById('ideaOk').style.display = 'block';
  }, 1000);
});