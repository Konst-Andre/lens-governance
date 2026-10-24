// pw_quiet.js · у сторінці: window.__aeQuiet(ms) — «усе, що мало статись за ms, сталось» (таймери з терміном у вікні · скінченні анімації ·
// запити в дорозі · два кадри); інакше — до межі. Вантажать обгортки pw_quiet.py (Python) і pw_quiet.mjs (Node) як init script (path — абсолютний).
// живе доки: прилади Playwright чекають через wait_for_timeout / waitForTimeout. Народився в AE S103 (замір і зуби — AE-Simulator:docs/DECISIONS.md В-216), wsd 1.21.
(() => { if (window.__aeQ) return; const Q = window.__aeQ = { t: new Map(), net: 0 };
  const st = window.setTimeout.bind(window), ct = window.clearTimeout.bind(window);
  window.setTimeout = function (f, d, ...a) { if (typeof f !== 'function') return st(f, d, ...a);
    d = Math.max(0, +d || 0); const id = st(function () { Q.t.delete(id); return f.apply(this, a); }, d); Q.t.set(id, performance.now() + d); return id; };
  window.clearTimeout = function (id) { Q.t.delete(id); return ct(id); };
  const F = window.fetch; if (F) window.fetch = function (...a) { Q.net++; let p; try { p = F.apply(this, a); } catch (e) { Q.net--; throw e; } return p.finally(() => { Q.net--; }); };
  const S = XMLHttpRequest.prototype.send; XMLHttpRequest.prototype.send = function (...a) { Q.net++; this.addEventListener('loadend', () => { Q.net--; }, { once: true }); return S.apply(this, a); };
  const busy = end => { const now = performance.now();
    for (const d of Q.t.values()) if (d <= end) return true;
    if (Q.net > 0) return true;
    for (const an of (document.getAnimations ? document.getAnimations() : [])) { if (an.playState !== 'running') continue;
      const c = an.effect && an.effect.getComputedTiming(); if (!c || !isFinite(c.endTime)) continue;
      if (now + (c.endTime - (+an.currentTime || 0)) / (an.playbackRate || 1) <= end) return true; }
    return false; };
  window.__aeQuiet = ms => new Promise(res => { const end = performance.now() + ms; let calm = 0;
    const tick = () => { if (performance.now() >= end) return res('cap');
      if (busy(end)) { calm = 0; return st(tick, 10); }
      if (++calm >= 2) return res('quiet');
      requestAnimationFrame(() => st(tick, 0)); };
    tick(); });
})();
