> живе доки: назавжди (вічне, wsd 1.8) — донор-модуль переживає продукт-джерело
> KERNEL v2 · 01.08.2026 — спільне ядро сімейства Lens

# `Lens_module_maint_v1` — донор-модуль «Обслуговування»

**Що це.** Самодостатній блок «самоперевірка версії + встановлення на робочий стіл»,
знятий 1:1 з `StockCheck_port_b28.html` (v2.17.0 · b28, device✓ на iPhone XS/iOS 18,
iPhone 15 Pro/iOS 26, Android-планшет; Safari · Telegram webview · standalone PWA; обидві теми).

**Чому донор-модуль, а не запис у Cookbook** (поріг wsd 12.11): споживачів ≥2
(QR Lens, PharmaLens) і коду >100 рядків — фактично 480 рядків у трьох шарах.
Cookbook лишає *чому* (записи A79/A80), цей файл дає *робочий фрагмент*.

**Куди канонити:** нікуди. Це кінцевий дім коду. Записи-патерни живуть у Cookbook.

---

## §0 Що модуль робить — чотири незалежні функції

| # | функція | механізм | що зламається без неї |
|---|---|---|---|
| 1 | **самоперевірка версії** | `fetch(location.pathname, {cache:'no-store'})` → регекс по `APP_BUILD` у відповіді → порівняння з власною константою | користувач сидить на старому білді й не знає про це |
| 2 | **застосування оновлення** | `location.replace(pathname + '?v=' + ver)` — query обходить HTTP-кеш | reload віддає ту саму кешовану оболонку |
| 3 | **встановлення (Android/Chrome)** | перехоплення `beforeinstallprompt` → відкладений `prompt()` за тапом користувача | нативний банер з'їдається браузером і зникає назавжди |
| 4 | **інструкція (iOS/Safari)** | `beforeinstallprompt` у Safari не існує → покрокова інструкція «Поділитись → На екран Додому» | на iOS кнопка встановлення мертва без пояснення |

**Ключове рішення архітектури:** застосунок — **один HTML-файл**. Тому самоперевірка
не потребує ні маніфесту версій, ні service worker: вона тягне **сам себе** і читає
власну константу з тексту відповіді. Це працює рівно доти, доки продукт лишається
single-file; при переході на бандл механізм треба міняти, не переносити.

---

## §1 Рішення по service worker — НЕ потрібен

**Питання стояло так** (`StockCheck_session_summary_b27.md` §6): після тапу «Оновити»
версія свіжа, але swipe-up kill → перезапуск → знову стара, і знову пропозиція оновити.
Гіпотеза була «діра, потрібен SW із network-first на HTML».

**Перевірено на девайсі (Konst, 08.2026) — діри немає.** GitHub Pages віддає
`Cache-Control: max-age=600`. Симптом спостерігався **всередині** цього вікна.
Фактична поведінка:

- тап «Оновити» → сторінка перезавантажується з query → **актуальна версія в сеансі**;
- kill **у межах 10 хв** після деплою → повернення до старої (кеш ще свіжий, не перевалідовувався);
- звичайне користування (відійшов, повернувся пізніше) → кеш протух сам → **актуальна версія
  підтягнулась, пропозиція оновити більше не з'являлась**.

**Вирок: service worker не заводиться.** Він купував би вікно ≤10 хв ціною власного
кешу, циклу оновлення SW і класу помилок «застряг на старій версії SW» — тобто міняв би
десятихвилинну затримку на постійну складність.

**Механізм ⟂ спостереження (wsd 12.10):**
- *Механізм:* HTTP-кеш хоста — єдиний шар між користувачем і файлом; вікно застарілості
  дорівнює `max-age` хоста, і застосунок на нього не впливає.
- *Спостереження:* `[08.2026]` GitHub Pages = `max-age=600`. **Перевірити при зміні хостингу** —
  на хості з довгим `max-age` (година+) цей висновок не переноситься.

---

## §2 Точки під'єднання (що модуль очікує від хоста)

| залежність | форма | звідки в StockCheck |
|---|---|---|
| `APP_BUILD` | `{ver, build, date}`, оголошена **до** модуля | wsd 10.6 |
| `$(id)` | `document.getElementById` | базовий хелпер |
| `openSheet/closeSheet/closeSheets` | наявні функції шіт-шару | модуль їх **обгортає**, тіла не переписує (wsd 10.7) |
| `#mtCard` · `#mtEb` · `#sh-install` | вузли HTML-шару §4 | нижче |
| токени теми | `--accent` · `--crit` · `--text-2` · `--font` | будь-який Lens |

**Модуль НЕ вимагає:** service worker · маніфест версій · мережевий бекенд · зовнішніх бібліотек.

---

## §3 Три шари — порядок вставки

**HTML/CSS завжди перед JS** (wsd 1.5). Порядок: CSS → HTML → JS.

---

## §4 CSS-шар

Вставляти після базових токенів, **до** продуктових компонентів.

> ⚠ **Класи префіксовані `.ins-*` свідомо.** У першій редакції блок ніс `.sec`/`.pri` —
> вони зіткнулися з глобальними `.sec` (секційний заголовок Home) і `.pri`, і колізія
> доїхала до девайса. Скоуп `.ins-cta .sec` не рятує: він перебиває лише **оголошені**
> властивості, а `text-transform`/`display`/`margin` протікають далі.
> При порті в новий продукт — грепнути `\.ins-` на 0 збігів **до** вставки.

