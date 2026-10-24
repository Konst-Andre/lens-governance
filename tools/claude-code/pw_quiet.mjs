// pw_quiet.mjs · пара pw_quiet.py для приладів Node: page.waitForTimeout(N) = «тиша до N мс» — усе, що мало статись у вікні, сталось
// (таймери з терміном у вікні · скінченні анімації · запити · два кадри), інакше — до межі. Скрипт сторінки — pw_quiet.js. wsd 1.21; AE S103 (В-216).
// живе доки: прилади Playwright (Node) чекають через waitForTimeout.
// Вживання:  import { install, report } from '<ядро>/tools/claude-code/pw_quiet.mjs';  await install(page);  … console.log(report());
// Цикл-опитування стану з боку приладу — page.waitReal(ms) (справжній час). QUIET=0 — старі паузи (негативний контроль). Самоперевірка: node pw_quiet.mjs selftest
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const JS = join(dirname(fileURLToPath(import.meta.url)), 'pw_quiet.js');
const STATS = { calls: 0, saved: 0, cap: 0 };
const off = () => process.env.QUIET === '0' || process.env.AE_QUIET === '0';

export async function install(page) {
  if (off()) { page.waitReal = page.waitForTimeout.bind(page); return page; }
  await page.addInitScript({ path: JS });
  const real = page.waitForTimeout.bind(page);
  page.waitReal = real;   // цикли-опитування стану з боку приладу — справжній час (AE S103, п. 114)
  page.waitForTimeout = async ms => {
    const t0 = Date.now(); let r;
    try { r = await page.evaluate(m => window.__aeQuiet ? window.__aeQuiet(m) : 'none', ms); } catch { r = 'err'; }   // перехід сторінки — добрати справжнім часом
    const left = ms - (Date.now() - t0); if ((r === 'none' || r === 'err') && left > 0) await real(left);
    STATS.calls++; STATS.cap += r === 'cap'; STATS.saved += Math.max(0, ms - (Date.now() - t0));
  };
  return page;
}

export function report() {
  return off() || !STATS.calls ? 'тиша: вимкнено (QUIET=0) — фіксовані паузи' : `тиша: пауз ${STATS.calls} · до межі ${STATS.cap} · зекономлено ${Math.round(STATS.saved / 1000)} с`;
}

if (process.argv[2] === 'selftest') {
  const PW = ['/opt/node-tools/node_modules/playwright/index.mjs', 'playwright']; let pw;
  for (const p of PW) { try { pw = await import(p); break; } catch {} }
  let ok = 0, n = 0; const t = (c, m) => { n++; ok += !!c; console.log((c ? '✓ ' : '✗ ') + m); };
  const b = await pw.chromium.launch(); const pg = await install(await b.newPage());
  await pg.goto('data:text/html,<button onclick="setTimeout(()=>document.body.dataset.ok=1,120)">b</button>');
  let s = Date.now(); await pg.waitForTimeout(500); let d = Date.now() - s; t(d < 200, `порожня сторінка → не чекає межу (${d} мс < 200)`);
  await pg.click('button'); s = Date.now(); await pg.waitForTimeout(500); d = Date.now() - s;
  t(await pg.evaluate(() => document.body.dataset.ok) === '1' && d >= 110 && d < 400, `таймер 120 мс у вікні → дочекано (${d} мс), результат є`);
  await pg.evaluate(() => setTimeout(() => {}, 900)); s = Date.now(); await pg.waitForTimeout(300); d = Date.now() - s; t(d < 200, `таймер поза вікном → не тримає (${d} мс)`);
  await b.close(); console.log(`─── pw_quiet.mjs selftest: ${ok}/${n} ───`); process.exit(ok === n ? 0 : 1);
}
