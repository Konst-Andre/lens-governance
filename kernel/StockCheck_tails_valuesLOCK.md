> живе доки: назавжди (вічне, wsd 1.8) — значення хвостів StockCheck

# StockCheck · Tails H1/H2/H3 — VALUES LOCK ✅

> Device-verified: **обидві теми, оком** (Konst, 24.07.2026) · стенд `StockCheck_tails_stagebench_v1.html`
> Copy-bet: `dark · xs :: sheetBaseD=1 · gcLiftD=2 · ridgeD=4 · bdD=6 · micD=9 ·`
> `sheetBaseL=0 · gcTintL=1 · dropL=6 · bdL=45 · micL=80 · gcRad=14 ·`
> `pill=0 · cntGap=0 · cntSize=11 · cntW=700 · cntOp=100`
> Ціль порту: `StockCheck_port_b18.html` → `b19` · тоді Фармастор v2 §11.

---

## H2 · Картки груп меню — читабельні на темній

**Принцип (canon-ready):** видимість `.gcard` на OLED вирішується **опусканням підлоги шіта**,
НЕ підйомом картки. Опустив підлогу → контраст росте, картка лишається спокійною (без неон-ризику, A45).
Підняв картку → повзе до неону. Konst-вибір довів другий шлях зайвим.

### Темна тема
| важіль | значення | CSS |
|---|---|---|
| база `.sheet` | **card** (було surface-2) | `background:var(--card)` |
| `.gcard` fill | +2% #fff у surface-3 | `color-mix(in srgb,#fff 2%,var(--surface-3))` |
| `.gcard` ridge | inset білий .04 | `inset 0 1px 0 rgba(255,255,255,.04)` |
| `.gcard` border | білий .06 | `rgba(255,255,255,.06)` |
| `.mi-ic` lift | +9% #fff над gcBg | `color-mix(#fff 9%,gcBg)` (вкладено) |

**Результат ΔL* шіт↔картка:** 2.4 → **~6.8** (комфортно-читабельно).

### Світла тема
Проблеми видимості не мала (ΔL*≈4.5 тон уже тягне). Правки — ледь-ледь, «белт поверх тону».
| важіль | значення | CSS |
|---|---|---|
| база `.sheet` | card #fff (без змін) | — |
| `.gcard` fill | +1% text у surface-3 | `color-mix(in srgb,var(--text) 1%,var(--surface-3))` |
| `.gcard` drop | 6px | `0 3px 6px -6px rgba(20,50,42,.30)` |
| `.gcard` border | 45% border у border-subtle | `color-mix(in srgb,var(--border) 45%,var(--border-subtle))` |
| `.mi-ic` fill | 80% #fff (було 55) | `color-mix(in srgb,#fff 80%,var(--surface-3))` |

### Спільне
- `gcRad` = **14** (без змін)

**⚠️ Свідома відмова від канону (записати):** `dropL=6` на світлій < A66-порогу «drop ≥14px».
Обґрунтування: світла тема несе елевацію **тоном** (ΔL*≈4.5), drop лише шепіт-белт. НЕ «лагодити» назад до 14.

---

## H1 · Лічильник статус-чіпа — де-пігулено

**Корінь:** `.bc.filt .cnt` успадковував пігулку від базового `.cnt` (min-width:42 · padding · border ·
bg · radius). Роздувало `.bc` +6px висоти й крав +27px ширини → сусідня область у «Дні…».

**Фікс (скоуп строго `.bc.filt .cnt`, базу НЕ чіпати — вона потрібна іншим лічильникам):**
```css
.bc.filt .cnt{min-width:0;padding:0;border:0;background:none;border-radius:0;
  margin-left:0;font-size:11px;font-weight:700;color:var(--muted);font-variant-numeric:tabular-nums}
```
Специфічність `.bc.filt .cnt` (0,3,0) > `[data-theme=dark] .cnt` (0,2,0) → `background:none` тримається в
ОБОХ темах одним правилом. Дарк-оверрайд бази не потрібен.

**Base `.cnt` лишається пігулкою** — її використовують `.ebrow .cnt` (р.1895) і `#s-cmp .ebrow .cnt` (свій блок).

---

## H3 · About — A58 grouped-card

Успадковує матеріал H2 (`.gcard` уже полагоджено) — окремих важелів не потребує.
Структура: eyebrow «Збірка» → `.gcard` з kv-рядками (Версія/Білд/Дата) → eyebrow «Автор» →
`.gcard` (Konst.Andre + Telegram-рядок). Плоскі `.about-row` зняти.
**Бонус-чистка:** логотип-літера у StockCheck = `SC`, не хардкод `Ф`; `console.log` бренд-рядок.

---

## Порт назад у Фармастор v2 §11

- **§11.1 (H1)** — фікс ідентичний, порт 1:1.
- **§11.3 (H2)** — **переписати діагноз**: не translucency, а Δ-тон сусідніх щаблів + відсутній ridge.
  Рішення «опусти підлогу шіта» переносне. Перевірити токени Фармастора: чи там `.sheet`=surface-2, `.gcard`=surface-3.
- **§11.2 (H3 About)** — A58-форма переносна; у Фармастора логотип `Ф` **правильний** (чистку не переносити).

**Канон-дельта Cookbook:** A58/A66 доповнити принципом «OLED-видимість вкладеної картки = опустити підлогу
контейнера, не піднімати картку (A45 anti-neon)». ΔL*-орієнтир: <3 слабко · 3–4.5 межа · ≥4.5 читається.