```css
/* ═══════════════════════════════════════════════════════════════════════════
   NODE 2.2 · ОБСЛУГОВУВАННЯ (порт зі stage-bench maint_v3, значення §2 самері)
   Крапка · антистрибок · стани рядка · інструкція · ефект duo.
   ⚠ кожне [data-theme="dark"] тут ПРОДУБЛЬОВАНО в @media(prefers-color-scheme)
     нижче — A69 auto-dark parity (різниця стенд↔продукт, стенд дубля не має).
   ═══════════════════════════════════════════════════════════════════════════ */
:root{
  /* крапка — device-lock: size 10 · dx 3 · dy 3 · col accent · ring OFF · pulse OFF */
  --dotS:10px; --dotX:3px; --dotY:3px; --dotRW:0px;
  /* антистрибок — слот-хвіст 84px тримає текстову колонку рівно на 187px (Д1) */
  --miH:54px; --actW:84px;
  /* ефект duo — device-lock: delay 120 (у JS) · dur 990 · rep 3 · int 60 · duo 3% */
  --fxDur:990ms; --fxRep:3; --fxInt:60; --fxDuo:3;
}

/* ─── тиха крапка апдейта: три кебаби (острівець 44 + два хедери 38) ─── */
.kdot{display:none;position:absolute;top:var(--dotY);right:var(--dotX);
  width:var(--dotS);height:var(--dotS);border-radius:50%;background:var(--accent);
  pointer-events:none;box-shadow:0 0 0 var(--dotRW) var(--dotRC,var(--bg))}
.kdot.on{display:block}
.isl-menu{position:relative}          /* ⚠ у b25 його не було — без нього крапка тікає з кнопки */
.isl-menu .kdot{--dotRC:var(--surface-2)}
.icon-btn .kdot{--dotRC:var(--bg)}

/* ─── антистрибок (device-знахідка 28.07): бейдж забирає ширину в текстової
       колонки → підпис іде у 2-й рядок → рядок росте. Три замки:
       слот-хвіст фіксованої ширини · min-height рядка · без переносу.
       Копія переписана під 187px ≈ 34 симв. → ellipsis тут аварійна сітка (Д1). ─── */
#sheet .mi{min-height:var(--miH)}
#sheet .mi-tx b,#sheet .mi-tx span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mi-act{flex:none;display:flex;align-items:center;justify-content:flex-end;min-width:var(--actW)}

/* ─── стани рядка версії ─── */
.mi.upd .mi-ic{color:var(--accent);background:color-mix(in srgb,var(--accent) 10%,transparent)}
.mi.warnst .mi-ic{color:var(--warn);background:color-mix(in srgb,var(--warn) 12%,transparent)}
.mi.quiet{cursor:default}
/* b27: колір ПРИБРАНО. Неінтерактивність рядка вже несуть три сигнали —
   немає .doact, немає .mi-chev, немає .pressable (отже й прес-анімації).
   Приглушення ЗАГОЛОВКА заявляло «вміст менш важливий» (хибно: версія важлива)
   і робило весь блок «Обслуговування» блідішим за ДІЇ/СЕАНС (device, 30.07).
   Прецедент каналу: .mi.danger b — заголовок несе СЕМАНТИКУ, не ІЄРАРХІЮ. */
.mi.quiet b{font-weight:700}

/* ─── інструкція «Додати на екран Додому» · стиль glyph + крок 0 банером ─── */
.ins-hd{padding:4px 18px 2px;font:800 17px/1.25 var(--font);color:var(--text)}
.ins-sub{padding:4px 18px 10px;font:600 12px/1.45 var(--font);color:var(--muted)}
.step0b{margin:0 12px 10px;padding:10px 12px;border-radius:12px;display:flex;gap:10px;align-items:flex-start;
  background:color-mix(in srgb,var(--warn) 12%,transparent);border:1px solid color-mix(in srgb,var(--warn) 34%,transparent)}
.step0b .s0i{flex:none;color:var(--warn);display:flex;margin-top:1px}
.step0b .s0i svg{width:17px;height:17px}
.step0b .s0t{font:700 12px/1.4 var(--font);color:var(--text)}
.step0b .s0t span{display:block;font-weight:600;color:var(--text-2);margin-top:3px}
.stp{display:flex;gap:11px;align-items:flex-start;padding:11px 13px;border-bottom:1px solid var(--border-subtle)}
[data-theme="dark"] .stp{border-bottom-color:var(--border)}
.stp:last-child{border-bottom:none}
.stp .tx{flex:1;font:700 13px/1.35 var(--font);color:var(--text)}
.stp .tx span{display:block;font:600 11.5px/1.35 var(--font);color:var(--muted);margin-top:3px}
.stp .gl{flex:none;width:30px;height:30px;border-radius:9px;display:grid;place-items:center;
  background:color-mix(in srgb,#fff 80%,var(--surface-3));border:1px solid rgba(20,50,42,.12);color:var(--text-2)}
[data-theme="dark"] .stp .gl{background:color-mix(in srgb,#fff 9%,var(--surface-3));border-color:rgba(255,255,255,.045)}
.stp .gl svg{width:16px;height:16px}
/* крок 0 у glyph-стилі не має цифри — позначкою лишається тон, інакше
   обов'язковий передкрок мовчки прирівнюється до звичайного */
.stp.zero .gl{color:var(--warn);background:color-mix(in srgb,var(--warn) 12%,transparent);
  border-color:color-mix(in srgb,var(--warn) 34%,transparent)}
.ins-cta{margin:14px 12px 2px;display:flex;gap:8px;align-items:stretch}
/* ⚠ ПРЕФІКСОВАНІ ІМЕНА (правило b24 §4.2-bis, прецедент dpicker): голі .sec/.pri
   у single-file продукті вже зайняті — .sec (р.~600) це заголовок секції.
   Скоуп .ins-cta .sec НЕ рятує: він перебиває лише оголошені властивості,
   а text-transform / display / margin протікають і ламають пару кнопок. */
.ins-cta button{flex:1 1 0;display:block;box-sizing:border-box;margin:0;
  border:none;border-radius:12px;padding:13px 0;text-align:center;
  text-transform:none;letter-spacing:normal;font:800 13.5px/1 var(--font);cursor:pointer}
.ins-cta .ins-sec{background:var(--surface-3);color:var(--text-2);border:1px solid var(--border)}
.ins-cta .ins-pri{background:var(--accent);color:#fff}
[data-theme="dark"] .ins-cta .ins-pri{background:linear-gradient(180deg,hsl(163 55% 34%),hsl(163 55% 30%))}
.ins-cta .ins-sec.is-pressed,.ins-cta .ins-pri.is-pressed{transform:scale(.96);transition-duration:.06s}

/* ─── ефект duo (ореол + мікропульс) · грає ПІСЛЯ осідання шіта (Д3) ───
   Клас вішається на body, знімається на закритті → ефект можна повторити.
   Ореол праворуч підрізається .gcard{overflow:hidden} — так само, як на стенді,
   де значення й арбітрувались; паритет свідомий, не недогляд. */
.fx-duo .mi.upd .doact{animation:fxGlow var(--fxDur) ease-in-out var(--fxRep),
  fxDuo var(--fxDur) ease-in-out var(--fxRep)}
@keyframes fxGlow{0%,100%{box-shadow:0 0 0 0 transparent}
  50%{box-shadow:0 0 calc(var(--fxInt)/4 * 1px) calc(var(--fxInt)/30 * 1px) color-mix(in srgb,var(--accent) 55%,transparent)}}
@keyframes fxDuo{0%,100%{transform:scale(1)}50%{transform:scale(calc(1 + var(--fxDuo)/100))}}
/* reduced-motion: рух геть, ореол лишається робочою заміною (§3 п.8) */
@media(prefers-reduced-motion:reduce){
  .fx-duo .mi.upd .doact{animation:fxGlow var(--fxDur) ease-in-out var(--fxRep)}
}
/* ══════════════════════ кінець NODE 2.2 CSS ══════════════════════ */
.throw{display:flex;align-items:center;gap:12px;padding:11px 13px 3px}
.thlbl{flex:1;font:700 13.5px/1 var(--font);color:var(--text)}
.thseg{display:flex;gap:0;margin:0 13px;padding:3px;border-radius:11px;position:relative;overflow:hidden;
  background:color-mix(in srgb,var(--bg-soft) 82%,var(--card));border:1px solid var(--border-subtle);
  box-shadow:inset 0 1px 2px rgba(20,50,42,.15)}
[data-theme="dark"] .thseg{background:color-mix(in srgb,var(--card),#000 20%);border-color:color-mix(in srgb,var(--border),#000 16%);
  box-shadow:inset 0 2px 5px rgba(0,0,0,.5),inset 0 -1px 0 rgba(255,255,255,.08)}
.thseg button{flex:1;border:none;background:transparent;padding:8px 4px;border-radius:9px;cursor:pointer;font:700 12px/1 var(--font);color:var(--muted);transition:color .15s;position:relative;z-index:1}
.thseg button.on{color:#fff}
.seg-thumb{position:absolute;top:3px;bottom:3px;left:0;width:0;border-radius:9px;z-index:0;opacity:0;pointer-events:none;background:var(--accent);box-shadow:0 1px 3px -1px color-mix(in srgb,var(--accent) 40%,transparent);transition:transform var(--seg-dur) var(--seg-ease),width var(--seg-dur) var(--seg-ease)}
[data-theme="dark"] .seg-thumb{background:linear-gradient(180deg,hsl(163 55% 34%),hsl(163 55% 30%))}
.seg-thumb.seg-no-anim{transition:none}
@media(prefers-reduced-motion:reduce){.seg-thumb{transition:none}}
/* confirm-шіт (A59) */
.cf-wrap{padding:6px 20px 10px}
.cf-title{font:800 17px/1.3 var(--font);color:var(--text)}
.cf-desc{font:600 13px/1.45 var(--font);color:var(--text-2);margin-top:8px}
.cf-btns{display:flex;gap:10px;margin-top:18px}
.cf-btns button{flex:1;border:none;border-radius:12px;padding:13px;font:800 14px/1 var(--font);cursor:pointer}
.cf-cancel{background:var(--surface-3);color:var(--text)}
[data-theme="dark"] .cf-cancel{background:color-mix(in srgb,var(--surface-3),#fff 3%)}
.cf-ok{background:var(--crit);color:#fff}
.cf-cancel.is-pressed,.cf-ok.is-pressed{transform:scale(.96);transition-duration:.06s}

/* ═══════════ §5.1-PICKER · шіт вибору пари візитів (b24, порт stagebench v2_3) ═══════════
   Модель anchor: слоти = ТАБЛО (<div>, не кнопки) — у шіті рівно один інтерактивний
   об'єкт, список візитів. Режим у продукті один, тож pointer-events-хак і .slot.act
   зі стенду НЕ переїжджають (там вони обслуговували важіль pickMode).
   Усе скоуплено під #sh-period: .slot/.vrow/.vtag — імена, що легко колідують із FILL. */
/* well-матеріал (A65). Токени --well* оголошені у скоупі #s-cmp (р.~678), а шіт живе
   на рівні <body> → до них не дотягується. Локальна копія 1:1.
   БОРГ (A45-маніфест): підняти --well* у :root і прибрати цей дубль. */
#sh-period{--wellBg:color-mix(in srgb,var(--bg-soft) 68%,var(--card));
  --wellBd:var(--border-subtle);
  --wellSh:inset 0 1px 2px rgba(20,50,42,.10)}
[data-theme="dark"] #sh-period{--wellBg:color-mix(in srgb,var(--card),#000 22%);
  --wellBd:color-mix(in srgb,var(--border),#000 18%);
  --wellSh:inset 0 1.5px 3px rgba(0,0,0,.5),inset 0 -1px 0 rgba(255,255,255,.07)}

#sh-period .slots{display:flex;align-items:center;gap:8px;margin:0 12px}
#sh-period .slot{flex:1 1 0;min-width:0;display:flex;flex-direction:column;align-items:flex-start;gap:3px;
  padding:9px 12px 10px;border-radius:13px;font-family:var(--font);text-align:left;
  background:var(--wellBg);border:1px solid var(--wellBd);box-shadow:var(--wellSh)}
#sh-period .sl-k{font:800 9.5px/1 var(--font);text-transform:uppercase;letter-spacing:.7px;color:var(--muted)}
#sh-period .sl-v{font:800 17px/1 var(--font);color:var(--text);font-variant-numeric:tabular-nums;letter-spacing:-.3px}
#sh-period .sl-arr{flex:0 0 auto;color:var(--muted);font-size:15px;font-weight:800}
/* рядок-підказка ЗАВЖДИ в потоці з фіксованою висотою: текст міняється, коробка — ні.
   Поява/зникнення рядка перебудовувала б висоту bottom-anchored шіта → ривок. */
#sh-period .pkhint{margin:9px 14px 0;height:16px;font:600 11.5px/16px var(--font);color:var(--muted);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:color .18s ease}
#sh-period .pkhint.warn{color:var(--warn)}

#sh-period .vlist{max-height:40dvh;overflow-y:auto;overflow-x:hidden;overscroll-behavior:contain;-webkit-overflow-scrolling:touch}
#sh-period .vlist::-webkit-scrollbar{display:none}
/* ФІКСОВАНА висота рядка. .vtag вищий за .vd (9.5px+8 padding+2 border ≈ 19.5 проти 15),
   тож рядок З бейджем був на ~4.5px вищим за рядок БЕЗ: 1 бейдж (якір) → 2 бейджі (пара)
   давало +4.5px списку і шіт підстрибував. Висота не залежить від вмісту рядка. */
#sh-period .vrow{display:flex;align-items:center;gap:10px;width:100%;height:44px;padding:0 13px;
  background:transparent;border:none;border-bottom:1px solid var(--border-subtle);
  font-family:var(--font);cursor:pointer;text-align:left}
[data-theme="dark"] #sh-period .vrow{border-bottom-color:var(--border)}
#sh-period .vrow:last-child{border-bottom:none}
#sh-period .vd{font:800 15px/1 var(--font);color:var(--text);font-variant-numeric:tabular-nums;letter-spacing:-.2px;flex:0 0 auto;min-width:48px}
#sh-period .vm{flex:1;min-width:0;font:600 11.5px/1 var(--font);color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
/* теги дзеркалять таблицю Динаміки: was = нейтральний (.well.was) · now = accent (.well.now) */
#sh-period .vtag{flex:0 0 auto;font:800 9.5px/1 var(--font);text-transform:uppercase;letter-spacing:.5px;padding:4px 7px;border-radius:7px;white-space:nowrap}
#sh-period .vtag.was{color:var(--text-2);background:var(--surface-2);border:1px solid var(--border)}
[data-theme="dark"] #sh-period .vtag.was{background:var(--surface-3)}
#sh-period .vtag.now{color:var(--accent-ink);background:color-mix(in srgb,var(--accent) 16%,var(--card));border:1px solid color-mix(in srgb,var(--accent) 38%,transparent)}
[data-theme="dark"] #sh-period .vtag.now{background:color-mix(in srgb,var(--accent) 24%,var(--surface-3));border-color:color-mix(in srgb,var(--accent) 45%,transparent)}
#sh-period .vrow.sel{background:color-mix(in srgb,var(--accent) 7%,transparent)}
[data-theme="dark"] #sh-period .vrow.sel{background:color-mix(in srgb,var(--accent) 12%,transparent)}
#sh-period .vrow.is-pressed{background:var(--surface-2)}
[data-theme="dark"] #sh-period .vrow.is-pressed{background:var(--surface-3)}

/* CTA-гама ПОРТОВАНА з білда 1:1 — .btn-copy (FILL) + .cf-cancel. Акцент/насиченість
   для цього класу кнопок уже залочені окремими бенчами; одна гама на всі первинні дії. */
#sh-period .pkcta{display:flex;gap:9px;margin:14px 12px 0}
#sh-period .pkcta button{flex:1;padding:14px 0;border-radius:12px;font:800 14px/1 var(--font);cursor:pointer;border:none;
  transition:transform .22s var(--spring),filter .12s ease,opacity .18s ease}
#sh-period .pkcta .pk-sec{background:var(--surface-3);color:var(--text)}
[data-theme="dark"] #sh-period .pkcta .pk-sec{background:color-mix(in srgb,var(--surface-3),#fff 3%)}
#sh-period .pkcta .pk-pri{color:#fff;
  background:linear-gradient(180deg,color-mix(in srgb,#fff 16%,var(--accent)),var(--accent));
  box-shadow:0 3px 10px -3px color-mix(in srgb,var(--accent) 27%,transparent),0 1px 2px rgba(20,50,42,.14)}
[data-theme="dark"] #sh-period .pkcta .pk-pri{background:linear-gradient(180deg,hsl(163 55% 34%),hsl(163 55% 30%));
  box-shadow:inset 0 1px 0 rgba(255,255,255,.10)}
#sh-period .pkcta button.is-pressed{transform:scale(.96);transition-duration:.06s}
#sh-period .pkcta .pk-pri.off{opacity:.42;pointer-events:none}
[data-theme="dark"] #sh-period .pkcta .pk-pri.off{opacity:.30}   /* на OLED .42 ще читалось як активна */

```

---

## §5 HTML-шар

### 5.1 Картка блоку — вставляти в кінець екрана налаштувань/меню

> Статичний рядок усередині — **коректний перший кадр** (стан «перевірка ще не відповіла»),
> а не заглушка за wsd 3.9: `renderMaint()` перебудовує вміст, підміни-миготіння немає.

```html
  <!-- NODE 2.2 · ОБСЛУГОВУВАННЯ. Вміст перебудовує renderMaint(); статичний рядок
       нижче — це КОРЕКТНИЙ перший кадр (стан idle: перевірка ще не відповіла),
       а не заглушка, тож підміни-миготіння немає. -->
  <div class="eb" id="mtEb">Обслуговування</div>
  <div class="gcard" id="mtCard">
    <div class="mi quiet">
      <span class="mi-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-2.6-6.4"/><polyline points="21 4 21 10 15 10"/></svg></span>
      <span class="mi-tx"><b id="mtIdleVer">Версія</b><span>Перевіряємо оновлення…</span></span>
      <span class="mi-act"></span>
    </div>
  </div>

  <div class="eb">Сеанс</div>
  <div class="gcard">
    <div class="mi pressable" onclick="openAbout()">
      <span class="mi-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg></span>
      <span class="mi-tx"><b>Про додаток</b><span id="aboutVer">Версія — шелл</span></span>
      <span class="mi-act"><span class="mi-chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></span></span>
    </div>
    <div class="mi danger pressable" onclick="clearData()">
      <span class="mi-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></span>
      <span class="mi-tx"><b id="clearLbl">Очистити всі дані</b><span id="clearSub">Усі аптеки та візити</span></span>
      <span class="mi-act"><span class="mi-chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></span></span>
    </div>
  </div>
</div>

```

### 5.2 Шіт інструкції — вставляти поруч з іншими `.sheet`

```html
<div class="sheet" id="sh-install" role="dialog" aria-label="Додати на екран Додому">
  <div class="grip"></div>
  <div class="ins-hd" id="insHd">Додати на екран Додому</div>
  <div class="ins-sub" id="insSub">Кілька кроків у Safari — далі StockCheck відкривається з робочого столу.</div>
  <div id="insBody"></div>
  <div class="ins-cta">
    <button class="ins-sec pressable" onclick="closeSheets()">Закрити</button>
    <button class="ins-pri pressable" onclick="closeSheets()">Готово</button>
  </div>
</div>

```

---

## §6 JS-шар

Вставляти **в кінець** скрипта, після оголошення `APP_BUILD` і шіт-функцій.

```javascript
/* ══════════════════════════════════════════════════════════════════════════════
   NODE 2.2 · ОБСЛУГОВУВАННЯ — самоперевірка версії + «Додати на екран Додому»
   Порт зі stage-bench maint_v3. Значення §2 самері (device-lock 29.07).
   Самодостатній модуль: назовні віддає лише обгортки над openSheet/closeSheet/
   closeSheets — тіла наявних функцій не переписуються (wsd 10.7).
   ══════════════════════════════════════════════════════════════════════════════ */
(function(){
  var $=function(id){return document.getElementById(id);};

  /* ── гліфи: інлайн-SVG, без емодзі (правило продукту) ────────────────────── */
  var MG={
    refresh:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-2.6-6.4"/><polyline points="21 4 21 10 15 10"/></svg>',
    check:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><polyline points="8.5 12.2 11 14.7 15.7 9.6"/></svg>',
    cloudoff:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 16.5a3.5 3.5 0 0 0-1.6-6.6A5.5 5.5 0 0 0 7 8.2"/><path d="M6.5 9A4.5 4.5 0 0 0 7 18h9"/><line x1="3" y1="3" x2="21" y2="21"/></svg>',
    home:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z"/></svg>',
    share:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 15V3.5"/><polyline points="8 7 12 3 16 7"/><path d="M6 12H4.6A1.6 1.6 0 0 0 3 13.6v6.8A1.6 1.6 0 0 0 4.6 22h14.8a1.6 1.6 0 0 0 1.6-1.6v-6.8A1.6 1.6 0 0 0 19.4 12H18"/></svg>',
    scroll:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="2.5"/><line x1="8" y1="8" x2="16" y2="8"/><line x1="8" y1="12" x2="16" y2="12"/><polyline points="9.5 16 12 18.5 14.5 16"/></svg>',
    add:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
    dots:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><circle cx="8" cy="12" r=".9" fill="currentColor"/><circle cx="12" cy="12" r=".9" fill="currentColor"/><circle cx="16" cy="12" r=".9" fill="currentColor"/></svg>',
    warn:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4.5 21 20H3z"/><line x1="12" y1="10" x2="12" y2="14.5"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    chev:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>'
  };

  /* ── стан. env НЕ зберігається — обчислюється щоразу (Д4: детект спроможності,
        не платформи; факт події важливіший за будь-який запам'ятований прапорець) ── */
  var MT={ ver:'idle', newVer:'', newBuild:'', bip:null, installed:false, pending:null, last:0 };

  function mtStandalone(){
    try{ if(window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) return true; }catch(e){}
    return navigator.standalone===true;
  }
  function mtIOS(){
    return /iP(hone|od|ad)/.test(navigator.userAgent)
        || (navigator.platform==='MacIntel' && navigator.maxTouchPoints>1);   /* iPad з desktop-UA */
  }
  /* [07.2026] Telegram-webview — ЄДИНИЙ дозволений UA-виняток (Д2/Д4): пункту
     «На Початковий екран» там немає взагалі, і жоден API про це не повідомляє.
     Три сигнали, бо iOS-webview не завжди несе «Telegram» у UA.
     Промах деградує м'яко: користувач отримає звичайну iOS-інструкцію без кроку 0.
     Перевірити при мажорному оновленні Telegram. */
  function mtTG(){
    try{
      if(/Telegram/i.test(navigator.userAgent)) return true;
      if(typeof window.TelegramWebviewProxy!=='undefined') return true;
      if(window.TelegramWebview) return true;
    }catch(e){}
    return false;
  }
  function mtEnv(){
    if(MT.installed || mtStandalone()) return 'standalone';
    if(MT.bip) return 'android';                       /* подія прилетіла → КНОПКА */
    if(mtIOS()) return mtTG() ? 'telegram' : 'safari';
    return 'android_np';                               /* не iOS, події не було → інструкція */
  }

  /* ── рядок версії: варіант B — живе завжди, показує стан ─────────────────── */
  function mtUpdRow(){
    if(MT.ver==='upd'){
      return '<div class="mi upd pressable" id="miUpd"><span class="mi-ic">'+MG.refresh+'</span>'
        +'<span class="mi-tx"><b>Оновити до '+esc(MT.newVer||'нової версії')+'</b>'
        +'<span>Зараз '+esc(APP_BUILD.ver)+' \u00b7 з перезапуском</span></span>'
        +'<span class="mi-act"><span class="doact">Оновити</span></span></div>';
    }
    if(MT.ver==='ok'){
      return '<div class="mi quiet"><span class="mi-ic">'+MG.check+'</span>'
        +'<span class="mi-tx"><b>Версія актуальна</b>'
        +'<span>'+esc(APP_BUILD.ver)+' \u00b7 щойно перевірено</span></span>'
        +'<span class="mi-act"></span></div>';
    }
    if(MT.ver==='fail'){
      return '<div class="mi warnst pressable" id="miRetry"><span class="mi-ic">'+MG.cloudoff+'</span>'
        +'<span class="mi-tx"><b>Не вдалося перевірити</b>'
        +'<span>Немає зв\u0027язку \u00b7 спробує пізніше</span></span>'
        +'<span class="mi-act"><span class="doact">Ще раз</span></span></div>';
    }
    return '<div class="mi quiet"><span class="mi-ic">'+MG.refresh+'</span>'
      +'<span class="mi-tx"><b id="mtIdleVer">Версія '+esc(APP_BUILD.ver)+'</b>'
      +'<span>Перевіряємо оновлення\u2026</span></span>'
      +'<span class="mi-act"></span></div>';
  }

  function mtInsRow(){
    var env=mtEnv();
    if(env==='android'){
      return '<div class="mi pressable" id="miIns"><span class="mi-ic">'+MG.home+'</span>'
        +'<span class="mi-tx"><b>Встановити застосунок</b><span>Запуск без браузера</span></span>'
        +'<span class="mi-act"><span class="doact">Встановити</span></span></div>';
    }
    var sub = env==='telegram'   ? 'Спершу відкрити в Safari'
            : env==='android_np' ? 'Через меню браузера'
            :                      'Без адресного рядка';
    return '<div class="mi pressable" id="miIns"><span class="mi-ic">'+MG.home+'</span>'
      +'<span class="mi-tx"><b>Додати на екран Додому</b><span>'+sub+'</span></span>'
      +'<span class="mi-act"><span class="mi-chev">'+MG.chev+'</span></span></div>';
  }

  function renderMaint(){
    var card=$('mtCard'); if(!card) return;
    var h=mtUpdRow();
    if(mtEnv()!=='standalone') h+=mtInsRow();          /* у standalone рядок зайвий */
    card.innerHTML=h;
    var u=$('miUpd');   if(u) u.addEventListener('click',mtDoUpdate);
    var r=$('miRetry'); if(r) r.addEventListener('click',function(){ mtCheck(true); });
    var i=$('miIns');   if(i) i.addEventListener('click', mtEnv()==='android' ? mtDoInstall : openInstall);
    mtApplyDot();
  }

  /* ── крапка: тихий сигнал апдейта на всіх трьох кебабах ──────────────────── */
  function mtApplyDot(){
    var on = MT.ver==='upd';
    var list=document.querySelectorAll('.js-kdot');
    Array.prototype.forEach.call(list,function(d){ d.classList.toggle('on',on); });
  }

  /* ── інструкція ─────────────────────────────────────────────────────────── */
  function mtSteps(){
    var env=mtEnv(), a=[];
    if(env==='android_np'){
      /* назви пунктів НЕ цитуємо дослівно — скріншота Android немає (Д2) */
      a.push({g:MG.dots,t:'Меню браузера — «⋮» вгорі праворуч',
        s:'Три крапки в правому верхньому куті Chrome.'});
      a.push({g:MG.home,t:'Пункт про встановлення застосунку',
        s:'Формулювання різниться між версіями браузера; це пункт із іконкою додавання на екран.'});
      a.push({g:MG.add,t:'Підтвердити',
        s:'Іконка стане на головний екран; далі запуск звідти.'});
      return a;
    }
    /* кроки iOS — із вбудованим запасним шляхом, БЕЗ гілки по версії iOS:
       лейаут Safari обирає користувач, не версія, і детектувати його нічим */
    a.push({g:MG.share,t:'Тап на «Поділитися»',
      s:'Стрілка вгору в нижній панелі. Не бачиш стрілки — тапни «…» біля адреси, там «Поділитися».'});
    a.push({g:MG.scroll,t:'Знайти «На Початковий екран»',
      s:'Прогорни список дій. Немає в списку — тапни «Ще» в кінці ряду.'});
    a.push({g:MG.add,t:'«Додати» вгорі праворуч',
      s:'Якщо в діалозі є перемикачі — не чіпай їх, лиши як є.'});
    return a;
  }
  function renderInstall(){
    var body=$('insBody'); if(!body) return;
    var env=mtEnv(), h='';
    if(env==='telegram'){                              /* крок 0 — банером, не кроком */
      h+='<div class="step0b"><span class="s0i">'+MG.warn+'</span>'
        +'<span class="s0t">Спершу відкрий у Safari'
        +'<span>Ти зараз у браузері Telegram — у ньому пункту «На Початковий екран» немає взагалі. '
        +'Тап «…» внизу праворуч → «Відкрити в Safari».</span></span></div>';
    }
    h+='<div class="gcard">';
    mtSteps().forEach(function(s){
      h+='<div class="stp"><span class="gl">'+s.g+'</span>'
        +'<span class="tx">'+s.t+'<span>'+s.s+'</span></span></div>';
    });
    h+='</div>';
    body.innerHTML=h;
    $('insHd').textContent = env==='android_np' ? 'Встановити застосунок' : 'Додати на екран Додому';
    $('insSub').textContent = env==='telegram'
      ? 'У Telegram потрібен зайвий крок — інакше пункту просто не буде.'
      : env==='android_np'
        ? 'Браузер не запропонував встановлення сам — тоді через його меню.'
        : 'Кілька кроків у Safari — далі StockCheck відкривається з робочого столу.';
  }

  /* ── ЗАМОРОЗКА (Д5): асинхронний результат не вставляє рядок під палець ──── */
  function mtAnySheet(){ return !!document.querySelector('.sheet.on'); }
  function mtSet(k,v){
    if(mtAnySheet()){ MT.pending=MT.pending||{}; MT.pending[k]=v; return; }
    MT[k]=v; mtApply();
  }
  function mtApply(){ renderMaint(); renderInstall(); }
  function mtFlush(){
    if(!MT.pending) return;
    var p=MT.pending; MT.pending=null;
    Object.keys(p).forEach(function(k){ MT[k]=p[k]; });
    mtApply();
  }
  /* Гард зливу. closeSheet() у продукті — це ще й ПЕРШИЙ КРОК передачі
     меню→About / меню→confirm / меню→install. Злити стан прямо на closeSheet
     означало б перебудувати рядок за 120 мс до появи наступного шіта — рівно те,
     від чого заморозка й захищає. 320 мс перекриває хід шіта (260) і паузу
     передачі (120), а умова «жоден шіт не відкритий» відрізняє справжнє
     закриття від проміжного. */
  var mtFlushT=null;
  function mtScheduleFlush(){
    clearTimeout(mtFlushT);
    mtFlushT=setTimeout(function(){ if(!mtAnySheet()) mtFlush(); },320);
  }

  /* ── САМОПЕРЕВІРКА ВЕРСІЇ ───────────────────────────────────────────────── */
  var MT_MIN=5*60*1000;                                /* тротлінг visibilitychange */
  function mtCheck(force){
    var now=Date.now();
    if(!force && now-MT.last<MT_MIN) return;
    MT.last=now;
    if(!window.fetch){ mtSet('ver','fail'); return; }
    /* location.pathname, а не './index.html': у standalone start_url — тека,
       і pathname віддає той самий документ у обох випадках, не залежачи від імені файлу */
    fetch(location.pathname+'?cb='+now,{cache:'no-store'})
      .then(function(r){ if(!r.ok) throw new Error('http'); return r.text(); })
      .then(function(txt){
        /* ⚠ ПАСТКА САМО-ЗБІГУ: сторінка читає власний текст, у якому лежить і цей
           код. Патерн зібраний конкатенацією — суцільного літерала в файлі не
           існує, тож знайти сам себе він фізично не може. Порядок рядків
           (APP_BUILD вище) — слабша, друга страховка: її ламає будь-який патч. */
        var q=String.fromCharCode(39);
        var reB=new RegExp('build'+'\\s*:\\s*'+q+'([^'+q+']+)'+q);
        var reV=new RegExp('ver'+'\\s*:\\s*'+q+'(v[0-9][^'+q+']*)'+q);
        var mb=reB.exec(txt); if(!mb) throw new Error('nomatch');
        var mv=reV.exec(txt);
        MT.newBuild=mb[1]; MT.newVer=mv?mv[1]:'';
        mtSet('ver', mb[1]===APP_BUILD.build ? 'ok' : 'upd');
      })
      .catch(function(){ mtSet('ver','fail'); });
  }
  function mtDoUpdate(){
    var v=MT.newBuild||('t'+Date.now());
    location.replace(location.pathname+'?v='+encodeURIComponent(v));
  }

  /* ── ANDROID: детект по ФАКТУ події, не по бренду/версії (Д4) ───────────── */
  window.addEventListener('beforeinstallprompt',function(e){
    e.preventDefault();                                /* перехоплюємо банер Chrome (§1-7) */
    mtSet('bip',e);
  });
  window.addEventListener('appinstalled',function(){
    mtSet('installed',true); mtSet('bip',null);        /* рядок зникає без перезавантаження */
  });
  function mtDoInstall(){
    var e=MT.bip; if(!e){ openInstall(); return; }
    try{ e.prompt(); }catch(err){}
    var done=function(){ mtSet('bip',null); };         /* подія одноразова, повторно не годиться */
    if(e.userChoice && e.userChoice.then) e.userChoice.then(done,done); else done();
  }

  /* ── ДВИГУН ЕФЕКТУ duo (Д3): грає ПІСЛЯ осідання шіта, ніколи одночасно ──
     transitionend — основний канал, setTimeout(340) — страхувальний (подія не
     приходить, коли переходити не було чому: шіт уже відкритий, reduced-motion,
     переривання), fxArmed гарантує рівно один запуск із двох. */
  var mtSheet=$('sheet'), fxArmed=false, fxT=null, fxClr=null;
  var FX_DELAY=120, FX_TOTAL=990*3+400;
  function fxStrip(){ document.body.classList.remove('fx-duo'); }
  function mtDisarm(){ fxArmed=false; clearTimeout(fxT); fxStrip(); }
  function fxFire(){
    if(!fxArmed) return;
    fxArmed=false; clearTimeout(fxT);
    if(MT.ver!=='upd') return;                         /* коли=every, але лише за реального апдейта */
    setTimeout(function(){
      if(!mtSheet.classList.contains('on')) return;
      fxStrip(); void document.body.offsetWidth;       /* reflow — інакше animation не рестартує */
      document.body.classList.add('fx-duo');
      clearTimeout(fxClr); fxClr=setTimeout(fxStrip,FX_TOTAL);
    },FX_DELAY);
  }
  if(mtSheet){
    mtSheet.addEventListener('transitionend',function(e){
      if(e.target!==mtSheet || e.propertyName!=='transform') return;
      if(!mtSheet.classList.contains('on')) return;    /* закриття — не тригер */
      fxFire();
    });
  }

  /* ── шіт інструкції: передача меню→install за зразком A58 ───────────────── */
  function openInstall(){
    mtDisarm();
    closeSheet();
    setTimeout(function(){
      $('scrim').classList.add('on');
      $('sh-install').classList.add('on');
    },120);
  }

  /* ── обгортки над наявними функціями (10.7: інтерфейс, не переписування) ── */
  var _openSheet=openSheet;
  openSheet=function(){
    _openSheet.apply(this,arguments);
    fxArmed=true; clearTimeout(fxT); fxT=setTimeout(fxFire,340);
  };
  var _closeSheet=closeSheet;
  closeSheet=function(){
    _closeSheet.apply(this,arguments);
    mtDisarm(); mtScheduleFlush();
  };
  var _closeSheets=closeSheets;
  closeSheets=function(){
    _closeSheets.apply(this,arguments);
    var si=$('sh-install'); if(si) si.classList.remove('on');
    mtDisarm(); mtScheduleFlush();
  };

  /* ── старт ──────────────────────────────────────────────────────────────── */
  document.addEventListener('visibilitychange',function(){
    if(document.visibilityState==='visible') mtCheck(false);
  });
  mtApply();
  setTimeout(function(){ mtCheck(true); },800);        /* не конкуруємо з першим кадром */
})();

</script>
</body>
</html>
```

---

## §7 Чек-ліст порту в новий продукт

- [ ] `APP_BUILD` оголошено **до** модуля, формат `{ver, build, date}` (wsd 10.6)
- [ ] `grep '\.ins-'` у цільовому файлі → **0** збігів до вставки (колізія класів)
- [ ] `grep 'fx-duo'` → 0 збігів до вставки
- [ ] `openSheet`/`closeSheet`/`closeSheets` існують і мають очікувану сигнатуру (wsd 10.7)
- [ ] вузли `#mtCard` · `#mtEb` · `#sh-install` присутні в розмітці
- [ ] регекс самоперевірки збігається з **фактичним** написанням `APP_BUILD` у цільовому файлі
      (пробіли й лапки в об'єкті відрізняються між продуктами — звірити грепом, не оком)
- [ ] `node --check` після вставки
- [ ] device-тест **трьох** оточень: Safari · webview · standalone PWA, **обидві** теми
- [ ] `display-mode:standalone` для детекту режиму — **НЕ** `--sab` і не `navigator.standalone`
      як єдине джерело (Cookbook A11/A12)

---

## §8 Відомі межі

1. **Single-file залежність** — §0. При бандлі механізм самоперевірки переписується.
2. **`beforeinstallprompt` відсутній у Safari** `[08.2026]`. Це не баг, а межа платформи;
   гілка iOS показує інструкцію. **Перевірити при наступному мажорному iOS** (wsd 12.10).
3. **Іконка робочого столу — статичний ресурс оболонки ОС**, узятий у момент встановлення.
   Застосунок не має каналу впливу на неї після встановлення (Cookbook A75).
4. **Вікно `max-age` хоста** — §1. Не діра, але й не нуль: між деплоєм і протуханням кешу
   користувач може бачити стару версію після kill.

---

## §9 Матриця

`StockCheck_maint_jsdom_matrix.js` — 61 твердження, покриває стани блоку, freeze/pending
з гардом 320 ms, гілки оточення. При порті — адаптувати селектори, не переписувати логіку.
