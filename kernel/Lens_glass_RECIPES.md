# Рецепти скла — GlassKit 1.41 (MIT): як побудовано, токени обох тем, крапля, правила

> живе доки: продукти Lens будують скляний інтерфейс; нова мажорна версія GlassKit — новий витяг (той самий метод, §0), старий → `archive/`.
> читається коли: будую чи приміряю скляний елемент у будь-якому продукті (капсула · таби й крапля · кнопки й FAB · перемикач · випадайки · щити · фокус поля · сайдбар · картка) і треба знати, **як це зроблено** й що в CSS існує саме заради Safari/WebKit · не читається: цілком і на старті — точково за «Змістом».
> дім: `kernel/` (крос-Lens: знання не має загинути разом із продуктом — тест wsd 1.19) · створено: 21.11.2026, EquipLens S40 («так з підсиленням» Konst: «перенести готове, щоб не загубилось, потім адаптувати… щоб мій агент розумів, як працювати зі склом на WebKit»).
> **Межа:** тут — чуже, дослівно; **наше** (правила з вироків, адаптація під токени продукту) — у довіднику матеріалу продукту, перший — `EquipLens:lens/EquipLens_MATERIAL.md`. Розбір GlassKit і вирок «бібліотеку не беремо, беремо CSS-ідеї» — `kernel/Lens_fx_candidates.md` FX-5 (крапля — FX-5f, спливні — FX-5g). Кукбук (A100–A102 про край і світлотінь) — старший за чужий рецепт: рецепт — точка старту, рішення — рецепт ⟂ світ ⟂ замір.

## §0 Джерела, метод, верність

| джерело | що в ньому | розмір |
|---|---|---|
| npm `@jungherz-de/glasskit` 1.41.0 — https://unpkg.com/@jungherz-de/glasskit@1.41.0/glasskit.css | **як побудовано**: токени тем, кожен компонент, `-webkit-` і `@supports` | 231 130 байт · завантажено 21.11.2026 |
| той самий пакет — https://unpkg.com/@jungherz-de/glasskit@1.41.0/SKILL.md | довідник для ШІ: токени таблицями, правила й типові помилки, композиції (дешборд, бек-офіс із сайдбаром) | 190 657 байт · завантажено 21.11.2026 |
| той самий пакет — https://unpkg.com/@jungherz-de/glasskit@1.41.0/glasskit-droplet.js | **крапля** — механіка | 13 387 байт · завантажено 21.11.2026 |
| https://raw.githubusercontent.com/JUNGHERZ/GlassKit-Elements/main/SKILL.md (коміт `95ef476`, 19.11.2026) | API вебкомпонентів (атрибути, події, стани) — **жодного `backdrop-filter`**: «як будується» тут нема; взято лише ядро понять, таби й правила | 198 580 байт |

**Метод (повторюваний).** Читав не Opus, а Haiku 5.5 (`claude -p --model haiku --effort medium --tools ""`, файл у запиті) — три прогони паралельно; Opus читав лише контрольні місця й підсумки. **Верність — машиною:** кожне CSS/JS-оголошення з блоків коду витягу шукається дослівно (без пробілів) у джерелах: §1 — 805 з 805, §2 — 32 з 32, §3 — 11 з 11 CSS (один «✗» — рядок JS `new CSSStyleSheet()`, не оголошення). Контрольне читання Opus (капсула, поле з фокусом, перемикач, токени) — збіг значень. **Покриття** — 11 предметів запиту, усі є. **Не перевірено машиною:** пояснення українською (перефраз haiku) і повнота списку «Неочевидне для WebKit» (сам витяг каже: «не повний»). Ціна й порівняння — `EquipLens:sessions/EquipLens_session_summary_S40_BG.md` §1 рядок 43.

**Як брати в продукт.** Числа тут — GlassKit, не наші: у продукт — лише через рядок адаптації в довіднику матеріалу (токен GlassKit → токен продукту → вирок пристрою). Ліцензія MIT вимагає зберегти позначку нижче в кожній копії суттєвої частини коду.

<details><summary>Ліцензія GlassKit (MIT) — дослівно</summary>

```text
MIT License

Copyright (c) 2026 Jungherz GmbH

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
</details>

<!-- ratchet-ok: розділи §1–§3 — дослівний витяг джерела (перевірений машиною), читаються точково за «Змістом»; різати — псувати витяг; нова версія GlassKit — новий витяг, старий в archive/ -->

## Зміст

§1 Як побудовано (`glasskit.css`): токени обох тем · капсула й `.glass-nav` · плаваючі таби й `--droplet` · кнопки й FAB (`.glass-tab-bar__accessory`) · перемикач · `.glass-select`, popover, tooltip, menu · overlay, modal, sheet · фокус поля (input, textarea, search) · сайдбар, rail, top bar · картка · WebKit і доступність · «Неочевидне для WebKit» (16 пунктів)
§2 Крапля (`glasskit-droplet.js`) і правила GlassKit-Elements
§3 Токени таблицями, правила й типові помилки, композиції (SKILL.md пакета)

## §1 Як побудовано — витяг з `glasskit.css`

## GlassKit 1.41.0: рецепти конструкцій

Джерело: `glasskit.css` (v1.41.0, Jungherz GmbH, MIT). Фрагменти CSS скопійовано з наданого джерела без змін. Там, де в джерелі чогось немає, написано «нема в джерелі».

**Загальне.** Темна тема є за замовчуванням (`:root, [data-theme="dark"]`), світла вмикається через `[data-theme="light"]`. Окремих світлих блоків для компонентів немає: компоненти читають токени, тож світла тема керується токенами. Виняток: `[data-theme="light"] .glass-theme-toggle` (перемикання іконок).

---

### 1. Дизайн-токени

#### 1.1 Скляні поверхні

**Темна тема** (`:root, [data-theme="dark"]`):

```css
--gl-surface-1:            rgba(255, 255, 255, 0.08);
--gl-surface-2:            rgba(255, 255, 255, 0.10);
--gl-surface-3:            rgba(255, 255, 255, 0.14);
--gl-surface-4:            rgba(255, 255, 255, 0.16);
--gl-surface-5:            rgba(255, 255, 255, 0.22);
--gl-surface-milk:         rgba(255, 255, 255, 0.55);
--gl-surface-milk-strong:  rgba(255, 255, 255, 0.75);
--gl-surface-overlay:      rgba(0, 0, 0, 0.50);

--gl-card-glow-top:        rgba(255, 255, 255, 0.32);
--gl-card-glow-mid:        rgba(255, 255, 255, 0.22);
--gl-card-glow-low:        rgba(255, 255, 255, 0.14);
--gl-card-glow-bottom:     rgba(255, 255, 255, 0.08);
--gl-dialog-glow-top:      var(--gl-card-glow-mid);
--gl-dialog-well:          rgba(0, 0, 0, 0.10);
--gl-dialog-raised:        var(--gl-surface-3);
--gl-dialog-control:       var(--gl-surface-1);
```

**Світла тема** (`[data-theme="light"]`):

```css
--gl-surface-1:            rgba(255, 255, 255, 0.50);
--gl-surface-2:            rgba(255, 255, 255, 0.60);
--gl-surface-3:            rgba(255, 255, 255, 0.70);
--gl-surface-4:            rgba(255, 255, 255, 0.75);
--gl-surface-5:            rgba(255, 255, 255, 0.85);
--gl-surface-milk:         rgba(255, 255, 255, 0.85);
--gl-surface-milk-strong:  rgba(255, 255, 255, 0.92);
--gl-surface-overlay:      rgba(0, 0, 0, 0.25);

--gl-card-glow-top:        rgba(255, 255, 255, 0.90);
--gl-card-glow-mid:        rgba(255, 255, 255, 0.78);
--gl-card-glow-low:        rgba(255, 255, 255, 0.65);
--gl-card-glow-bottom:     rgba(255, 255, 255, 0.50);
--gl-dialog-glow-top:      initial;
--gl-dialog-well:          initial;
--gl-dialog-raised:        initial;
--gl-dialog-control:       initial;
--gl-badge-selected-color: initial;
```

#### 1.2 Кольори тексту та акцент

**Темна:**

```css
--gl-color-primary:        #f5a623;
--gl-color-primary-dark:   #d4692a;
--gl-color-primary-mid:    color-mix(in srgb, var(--gl-color-primary) 32%, var(--gl-color-primary-dark));
--gl-color-bg-dark:        #0e2530;
--gl-color-bg-mid:         #1a3d4e;
--gl-color-bg-light:       #1b3e50;
--gl-color-text:           #ffffff;
--gl-color-text-muted:     rgba(255, 255, 255, 0.65);
--gl-color-text-heading:   #ffffff;
--gl-color-primary-on-glass: color-mix(in srgb, var(--gl-color-primary-text) 60%, #ffffff);
--gl-color-primary-text:   var(--gl-color-primary);
--gl-color-on-primary:     #ffffff;
```

**Світла:**

```css
--gl-color-primary:        #e8852d;
--gl-color-primary-dark:   #c96a1e;
--gl-color-primary-mid:    color-mix(in srgb, var(--gl-color-primary) 52%, var(--gl-color-primary-dark));
--gl-color-bg-dark:        #e8ecf1;
--gl-color-bg-mid:         #f0f4f8;
--gl-color-bg-light:       #f5f7fa;
--gl-color-text:           #1a2a36;
--gl-color-text-muted:     rgba(26, 42, 54, 0.68);
--gl-color-text-heading:   #0f1f2a;
--gl-color-primary-on-glass: var(--gl-color-primary-text);
--gl-color-primary-text:   var(--gl-color-primary);
```

Іконки, темна / світла:

```css
/* темна */
--gl-icon-default:         rgba(255, 255, 255, 0.6);
--gl-icon-muted:           rgba(255, 255, 255, 0.45);
--gl-icon-strong:          rgba(255, 255, 255, 0.8);
--gl-icon-on-secondary:    #1a3a4a;
--gl-icon-on-tertiary:     rgba(255, 255, 255, 0.6);

/* світла */
--gl-icon-default:         rgba(26, 42, 54, 0.65);
--gl-icon-muted:           rgba(26, 42, 54, 0.55);
--gl-icon-strong:          rgba(26, 42, 54, 0.80);
--gl-icon-on-secondary:    #1a3a4a;
--gl-icon-on-tertiary:     rgba(26, 42, 54, 0.65);
```

#### 1.3 Межі, фокус

**Темна:**

```css
--gl-border-subtle:        rgba(255, 255, 255, 0.18);
--gl-border-medium:        rgba(255, 255, 255, 0.30);
--gl-border-strong:        rgba(255, 255, 255, 0.40);
--gl-border-milk:          rgba(255, 255, 255, 0.60);
--gl-border-warm:          color-mix(in srgb, color-mix(in srgb, var(--gl-color-primary) 68%, #ffffff) 35%, transparent);
--gl-focus-ring:           color-mix(in srgb, var(--gl-color-primary) 15%, #ffffff);
--gl-border-focus:         var(--gl-focus-ring);
```

**Світла:**

```css
--gl-border-subtle:        rgba(0, 0, 0, 0.08);
--gl-border-medium:        rgba(0, 0, 0, 0.12);
--gl-border-strong:        rgba(0, 0, 0, 0.15);
--gl-border-milk:          rgba(0, 0, 0, 0.10);
--gl-border-warm:          color-mix(in srgb, var(--gl-color-primary) 30%, transparent);
--gl-focus-ring:           var(--gl-color-primary-on-surface);
--gl-border-focus:         var(--gl-focus-ring);
```

`--gl-color-primary-on-surface` (світла) = `color-mix(in srgb, var(--gl-color-primary) 60%, #000000)`.

#### 1.4 Блюр, радіуси (однакові в обох темах)

```css
--gl-blur:                 24px;
--gl-blur-light:           16px;
--gl-blur-soft:            12px;
--gl-blur-heavy:           40px;

--gl-radius-pill:          50%;
--gl-radius-full:          9999px;
--gl-radius-card:          24px;
--gl-radius-btn:           16px;
--gl-radius-input:         14px;
--gl-radius-sm:            12px;
--gl-radius-xs:            8px;
```

У світлій темі блок блюру й радіусів не перевизначено.

#### 1.5 Тіні

**Темна:**

```css
--gl-shadow-card:          0 8px 32px rgba(0, 0, 0, 0.18);
--gl-shadow-btn:           0 4px 16px rgba(0, 0, 0, 0.12);
--gl-shadow-btn-primary:   0 6px 24px color-mix(in srgb, var(--gl-color-primary-mid) 35%, transparent),
                           0 2px 8px rgba(0, 0, 0, 0.15);
--gl-shadow-glow:          0 2px 12px rgba(255, 255, 255, 0.08),
                           0 4px 16px rgba(0, 0, 0, 0.15);
--gl-shadow-modal:         0 24px 80px rgba(0, 0, 0, 0.4),
                           0 8px 32px rgba(0, 0, 0, 0.2);
--gl-shadow-toast:         0 8px 32px rgba(0, 0, 0, 0.25);
--gl-shadow-focus:         0 0 0 2px var(--gl-focus-ring);
```

**Світла:**

```css
--gl-shadow-card:          0 4px 20px rgba(0, 0, 0, 0.06);
--gl-shadow-btn:           0 2px 10px rgba(0, 0, 0, 0.06);
--gl-shadow-btn-primary:   0 4px 16px color-mix(in srgb, var(--gl-color-primary) 25%, transparent),
                           0 2px 6px rgba(0, 0, 0, 0.08);
--gl-shadow-glow:          0 2px 8px rgba(0, 0, 0, 0.05),
                           0 4px 12px rgba(0, 0, 0, 0.04);
--gl-shadow-modal:         0 16px 48px rgba(0, 0, 0, 0.12),
                           0 4px 16px rgba(0, 0, 0, 0.08);
--gl-shadow-toast:         0 4px 20px rgba(0, 0, 0, 0.10);
--gl-shadow-focus:         0 0 0 2px var(--gl-focus-ring);
```

**Внутрішнє світло (inset highlights).**

Темна:

```css
--gl-inset-subtle:         inset 0 1px 1px rgba(255, 255, 255, 0.10);
--gl-inset-medium:         inset 0 1px 1px rgba(255, 255, 255, 0.15);
--gl-inset-strong:         inset 0 1px 2px rgba(255, 255, 255, 0.25);
--gl-inset-milk:           inset 0 1px 2px rgba(255, 255, 255, 0.40);
```

Світла:

```css
--gl-inset-subtle:         inset 0 1px 1px rgba(255, 255, 255, 0.60);
--gl-inset-medium:         inset 0 1px 1px rgba(255, 255, 255, 0.70);
--gl-inset-strong:         inset 0 1px 2px rgba(255, 255, 255, 0.80);
--gl-inset-milk:           inset 0 1px 2px rgba(255, 255, 255, 0.90);
```

#### 1.6 Gloss (однаковий в обох темах)

```css
--gl-gloss-card:           linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.5) 30%,
                             rgba(255,255,255,0.6) 50%, rgba(255,255,255,0.5) 70%, transparent 100%);
--gl-gloss-modal:          linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 30%,
                             rgba(255,255,255,0.5) 50%, rgba(255,255,255,0.4) 70%, transparent 100%);
--gl-gloss-progress:       linear-gradient(to bottom, rgba(255,255,255,0.3) 0%, transparent 100%);
--gl-range-thumb-border:   2px solid rgba(255,255,255,0.5);
--gl-gloss-droplet:        radial-gradient(60% 55% at 32% 12%, rgba(255,255,255,0.42) 0%, transparent 70%),
                           radial-gradient(75% 60% at 50% 112%, rgba(255,255,255,0.18) 0%, transparent 70%);
```

#### 1.7 Фон-сцена

```css
/* темна */
--gl-bg-aurora-1:          rgba(60, 160, 160, 0.25);
--gl-bg-aurora-2:          rgba(200, 140, 60, 0.12);
--gl-bg-aurora-3:          rgba(80, 180, 200, 0.18);
--gl-bg-light-streak-1:    rgba(90, 210, 200, 0.14);
--gl-bg-light-streak-2:    rgba(110, 200, 190, 0.10);
--gl-bg-warm-glow:         rgba(220, 160, 70, 0.10);

/* світла */
--gl-bg-aurora-1:          rgba(100, 200, 220, 0.15);
--gl-bg-aurora-2:          rgba(240, 180, 100, 0.10);
--gl-bg-aurora-3:          rgba(120, 200, 230, 0.12);
--gl-bg-light-streak-1:    rgba(140, 230, 220, 0.10);
--gl-bg-light-streak-2:    rgba(160, 220, 210, 0.08);
--gl-bg-warm-glow:         rgba(240, 180, 100, 0.08);
```

**Як побудовано (токени).** Скло складається з трьох шарів: напівпрозора заливка `--gl-surface-*`, рамка `--gl-border-*` і внутрішнє світло `--gl-inset-*`. У світлій темі всі три шари підвищують непрозорість і зменшують тінь, а блюр лишається того самого розміру.

---

### 2. `.glass-pill` і `.glass-nav`

**Селектори:** `.glass-nav`, `.glass-pill`, `.glass-pill svg`, `.glass-pill ::slotted(svg)`. Суміжний `.glass-theme-toggle` має той самий рецепт.

```css
.glass-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--gl-space-xs);
}

.glass-pill {
  width: 46px; height: 46px;
  border-radius: var(--gl-radius-pill);
  background: var(--gl-surface-3);
  backdrop-filter: blur(var(--gl-blur));
  -webkit-backdrop-filter: blur(var(--gl-blur));
  border: 1.5px solid var(--gl-border-strong);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: var(--gl-transition);
  color: var(--gl-color-text);
  box-shadow: var(--gl-shadow-glow), var(--gl-inset-medium);
  outline: none;
  -webkit-tap-highlight-color: transparent;
}

.glass-pill svg,
.glass-pill ::slotted(svg) {
  width: 20px; height: 20px;
  fill: none; stroke: var(--gl-color-text); stroke-width: 2.2;
  stroke-linecap: round; stroke-linejoin: round;
}
```

**Стани:**

```css
.glass-pill:hover { background: var(--gl-surface-5); transform: scale(1.05); }
.glass-pill:active { transform: scale(0.95); }
/* A mark for the keyboard (since 1.40.0), as on .glass-btn. */
.glass-pill:focus-visible { outline: 2px solid var(--gl-focus-ring); outline-offset: 2px; }
/* Disabled: dimmed, not-allowed cursor, no hover — see .glass-btn:disabled. */
.glass-pill:disabled,
.glass-pill[aria-disabled="true"] { opacity: 0.45; cursor: not-allowed; }
.glass-pill:disabled:is(:hover, :active),
.glass-pill[aria-disabled="true"]:is(:hover, :active) { background: var(--gl-surface-3); transform: none; }
```

**Світла тема:** окремого правила нема. Ефект дають токени: `--gl-surface-3` стає 0.70, `--gl-surface-5` — 0.85, `--gl-border-strong` — `rgba(0, 0, 0, 0.15)`, `--gl-color-text` — `#1a2a36`.

**Як побудовано:**
- Круглий скляний елемент 46×46 з `--gl-radius-pill`, блюр 24px, світла рамка і тіні з токенів.
- При наведенні заливка світлішає до `--gl-surface-5`, при натисканні стискається до 0.95.

---

### 3. Плаваючий таб-бар, `--droplet` і активний пункт

**Селектори:** `.glass-tab-bar-dock`, `.glass-tab-bar.glass-tab-bar--floating`, `.glass-tab-bar--floating .glass-tab-bar__item`, `.glass-tab-bar__item.is-active`, `.glass-tab-bar.glass-tab-bar--droplet[data-droplet]::before`, `[data-droplet-dir]`, `[data-droplet-lift]`, `[data-droplet-drag]`, `.is-under-droplet`.

**Док (контейнер):**

```css
.glass-tab-bar-dock {
  position: fixed; left: 50%;
  bottom: calc(var(--gl-tab-bar-floating-bottom) + env(safe-area-inset-bottom, 0px));
  transform: translateX(-50%);
  display: flex; align-items: center;
  gap: var(--gl-tab-bar-floating-gap);
  z-index: var(--gl-tab-bar-z-index, 900);
  max-width: calc(100vw - 2 * var(--gl-space-md));
}
```

**Плаваюча панель:**

```css
.glass-tab-bar.glass-tab-bar--floating {
  position: static;
  left: auto; right: auto; bottom: auto;
  height: auto; width: max-content;
  padding: var(--gl-tab-bar-floating-padding);
  border-radius: var(--gl-tab-bar-floating-radius);
  border: 1px solid var(--gl-border-subtle);
  background: linear-gradient(to bottom,
    var(--gl-surface-3) 0%, var(--gl-surface-1) 100%
  );
  box-shadow:
    0 8px 32px rgba(0,0,0,0.18),
    0 2px 8px rgba(0,0,0,0.08),
    var(--gl-inset-subtle);
  display: flex; justify-content: flex-start; align-items: center;
  gap: var(--gl-space-2xs);
}
```

Тіні панелі записані літералами, а не токенами `--gl-shadow-*`. Тому в світлій темі вони такі самі, як у темній.

**Пункт:**

```css
.glass-tab-bar--floating .glass-tab-bar__item {
  position: relative;
  border-radius: var(--gl-tab-bar-item-radius, var(--gl-radius-full));
  padding: var(--gl-space-2xs) var(--gl-space-sm);
  min-width: auto;
  align-items: center;
}

.glass-tab-bar--floating .glass-tab-bar__item > * {
  position: relative; z-index: 1;
}

.glass-tab-bar--floating .glass-tab-bar__item.is-active::before {
  content: '';
  position: absolute; inset: 0;
  border-radius: inherit;
  background: radial-gradient(circle at center,
    color-mix(in srgb, var(--gl-tab-bar-spotlight-color) 28%, transparent) 0%,
    color-mix(in srgb, var(--gl-tab-bar-spotlight-color) 10%, transparent) 55%,
    transparent 100%
  );
  opacity: var(--gl-tab-bar-spotlight-opacity, 1);
  pointer-events: none; z-index: 0;
}

.glass-tab-bar--floating .glass-tab-bar__item.is-active .glass-tab-bar__icon::after {
  display: none;
}
```

**Активний пункт (базовий бар):**

```css
.glass-tab-bar__item.is-active {
  background: var(--gl-tab-bar-active-bg, none);
  box-shadow: var(--gl-tab-bar-active-shadow, none);
}

.glass-tab-bar__item.is-active .glass-tab-bar__icon { color: var(--gl-tab-bar-active-color, var(--gl-color-primary-text)); }

.glass-tab-bar__item.is-active .glass-tab-bar__icon > :where(:not(.glass-tab-bar__badge)),
.glass-tab-bar__item.is-active .glass-tab-bar__icon ::slotted(*) {
  filter: var(--gl-tab-bar-active-glow, drop-shadow(0 0 6px color-mix(in srgb, var(--gl-color-primary) 35%, transparent)));
}

.glass-tab-bar__item.is-active .glass-tab-bar__label {
  color: var(--gl-tab-bar-active-color, var(--gl-color-primary-text));
  font-weight: var(--gl-tab-bar-active-weight, var(--gl-font-weight-medium));
}
```

**Droplet: капля.** Блок `::before` рядка:

```css
:is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet]::before {
  content: '';
  position: absolute; z-index: -1;
  top: var(--gl-droplet-top, 0px);
  bottom: var(--gl-droplet-bottom, 0px);
  left: var(--gl-droplet-left, 0px);
  right: var(--gl-droplet-right, 0px);
  border-radius: var(--gl-radius-sm);
  background:
    var(--gl-gloss-droplet, none),
    linear-gradient(to bottom, var(--gl-surface-5) 0%, var(--gl-surface-3) 100%);
  box-shadow:
    0 4px 14px rgba(0,0,0,0.18), 0 1px 3px rgba(0,0,0,0.12),
    inset 0 0 0 1px var(--gl-border-subtle),
    var(--gl-inset-strong);
  backdrop-filter: blur(var(--gl-blur-light)) saturate(1.6);
  -webkit-backdrop-filter: blur(var(--gl-blur-light)) saturate(1.6);
  pointer-events: none;
  transition:
    transform var(--gl-droplet-settle-duration, 0.55s) var(--gl-droplet-settle-easing, cubic-bezier(0.34, 1.8, 0.5, 1)),
    box-shadow 0.3s ease;
}

.glass-tab-bar.glass-tab-bar--droplet[data-droplet]::before {
  border-radius: var(--gl-tab-bar-item-radius, var(--gl-radius-full));
  background:
    var(--gl-gloss-droplet, none),
    var(--gl-tab-bar-active-bg, linear-gradient(to bottom, var(--gl-surface-5) 0%, var(--gl-surface-3) 100%));
  box-shadow:
    var(--gl-tab-bar-active-shadow, 0 4px 14px rgba(0,0,0,0.18), 0 1px 3px rgba(0,0,0,0.12)),
    inset 0 0 0 1px var(--gl-border-subtle),
    var(--gl-inset-strong);
}
```

**Droplet: рух по напрямку** (фрагмент `right`; `left`, `up`, `down` симетричні):

```css
:is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet][data-droplet-dir="right"]::before {
  transition:
    right var(--gl-droplet-duration, 0.3s) var(--gl-droplet-easing, cubic-bezier(0.3, 1.2, 0.5, 1)),
    left var(--gl-droplet-trail-duration, 0.5s) var(--gl-droplet-trail-easing, cubic-bezier(0.5, 1.5, 0.45, 0.92)) var(--gl-droplet-trail-delay, 0.04s),
    top var(--gl-droplet-duration, 0.3s) ease, bottom var(--gl-droplet-duration, 0.3s) ease,
    transform var(--gl-droplet-settle-duration, 0.55s) var(--gl-droplet-settle-easing, cubic-bezier(0.34, 1.8, 0.5, 1)),
    box-shadow 0.3s ease;
}
```

**Droplet: під час руху, утримання пальцем:**

```css
:is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet][data-droplet-lift]::before,
:is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet][data-droplet-drag]::before {
  box-shadow:
    0 10px 24px rgba(0,0,0,0.24), 0 2px 6px rgba(0,0,0,0.14),
    inset 0 0 0 1px var(--gl-border-medium),
    var(--gl-inset-strong);
}
:is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet][data-droplet-lift]::before {
  transform: scale(1, var(--gl-droplet-lift, 0.86));
}
:is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet][data-droplet-drag]::before {
  transform: scale(1.1, 1.22);
  transition:
    left 0.1s ease-out, right 0.1s ease-out,
    transform 0.25s ease-out, box-shadow 0.25s ease;
}
```

**Пункти під краплею та неактивні стани:**

```css
.glass-tab-bar--droplet[data-droplet] .glass-tab-bar__item.is-active { background: none; box-shadow: none; }
.glass-tab-bar--droplet[data-droplet] .glass-tab-bar__item.is-active:focus-visible { box-shadow: var(--gl-shadow-focus); }
.glass-tab-bar--droplet[data-droplet] .glass-tab-bar__item.is-active::before { display: none; }
.glass-tab-bar--droplet[data-droplet] .glass-tab-bar__icon { transition: color 0.25s ease, transform var(--gl-droplet-lens-duration, 0.4s) var(--gl-droplet-lens-easing, cubic-bezier(0.34, 1.6, 0.5, 1)); }
.glass-tab-bar--droplet[data-droplet] .glass-tab-bar__item.is-under-droplet .glass-tab-bar__icon { transform: scale(1.15); }
.glass-tab-bar--droplet[data-droplet] .glass-tab-bar__item.is-under-droplet :is(.glass-tab-bar__icon, .glass-tab-bar__label) { color: var(--gl-tab-bar-active-color, var(--gl-color-primary-text)); }
.glass-tab-bar--droplet[data-droplet-drag] .glass-tab-bar__item.is-active:not(.is-under-droplet) :is(.glass-tab-bar__icon, .glass-tab-bar__label) { color: var(--gl-tab-bar-color, var(--gl-icon-muted)); }

:is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet]:has(:is(.glass-tab-bar__item.is-active, .glass-segmented__item[aria-pressed="true"]):disabled)::before { opacity: 0.45; }
```

**Пункт, стани hover і focus:**

```css
.glass-tab-bar__item:not(.is-active):hover .glass-tab-bar__icon,
.glass-tab-bar__item:not(.is-active):hover .glass-tab-bar__label { color: var(--gl-tab-bar-hover-color, var(--gl-icon-default)); }

.glass-tab-bar__item:focus-visible { box-shadow: var(--gl-shadow-focus); }
```

**Light theme.** Окремих правил для таб-бара у світлій темі нема. Колір спотлайту (`--gl-tab-bar-spotlight-color`) береться з `--gl-color-primary`, тобто `#e8852d`. Фон капель і пунктів береться з `--gl-surface-5` і `--gl-surface-3` світлої теми. Тіні панелі та капель мають ті самі літеральні значення, що й у темній.

**Як побудовано:**
- Плаваюча панель — це `position: static` всередині fixed-доку. Капля (`::before` рядка) стоїть під пунктами з `z-index: -1` і рухається через `left`/`right`/`top`/`bottom`, які скрипт виставляє з `--gl-droplet-*`.
- Напрямок руху задається атрибутом `data-droplet-dir`, а тримання пальцем — `data-droplet-drag`. Кожен стан має свій набір `transition`.
- Пункт, над яким стоїть капля, отримує `.is-under-droplet` і збільшується як під лінзою.

---

### 4. Кнопки: primary, secondary, ghost (tertiary), FAB

У джерелі є `.glass-btn--primary`, `.glass-btn--secondary` і `.glass-btn--tertiary`. Ghost-варіанта з такою назвою нема в джерелі. Найближчий аналог — `.glass-btn--tertiary` із прозорим фоном `--gl-surface-2`. FAB-класу з такою назвою нема в джерелі. Найближче — `.glass-tab-bar__accessory` (круглий плаваючий елемент, див. нижче).

#### 4.1 База

```css
.glass-btn {
  display: flex; align-items: center; justify-content: center;
  gap: 10px; width: 100%; height: var(--gl-btn-height, 56px);
  padding-inline: var(--gl-btn-padding-x, var(--gl-space-xl));
  border: none; border-radius: var(--gl-btn-radius, var(--gl-radius-btn));
  font-family: var(--gl-font-family);
  font-size: var(--gl-font-size-btn);
  font-weight: var(--gl-font-weight-semibold);
  cursor: pointer; transition: var(--gl-transition);
  outline: none; -webkit-tap-highlight-color: transparent;
}

.glass-btn:focus-visible { outline: 2px solid var(--gl-focus-ring); outline-offset: 2px; }

a.glass-btn { display: inline-flex; text-decoration: none; }
.glass-btn[hidden] { display: none; }

.glass-btn svg,
.glass-btn ::slotted(svg) {
  width: 20px; height: 20px; flex-shrink: 0;
  fill: none; stroke: currentColor;
  stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
}
```

#### 4.2 Primary

```css
.glass-btn--primary {
  background: var(--gl-btn-primary-bg, linear-gradient(135deg,
    var(--gl-color-primary) 0%, var(--gl-color-primary-mid) 50%,
    var(--gl-color-primary-dark) 100%
  ));
  color: var(--gl-color-on-primary, #ffffff);
  border: 1px solid var(--gl-border-warm);
  box-shadow: var(--gl-shadow-btn-primary), var(--gl-inset-strong);
}
.glass-btn--primary svg,
.glass-btn--primary ::slotted(svg) { fill: var(--gl-icon-on-primary); stroke: var(--gl-icon-on-primary); stroke-width: 0; }
.glass-btn--primary:hover { transform: translateY(-1px); }
.glass-btn--primary:active { transform: translateY(1px); }
```

Світла тема: окремого правила нема. Градієнт бере `--gl-color-primary` (`#e8852d`), `--gl-color-primary-mid` (52 %) і `--gl-color-primary-dark` (`#c96a1e`). Тінь `--gl-shadow-btn-primary` стає світлішою (25 %).

#### 4.3 Secondary

```css
.glass-btn--secondary {
  background: linear-gradient(to bottom,
    var(--gl-surface-milk-strong) 0%, var(--gl-surface-milk) 100%
  );
  backdrop-filter: blur(var(--gl-blur));
  -webkit-backdrop-filter: blur(var(--gl-blur));
  border: 1.5px solid var(--gl-border-milk);
  color: var(--gl-color-text-on-light);
  box-shadow: var(--gl-shadow-btn), var(--gl-inset-milk);
}
.glass-btn--secondary svg,
.glass-btn--secondary ::slotted(svg) {
  fill: none; stroke: var(--gl-icon-on-secondary);
  stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
}
.glass-btn--secondary:hover { transform: translateY(-1px); }
.glass-btn--secondary:active { transform: translateY(1px); }
```

Світла тема: `--gl-surface-milk-strong` стає 0.92, `--gl-surface-milk` — 0.85, `--gl-border-milk` — `rgba(0, 0, 0, 0.10)`. Текст `#1a3a4a` лишається тим самим.

#### 4.4 Tertiary (ghost)

```css
.glass-btn--tertiary {
  background: var(--gl-ctx-btn-tertiary-bg, var(--gl-surface-2));
  backdrop-filter: var(--gl-ctx-control-backdrop, blur(var(--gl-blur-light)));
  -webkit-backdrop-filter: var(--gl-ctx-control-backdrop, blur(var(--gl-blur-light)));
  border: 1px solid var(--gl-border-subtle);
  color: var(--gl-color-text-muted);
  box-shadow: 0 4px 12px rgba(0,0,0,0.10), var(--gl-inset-subtle);
}
.glass-btn--tertiary svg,
.glass-btn--tertiary ::slotted(svg) {
  fill: none; stroke: var(--gl-icon-on-tertiary);
  stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
}
.glass-btn--tertiary:hover {
  background: var(--gl-surface-4); color: var(--gl-color-text);
  transform: translateY(-1px);
}
.glass-btn--tertiary:active { transform: translateY(1px); }
.glass-btn--tertiary:disabled:hover,
.glass-btn--tertiary[aria-disabled="true"]:hover {
  background: var(--gl-ctx-btn-tertiary-bg, var(--gl-surface-2)); color: var(--gl-color-text-muted);
}
```

Світла тема: `--gl-surface-2` стає 0.60, `--gl-surface-4` — 0.75.

#### 4.5 Стани і розміри

```css
.glass-btn:disabled,
.glass-btn[aria-disabled="true"] { opacity: 0.45; cursor: not-allowed; }
.glass-btn:disabled:is(:hover, :active),
.glass-btn[aria-disabled="true"]:is(:hover, :active) { transform: none; }

.glass-btn--sm {
  height: var(--gl-btn-height-sm, 44px); font-size: var(--gl-font-size-sm);
  padding-inline: var(--gl-btn-padding-x-sm, var(--gl-btn-padding-x, var(--gl-space-xl)));
  border-radius: var(--gl-btn-radius-sm, var(--gl-btn-radius, var(--gl-radius-sm)));
}
.glass-btn--lg { height: var(--gl-btn-height-lg, 64px); font-size: var(--gl-font-size-lg); }
.glass-btn--auto { width: auto; padding-block: 0; }
```

Стану `:active` для primary і secondary окремо нема: є `translateY(1px)`, а кольори лишаються ті самі.

#### 4.6 FAB: `.glass-tab-bar__accessory`

```css
.glass-tab-bar__accessory {
  width: var(--gl-tab-bar-accessory-size);
  height: var(--gl-tab-bar-accessory-size);
  border-radius: var(--gl-radius-pill);
  background: linear-gradient(to bottom,
    var(--gl-surface-3) 0%, var(--gl-surface-1) 100%
  );
  backdrop-filter: blur(var(--gl-blur));
  -webkit-backdrop-filter: blur(var(--gl-blur));
  border: 1px solid var(--gl-border-subtle);
  box-shadow:
    0 8px 32px rgba(0,0,0,0.18),
    0 2px 8px rgba(0,0,0,0.08),
    var(--gl-inset-subtle);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: var(--gl-transition);
  outline: none; padding: 0;
  -webkit-tap-highlight-color: transparent;
  flex-shrink: 0;
  color: var(--gl-icon-default);
}

.glass-tab-bar__accessory:where(:not(:disabled, [aria-disabled="true"])):hover {
  transform: translateY(-1px);
  color: var(--gl-icon-strong);
}
.glass-tab-bar__accessory:disabled,
.glass-tab-bar__accessory[aria-disabled="true"] { opacity: 0.45; cursor: not-allowed; }
.glass-tab-bar__accessory:focus-visible {
  box-shadow:
    0 8px 32px rgba(0,0,0,0.18),
    var(--gl-shadow-focus),
    var(--gl-inset-subtle);
}

.glass-tab-bar__accessory--accent {
  background: linear-gradient(135deg,
    var(--gl-color-primary) 0%,
    color-mix(in srgb, var(--gl-color-primary) 70%, transparent) 100%
  );
  border-color: color-mix(in srgb, var(--gl-color-primary) 50%, transparent);
  box-shadow:
    0 8px 32px color-mix(in srgb, var(--gl-color-primary) 35%, transparent),
    var(--gl-inset-medium);
}
.glass-tab-bar__accessory--accent,
.glass-tab-bar__accessory--accent:hover { color: var(--gl-color-on-primary, #ffffff); }
```

Варіанти `--success` і `--error` мають такий самий рецепт, але з `--gl-color-success` або `--gl-color-error`.

**Як побудовано:**
- Primary — це градієнт трьох стопів від `--gl-color-primary` до `--gl-color-primary-dark` із рамкою `--gl-border-warm` і внутрішнім світлом. Hover піднімає кнопку на 1px.
- Secondary — молочна (milk) поверхня, яка не залежить від теми, з темним текстом `#1a3a4a`.
- Tertiary — це прозорі «ghost»-кнопки з м'яким текстом, які при наведенні стають світлішими.

---

### 5. Перемикач (toggle)

**Селектори:** `.glass-toggle`, `.glass-toggle__input`, `.glass-toggle__track`, `.glass-toggle__thumb`, `.glass-toggle__label`.

```css
.glass-toggle {
  display: inline-flex; align-items: flex-start;
  gap: var(--gl-space-sm); cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.glass-toggle__input {
  position: absolute; z-index: 1; opacity: 0; cursor: inherit;
  width: var(--gl-toggle-width, 52px); height: var(--gl-toggle-height, 30px); margin: 0; font: inherit;
  margin-top: max(0px, calc((1lh - var(--gl-toggle-height, 30px)) / 2));
}

.glass-toggle__track {
  position: relative; width: var(--gl-toggle-width, 52px); height: var(--gl-toggle-height, 30px);
  background: var(--gl-toggle-track-bg, var(--gl-surface-2));
  backdrop-filter: blur(var(--gl-blur-soft));
  -webkit-backdrop-filter: blur(var(--gl-blur-soft));
  border: 1.5px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-full);
  transition: var(--gl-transition);
  box-shadow: var(--gl-inset-subtle);
  flex-shrink: 0;
  margin-top: max(0px, calc((1lh - var(--gl-toggle-height, 30px)) / 2));
}

.glass-toggle__thumb {
  position: absolute;
  top: calc((var(--gl-toggle-height, 30px) - var(--gl-toggle-thumb-size, 22px)) / 2 - 1px);
  left: calc((var(--gl-toggle-height, 30px) - var(--gl-toggle-thumb-size, 22px)) / 2 - 1px);
  width: var(--gl-toggle-thumb-size, 22px); height: var(--gl-toggle-thumb-size, 22px);
  border-radius: var(--gl-radius-pill);
  background: var(--gl-toggle-thumb-bg);
  box-shadow: 0 2px 6px rgba(0,0,0,0.2), var(--gl-inset-milk);
  transition: var(--gl-transition);
}

.glass-toggle__input:checked + .glass-toggle__track {
  background: var(--gl-toggle-track-bg-checked, linear-gradient(135deg,
    var(--gl-color-primary) 0%, var(--gl-color-primary-dark) 100%
  ));
  border-color: var(--gl-border-warm);
}

.glass-toggle__input:checked + .glass-toggle__track .glass-toggle__thumb {
  transform: translateX(calc(var(--gl-toggle-width, 52px) - var(--gl-toggle-height, 30px)));
}

.glass-toggle__thumb:dir(rtl) {
  left: auto; right: calc((var(--gl-toggle-height, 30px) - var(--gl-toggle-thumb-size, 22px)) / 2 - 1px);
}
.glass-toggle__input:checked + .glass-toggle__track .glass-toggle__thumb:dir(rtl) {
  transform: translateX(calc(var(--gl-toggle-height, 30px) - var(--gl-toggle-width, 52px)));
}

.glass-toggle__label {
  font-size: var(--gl-font-size-base);
  color: var(--gl-color-text);
  user-select: none;
  margin-top: max(0px, calc((var(--gl-toggle-height, 30px) - 1lh) / 2));
}
```

**Стани:**

```css
.glass-toggle__input:focus-visible + .glass-toggle__track { box-shadow: var(--gl-shadow-focus); }
.glass-toggle__input:disabled { cursor: not-allowed; }
.glass-toggle__input:disabled + .glass-toggle__track,
.glass-toggle__input:disabled ~ .glass-toggle__label { opacity: 0.45; cursor: not-allowed; }
.glass-toggle:has(> .glass-toggle__input:disabled) { cursor: not-allowed; }
```

Hover і active для перемикача окремо не визначено. Анімація йде через `transition` на thumb.

**Light theme:**
- Фон thumb: `--gl-toggle-thumb-bg: linear-gradient(to bottom, #ffffff 0%, #f0f0f0 100%)`. У темній темі там `rgba(255,255,255,0.9)` → `rgba(255,255,255,0.7)`.
- Track: `--gl-surface-2` стає 0.60. Рамка `--gl-border-medium` стає `rgba(0, 0, 0, 0.12)`.
- Увімкнений стан однаковий в обох темах.

**Як побудовано:**
- Інпут з `opacity: 0` лежить поверх треку, тож клік і фокус ідуть у справжній `<input>`, а не в декор.
- Thumb переміщається через `translateX`, а відстань дорівнює `width − height`.
- Розміри треку і thumb беруться з токенів `--gl-toggle-*`, тож compact-щільність їх змінює.

---

### 6. Select, випадаючі панелі (popover, menu, tooltip)

#### 6.1 `.glass-select`

```css
.glass-select {
  width: 100%; height: var(--gl-control-height, 52px);
  padding: 0 var(--gl-space-3xl) 0 var(--gl-control-padding-x, var(--gl-space-md));
  background: var(--gl-surface-2);
  backdrop-filter: blur(var(--gl-blur-light));
  -webkit-backdrop-filter: blur(var(--gl-blur-light));
  border: 1.5px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-input);
  color: var(--gl-color-text);
  font-family: var(--gl-font-family);
  font-size: var(--gl-font-size-base);
  transition: var(--gl-transition);
  outline: none;
  box-shadow: var(--gl-inset-subtle);
  cursor: pointer;
  appearance: none; -webkit-appearance: none;
  background-image: var(--gl-select-chevron, url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.65)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E"));
  background-repeat: no-repeat;
  background-position: right 16px center;
}

.glass-select:dir(rtl) {
  padding: 0 var(--gl-control-padding-x, var(--gl-space-md)) 0 var(--gl-space-3xl);
  background-position: left 16px center;
}

.glass-select option { background: var(--gl-color-bg-mid); color: var(--gl-color-text); }
.glass-select:has(> option:first-child[value=""][disabled]:checked) { color: var(--gl-placeholder); }
```

**Стани:**

```css
.glass-select:focus {
  border-color: var(--gl-border-focus);
  box-shadow: var(--gl-shadow-focus), var(--gl-inset-medium);
}
.glass-select:disabled,
.glass-textarea:disabled { opacity: 0.4; cursor: not-allowed; }
```

**Light theme:** шеврон береться з `--gl-select-chevron` світлої теми: `stroke='rgba(26,42,54,0.68)'`. Фон `--gl-surface-2` стає 0.60. Фон `option` — це `--gl-color-bg-mid` (`#f0f4f8`).

#### 6.2 Popover (`.glass-popover`)

```css
.glass-popover {
  position: absolute;
  top: calc(100% + var(--gl-space-xs));
  left: 50%;
  transform: translateX(-50%) translateY(-4px) scale(0.96);
  transform-origin: top center;
  min-width: 220px;
  padding: var(--gl-space-sm);
  background: var(--gl-surface-3);
  backdrop-filter: blur(var(--gl-blur));
  -webkit-backdrop-filter: blur(var(--gl-blur));
  border: 1px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-card);
  box-shadow: var(--gl-shadow-card), var(--gl-inset-strong);
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition:
    opacity .18s ease,
    transform .18s cubic-bezier(.2,.8,.2,1),
    visibility 0s linear .18s;
  z-index: 50;
}
.glass-popover.is-open {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transform: translateX(-50%) translateY(0) scale(1);
}

.glass-popover[popover] {
  position: fixed; inset: auto; margin: 0;
  transform: translateY(-4px) scale(0.96);
  transition-property: opacity, transform, overlay, display;
  transition-duration: .18s;
  transition-timing-function: ease;
  transition-behavior: allow-discrete;
}
.glass-popover[popover]:popover-open {
  opacity: 1; visibility: visible; pointer-events: auto;
  transform: none;
  animation: glass-popover-in .22s cubic-bezier(.2,.8,.2,1);
}
@keyframes glass-popover-in { from { opacity: 0; transform: translateY(-4px) scale(0.96); } }
```

Стани: `.is-open` і `:popover-open`. Hover і focus окремо не визначено. Світла тема: `--gl-surface-3` стає 0.70, `--gl-border-medium` — `rgba(0, 0, 0, 0.12)`.

#### 6.3 Tooltip

```css
.glass-tooltip {
  max-width: var(--gl-tooltip-max-width, 240px);
  padding: 6px 12px;
  border: 1px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-sm);
  background: var(--gl-tooltip-bg, color-mix(in srgb, var(--gl-color-bg-mid) 80%, transparent));
  backdrop-filter: blur(var(--gl-blur));
  -webkit-backdrop-filter: blur(var(--gl-blur));
  box-shadow: var(--gl-shadow-card), var(--gl-inset-strong);
  color: var(--gl-tooltip-color, var(--gl-color-text));
  font-family: var(--gl-font-family);
  font-size: var(--gl-font-size-xs); font-weight: var(--gl-font-weight-medium);
  line-height: 1.4;
  overflow-wrap: anywhere;
}
.glass-tooltip[popover]:popover-open { opacity: 1; animation: glass-fade-in .12s ease; }
```

#### 6.4 Menu (`.glass-menu`)

```css
.glass-menu {
  min-width: 180px; max-width: min(320px, calc(100vw - 16px));
  max-height: min(70vh, 480px);
  overflow-y: auto; overscroll-behavior: contain;
  padding: 6px;
  background: var(--gl-surface-3);
  backdrop-filter: blur(var(--gl-blur));
  -webkit-backdrop-filter: blur(var(--gl-blur));
  border: 1px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-card);
  box-shadow: var(--gl-shadow-card), var(--gl-inset-strong);
  color: var(--gl-color-text);
  font-family: var(--gl-font-family);
}

.glass-menu__item {
  display: flex; align-items: center; gap: 10px;
  width: 100%; min-height: 40px;
  padding: 8px 12px;
  border: 0; border-radius: calc(var(--gl-radius-card) - 6px);
  background: none;
  color: var(--gl-color-text);
  font: inherit; font-size: var(--gl-font-size-sm); text-align: start;
  cursor: pointer; outline: none; user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.glass-menu__item:hover,
.glass-menu__item:focus,
.glass-menu__item.is-focused { background: var(--gl-surface-2); }
.glass-menu__item:focus-visible,
.glass-menu__item.is-focus-visible { box-shadow: inset 0 0 0 2px var(--gl-border-focus); }
.glass-menu__item--danger { color: var(--gl-color-error-on-surface, var(--gl-color-error)); }
.glass-menu__item[aria-disabled="true"],
.glass-menu__item.is-disabled { opacity: 0.45; cursor: not-allowed; }
```

Галочка (`.glass-menu__check`) з'являється через `[aria-checked="true"]` або `.is-checked`. Відступ між елементами ділять `__separator` і `__group-label`.

**Light theme:** `--gl-surface-3` стає 0.70, `--gl-surface-2` (hover) — 0.60. Колір danger береться з `--gl-color-error-on-surface`, у світлій темі це `color-mix(in srgb, #dc3545 82%, #000000)`.

**Як побудовано:**
- Панель — це скло `--gl-surface-3` з блюром 24px. Вона лежить в top layer через `popover`, тож її не обрізає сусідній `overflow: hidden`.
- Вхід і вихід анімуються через `transition-behavior: allow-discrete` і `@keyframes glass-popover-in`.
- Пункт меню при фокусі отримує внутрішнє кільце `inset 0 0 0 2px`, а не `outline`.

---

### 7. Modal, sheet і їх підкладка (overlay)

#### 7.1 Overlay і `<dialog>`

```css
.glass-modal-overlay {
  position: fixed; inset: 0;
  background: var(--gl-surface-overlay);
  backdrop-filter: blur(var(--gl-blur-overlay, var(--gl-blur-soft)));
  -webkit-backdrop-filter: blur(var(--gl-blur-overlay, var(--gl-blur-soft)));
  display: flex; align-items: center; justify-content: center;
  padding: var(--gl-space-lg); z-index: 1000;
  opacity: 0; pointer-events: none;
  transition: var(--gl-transition-modal);
  font-family: var(--gl-font-family);
  -webkit-font-smoothing: antialiased;
}
.glass-modal-overlay.is-active { opacity: 1; pointer-events: auto; }

dialog.glass-modal-overlay {
  width: auto; height: auto; max-width: none; max-height: none;
  margin: 0; border: 0; color: inherit; outline: none;
}
dialog.glass-modal-overlay:not([open]) { display: none; }
dialog.glass-modal-overlay::backdrop { background: transparent; }
```

#### 7.2 Modal

```css
.glass-modal {
  width: 100%; max-width: var(--gl-modal-max-width, 340px);
  background: var(--gl-modal-bg, linear-gradient(to bottom,
    var(--gl-dialog-glow-top, var(--gl-card-glow-top)) 0%, var(--gl-card-glow-bottom) 100%
  ));
  backdrop-filter: blur(var(--gl-blur-heavy));
  -webkit-backdrop-filter: blur(var(--gl-blur-heavy));
  border: 1.5px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-card);
  overflow: hidden;
  box-shadow: var(--gl-shadow-modal);
  transform: scale(0.9) translateY(20px);
  transition: var(--gl-transition-modal);
  position: relative;
}
.glass-modal-overlay.is-active .glass-modal { transform: scale(1) translateY(0); }

.glass-modal::before {
  content: '';
  position: absolute; top: 0; left: 10%; right: 10%; height: 1px;
  background: var(--gl-gloss-modal);
}
```

Дії внизу:

```css
.glass-modal__footer { display: flex; border-top: 1px solid var(--gl-border-subtle); }

.glass-modal__action {
  flex: 1; height: var(--gl-modal-action-height, 52px);
  background: transparent; border: none;
  font-family: var(--gl-font-family);
  font-size: var(--gl-font-size-btn);
  font-weight: var(--gl-font-weight-medium);
  color: var(--gl-color-text-muted);
  cursor: pointer; transition: var(--gl-transition-fast); outline: none;
}
.glass-modal__action:hover { background: var(--gl-surface-1); }
.glass-modal__action:focus-visible {
  outline: 2px solid var(--gl-focus-ring); outline-offset: -4px;
  border-radius: calc(var(--gl-radius-card) - 1.5px);
}
.glass-modal__action:disabled { opacity: 0.45; cursor: not-allowed; }
.glass-modal__action:disabled:hover { background: transparent; }
.glass-modal__action + .glass-modal__action { border-inline-start: 1px solid var(--gl-border-subtle); }
.glass-modal__action--primary { color: var(--gl-ctx-primary-text, var(--gl-color-primary-text)); font-weight: var(--gl-font-weight-semibold); }
.glass-modal__action--danger { color: var(--gl-color-error); font-weight: var(--gl-font-weight-semibold); }
```

Контекст карток усередині модального вікна:

```css
.glass-modal, .glass-sheet {
  --gl-ctx-segmented-bg: var(--gl-dialog-well);
  --gl-ctx-segmented-active-bg: var(--gl-dialog-raised);
  --gl-ctx-btn-tertiary-bg: var(--gl-dialog-control);
  --gl-ctx-control-backdrop: none;
  --gl-ctx-primary-text: var(--gl-color-primary-on-glass);
}
```

#### 7.3 Sheet (нижня шторка)

```css
.glass-sheet-overlay {
  position: fixed; inset: 0; z-index: var(--gl-sheet-z-index, 1000);
  display: flex; align-items: flex-end; justify-content: center;
  background: var(--gl-surface-overlay);
  backdrop-filter: blur(var(--gl-blur-overlay, var(--gl-blur-soft)));
  -webkit-backdrop-filter: blur(var(--gl-blur-overlay, var(--gl-blur-soft)));
  font-family: var(--gl-font-family);
  -webkit-font-smoothing: antialiased;
  opacity: 0;
  transition: var(--gl-transition-modal); transition-property: opacity;
}
.glass-sheet-overlay[hidden] { display: none; }
.glass-sheet-overlay.is-active { opacity: 1; }

.glass-sheet {
  width: min(100%, 560px); max-height: 88dvh; overflow: auto;
  padding: 8px var(--gl-space-lg) calc(var(--gl-space-lg) + env(safe-area-inset-bottom, 0px));
  background: var(--gl-sheet-bg, linear-gradient(to bottom,
    var(--gl-dialog-glow-top, var(--gl-card-glow-top)) 0%, var(--gl-card-glow-bottom) 100%
  ));
  backdrop-filter: blur(var(--gl-blur-heavy));
  -webkit-backdrop-filter: blur(var(--gl-blur-heavy));
  color: var(--gl-color-text);
  border: 1.5px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-card) var(--gl-radius-card) 0 0;
  box-shadow: var(--gl-shadow-modal);
}
.glass-sheet-overlay .glass-sheet {
  transform: translateY(100%);
  transition: var(--gl-transition-modal); transition-property: transform;
}
.glass-sheet-overlay.is-active .glass-sheet { transform: translateY(0); }
.glass-sheet-overlay--modeless { background: none; backdrop-filter: none; -webkit-backdrop-filter: none; pointer-events: none; }
.glass-sheet-overlay--modeless .glass-sheet { pointer-events: auto; }
```

Для `dialog.glass-sheet-overlay` є `overflow: clip;` (з коментарем про версію 1.39.0).

**Light theme:**
- `--gl-dialog-glow-top`, `--gl-dialog-well`, `--gl-dialog-raised`, `--gl-dialog-control` і `--gl-badge-selected-color` стають `initial`. Це значить, що `var(--gl-dialog-glow-top, var(--gl-card-glow-top))` падає в fallback і бере `--gl-card-glow-top` (`rgba(255,255,255,0.90)`). Це моє міркування про поведінку `initial`, у джерелі цього не написано.
- Тіні модалки: `--gl-shadow-modal` стає `0 16px 48px rgba(0, 0, 0, 0.12), 0 4px 16px rgba(0, 0, 0, 0.08)`.
- Підкладка: `--gl-surface-overlay` стає `rgba(0, 0, 0, 0.25)`.

**Як побудовано:**
- Підкладка є окремим fixed-шаром з блюром і затемненням. Вона показується через клас `.is-active`, а `<dialog>` лягає в top layer, так що сторінка під ним неактивна.
- Модальне вікно має скло з блюром 40px, градієнтом картки і верхнім бліком `--gl-gloss-modal`. Шторка має той самий матеріал, але лежить знизу з `translateY(100%)`.

---

### 8. Input, textarea, search: фокус на склі

**Селектори:** `.glass-input`, `.glass-input:focus`, `.glass-input--error:focus`, `.glass-textarea`, `.glass-textarea:focus`, `.glass-search`, `.glass-search .glass-input`.

#### 8.1 Input

```css
.glass-input {
  width: 100%; height: var(--gl-control-height, 52px);
  padding: 0 var(--gl-control-padding-x, var(--gl-space-md));
  background: var(--gl-surface-2);
  backdrop-filter: blur(var(--gl-blur-light));
  -webkit-backdrop-filter: blur(var(--gl-blur-light));
  border: 1.5px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-input);
  color: var(--gl-color-text);
  font-family: var(--gl-font-family);
  font-size: var(--gl-font-size-base);
  transition: var(--gl-transition);
  outline: none;
  box-shadow: var(--gl-inset-subtle);
  -webkit-tap-highlight-color: transparent;
  text-overflow: ellipsis;
}

.glass-input::placeholder { color: var(--gl-placeholder); }

.glass-input:focus {
  border-color: var(--gl-border-focus);
  background: var(--gl-surface-3);
  box-shadow: var(--gl-shadow-focus), var(--gl-inset-medium);
}

.glass-input:disabled { opacity: 0.4; cursor: not-allowed; }
.glass-input--error { border-color: var(--gl-color-error); }

.glass-input--error:focus {
  --gl-focus-ring: color-mix(in srgb, var(--gl-color-error-on-surface) 70%, var(--gl-color-text));
  border-color: var(--gl-focus-ring);
  box-shadow: 0 0 0 2px var(--gl-focus-ring), var(--gl-inset-medium);
}
```

Дата і час (вилучається нативний вигляд на iOS):

```css
.glass-input[type="date"],
.glass-input[type="time"],
.glass-input[type="datetime-local"],
.glass-input[type="month"] {
  -webkit-appearance: none; appearance: none;
}
.glass-input::-webkit-date-and-time-value { text-align: start; }
.glass-input::-webkit-calendar-picker-indicator { display: var(--gl-input-picker-icon, revert); }
```

#### 8.2 Textarea

```css
.glass-textarea {
  width: 100%; min-height: var(--gl-textarea-min-height, 120px);
  padding: var(--gl-space-md) var(--gl-control-padding-x, var(--gl-space-md));
  background: var(--gl-surface-2);
  backdrop-filter: blur(var(--gl-blur-light));
  -webkit-backdrop-filter: blur(var(--gl-blur-light));
  border: 1.5px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-input);
  color: var(--gl-color-text);
  font-family: var(--gl-font-family);
  font-size: var(--gl-font-size-base);
  line-height: 1.5; resize: vertical;
  transition: var(--gl-transition);
  outline: none;
  box-shadow: var(--gl-inset-subtle);
  field-sizing: var(--gl-textarea-field-sizing, fixed);
}
.glass-textarea:read-only { resize: none; }
.glass-textarea::placeholder { color: var(--gl-placeholder); }
.glass-textarea:focus {
  border-color: var(--gl-border-focus);
  background: var(--gl-surface-3);
  box-shadow: var(--gl-shadow-focus), var(--gl-inset-medium);
}
```

#### 8.3 Search

```css
.glass-search {
  position: relative; display: flex; align-items: center;
}

.glass-search__icon {
  position: absolute; inset-inline-start: var(--gl-space-md);
  width: 18px; height: 18px;
  stroke: var(--gl-icon-muted) !important;
  stroke-width: 2 !important;
  stroke-linecap: round !important;
  stroke-linejoin: round !important;
  fill: none !important;
  pointer-events: none;
  z-index: 2;
}

.glass-search .glass-input {
  padding-inline-start: 44px;
  border-radius: var(--gl-radius-full);
}
```

**Кільце фокусу.** `--gl-focus-ring` у темній темі дорівнює `color-mix(in srgb, var(--gl-color-primary) 15%, #ffffff)`, а в світлій — `--gl-color-primary-on-surface`. Межа при фокусі йде через `--gl-border-focus`, яке дорівнює `--gl-focus-ring`. Поверхня при фокусі — `--gl-surface-3`.

**Як побудовано:**
- Поле — це скло `--gl-surface-2` з блюром 16px. При фокусі поверхня світлішає до `--gl-surface-3`, а кільце `--gl-shadow-focus` додається до внутрішнього світла.
- Помилка має окремий фокусний кільцевий колір, який змішується з `--gl-color-text`. Це зроблено, щоб кільце було контрастним на склі.

---

### 9. Sidebar, rail, top bar: варіанти таб-бара

Варіанти задаються класами-модифікаторами на `.glass-tab-bar`: `--vertical`, `--start`/`--end`, `--rail`, `--labels`, `--top`, а також `.glass-tab-bar-dock--vertical` для плаваючого доку.

**Сайдбар (`--vertical`):**

```css
.glass-tab-bar.glass-tab-bar--vertical {
  position: relative; inset: auto;
  height: 100%; width: auto;
  flex-direction: column; justify-content: flex-start; align-items: stretch;
  gap: var(--gl-space-2xs);
  padding: var(--gl-space-sm);
  border-top: none;
  border-inline-end: 1px solid var(--gl-border-subtle);
  overflow-y: auto; overscroll-behavior: contain;
  box-shadow: var(--gl-inset-subtle);
}
.glass-tab-bar--vertical .glass-tab-bar__item {
  position: relative;
  flex-direction: row; justify-content: flex-start;
  gap: var(--gl-space-sm);
  width: 100%; min-width: 0; min-height: 44px;
  padding: var(--gl-space-xs) var(--gl-space-md);
  text-align: start; text-decoration: none;
}
.glass-tab-bar--vertical .glass-tab-bar__item:not(.is-active):hover { background: var(--gl-surface-1); }
.glass-tab-bar--vertical .glass-tab-bar__item.is-active { background: var(--gl-tab-bar-active-bg, var(--gl-surface-3)); }
```

**Фіксація до краю (`--start`, `--end`):**

```css
.glass-tab-bar.glass-tab-bar--vertical:is(.glass-tab-bar--start, .glass-tab-bar--end) {
  position: fixed; top: 0; bottom: 0; height: auto;
  padding-top: max(var(--gl-space-sm), env(safe-area-inset-top, 0px));
  padding-bottom: max(var(--gl-space-sm), env(safe-area-inset-bottom, 0px));
  z-index: var(--gl-tab-bar-z-index, 900);
}
.glass-tab-bar.glass-tab-bar--vertical.glass-tab-bar--start { inset-inline-start: 0; inset-inline-end: auto; }
.glass-tab-bar.glass-tab-bar--vertical.glass-tab-bar--end {
  inset-inline-end: 0; inset-inline-start: auto;
  border-inline-end: none; border-inline-start: 1px solid var(--gl-border-subtle);
}
```

**Rail (лише іконки, 72px):**

```css
.glass-tab-bar.glass-tab-bar--vertical.glass-tab-bar--rail {
  width: var(--gl-tab-bar-rail-width, 72px);
  align-items: center;
  padding-inline: var(--gl-space-xs);
}
.glass-tab-bar--rail .glass-tab-bar__item {
  justify-content: center;
  width: auto; min-width: 48px; min-height: 48px;
  padding: var(--gl-space-sm);
}
.glass-tab-bar--rail .glass-tab-bar__label {
  position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
  overflow: hidden; clip-path: inset(50%); white-space: nowrap; border: 0;
}
```

**Rail з підписами (`--labels`):**

```css
.glass-tab-bar--rail.glass-tab-bar--labels .glass-tab-bar__item {
  flex-direction: column; justify-content: center;
  gap: var(--gl-space-2xs);
  width: 100%; min-height: var(--gl-tab-bar-rail-item-height, 62px);
  padding: var(--gl-space-xs) var(--gl-space-2xs);
  border-radius: var(--gl-tab-bar-item-radius, var(--gl-radius-btn));
}
```

**Плаваючий rail на краю:**

```css
.glass-tab-bar.glass-tab-bar--floating.glass-tab-bar--vertical:is(.glass-tab-bar--start, .glass-tab-bar--end) {
  top: calc(var(--gl-tab-bar-floating-inset, 16px) + env(safe-area-inset-top, 0px));
  bottom: calc(var(--gl-tab-bar-floating-inset, 16px) + env(safe-area-inset-bottom, 0px));
  height: auto; max-height: none;
  padding: var(--gl-space-sm) var(--gl-space-xs);
  border: 1px solid var(--gl-border-subtle);
  border-radius: var(--gl-tab-bar-rail-radius, var(--gl-radius-card));
  overflow-y: auto;
}
```

**Верхній бар (`--top`):**

```css
.glass-tab-bar.glass-tab-bar--top {
  position: relative; inset: auto;
  height: auto;
  align-items: center;
  padding-bottom: var(--gl-space-xs);
  border-top: none; border-bottom: 1px solid var(--gl-border-subtle);
  box-shadow: 0 4px 20px rgba(0,0,0,0.08), var(--gl-inset-subtle);
}
@media (min-width: 640px) {
  .glass-tab-bar--top .glass-tab-bar__item {
    flex-direction: row; gap: var(--gl-space-xs);
    padding-inline: var(--gl-space-md);
  }
  .glass-tab-bar--top .glass-tab-bar__label { font-size: var(--gl-font-size-sm); }
}
```

**Бейдж (лічильник) на пункті:**

```css
.glass-tab-bar__badge {
  position: absolute; top: var(--gl-tab-bar-badge-top, -4px); inset-inline-end: var(--gl-tab-bar-badge-end, -8px);
  min-width: var(--gl-tab-bar-badge-size, 16px); height: var(--gl-tab-bar-badge-size, 16px); padding: 0 4px;
  border-radius: var(--gl-radius-full);
  background: var(--gl-color-error-dark, #d63027); color: #ffffff;
  font-size: 10px; font-weight: var(--gl-font-weight-semibold);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 6px color-mix(in srgb, var(--gl-color-error) 40%, transparent);
  outline: var(--gl-tab-bar-badge-ring-width, 0px) solid var(--gl-tab-bar-badge-ring-color, var(--gl-color-bg-mid));
}
```

**Light theme:** окремого блоку нема. Таб-бар читає `--gl-surface-3` і `--gl-surface-1` світлої теми. Колір бейджа `--gl-color-error-dark` у світлій темі — `#b02a37`. Кільце бейджа (`--gl-color-bg-mid`) стає `#f0f4f8`.

**Як побудовано:**
- Варіанти є одним компонентом із різними класами-модифікаторами. Сама панель змінює тільки розкладку (колонка, рейл, верхня смуга), а пункти, іконки, бейдж і дроплет лишаються тими самими.
- Рейл ховає текст через `clip-path: inset(50%)`, але залишає його для асистивних технологій.

---

### 10. Картка (`.glass-card`)

```css
.glass-card {
  background: var(--gl-surface-2);
  backdrop-filter: blur(var(--gl-blur));
  -webkit-backdrop-filter: blur(var(--gl-blur));
  border: 1.5px solid var(--gl-border-medium);
  border-radius: var(--gl-radius-card);
  padding: var(--gl-space-3xl) var(--gl-space-xl) var(--gl-space-2xl);
  box-shadow: var(--gl-shadow-card), var(--gl-inset-strong);
  --gl-list-flush-inset: var(--gl-space-xl);
  --gl-ctx-primary-text: var(--gl-color-primary-on-glass);
}

.glass-card--glow {
  position: relative; overflow: hidden;
  background: linear-gradient(to bottom,
    var(--gl-card-glow-top) 0%,
    var(--gl-card-glow-mid) 25%,
    var(--gl-card-glow-low) 55%,
    var(--gl-card-glow-bottom) 100%
  );
}

.glass-card--glow::before {
  content: '';
  position: absolute; top: 0; left: 10%; right: 10%; height: 1px;
  background: var(--gl-gloss-card);
  z-index: 1;
}

.glass-card__icon {
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto var(--gl-space-lg);
}

.glass-card__icon svg {
  width: 64px; height: 64px;
  stroke: var(--gl-card-icon-color); stroke-width: 1.2; fill: none;
}

.glass-card__text {
  color: var(--gl-card-text-color);
  font-size: var(--gl-font-size-base);
  font-weight: var(--gl-font-weight-normal);
  line-height: 1.55; text-align: center;
}
```

**Стани:** картка стану hover, active, focus і disabled не має. Підсвічення тільки через gloss-смужку `::before`.

**Light theme:**
- `--gl-surface-2` стає 0.60. `--gl-border-medium` — `rgba(0, 0, 0, 0.12)`. `--gl-shadow-card` — `0 4px 20px rgba(0, 0, 0, 0.06)`.
- Градієнт glow: `--gl-card-glow-top` 0.90 → `--gl-card-glow-bottom` 0.50.
- Колір іконки `--gl-card-icon-color` — `rgba(26, 42, 54, 0.65)`. Колір тексту `--gl-card-text-color` — `rgba(26, 42, 54, 0.68)`.
- Акцентний текст на картці: `--gl-color-primary-on-glass` у світлій темі дорівнює `--gl-color-primary-text` (`#e8852d`). У темній він світлішає на 60 % білого.

**Як побудовано:**
- Картка — скло `--gl-surface-2` з блюром 24px. Варіант `--glow` дає вертикальний градієнт від світлого до прозорого і тонку смужку-блік зверху.
- Відступи йдуть через `--gl-space-*`, тож картка масштабується разом із сіткою.

---

### 11. WebKit, доступність, режими

#### 11.1 Усі `-webkit-` властивості в джерелі

| Властивість | Селектор(и) |
|---|---|
| `-webkit-backdrop-filter` | Практично всі скляні компоненти: `.glass-pill`, `.glass-card`, `.glass-btn--primary/secondary/tertiary`, `.glass-status`, `.glass-input`, `.glass-textarea`, `.glass-select`, `.glass-toggle__track`, `.glass-checkbox__box`, `.glass-radio__circle`, `.glass-avatar`, `.glass-modal`, `.glass-sheet`, `.glass-toast`, `.glass-tab-bar`, `.glass-tab-bar__accessory`, `.glass-tab-bar-dock`, `.glass-popover`, `.glass-tooltip`, `.glass-menu`, `.glass-sort__ghost`, `.glass-table--sticky thead th`, `.glass-accordion__item`, `.glass-list`, `.glass-list__item--tile`, `.glass-modal-overlay`, `.glass-sheet-overlay`, а також `.glass-tab-bar.glass-tab-bar--droplet[data-droplet]::before` |
| `-webkit-font-smoothing: antialiased` | `.glass-bg`, `.glass-modal-overlay`, `.glass-toast`, `.glass-sheet-overlay` |
| `-webkit-tap-highlight-color: transparent` | майже всі інтерактивні компоненти: `.glass-pill`, `.glass-btn`, `.glass-toggle`, `.glass-checkbox`, `.glass-radio`, `.glass-input`, `.glass-textarea`, `.glass-tab-bar__item`, `.glass-tab-bar__accessory`, `.glass-theme-toggle`, `.glass-toast__action`, `.glass-toast__close`, `.glass-accordion__trigger`, `.glass-segmented__item`, `.glass-date-strip__day`, `.glass-calendar__nav`, `.glass-calendar__day`, `.glass-sheet__close`, `.glass-badge--interactive` |
| `-webkit-appearance: none` (з `appearance: none`) | `.glass-input[type="date"]`, `[type="time"]`, `[type="datetime-local"]`, `[type="month"]`, `.glass-select`, `.glass-range`, `.glass-toast__action`, `.glass-toast__close`, `.glass-badge--interactive`, `.glass-segmented__item`, `.glass-date-strip__day`, `.glass-calendar__nav`, `.glass-calendar__day`, `.glass-sheet__close`, `.glass-range::-webkit-slider-thumb` |
| `-webkit-appearance: none` (без `appearance`) | `.glass-range::-webkit-slider-thumb` (рядок з `appearance: none` стоїть поруч), `.glass-select`, `.glass-range` |
| `::-webkit-calendar-picker-indicator` | `.glass-input` |
| `::-webkit-date-and-time-value` | `.glass-input` |
| `::-webkit-slider-thumb` | `.glass-range` |
| `::-webkit-scrollbar` | `.glass-segmented--scroll`, `.glass-date-strip` |
| `-webkit-box`, `-webkit-line-clamp`, `-webkit-box-orient` | `.glass-list__subtitle--wrap` |
| `-webkit-print-color-adjust: exact` | `@media print`, список з п.37 джерела |

Розрізнення `-webkit-appearance` і `appearance` у блоці `.glass-range` видно в такому фрагменті:

```css
.glass-range {
  -webkit-appearance: none; appearance: none;
  width: 100%; height: 6px;
  border-radius: var(--gl-radius-full);
  background: var(--gl-range-track-bg);
  border: 1px solid var(--gl-range-track-border);
  outline: none; cursor: pointer;
}

.glass-range::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none;
  box-sizing: border-box;
  width: 26px; height: 26px;
  border-radius: var(--gl-radius-pill);
  background: linear-gradient(135deg,
    var(--gl-color-primary) 0%, var(--gl-color-primary-dark) 100%
  );
  border: var(--gl-range-thumb-border);
  box-shadow: 0 2px 8px color-mix(in srgb, var(--gl-color-primary-mid) 35%, transparent), var(--gl-inset-strong);
  margin-top: -2px; cursor: pointer;
  transition: var(--gl-transition);
}
```

Крім цього, `-webkit-` префікси для `backdrop-filter` стоять не в одному місці. Вони дублюють стандартну властивість, а не замінюють її.

#### 11.2 `@supports`, `prefers-*`, solid, forced-colors

**`@supports`:** у джерелі нема (нема в джерелі). Замість нього є коментарі про fallback через ланцюжки `var(...)`, наприклад `--gl-select-chevron` або `--gl-tab-bar-active-glow`.

**`prefers-reduced-motion`:** є в кількох місцях.

```css
/* Droplet — вимикає переходи капель */
@media (prefers-reduced-motion: reduce) {
  :is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet]::before,
  :is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet][data-droplet-dir]::before,
  :is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet][data-droplet-drag]::before,
  :is(.glass-tab-bar.glass-tab-bar--droplet, .glass-segmented.glass-segmented--droplet)[data-droplet][data-droplet-axis="y"][data-droplet-drag]::before { transition: none; }
  .glass-tab-bar--droplet[data-droplet] .glass-tab-bar__icon { transition: color 0.25s ease, transform 0s; }
  .glass-segmented--droplet[data-droplet] .glass-segmented__dot,
  .glass-segmented--droplet[data-droplet] .glass-segmented__icon { transition: none; }
}

/* Accordion */
@media (prefers-reduced-motion: reduce) {
  .glass-accordion__content { transition: none; }
}

/* Popover, tooltip, menu */
@media (prefers-reduced-motion: reduce) {
  .glass-popover[popover], .glass-popover[popover]:popover-open,
  .glass-tooltip[popover], .glass-tooltip[popover]:popover-open,
  .glass-menu[popover], .glass-menu[popover]:popover-open { transition: none; animation: none; }
}

/* Sheet */
@media (prefers-reduced-motion: reduce) {
  .glass-sheet-overlay, .glass-sheet-overlay .glass-sheet { transition: none; }
}

/* Skeleton */
@media (prefers-reduced-motion: reduce) {
  .glass-skeleton__line { animation: none; }
}
```

**`prefers-reduced-transparency`:** нема в джерелі.

**`prefers-contrast`:** нема в джерелі.

**Solid-поверхні (`data-surface="solid"`):** вимикають блюр, внутрішнє світло і gloss. Поверхні стають непрозорими, на основі `--gl-color-bg-mid`:

```css
[data-surface="solid"],
[data-surface="tint"],
[data-surface="solid"] [data-theme="dark"],
[data-surface="tint"] [data-theme="dark"] {
  --gl-surface-1:            var(--gl-solid-surface-1);
  --gl-surface-2:            var(--gl-solid-surface-2);
  --gl-blur:                 0px;
  --gl-blur-light:           0px;
  --gl-blur-soft:            0px;
  --gl-blur-heavy:           0px;
  --gl-inset-subtle:         inset 0 0 0 transparent;
  --gl-gloss-card:           none;
  --gl-gloss-modal:          none;
  --gl-gloss-progress:       none;
  --gl-gloss-droplet:        none;
  --gl-range-thumb-border:   2px solid transparent;
}
```

Є також варіант `data-surface="tint"`, де поверхні стають напівпрозорими тінтами тексту (без блюру). Компоненти поверх контенту (модалки, панелі, таб-бар) лишаються твердими.

**Forced colors (Windows high contrast).** Тіні зникають, тож фокус має бути через `outline`:

```css
@media (forced-colors: active) {
  .glass-input:focus,
  .glass-textarea:focus,
  .glass-select:focus,
  .glass-toggle__input:focus-visible + .glass-toggle__track,
  .glass-checkbox__input:focus-visible + .glass-checkbox__box,
  .glass-radio__input:focus-visible + .glass-radio__circle,
  .glass-range:focus-visible,
  .glass-toast__action:focus-visible,
  .glass-toast__close:focus-visible,
  .glass-tab-bar__item:focus-visible,
  .glass-tab-bar__accessory:focus-visible,
  .glass-badge--interactive:focus-visible,
  .glass-breadcrumbs__crumb:focus-visible,
  .glass-table__sort:focus-visible,
  .glass-segmented__item:focus-visible,
  .glass-sheet__close:focus-visible,
  .glass-date-strip__day:focus-visible,
  .glass-calendar__nav:focus-visible,
  .glass-calendar__day:focus-visible { outline: 2px solid; outline-offset: 2px; }

  .glass-accordion__trigger:focus-visible,
  .glass-menu__item:focus-visible,
  .glass-menu__item.is-focus-visible,
  .glass-list__item--interactive:focus-visible,
  .glass-tree__row:focus-visible,
  .glass-tree__row.is-focus-visible,
  .glass-tree [role="treeitem"]:focus-visible > .glass-tree__row { outline: 2px solid; outline-offset: -2px; }
}
```

**Друк:**

```css
@media print {
  .glass-toggle__track,
  .glass-checkbox__box,
  .glass-radio__circle,
  .glass-progress__fill,
  .glass-range,
  .glass-steps__item--current .glass-steps__num,
  .glass-date-strip__day[aria-pressed="true"],
  .glass-calendar__day[aria-pressed="true"],
  .glass-date-strip__mark,
  .glass-calendar__mark,
  .glass-segmented__dot {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
```

**Як побудовано:**
- Режими перемикаються атрибутами на `<html>`: `data-theme`, `data-density`, `data-surface`. Кожен режим перевизначає лише токени, а не правила компонентів.
- Доступність закладена в кількох місцях: `focus-visible` через `--gl-shadow-focus` або `outline`, `prefers-reduced-motion` вимикає переходи, а `forced-colors` замінює тіні на `outline`.

---

### Неочевидне для WebKit

Ці речі є в CSS саме через поведінку Safari/WebKit (або через пов'язані з нею обмеження iOS).

1. **`-webkit-backdrop-filter` поруч із `backdrop-filter`** (наприклад, `.glass-pill`, `.glass-card`, `.glass-modal`). Скло працює тільки з префіксом. У джерелі префікс дубльовано в кожному скляному правилі.

2. **`.glass-input[type="date"]` (і `time`, `datetime-local`, `month`) з `-webkit-appearance: none`.** У коментарі сказано, що iOS малює ці поля як нативний контрол із власною шириною: поле виходило ширшим за колонку, а значення — по центру. Без вигляду iOS дає ширину колонки, а піккер лишається робочим.

3. **`.glass-input::-webkit-date-and-time-value { text-align: start; }`** — окреме правило. У коментарі сказано, що браузер, який не знає цього псевдоелемента, відкидає все правило, тож його винесено окремо.

4. **`.glass-input::-webkit-calendar-picker-indicator { display: var(--gl-input-picker-icon, revert); }`** — стрілка піккера дати в WebKit. Токен `--gl-input-picker-icon: none` її ховає.

5. **`.glass-range::-webkit-slider-thumb` і `.glass-range::-moz-range-thumb`** — два окремі правила для двох движків. У коментарі сказано, що список із обома селекторами браузер відкидає повністю.

6. **`.glass-tab-bar__badge` з `outline` замість `box-shadow` у `0px`.** Коментар: тіньовий шар нульового розміру все одно фарбував краї в WebKit і Firefox.

7. **`.glass-tab-bar` з `padding-bottom: max(var(--gl-space-xs), env(safe-area-inset-bottom, 0px));`** — відступ від індикатора дому на iPhone з `viewport-fit=cover`. Також `.glass-toast` із `--gl-toast-top` (коментар пише про `env(safe-area-inset-top)`), `.glass-sheet` із `padding-bottom` через `env(safe-area-inset-bottom)`.

8. **`.glass-tab-bar { align-items: flex-start; align-items: safe center; }`** — перший рядок є запасним для браузерів без `safe`. Другий рядок працює там, де inset менший за потребу елементів (iPhone з `viewport-fit=cover`).

9. **`touch-action: pan-y` на `.glass-tab-bar.glass-tab-bar--droplet[data-droplet]` і `pan-x` для колонки.** Дозволяє свайп сторінки, але перехоплює вертикальний чи горизонтальний дрег капель на сенсорних екранах iOS.

10. **`.glass-segmented--scroll::-webkit-scrollbar { display: none; }`** і `.glass-date-strip::-webkit-scrollbar`. Поруч стоїть `scrollbar-width: none` для Firefox. Це сховані смуги прокрутки в WebKit.

11. **`.glass-list__subtitle--wrap` з `display: -webkit-box`, `-webkit-line-clamp`, `-webkit-box-orient`.** Ліміт рядків (за замовчуванням 3) у WebKit досі реалізовано тільки через ці властивості. У коментарі є окремий рядок: `display: -webkit-box` перебиває атрибут `hidden`.

12. **`.glass-table--sticky thead th` з `-webkit-backdrop-filter`.** Блюр заголовка при прокрутці таблиці. Окремий рядок: `border-bottom: 0` і `box-shadow: inset 0 -1px 0`, бо `border` колапсованої таблиці не рухається разом із клітинкою.

13. **`-webkit-font-smoothing: antialiased`** на `.glass-bg`, `.glass-modal-overlay`, `.glass-toast`, `.glass-sheet-overlay`. Ця властивість діє лише в WebKit (macOS і iOS).

14. **`-webkit-tap-highlight-color: transparent`** на всіх інтерактивних елементах. Прибирає синій відгук при тапі на iOS Safari.

15. **`dialog.glass-modal-overlay` і `dialog.glass-sheet-overlay` з `overflow: clip`** (у sheet). У коментарі сказано, що `hidden` робить діалог контейнером прокрутки, і при фокусі в шторці сторінка «їде». Це поведінка, спільна для всіх браузерів, але в коментарі вона описана на прикладі фокусу з `showModal()`.

16. **`.glass-tab-bar__item` з `transition-property: color, background-color, box-shadow, opacity, transform;`** замість `all`. Коментар: при `all` зміна розкладки тривала 250 мс, і виміряний розмір пункту був ще старим.

Цей список не повний: частину рішень джерело пояснює загальною поведінкою браузерів, а не окремо WebKit.

## §2 Крапля і правила GlassKit-Elements — витяг

## GlassKit: крапля (droplet) і витяги з SKILL.md

**Джерела:** `glasskit-droplet.js` (`@jungherz-de/glasskit` 1.41.0) і GlassKit-Elements SKILL.md (розділи 2, 3.3, 6).

**Обмеження:** `glasskit.css` у джерелі немає. Тому CSS-переходи, easing-и і типові значення токенів, які задає стилі, позначаю як «нема в джерелі».

---

### A. Крапля (droplet)

#### A.1 Що робить модуль

Модуль не малює краплю. Малює її CSS (`::before` рядка). JS робить чотири речі:

- ставить атрибути `data-droplet*` на рядок;
- записує чотири CSS-змінні з геометрією обраного елемента;
- веде лінзу: елемент під краплею отримує клас `is-under-droplet`;
- обробляє перетягування пальцем.

Селектори:

```js
const ROWS = '.glass-tab-bar--droplet, .glass-segmented--droplet';
const ITEMS = '.glass-tab-bar__item, .glass-segmented__item';
```

Обраний елемент — це таб із `.is-active` або опція з `aria-pressed="true"`:

```js
  const isChosen = options.isChosen
    || (it => it.classList.contains('is-active') || it.getAttribute('aria-pressed') === 'true');
```

#### A.2 Константи

| Параметр | Значення | Джерело |
|---|---|---|
| Тривалість лінзи, fallback (`--gl-droplet-duration`) | 300 ms | JS, лише коли токен порожній |
| Затримка заднього краю, fallback (`--gl-droplet-trail-delay`) | 40 ms | JS, лише коли токен порожній |
| Тривалість заднього краю, fallback (`--gl-droplet-trail-duration`) | 500 ms | JS, лише коли токен порожній |
| Запас лінзи після руху | +80 ms | JS |
| Сумарний час ведення лінзи без токенів | 620 ms | обчислено: max(300, 40 + 500) + 80 |
| Підйом (lift), fallback (`--gl-droplet-lift-duration`) | 280 ms | JS |
| Коефіцієнт підйому (`--gl-droplet-lift`) | 0.86; `1` = без стиснення | SKILL.md, 3.3 |
| Поріг «позиція змінилась» для переходу | більше 1 px | JS |
| Поріг виявлення прокрутки | більше 1 px | JS |
| Допуск масштабу, `border-box` | 0.05 | JS |
| Допуск масштабу, інші | 0.5 | JS |
| Поріг перерахунку при resize | більше 0.5 px | JS |
| Початок перетягування | 8 px | JS |
| Зона автопрокрутки біля краю рядка | 32 px | JS |
| Крок автопрокрутки | 6 px за кадр | JS |
| Вікно ігнорування кліку після перетягування | 400 ms | JS |
| Кнопка миші для старту | 0 (ліва) | JS |
| Easing і тривалість переднього краю (`-duration`, `-easing`) за замовчуванням | нема в джерелі | CSS |
| Easing заднього краю (`-trail-easing`) за замовчуванням | нема в джерелі | CSS |
| `-settle-duration`, `-settle-easing`, `-lens-duration`, `-lens-easing` за замовчуванням | нема в джерелі | CSS |

Токени `--gl-droplet-*` вказані в SKILL.md (3.3) і читаються модулем через `getComputedStyle`. Fallback-значення з JS потрібні лише тоді, коли змінна порожня. Якщо `glasskit.css` задає її, береться значення з CSS.

#### A.3 Алгоритм покроково

**Крок 1. Прикріплення.** Один рядок прикріплюється один раз. Повторний виклик повертає той самий handle:

```js
export function attachDroplet(row, options = {}) {
  if (attached.has(row)) return attached.get(row);
```

Одразу створюються три спостерігачі: `ResizeObserver` на рядок і на елементи, `MutationObserver` на зміни `class` і `aria-pressed`, та слухачі `pointer*`.

```js
  const mo = new MutationObserver(update);
  mo.observe(row, { subtree: true, childList: true, attributes: true, attributeFilter: ['class', 'aria-pressed'] });
```

**Крок 2. Вибір.** `update()` шукає обраний елемент. Якщо його немає, знімає `data-droplet`. Якщо є і він змінився, викликає `place()` з перевіркою, чи була крапля вже на екрані:

```js
    if (it !== chosen) place(it, chosen !== null && row.dataset.droplet !== undefined);
```

**Крок 3. Розміщення з рухом.** `place(it, travel)` вирішує, чи йде крапля в подорож. Якщо так, ставить напрямок і підйом, запускає лінзу:

```js
    if (travel && motion.matches && Math.abs(to - pos) > 1) {
      row.dataset.dropletDir = axisY ? (to > pos ? 'down' : 'up') : (to > pos ? 'right' : 'left');
      row.dataset.dropletLift = '';
      clearTimeout(liftTimer);
      liftTimer = setTimeout(() => { delete row.dataset.dropletLift; }, token('lift-duration', 280));
      follow();
    } else {
      delete row.dataset.dropletDir;
    }
```

**Крок 4. Запис геометрії.** `put()` записує чотири CSS-змінні. Ліва і права межі, верх і низ задаються окремо:

```js
  const set = (k, px) => row.style.setProperty(`--gl-droplet-${k}`, `${px}px`);
```

```js
  const put = b => {
    pos = axisY ? b.top : b.left;
    set('left', b.left); set('right', row.clientWidth - b.left - b.width);
    set('top', b.top); set('bottom', row.clientHeight - b.top - b.height);
  };
```

**Крок 5. Підйом.** `data-droplet-lift` стоїть, поки йде рух, і знімається через `lift-duration`. Це дає «стиснення»: краплю піднято, її тінь глибша.

**Крок 6. Лінза під час руху.** `follow()` читає `::before` рядка кожен кадр і рахує центр краплі. Цикл триває довше за рух на 80 ms:

```js
    const length = Math.max(token('duration', 300), token('trail-delay', 40) + token('trail-duration', 500)) + 80;
```

Центр рахується так:

```js
      const cs = getComputedStyle(row, '::before');
      // ...
        const l = parseFloat(cs.left), r = parseFloat(cs.right);
        lens(l + (row.clientWidth - l - r) / 2);
```

Тобто лінза стежить за реальною позицією краплі, а не за окремим таймером.

`lens()` позначає найближчий доступний елемент. Доступний означає не `disabled` і не `aria-disabled="true"`. Позначка змінюється лише тоді, коли елемент справді змінився:

```js
    if (below !== under) {
      if (under) mark(under, false);
      if (below) mark(below, true);
      under = below;
    }
```

**Крок 7. Перетягування.** Слухачі `pointerdown` перевіряють, чи почався жест на обраному елементі. Якщо рядок прокручується, жест має починатися саме на ньому:

```js
    if (!chosen || drag || !usable(chosen) || (e.pointerType === 'mouse' && e.button !== 0)) return;
    if (scrolls() && !e.composedPath().includes(chosen)) return;
```

Рух дає краплю тільки після 8 px:

```js
    if (!drag.moved) {
      if (Math.abs(drag.client - drag.start) < 8) return;
      drag.moved = true;
      row.setPointerCapture(e.pointerId);
      delete row.dataset.dropletDir;
      row.dataset.dropletDrag = '';
    }
```

**Крок 8. Відпускання.** Якщо був рух, знімається `data-droplet-drag`, лінза гаситься. Цілі елемент вибирається лише на `pointerup`, не на `pointercancel`. Далі крапля сідає на обраний елемент:

```js
    if (!d.moved) return;                         // a tap: the item's own click does it
    delete row.dataset.dropletDrag;
    lens(null);
    const target = d.below || chosen;
    if (e.type === 'pointerup' && target !== chosen) choose(target);
    // Settle where the choice is, unless it already set the drop on its way.
    const next = items().find(isChosen) || chosen;
    if (next !== chosen || row.dataset.dropletDir === undefined) place(next, true);
    eatClick = true;                              // the click the drag ends in
    setTimeout(() => { eatClick = false; }, 400);
```

Клік, яким закінчується перетягування, гасить capture-слухач:

```js
  const click = e => { if (eatClick) { eatClick = false; e.stopPropagation(); e.preventDefault(); } };
```

**Крок 9. Вибір через `click`.** Дефолтний `choose` викликає `it.click()`. Тож вибір іде через обробник сторінки, а не напряму:

```js
  const choose = options.choose || (it => it.click());
```

**Крок 10. Знищення.** `destroy()` знімає спостерігачі, слухачі, атрибути і змінні та видаляє рядок з `WeakMap`.

#### A.4 Два краї і різний темп

У JS обидва краї рахуються разом, в одному `put()`. Різниця в часі живе в CSS. Згідно з SKILL.md (3.3), токени такі:

> `--gl-droplet-duration` and `-easing` (the leading edge), `-trail-duration`, `-trail-delay`, `-trail-easing` (the trailing one)

Як саме CSS застосовує ці токени до лівого і правого країв, нема в джерелі.

JS читає лише `duration`, `trail-delay`, `trail-duration` і `lift-duration`, і тільки для таймінгу лінзи та підйому.

SKILL.md описує поведінку так: передній край іде першим, задній іде за ним, біжить пласкіше і сідає з невеликим «коливанням». Точну криву для цього нема в джерелі.

Ще одна деталь з SKILL.md: краплю не можна налаштувати через `::part`. Вона є `::before` елемента `<nav>` у shadow root, тому часом керують лише токенами.

#### A.5 Ресайз і масштаб

Коли рядок або обраний елемент змінює розмір, `ResizeObserver` перераховує позицію. Якщо змін більше 0.5 px, крапля стає на місце без подорожі:

```js
  const ro = new ResizeObserver(() => {
    if (!chosen || drag?.moved) return;
    const b = { ...boxOf(chosen), rowWidth: row.clientWidth, rowHeight: row.clientHeight };
    if (!placed || Object.keys(b).some(k => Math.abs(b[k] - placed[k]) > 0.5)) place(chosen, false);
  });
```

Окремо модуль виправляє масштаб предків. Якщо батько має `transform: scale(...)`, прямокутники з `getBoundingClientRect` будуть у пікселях екрана. Модуль ділить відстані на масштаб:

```js
    const scale = (onScreen, own) => onScreen > 0 && own > 0 && Math.abs(onScreen - own) > tolerance ? onScreen / own : 1;
```

Для рядків, що прокручуються, позиція береться з `scrollLeft` (або `scrollTop` для колонки). Автопрокрутка під час перетягування працює біля країв зони 32 px.

#### A.6 RTL

**Нема в джерелі.** Модуль не читає `dir` і не має окремої обробки RTL. Він працює з фізичними іменами `left`/`right` і з `scrollLeft`.

Що з цього випливає: поведінка в RTL з джерела не видна. Перевірити треба на iPhone Safari з `dir="rtl"`.

Не плутайте з тим, що в SKILL.md сказано про `<glk-tab-dock dock="start|end">`: start і end там йдуть за напрямком письма. Це стосується доку, а не краплі.

#### A.7 Reduced motion

Модуль читає медіа-запит один раз, але перевіряє його при кожному `place`:

```js
  const motion = matchMedia('(prefers-reduced-motion: no-preference)');
```

Умова в `place` відсікає подорож, тож крапля просто стрибає на місце. Той самий шлях у `up()` теж використовує `place(next, true)`, і без руху він стрибає.

Під час перетягування пальцем `motion` не перевіряється. Крапля слідує за пальцем у будь-якому режимі.

SKILL.md підтверджує: `prefers-reduced-motion` змушує краплю стрибати.

#### A.8 Клавіатура

Модуль слухає лише `pointer*`. Клавішних обробників у ньому немає. Стрілки і `Enter` не керують краплею. Перетягування з клавіатури не передбачене.

Вибір з клавіатури все одно анімується. Ланцюжок такий: нативний `click` на табі → обробник сторінки змінює `is-active` або `aria-pressed` → `MutationObserver` викликає `update()` → `place(it, true)`.

Фокус показує SKILL.md (3.3): «Every bar shows a focus ring on the item that has the keyboard focus (GlassKit 1.32.0)». Навігація стрілками: нема в джерелі.

#### A.9 Підключення

**Усі рядки на сторінці** (з коментаря модуля):

```js
import { attachDroplets } from '@jungherz-de/glasskit/glasskit-droplet.js';
attachDroplets();                    // every --droplet row in the page
```

**Один рядок і керування:**

```js
import { attachDroplet } from '@jungherz-de/glasskit/glasskit-droplet.js';
const drop = attachDroplet(row);     // one row; drop.update(), drop.destroy()
```

**Опції для рядків, де елементи не в DOM рядка.** Це приклад, мій, не з джерела. У джерелі є лише перелік опцій:

```js
const drop = attachDroplet(row, {
  items: () => [...row.querySelectorAll('.my-item')],
  isChosen: it => it.dataset.selected === 'true',
  choose: it => it.click(),
  lens: (it, on) => it.classList.toggle('my-under', on),
});
```

Якщо `MutationObserver` не бачить елементи, після зміни вибору викликайте `drop.update()`. Так сказано в джерелі.

**Вертикальний рядок.** Вісь y визначається через `aria-orientation="vertical"` або `flex-direction: column`. Модуль ставить `data-droplet-axis="y"` і використовує напрямки `down`/`up`.

**Таб-бар у SKILL.md:**

```html
<glk-tab-dock>
  <glk-tab-bar floating droplet>
    <glk-tab-item label="Home" active>…</glk-tab-item>
    <glk-tab-item label="Docs">…</glk-tab-item>
  </glk-tab-bar>
</glk-tab-dock>
```

`droplet` можна задати і властивістю: `bar.droplet = true` (з 1.28.0; раніше це не працювало).

**Як web component підключає модуль:** нема в джерелі. У джерелі є лише те, що `glk-tab-bar droplet` і `glk-segmented droplet` працюють без додаткового імпорту, бо бандли вже містять модуль.

#### A.10 Що модуль пише у DOM (для CSS-автора)

- `data-droplet` на рядку: крапля є.
- `data-droplet-dir`: `right`, `left`, `down` або `up`; лише під час подорожі.
- `data-droplet-lift`: поки йде підйом.
- `data-droplet-drag`: поки тримають пальцем.
- `data-droplet-axis="y"`: вертикальний рядок.
- `--gl-droplet-left`, `-right`, `-top`, `-bottom`: у px, inline на рядку.
- `.is-under-droplet` на елементі під краплею.

Читає модуль із CSS: `--gl-droplet-duration`, `-trail-delay`, `-trail-duration`, `-lift-duration`. Решта читається тільки CSS.

---

### B. SKILL.md: ядро, таб-бар, правила

#### B.1 Основні поняття (розділ 2)

- **Префікс і рендер.** Елементи мають префікс `glk-*`. Рендеряться в відкритий Shadow DOM (`mode: 'open'`) з `adoptedStyleSheets`. Таблиця стилів одна на всі елементи. Токени оголошені на документі, а не в shadow roots.
- **Синхронізація теми.** Глобальний `MutationObserver` стежить за `<html data-theme>`, `<html data-density>` і `<html data-surface>` (з 1.24.0). Тому тему ставлять на `<html>`, а не на `<body>`.
- **Події.** Події `glk-*` мають `bubbles: true, composed: true`. Винятки: `glk-open`, `glk-close`, `glk-closed` лишаються на елементі (з 1.35.0). Нативний `input` приходить від браузера по одному разу на клавішу (з 1.36.0).
- **Форми.** `GlkFormElement` використовує `ElementInternals` (`static formAssociated = true`). Значення, reset і валідність внутрішнього поля підтримуються з 1.20.0. Елемент має бути всередині `<form>`, інакше `FormData` буде порожній.
- **Фокус.** Елементи з одним полем передають фокус полю: `element.focus()`, клік на лейбл, `<label for>`. З 1.33.2 `<glk-button>`, `<glk-pill>`, `<glk-tab-item>` і `<glk-tab-accessory>` передають фокус своїй кнопці або посиланню, включно з `autofocus`. Елементи з кількома контролами віддають фокус тому, який досягає Tab. Приклади: вибраний варіант `<glk-segmented>`, день `<glk-calendar>`, кнопка вибору в `<glk-image-picker>`.
- **Disabled.** Елементи форм слідують за своїм `disabled` і за `<fieldset disabled>` (з 1.22.3). Властивість `disabled` відображає атрибут.
- **Ролі на хості.** `<glk-menu-item>`, `<glk-tree-item>` тощо несуть роль і стани через `ElementInternals` (з 1.32.0). `<glk-progress>` є прогрес-баром (з 1.33.2).
- **Панелі.** `<glk-popover>`, `<glk-tooltip>`, `<glk-menu>` і «…» у `<glk-breadcrumbs>` відкриваються в top layer через popover API (з 1.32.0). Вони лежать поверх усіх stacking context і не обрізаються батьками. Їх перевертають і зсувають на краю в'юпорту. Потрібен popover API. У джерелі вказано: Chrome 114, Safari 17, Firefox 125. Відповідність версії iOS Safari нема в джерелі.

**Кастомні властивості.** `--gl-*`, визначені на `:root` або `<html>`, проходять через межі shadow DOM успадкуванням. Тобто тему можна задати одним глобальним стилем.

**Власний елемент.** `GlkElement` і `GlkFormElement` експортовані. Приклад з SKILL.md:

```js
class DemoCounter extends GlkElement {
  static get observedAttributes() { return ['count']; }
  render() {                       // build into this._wrapper
    this._btn = this.createElement('button', ['glass-btn', 'glass-btn--secondary', 'glass-btn--sm', 'glass-btn--auto']);
    this._wrapper.appendChild(this._btn);
  }
  setupEvents() {                  // runs on every connect
    this._onClick = () => { this.count += 1; this.emit('demo-count', { count: this.count }); };
    this._btn.addEventListener('click', this._onClick);
  }
  teardownEvents() { this._btn?.removeEventListener('click', this._onClick); }   // every disconnect
  onAttributeChanged() { this._btn.textContent = `Clicked ${this.count}×`; }      // after first render
  get count() { return Number(this.getAttribute('count')) || 0; }
  set count(v) { this.setAttribute('count', v); }
}
customElements.define('demo-counter', DemoCounter);
```

**Правила для підкласу** (з SKILL.md):

- будувати тільки в `this._wrapper`;
- слухачі тримати в `setupEvents()` / `teardownEvents()`, а не в `render()`;
- використовувати `emit()`, а не `dispatchEvent()`;
- не змішувати бандл і `base.js`: `instanceof` не спрацює між двома копіями `GlkElement`, а таблиця стилів буде завантажена двічі.

**Світлі діти (light DOM).** `<glk-select>` (`<option>`), `<glk-tab-item>` (`<svg>`) і `<glk-modal>` (`[slot="actions"]`) копіюють дітей у shadow tree. З 1.12.0 копії синхронізуються через `MutationObserver`. З 1.28.0 спостерігач дивиться і на атрибути дітей. Якщо треба примусово: `element.refresh()`.

**Переміщення елемента.** Переміщення DOM-вузла роз'єднує і знову з'єднує елемент. Слухачі та синхронізація теми відновлюються при кожному з'єднанні (з 1.12.0). Якщо тема змінилась, поки елемент був поза документом, він оновиться при з'єднанні (з 1.21.0).

**Брендинг (з 1.9.0).** Перевизначайте `--gl-*` будь-де в документі:

```css
/* brand.css, loaded after glasskit.css */
:root, [data-theme='dark'] { --gl-color-primary: #2e9e8f; }
[data-theme='light']       { --gl-color-primary: #21786d; }
```

**Primary як текст (з 1.26.0).** Для світлої і темної теми є окремий токен `--gl-color-primary-text`. Правило для світлої теми пишемо після темного, бо `:root` збігається і зі світлою темою:

```css
:root, [data-theme='dark'] { --gl-color-primary-text: color-mix(in srgb, var(--gl-color-primary) 18%, #ffffff); }
[data-theme='light']       { --gl-color-primary-text: var(--gl-color-primary); }
```

`--gl-tab-bar-active-color` задає колір іконки і підпису активного табу. Якщо не задано, береться `--gl-color-primary-text`. Світіння і точка лишаються в primary, спотлайт — у `--gl-tab-bar-spotlight-color`.

**Лише токени, без `color-scheme` (з 1.20.0).** Блоки токенів GlassKit раніше ставили `color-scheme` на документ, і сторінка ставала темною навіть там, де GlassKit не використовувався. Тепер на документ іде лише `@layer glasskit-defaults` з токенами. `color-scheme` ставиться на обгортку кожного елемента.

**Вимкнути дефолти:**

```html
<html data-glk-defaults="off">
```

**Іконки.** Іконка має бути прямим дитиною:

```html
<glk-button><svg viewBox="0 0 24 24">…</svg>Save</glk-button>
<glk-list-item title="Download"><svg slot="leading" viewBox="0 0 24 24">…</svg></glk-list-item>
```

Обгортка не працює:

```html
<!-- the assigned node is the <span>; the <svg> inside is unreachable from the shadow root -->
<glk-list-item title="…"><span slot="leading"><svg …></svg></span></glk-list-item>
```

Власні стилі перекривають `::slotted()` з shadow tree. Наприклад, `glk-list-item svg { width: 32px }` у вашому CSS діє. Але `.glass-list__leading` має фіксовані 28×28, тому збільшуйте і контейнер.

**CSS parts (з 1.8.0).** Для розкладки є parts. Приклади з джерела:

```css
glk-card::part(card) { border-radius: 8px; }
glk-modal::part(footer) { justify-content: flex-start; }
```

`height: 100%` на part працює тільки тоді, коли хост має визначену висоту.

#### B.2 Таб-бар `<glk-tab-bar>` + `<glk-tab-item>` (розділ 3.3)

**Базовий приклад:**

```html
<div class="glass-bg glass-bg--has-tab-bar">
  <!-- page content -->
  <glk-tab-bar>
    <glk-tab-item label="Home" active>
      <svg viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
    </glk-tab-item>
    <glk-tab-item label="Search">
      <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/></svg>
    </glk-tab-item>
    <glk-tab-item label="Profile" badge="3">
      <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/></svg>
    </glk-tab-item>
  </glk-tab-bar>
</div>
```

**Атрибути `<glk-tab-bar>`** (з таблиці SKILL.md):

- `static`: `position: relative` замість fixed. Для доків і превью.
- `floating`: пілюльний варіант, клас `.glass-tab-bar--floating`. Використовується всередині `<glk-tab-dock>`.
- `droplet`: активний таб сидить на краплі. Рекомендовано.
- `orientation`: `horizontal` (типово) або `vertical`.
- `rail`: з `vertical` дає лише іконки; `rail="labels"` тримає підписи під іконкою (з 1.33.0).
- `dock`: з `vertical` — `start` або `end`.
- `placement`: `bottom` (типово) або `top`.
- `label`: назва навігації (`aria-label` на `<nav>`). Потрібна, якщо навігацій кілька.

Слоти з 1.33.0: `leading` (марка або акcесуар), `trailing` (наприклад, акаунт). Вони не є табами: крапля, `active` і `glk-tab-change` їх ігнорують.

**Атрибути `<glk-tab-item>`:**

- `label`: назва табу.
- `active`: активний стан. Має `aria-current="page"` (з 1.32.0).
- `badge`: число на іконці.
- `badge-label`: слова для числа. Приклад з SKILL.md: `label="Customers" badge="3" badge-label="3 new"` читається як «Customers, 3 new».
- `badge-dot`: точка без числа (з 1.38.0). Не озвучується. Для озвучення дайте `badge-label`. Не використовуйте `badge="!"`.
- `href`: робить таб посиланням. Клік із середньою кнопкою або з модифікатором відкриває в новій вкладці, і `glk-tab-select` не спрацьовує.

**Іконка.** `<svg>` копіюється в shadow root. Все інше (шрифтова іконка, `<img>`, кастомний елемент) іде в `slot="icon"` (з 1.28.0):

```html
<glk-tab-item label="Home" active>
  <span slot="icon" class="material-icons" aria-hidden="true">home</span>
</glk-tab-item>
```

Шрифтову іконку позначте `aria-hidden="true"`, інакше її текст потрапить в назву табу.

**Події і скасування.** Спочатку `glk-tab-select` на табі, потім `glk-tab-change` `{ tab }` на барі. `glk-tab-select` можна скасувати (з 1.28.0), і він іде до зміни `active`:

```js
menuItem.addEventListener('glk-tab-select', (event) => {
  event.preventDefault();   // stays on the current tab
  openDrawer();
});
```

Після скасування `active` не змінюється, `glk-tab-change` не приходить, крапля не рухається. Якщо перетягування закінчилось на такому табі, крапля повертається назад.

**Токени** (з 1.28.0 і 1.33.0). Успадковуються в елементи:

- `--gl-tab-bar-color`, `--gl-tab-bar-hover-color`, `--gl-tab-bar-label-size`, `--gl-tab-bar-z-index`;
- `--gl-tab-bar-icon-size` (24px за замовчуванням);
- `--gl-tab-bar-item-radius` (унизу капсула, у рейлі з підписами 16px);
- `--gl-tab-bar-active-weight` (за замовчуванням medium).

Приклад з джерела:

```css
glk-tab-bar[placement="top"] {
  --gl-tab-bar-icon-size: 18px;
  --gl-tab-bar-item-radius: 12px;
  --gl-tab-bar-active-weight: 600;
}
```

Після 1.33.0 елементи анімують лише кольори, натискання і тінь. Зміна розкладки відбувається миттєво, без 250 ms ковзання.

**Поверхня активного табу (1.27.0):** `--gl-tab-bar-active-bg`, `--gl-tab-bar-active-shadow`, `--gl-tab-bar-spotlight-opacity: 0` (вимикає спотлайт), `--gl-tab-bar-active-glow: none` (вимикає світіння іконки).

**Floating і dock** (iOS 26-подібний варіант). Фон — `.glass-bg--has-tab-bar-floating`:

```html
<div class="glass-bg glass-bg--has-tab-bar-floating">
  <!-- page content -->
  <glk-tab-dock>
    <glk-tab-bar floating>
      <glk-tab-item label="Home" active>
        <svg viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
      </glk-tab-item>
      <glk-tab-item label="Docs" badge="3">
        <svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/></svg>
      </glk-tab-item>
      <glk-tab-item label="Upload">
        <svg viewBox="0 0 24 24"><path d="M12 16V4"/><polyline points="8 8 12 4 16 8"/></svg>
      </glk-tab-item>
    </glk-tab-bar>
    <glk-tab-accessory variant="accent" label="Compose">
      <svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
    </glk-tab-accessory>
  </glk-tab-dock>
</div>
```

`<glk-tab-accessory>` — капсула 56×56 px. Варіанти: `accent`, `success`, `error`. Подія: `glk-click` (не спрацьовує, якщо disabled).

**Droplet.** Розмітка — див. A.9. Поведінка з SKILL.md:

- крапля над баром, тап шле її на новий таб, передній край іде першим;
- палець можна тягнути вздовж бару;
- на краплі спотлайт, точка і світіння вимкнені;
- `prefers-reduced-motion` змушує краплю стрибати;
- solid і tint surface роблять краплю непрозорою.

**Таймінг краплі** (з 1.32.0). Значення з SKILL.md, приклад для швидкого руху до 240 ms ease-out:

```css
:root {
  --gl-droplet-duration: 240ms;       --gl-droplet-easing: ease-out;
  --gl-droplet-trail-duration: 240ms; --gl-droplet-trail-delay: 0ms; --gl-droplet-trail-easing: ease-out;
  --gl-droplet-lift: 1;               --gl-droplet-lift-duration: 0ms; --gl-droplet-settle-duration: 0ms;
  --gl-droplet-lens-duration: 240ms;  --gl-droplet-lens-easing: ease-out;
}
```

SKILL.md пояснює: `--gl-droplet-lift-duration: 0ms` обов'язковий. Без нього глибша тінь підйому згасає до ~600 ms.

**Сайдбар і рейл** (з 1.32.0). Один набір табів, різні розкладки.

```html
<!-- Sidebar, placed by the page's grid -->
<div style="display: grid; grid-template-columns: 240px 1fr; height: 100dvh">
  <glk-tab-bar orientation="vertical" droplet label="Main">
    <glk-tab-item label="Dashboard" href="/dashboard" active>…</glk-tab-item>
    <glk-tab-item label="Customers" href="/customers" badge="3" badge-label="3 new">…</glk-tab-item>
  </glk-tab-bar>
  <main>…</main>
</div>

<!-- Fixed to the end edge of the viewport; rail: icons alone, the labels as tooltips -->
<glk-tab-bar orientation="vertical" dock="end" rail droplet label="Main">…</glk-tab-bar>

<!-- A top bar in a sticky header -->
<header style="position: sticky; top: 0; z-index: 10">
  <glk-tab-bar placement="top" droplet label="Main">…</glk-tab-bar>
</header>
```

Перемикання за медіа-запитом:

```js
// One bar, three layouts: bottom on phones, rail between 1100 and 1400px, sidebar above.
// The page's own grid follows the same queries.
const bar = document.querySelector('glk-tab-bar');
const wide = matchMedia('(min-width: 1100px)'), roomy = matchMedia('(min-width: 1400px)');
const layout = () => {
  bar.orientation = wide.matches ? 'vertical' : 'horizontal';
  bar.rail = wide.matches && !roomy.matches;
};
wide.addEventListener('change', layout);
roomy.addEventListener('change', layout);
layout();
```

Рейл з підписами і маркою (з 1.33.0):

```html
<!-- A full-height rail of its own glass at the start edge, 16px from the edges -->
<glk-tab-bar floating orientation="vertical" rail="labels" dock="start" droplet label="Main"
             style="--gl-tab-bar-rail-width: 96px; --gl-tab-bar-label-size: 12px">
  <img slot="leading" src="/mark.svg" alt="" width="40" height="40">
  <glk-tab-accessory slot="leading" variant="accent" label="Assistant" show-label><svg>…</svg></glk-tab-accessory>
  <glk-tab-item label="App" active><svg>…</svg></glk-tab-item>
  <glk-tab-item label="Report"><svg>…</svg></glk-tab-item>
  <glk-tab-item label="Catalog"><svg>…</svg></glk-tab-item>
  <glk-button slot="trailing" variant="tertiary" size="sm auto" aria-label="Account">MK</glk-button>
</glk-tab-bar>
<main style="margin-inline-start: 128px">…</main>   <!-- 96 + 2 × 16 -->
```

#### B.3 Правила і типові помилки (розділ 6)

**Завжди:**

1. `data-theme` і `data-density` — на `<html>`.
2. Елементи форм — всередині `<form>`.
3. `<glk-list-item>` — прямий нащадок `<glk-list>`.
4. Popover-тригер — через `slot="trigger"`, не через ID.
5. Поповерами керують через API: `popover.open = true` або `popover.toggle()`, а не `classList.add('is-open')`.
6. У попові — `<glk-list bare>`, інакше буде подвійна поверхня скла.
7. Бібліотеку імпортуйте один раз.
8. SVG-іконки: `stroke: currentColor, stroke-width: 2`.
9. `title` на `<glk-sheet>`, `<glk-modal>`, `<glk-list-item>`, `<glk-accordion-item>`, `<glk-empty>` — це заголовок, а не підказка. Читайте і пишіть `el.title`. Після апгрейду `el.getAttribute('title')` дає `null`.
10. Один `<glk-tab-bar>` на одну навігацію, будь-яка розкладка.
11. Видаляти модалку або шит зі стану — після `glk-closed` або `await el.close()`, а не на `glk-close`.
12. `<glk-table>` потребує `glasskit.css` на сторінці.
13. Елементи меню, дерева і крихт — прямі діти своїх контейнерів.

**Типові помилки** (ліва колонка — код з таблиці):

| Помилка | Виправлення з джерела |
|---|---|
| `onclick="popover.togglePopover()"` | Колізія з нативним `HTMLElement.togglePopover()`. Використовуйте `.toggle()` на `<glk-popover>` або атрибут `open`. |
| `document.querySelector('.glass-modal').classList.add('is-active')` | Встановіть `<glk-modal>.open = true`. |
| `data-theme` безпосередньо на `<glk-*>` | Ставте на `<html>`. |
| `mypopover.open()` | `open` — відбиваюча властивість. Для методів: `.show()` / `.close()` / `.toggle()`. |
| `<glk-tab-bar>` без `.glass-bg--has-tab-bar` | Бар закриває нижній контент. Додайте модифікатор до зовнішнього `.glass-bg`. |
| `<glk-tab-bar floating>` без `<glk-tab-dock>` | Завжди обгортайте в `<glk-tab-dock>`. |
| `<glk-tab-dock>` з `--has-tab-bar` | Для floating потрібен `.glass-bg--has-tab-bar-floating`. |
| `<glk-toast>` при відкритій `<glk-modal>` | Усе поза модалкою неактивне: тост не клікається і не озвучується. |
| `glk-toggle[aria-checked="true"]` або `[role="switch"]` на хості | З 1.20.0 використовуйте `glk-toggle[checked]`. |
| `glk-tab-item` з `badge="3"`, озвучується як «3 Customers» | `badge-label="3 new"` (з 1.32.0). |
| `title="…"` як підказка для іконкової `<glk-button>` | `<glk-tooltip as-label>`. `title` не показується при фокусі клавіатурою і на тач-пристроях. |
| `<glk-popover>` зі списком кнопок для команд | `<glk-menu>` з `<glk-menu-item>`. |
| Disabled `<glk-menu-item>`, прибраний з меню | Залишайте з `disabled`: стрілки його досягають, і його оголошують як недоступний. |
| `::part(group)::before` для таймінгу краплі | Токени `--gl-droplet-*`. |
| `--gl-radius-full` на таб-барі для скруглення табів | `--gl-tab-bar-item-radius`. `--gl-radius-full` впливає на всі капсули. |
| Другий набір табів для сайдбару | Один бар: `orientation="vertical"` (+ `dock`, `rail`) або `placement="top"`. |

---

### Ризики для WebKit / iPhone Safari (зведення з джерела)

- **Popover в top layer:** потрібен popover API. У джерелі вказано Safari 17. Відповідність версії iOS — нема в джерелі.
- **RTL і краплі:** модуль не має явної обробки `dir`. Перевірити на пристрої.
- **Клавіатура і крапля:** жодного перетягування з клавіатури. Вибір через `click` працює і анімується.
- **Reduced motion:** крапля стрибає. Перевіряється через `matchMedia` при кожному розміщенні.
- **Масштаб предків:** модуль компенсує `transform: scale`, тож поп-ап з `scale(0.96)` не зсуває краплю.
- **CSS-переходи краплі:** таймінг країв і easing-и лежать у `glasskit.css`, якого немає в джерелі. Значення потрібно брати з файлу стилів на вашій версії.

## §3 Токени, правила, композиції — витяг зі SKILL.md пакета

## GlassKit 1.41.0: витяг з SKILL.md

Усі CSS, HTML і JS наведено дослівно з джерела. Скорочені фрагменти позначено як «фрагмент». Там, де в джерелі немає значення для світлої або темної теми, пишу «нема в джерелі».

---

### (A) Section 2: Design Tokens

#### Кольори

| Token | Dark | Light | Usage |
|---|---|---|---|
| `--gl-color-primary` | `#f5a623` | `#e8852d` | Primary color, buttons, active elements |
| `--gl-color-primary-dark` | `#d4692a` | `#c96a1e` | Gradient end value |
| `--gl-color-primary-mid` | derived → `#e07a24` | derived → `#d97826` | Gradient midpoint, mixed from primary + primary-dark |
| `--gl-color-text` | `#ffffff` | `#1a2a36` | Default text color |
| `--gl-color-text-muted` | `rgba(255,255,255,0.65)` | `rgba(26,42,54,0.68)` | Secondary text — 4.5:1 on the page and on glass since 1.31.0 (before 60 % / 55 %) |
| `--gl-color-text-heading` | `#ffffff` | `#0f1f2a` | Headings |
| `--gl-color-success` | `#34c759` | `#28a745` | Success |
| `--gl-color-error` | `#ff3b30` | `#dc3545` | Error |
| `--gl-color-warning` | `#ffcc00` | `#e6a800` | Warning |
| `--gl-color-success-dark` | `#2da44e` | `#1e7e34` | Gradient end / stronger fill |
| `--gl-color-error-dark` | `#d63027` | `#b02a37` | Gradient end / stronger fill |

#### Role Colors (since 1.7.0)

| Token | Role | Default |
|---|---|---|
| `--gl-color-on-primary` | Ink/icons **on** the primary fill — the button, the checkbox tick, the radio's dot (since 1.32.0), the accent accessory, the chosen day, the current step | `#ffffff` |
| `--gl-color-primary-fill` | The flat accent fills that carry text: the chosen day of `.glass-date-strip` and `.glass-calendar`, the number of the current step (since 1.32.0) | unset → `var(--gl-color-primary)` |
| `--gl-color-on-success` | Ink/icons on a filled success surface | `#ffffff` |
| `--gl-color-on-error` | Ink/icons on a filled error surface | `#ffffff` |
| `--gl-color-primary-on-surface` | Badge text on the primary tint | lightened (dark) / darkened (light) primary |
| `--gl-color-success-on-surface` | Badge text on the success tint | lightened / darkened success |
| `--gl-color-error-on-surface` | Badge text on the error tint | lightened / darkened error |
| `--gl-color-warning-on-surface` | Badge text on the warning tint (since 1.18.0) | lightened (dark) / darkened (light) warning |
| `--gl-color-primary-text` | Text and line icons in the primary straight on the page or the glass: `.glass-prose` links, icon and label of the active tab, `.glass-modal__action--primary`, `.glass-list__item--accent`, `.glass-range-value`, the accordion trigger on hover and the chevron of an open item (since 1.26.0) | `var(--gl-color-primary)` in both themes |
| `--gl-color-primary-on-glass` | The primary as text on the glass of a card, a modal or a sheet (since 1.35.0): links in `.glass-prose`, the range value, accent rows, the primary modal action. Dark: `color-mix(in srgb, var(--gl-color-primary-text) 60%, #ffffff)` — GlassKit's orange went from 4.18:1 to 5.54:1 as a link on a card; light: the primary text. Use it for links and chips of your own on a card | — |
| `--gl-dialog-glow-top`, `--gl-dialog-well`, `--gl-dialog-raised`, `--gl-dialog-control`, `--gl-badge-selected-color` | Dark glass (since 1.35.0, dark mode only): where the glow of modal and sheet starts (the card's mid glow), the segmented track on dialog glass (black 10 %), its chosen option (`--gl-surface-3`), a tertiary button there (`--gl-surface-1`), a chosen badge's label (the text colour). Unset in light mode | — |
| `--gl-color-primary-surface` / `-border` | Badge fill / border | `color-mix(… primary 25% / 30%, transparent)` |
| `--gl-color-success-surface` / `-border` | Badge fill / border | `color-mix(… success 15% / 30%, transparent)` |
| `--gl-color-error-surface` / `-border` | Badge fill / border | `color-mix(… error 15% / 30%, transparent)` |
| `--gl-color-warning-surface` / `-border` | Badge fill / border (since 1.18.0) | `color-mix(… warning 15% / 30%, transparent)` |
| `--gl-state-scrim` | Layer behind a badge tint | `rgba(0,0,0,0.30)` dark, `rgba(255,255,255,0.30)` light |

#### Glass Surfaces

У джерелі є лише колонка Dark. Light-значень нема в джерелі.

| Token | Dark | Usage |
|---|---|---|
| `--gl-surface-1` | `rgba(255,255,255, 0.08)` | Subtlest surface (status) |
| `--gl-surface-2` | `rgba(255,255,255, 0.10)` | Default (inputs, cards) |
| `--gl-surface-3` | `rgba(255,255,255, 0.14)` | Nav pills, badges |
| `--gl-surface-4` | `rgba(255,255,255, 0.16)` | Hover states |
| `--gl-surface-5` | `rgba(255,255,255, 0.22)` | Strong hover |
| `--gl-surface-milk` | `rgba(255,255,255, 0.55)` | Milky |
| `--gl-surface-milk-strong` | `rgba(255,255,255, 0.75)` | Secondary button |
| `--gl-surface-overlay` | `rgba(0,0,0, 0.50)` | Modal overlay |

#### Borders

Одне значення на токен, без поділу на теми (light: нема в джерелі).

| Token | Value |
|---|---|
| `--gl-border-subtle` | `rgba(255,255,255, 0.18)` |
| `--gl-border-medium` | `rgba(255,255,255, 0.30)` |
| `--gl-border-strong` | `rgba(255,255,255, 0.40)` |
| `--gl-border-milk` | `rgba(255,255,255, 0.60)` |
| `--gl-border-warm` | derived from primary → `rgba(255,200,100, 0.35)` |
| `--gl-focus-ring` | The keyboard's mark, one solid colour (since 1.40.0): `color-mix(in srgb, var(--gl-color-primary) 15%, #ffffff)`, in the light theme `var(--gl-color-primary-on-surface)` |
| `--gl-border-focus` | `var(--gl-focus-ring)` (until 1.39.0 a tint of the primary) |

#### Blur

| Token | Value |
|---|---|
| `--gl-blur` | `24px` (default) |
| `--gl-blur-light` | `16px` |
| `--gl-blur-soft` | `12px` |
| `--gl-blur-heavy` | `40px` |

Усі чотири дорівнюють `0px` під `data-surface="solid"`.

#### Gloss (since 1.24.0)

| Token | Value | Usage |
|---|---|---|
| `--gl-gloss-card` | `linear-gradient(90deg, …)` | Highlight along the top edge of `.glass-card--glow` |
| `--gl-gloss-modal` | `linear-gradient(90deg, …)` | The same on `.glass-modal` |
| `--gl-gloss-progress` | `linear-gradient(to bottom, …)` | Sheen on the progress fill |
| `--gl-range-thumb-border` | `2px solid rgba(255,255,255,0.5)` | Rim of the range thumb |
| `--gl-gloss-droplet` | `radial-gradient(…), radial-gradient(…)` | Highlight and caustic glow in the drop of `--droplet` rows (since 1.27.0) |

Однакові в обох темах. Light-значень окремо нема в джерелі.

#### Radii

| Token | Value | Usage |
|---|---|---|
| `--gl-radius-xs` | `8px` | Small elements |
| `--gl-radius-sm` | `12px` | Badges, small containers |
| `--gl-radius-input` | `14px` | Inputs, textareas |
| `--gl-radius-btn` | `16px` | Buttons (since 1.31.0 through `--gl-btn-radius`), lists, status card, toasts, accordion, segmented control |
| `--gl-radius-card` | `24px` | Cards |
| `--gl-radius-full` | `9999px` | Fully rounded |
| `--gl-radius-pill` | `50%` | Circle shape |

#### Spacing

| Token | Value |
|---|---|
| `--gl-space-2xs` | `4px` |
| `--gl-space-xs` | `8px` |
| `--gl-space-sm` | `12px` |
| `--gl-space-md` | `16px` |
| `--gl-space-lg` | `20px` |
| `--gl-space-xl` | `24px` |
| `--gl-space-2xl` | `32px` |
| `--gl-space-3xl` | `40px` |
| `--gl-space-4xl` | `56px` |

#### Density (since 1.21.0)

Default — перша колонка, Compact — друга (`data-density="compact"` на `<html>`).

| Token | Default | Compact | Used by |
|---|---|---|---|
| `--gl-control-height` | `52px` | `40px` | `.glass-input`, `.glass-select` (and the search field) |
| `--gl-control-padding-x` | unset → `var(--gl-space-md)` | `var(--gl-space-sm)` | Inner left/right padding of input, select, textarea |
| `--gl-btn-height` | `56px` | `40px` | `.glass-btn` |
| `--gl-btn-height-sm` | `44px` | `32px` | `.glass-btn--sm` |
| `--gl-btn-height-lg` | `64px` | `48px` | `.glass-btn--lg` |
| `--gl-textarea-min-height` | `120px` | `88px` | `.glass-textarea` |
| `--gl-list-item-min-height` | `56px` | `48px` | `.glass-list__item` |
| `--gl-list-item-padding-y` | unset → `var(--gl-space-md)` | `10px` | `.glass-list__item`, top and bottom |
| `--gl-toggle-width` | `52px` | `44px` | `.glass-toggle__track` |
| `--gl-toggle-height` | `30px` | `26px` | `.glass-toggle__track` |
| `--gl-toggle-thumb-size` | `22px` | `18px` | `.glass-toggle__thumb` |
| `--gl-check-size` | `24px` | `20px` | `.glass-checkbox__box`, `.glass-radio__circle` |
| `--gl-modal-action-height` | `52px` | `44px` | `.glass-modal__action` |

#### Shadows

У джерелі немає значень для більшості токенів (окрім `--gl-shadow-focus`), тому значення нема в джерелі.

| Token | Usage |
|---|---|
| `--gl-shadow-card` | Cards |
| `--gl-shadow-btn` | Default buttons |
| `--gl-shadow-btn-primary` | Primary button (orange glow) |
| `--gl-shadow-glow` | Glow effect |
| `--gl-shadow-modal` | Modal dialog |
| `--gl-shadow-toast` | Toast notifications |
| `--gl-shadow-focus` | Focus ring: `0 0 0 2px var(--gl-focus-ring)` (until 1.39.0 3px and a tint of the primary) |

#### Typography

| Token | Value |
|---|---|
| `--gl-font-size-xs` | `13px` |
| `--gl-font-size-sm` | `14px` |
| `--gl-font-size-base` | `15px` |
| `--gl-font-size-btn` | `16px` |
| `--gl-font-size-lg` | `18px` |
| `--gl-font-size-title` | `24px` |
| `--gl-font-size-modal` | `20px` |
| `--gl-font-weight-normal` | `400` |
| `--gl-font-weight-medium` | `500` |
| `--gl-font-weight-semibold` | `600` |

*Прозові блоки розділу 2 (рецепти AA, `contrast-color()`, приклади перевизначень) тут не переписано — за завданням вичерпні лише таблиці.*

---

### (B) Section 7: Rules & Common Mistakes

#### ✅ Завжди дотримуйся

1. **`glass-bg` як зовнішній контейнер** — без фонової обгортки не буде фонового світла «аврора», і скляні ефекти коректно не рендеряться.
2. **`glass-bg--has-tab-bar`** — коли є tab bar, цей модифікатор ставиться на `glass-bg`, інакше tab bar перекриває нижній вміст.
3. **Кнопки на всю ширину** — `glass-btn` має `width: 100%`. Для рядкових кнопок завжди додавай `glass-btn--auto`.
4. **Загортай інпути в `glass-input-group`** — для правильних відступів мітки та підказки.
5. **Став state-класи правильно:**
   - `is-active` → на `.glass-modal-overlay` (не на `.glass-modal`)
   - `is-active` → на `.glass-tab-bar__item`
   - `is-open` → на `.glass-accordion__item`
   - `is-open` → на `.glass-popover` (не на тригер чи anchor)
   - `is-visible` → на `.glass-toast`
6. **SVG-іконки** — GlassKit використовує inline SVG на основі stroke, не fill. Типові атрибути: `viewBox="0 0 24 24"`, stroke через `currentColor`.
7. **`data-theme`** — завжди на `<html>`, ніколи на `<body>` чи глибше.
8. **Розділювачі списку автоматичні** — ніколи не став `<hr>` чи інший роздільник між `.glass-list__item`. Розділювач малюється через `::after` і враховує `:has(.glass-list__leading)` для відступу.
9. **Назва перемикача popover** — ніколи не називай JS-функцію перемикання `togglePopover`. Вона конфліктує з нативним `HTMLElement.togglePopover()`. Використовуй префікс, наприклад `gkTogglePopover`.
10. **`data-density`** — як і `data-theme`, на `<html>`: `compact` або взагалі без атрибута. Для щільнішого UI став атрибут або токен щільності, але ніколи `height` на компонентах.
11. **Droplet потребує свого модуля** — `--droplet` на tab bar або segmented-рядку нічого не робить, доки `glasskit-droplet.js` не під'єднано (`attachDroplets()`). Рекомендуй обидва разом. Атрибути `data-droplet*` і властивості `--gl-droplet-left/-right/-top/-bottom` залиш модулю. Токени таймінгу (`--gl-droplet-duration` та решта, з 1.32.0) — твої.
12. **Одна навігація для всіх розкладок** — сайдбар, icon rail і top bar — це tab bar з `--vertical`, `--rail` та `--top` (з 1.32.0). Зберігай один набір елементів і перемикай модифікатори. Відкритий вигляд познач `aria-current="page"`, а `<nav>` назви.
13. **Панелі top layer потребують скрипта** — `.glass-popover[popover]`, `.glass-tooltip` і `.glass-menu` малює GlassKit, а розміщує скрипт (`gkPlace()` у 3.25). Клавіатура меню й дерева теж на скрипті (з 1.32.0). GlassKit Elements покриває обидва.

#### ❌ Типові помилки

| Помилка | Виправлення |
|---|---|
| `is-active` на `.glass-modal` замість `.glass-modal-overlay` | Постав `is-active` на overlay |
| `glass-btn` без варіанта (`--primary` тощо) | Завжди вказуй варіант |
| Інпути без обгортки `glass-input-group` | Загорни в `glass-input-group` |
| `glass-tab-bar` без `glass-bg--has-tab-bar` | Додай модифікатор на фоновий контейнер |
| `data-theme` на `<body>` | Став на `<html>` |
| Ширина прогресу через клас, а не inline-стиль | Використовуй `style="width: X%"` на `.glass-progress__fill` |
| Toggle без вкладеності `__track > __thumb` | Дотримуйся правильної BEM-ієрархії |
| Вручну доданий `<hr>` або роздільник між `.glass-list__item` | Прибери — розділювачі автоматичні через `::after` |
| `glass-list` всередині `glass-popover` без `--bare` | Додай `.glass-list--bare`, щоб прибрати подвійну скляну поверхню |
| JS-функція з назвою `togglePopover()` | Перейменуй на `gkTogglePopover()` або схоже, щоб не було конфлікту з нативним API |
| `.is-open` на кнопці-тригері замість `.glass-popover` | Клас стану належить елементу popover |
| Анімація вибору tab bar або segmented-рядка власним скриптом | `--droplet` плюс `glasskit-droplet.js` (з 1.27.0) |
| `data-droplet*` або `--gl-droplet-left` / `-right` / `-top` / `-bottom` вручну | Нехай `attachDroplet()` їх виставляє; твої лише токени таймінгу (з 1.32.0) |
| Копіювання станів tab bar на іконку-шрифт або перевизначення `stroke` на `.glass-tab-bar__icon svg` | Постав іконку в `.glass-tab-bar__icon` як є; задавай `--gl-tab-bar-color` / `--gl-tab-bar-hover-color` (з 1.28.0) |
| Перевизначення `font-size` підпису вкладки або `z-index` бару | `--gl-tab-bar-label-size`, `--gl-tab-bar-z-index` (з 1.28.0) |
| Перестилізація вибраного сегмента під темний бренд | `--gl-segmented-active-bg`, `-color`, `-shadow` (з 1.28.0) |
| Лічильник у тексті сегмента: «Tickets (1)» | `.glass-segmented__badge` після підпису; число в `aria-label` опції (з 1.29.0) |
| Тон на опції лише для фарбування лічильника, або `--gl-segmented-badge-bg` / `-color` задано кольором стану | `.glass-segmented__badge--error` (або `--primary`, `--success`, `--warning`) — без крапки (з 1.31.0) |
| `--gl-radius-btn` задано для кнопок-пігулок | `--gl-btn-radius: 9999px` — списки, тости й segmented зберігають своє (з 1.31.0) |
| Власний контур на `:focus-visible` для кнопок і пігулок, або тінт у `--gl-shadow-focus` | Нічого не робити для кнопок, пігулок, перемикача теми й дій модалки; `--gl-focus-ring` задає колір кожної позначки, суцільний (з 1.40.0) |
| `--gl-color-primary` затемнено, доки білий текст на primary-кнопці не пройде | `--gl-btn-primary-bg` і `--gl-color-primary-fill` затемнюють лише заливки, або змінюй ink через `--gl-color-on-primary` (з 1.32.0, розділ 2) |
| Правило на `.glass-radio__dot`, щоб зробити його темним із темним ink | Нічого: крапка йде за `--gl-color-on-primary` (з 1.32.0) |
| Сайдбар із `.glass-tab-bar` з власними `flex-direction`, `position` і `height` | `.glass-tab-bar--vertical`, з `--start` / `--end` для фіксованого боку, `--rail` для самих іконок; `--top` для top bar (з 1.32.0) |
| `.glass-bg--has-tab-bar` поруч із бічним баром | Він паддить лише нижній край; відступ контенту з боку бару роби сам |
| Перевизначення `transition` або `transform` для drop | Токени `--gl-droplet-*` (з 1.32.0) |
| Нативний атрибут `title` як підказка для іконкової кнопки | `.glass-tooltip` (3.36) — `title` не показується ні при фокусі клавіатурою, ні на touch |
| Команди як звичайні кнопки в popover без ролей меню | `.glass-menu` з `role="menu"` / `menuitem` (3.37), клавіатура з `<glk-menu>` |
| `›` або `/`, набрані між breadcrumbs | Не додавай: `.glass-breadcrumbs__item` малює шеврон, його не бачать скрінрідери, і він дзеркалиться в RTL |
| `--gl-radius-full`, змінений на tab bar, щоб закруглити його drop і елементи | `--gl-tab-bar-item-radius` (з 1.33.0); глобальний токен формує кожну пігулку й бейдж |
| Обгортка навколо плаваючого вертикального бару, що малює скло rail, а mark і accessory — сусідні елементи | `--floating --vertical --start` з `--rail --labels`, mark і `__accessory-item` всередині `__leading` (з 1.33.0) |
| `--gl-space-2xs` / `--gl-font-size-xs` піднято, щоб чіп був вищим | `.glass-badge--md` (з 1.33.0) |
| Посилання «Forgot password?» абсолютно позиціоновано поверх рядка мітки | `.glass-input-group--label-end` з `__label-end` після поля (з 1.33.0) |
| `position: sticky` на `th` всередині `.glass-table-wrap` | `.glass-table-wrap--sticky` + `.glass-table--sticky` (з 1.32.0); обгортка, що скролиться вбік, є scroll-контейнером в обох напрямках |
| `.glass-popover` без `[popover]` всередині картки або скрольованого блоку, що обрізає | Відкривай у top layer з атрибутом `popover` (з 1.32.0) |
| Перевизначення `height` для `.glass-btn`, `.glass-input` тощо для щільнішого UI | `data-density="compact"` на `<html>` або токен щільності; вирівнювання перемикача й підпису слідує за токенами, а не ручним `height` |

---

### (C) Section 5: State classes overview

| Клас стану | На яких елементах | Опис |
|---|---|---|
| `.is-active` | `.glass-modal-overlay`, `.glass-tab-bar__item` | Елемент активний або видимий |
| `.is-open` | `.glass-accordion__item`, `.glass-popover` | Пункт акордеона розгорнуто / popover видимий |
| `.is-visible` | `.glass-toast` | Тост видимий |
| `.is-under-droplet` | `.glass-tab-bar__item`, `.glass-segmented__item` | Елемент під drop рядка `--droplet`; встановлює лише `glasskit-droplet.js` (з 1.27.0) |
| `:checked` | Toggle, Checkbox, Radio (на input) | Нативний стан «відмічено» |
| `:focus` | Input, Textarea, Select | Фокусне кільце |
| `:focus-visible` | Кожен інший контрол | Позначка фокусу: кільце, а для Button, Pill, Theme Toggle і Modal action — контур (з 1.40.0) |
| `:disabled` | Input, Select, Textarea, Range (0.4); Button, Pill, Tab Bar Accessory, Modal action, list row, calendar arrow, Toggle, Checkbox, Radio (0.45) | Приглушено, курсор «заборонено», без hover (більшість з 1.21.2) |
| `[aria-disabled="true"]` | `a.glass-btn` та інші кнопки; дні date strip і calendar; `.glass-menu__item` | Як `:disabled`, для елементів, які не можна вимкнути. Посилання все одно переходить; пункт меню лишається досяжним стрілками |
| `:popover-open` | `.glass-popover[popover]`, `.glass-tooltip[popover]`, `.glass-menu[popover]`, `.glass-sort__ghost` | Показано в top layer через `showPopover()` або кнопку `popovertarget` (з 1.32.0) |
| `.is-checked` / `[aria-checked="true"]` | `.glass-menu__item` | Показує галочку (з 1.32.0) |
| `.is-focused` / `.is-focus-visible` | `.glass-menu__item`; `.is-focus-visible` також `.glass-tree__row` | Тінт або кільце фокусу для скрипта, який сам позначає фокус (з 1.32.0) |
| `.is-disabled` | `.glass-menu__item`, `.glass-tree__row` | Приглушено й неактивно, але все ще оголошується (з 1.32.0) |
| `.is-expanded`, `.is-selected`, `.is-leaf`, `.is-loading`, `.is-error` | `.glass-tree__row` | Розгорнуто, вибрано, без дочірніх, дочірні завантажуються, дочірні не завантажилися (з 1.32.0) |
| `.is-flash` | `.glass-list__item`, `.glass-tree__row` | Спалах 1,2 с для елемента, який змінився деінде, у `--gl-flash-color` (з 1.32.0) |
| `.is-drop-target` / `.is-drop-refused` | `.glass-breadcrumbs__crumb`, `.glass-breadcrumbs__current` | Перетягнутий елемент над крихтою: прийнято до рівня / відхилено (з 1.32.0) |
| `.is-sort-source`, `-before`, `-after`, `-inside`, `-refused` | `.glass-list__item`, `.glass-tree__row` | Стани перетягування для зміни порядку (з 1.32.0, 3.40) |
| `[aria-sort]` | `th` у `.glass-table` | Відсортована колонка і напрямок: стрілка з `__sort-icon` (з 1.32.0) |

---

### (D) Section 9: Web Components / Shadow DOM

Для Shadow DOM GlassKit постачає Constructable Stylesheet:

```js
import { glassSheet } from '@jungherz-de/glasskit/glasskit-styles.js';

class MyCard extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: 'open' });
    shadow.adoptedStyleSheets = [glassSheet];
    shadow.innerHTML = `
      <div class="glass-card glass-card--glow">
        <p class="glass-card__text"><slot></slot></p>
      </div>
    `;
  }
}
customElements.define('my-card', MyCard);
```

| Експорт | Тип | Опис |
|---|---|---|
| `glassSheet` | `CSSStyleSheet` | Повний лист: правила **і** оголошення токенів |
| `css` | `string` | Те саме рядком |
| `componentsSheet` | `CSSStyleSheet` | Лише правила компонентів, без оголошень токенів (з 1.9.0) |
| `componentsCss` | `string` | Те саме рядком |
| `tokensSheet` | `CSSStyleSheet` | Лише блоки з `--gl-*`: два блоки `[data-theme]` (з 1.9.0) і пресет `[data-density="compact"]` (з 1.21.0) |
| `tokensCss` | `string` | Те саме рядком |

Властивості `--gl-*` проходять крізь межу shadow через успадкування, тож приклад вище бере все, що визначено в документі, і перемикання теми працює глобально.

**Пастка: не став `data-theme` всередину shadow root, коли підключено `glassSheet`.** Повний лист містить `:root, [data-theme="dark"] { … }`. Якщо всередині shadow root є елемент із `data-theme`, селектор його матчить і локально перевизначає кожен токен. Правило, що матчить, завжди перебиває успадкування. Тоді `:root { --gl-color-primary: … }` проєкту мовчки перестає доходити до компонента. Темний блок також оголошує стандартні розміри контролів, тож `<html data-density="compact">` теж перестає доходити, якщо елемент не має `data-density`, дзеркаленого з `<html>`. Тоді пресет compact (він теж у повному листі) матчить.

Якщо всередині shadow root потрібен елемент із темою, підключи `componentsSheet` і переконайся, що токени є в документі:

```js
shadow.adoptedStyleSheets = [componentsSheet];

// once per page, if the document does not already link glasskit.css:
const defaults = new CSSStyleSheet();
defaults.replaceSync(`@layer glasskit-defaults { ${tokensCss} }`);
document.adoptedStyleSheets = [...document.adoptedStyleSheets, defaults];
```

Cascade layer дає звичайному брендовому листу перевагу над дефолтами. Так працює GlassKit Elements з 1.9.0.

**Пастка: нащадковий селектор не дістає іконку, передану через slot.** `.glass-btn svg` матчить лише справжніх нащадків. Іконка, передана ззовні, лишається в light DOM, і правило до неї не застосовується. З 1.10.0 кожне правило для іконки над slot має двійник `::slotted()`, тому передача іконки працює:

```html
<glk-button><svg viewBox="0 0 24 24">…</svg>Save</glk-button>
```

`::slotted()` матчить лише призначений вузол, а не його вміст. Іконка, загорнута в контейнер (`<span slot="leading"><svg …></span>`), лишиться без стилів, і її розмір мусить задати проєкт. Передавай `<svg>` напряму.

---

### (E) Section 6: Composition patterns

#### Dashboard with Cards

```html
<div class="glass-bg glass-bg--has-tab-bar">
  <nav class="glass-nav">
    <h1 class="glass-title">Dashboard</h1>
    <button class="glass-pill">
      <svg viewBox="0 0 24 24"><!-- Settings Icon --></svg>
    </button>
  </nav>

  <div class="gl-stack gl-stack--md">
    <div class="glass-card glass-card--glow">
      <div class="glass-card__icon">
        <svg viewBox="0 0 64 64"><!-- Icon --></svg>
      </div>
      <p class="glass-card__text">Capture and upload documents.</p>
    </div>

    <div class="glass-card glass-card--glow">
      <div class="glass-card__icon">
        <svg viewBox="0 0 64 64"><!-- Icon --></svg>
      </div>
      <p class="glass-card__text">Manage and archive contracts.</p>
    </div>
  </div>

  <nav class="glass-tab-bar">
    <button class="glass-tab-bar__item is-active">
      <span class="glass-tab-bar__icon"><svg viewBox="0 0 24 24"><!-- Home --></svg></span>
      <span class="glass-tab-bar__label">Home</span>
    </button>
    <button class="glass-tab-bar__item">
      <span class="glass-tab-bar__icon"><svg viewBox="0 0 24 24"><!-- Docs --></svg></span>
      <span class="glass-tab-bar__label">Contracts</span>
    </button>
    <button class="glass-tab-bar__item">
      <span class="glass-tab-bar__icon"><svg viewBox="0 0 24 24"><!-- Profile --></svg></span>
      <span class="glass-tab-bar__label">Profile</span>
    </button>
  </nav>
</div>
```

#### Back office (Sidebar + Breadcrumbs + Table + Menu)

```html
<div class="glass-bg" style="display: grid; grid-template-columns: auto 1fr; height: 100dvh">
  <nav class="glass-tab-bar glass-tab-bar--vertical glass-tab-bar--droplet" aria-label="Main">
    <a class="glass-tab-bar__item is-active" href="/invoices" aria-current="page">
      <span class="glass-tab-bar__icon"><svg viewBox="0 0 24 24"><!-- Icon --></svg></span>
      <span class="glass-tab-bar__label">Invoices</span>
    </a>
    <a class="glass-tab-bar__item" href="/customers" aria-label="Customers, 3 new">
      <span class="glass-tab-bar__icon"><svg viewBox="0 0 24 24"><!-- Icon --></svg><span class="glass-tab-bar__badge">3</span></span>
      <span class="glass-tab-bar__label">Customers</span>
    </a>
  </nav>

  <main class="gl-stack gl-stack--md gl-px" style="overflow-y: auto; padding-block: 24px">
    <nav class="glass-breadcrumbs" aria-label="Breadcrumb">
      <ol class="glass-breadcrumbs__list">
        <li class="glass-breadcrumbs__item"><a class="glass-breadcrumbs__crumb" href="/">Back office</a></li>
        <li class="glass-breadcrumbs__item"><span class="glass-breadcrumbs__current" aria-current="page">Invoices</span></li>
      </ol>
    </nav>
    <h1 class="glass-title">Invoices</h1>
    <div class="glass-table-frame">
      <div class="glass-table-wrap glass-table-wrap--sticky" style="--gl-table-max-height: calc(100dvh - 180px)">
        <table class="glass-table glass-table--sticky">
          <thead>
            <tr>
              <th aria-sort="descending"><button class="glass-table__sort" type="button">Date<svg class="glass-table__sort-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg></button></th>
              <th>Customer</th>
              <th class="glass-table__num">Amount</th>
              <th class="glass-table__actions" aria-label="Actions"></th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td data-label="Date">2026-10-27</td>
              <td data-label="Customer">Jungherz GmbH</td>
              <td class="glass-table__num" data-label="Amount">1,240.00</td>
              <td class="glass-table__actions">
                <button class="glass-btn glass-btn--tertiary glass-btn--sm glass-btn--auto" id="act-1042"
                        aria-label="Actions for invoice 1042" aria-haspopup="menu" aria-expanded="false" popovertarget="menu-1042">…</button>
                <div class="glass-menu" id="menu-1042" role="menu" aria-labelledby="act-1042" popover>
                  <button class="glass-menu__item" role="menuitem" tabindex="-1"><span class="glass-menu__label">Send again</span></button>
                  <hr class="glass-menu__separator">
                  <button class="glass-menu__item glass-menu__item--danger" role="menuitem" tabindex="-1"><span class="glass-menu__label">Cancel invoice</span></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>
</div>
```

Ключові моменти з джерела: між двома ширинами `<nav>` отримує `--rail`. На телефоні сторінка прибирає сітку, а той самий `<nav>` знімає `--vertical` і переходить на нижній край (з `.glass-bg--has-tab-bar`), або отримує `--end`, якщо телефон тримають відкритим. Заголовок липне до обгортки, а її висота задається `--gl-table-max-height`. Меню рядка відкривається в top layer, тож переповнення обгортки його не обрізає. `gkPlace()` (3.25) ставить його біля кнопки.

---

### (F) Component catalog: документовані правила

#### Background (3.1)

```html
<div class="glass-bg">
  <!-- All content goes here -->
</div>
```

З tab bar:

```html
<div class="glass-bg glass-bg--has-tab-bar">
  <!-- Content -->
  <nav class="glass-tab-bar">...</nav>
</div>
```

- Клас `.glass-bg` — обов'язкова зовнішня обгортка всього вмісту.
- `.glass-bg--has-tab-bar` додає нижній відступ 82px. Для плаваючого варіанта використовується `.glass-bg--has-tab-bar-floating`.
- Пастка: модифікатор паддить лише нижній край. Поруч із бічним баром відступ контенту з боку бару задається вручну.

#### Pill Button (3.3)

```html
<button class="glass-pill">
  <svg viewBox="0 0 24 24"><!-- Icon SVG --></svg>
</button>
```

- `.glass-pill` — круглa скляна іконкова кнопка 46×46px, використовується в `.glass-nav` або як окрема кнопка дії.
- `.glass-theme-toggle` — спеціалізована пігулка з автоматичним перемиканням місяць/сонце. З 1.41.0 має третю іконку `.icon-auto` для режиму auto.
- Стан `:disabled` приглушує до 0.45.
- Фокус: з 1.40.0 має контур 2px. Власний `:focus-visible` контур не додавай.
- У прикладах GlassKit іконкові кнопки мають `aria-label`, наприклад `aria-label="More"`.

Режим auto (з 1.41.0): з `data-theme-mode="auto"` на `<html>` перемикач показує `.icon-auto`. Стан зберігається в `localStorage`, а скрипт у `<head>` виставляє його до першого малювання. Скрипт, що перемикає лише `data-theme`, прибирає `data-theme-mode`.

#### Tab Bar (3.4)

Базова структура:

```html
<nav class="glass-tab-bar">
  <button class="glass-tab-bar__item is-active">
    <span class="glass-tab-bar__icon">
      <svg viewBox="0 0 24 24"><!-- Icon --></svg>
    </span>
    <span class="glass-tab-bar__label">Home</span>
  </button>
  <button class="glass-tab-bar__item">
    <span class="glass-tab-bar__icon">
      <svg viewBox="0 0 24 24"><!-- Icon --></svg>
      <span class="glass-tab-bar__badge">3</span>
    </span>
    <span class="glass-tab-bar__label">Contracts</span>
  </button>
  <button class="glass-tab-bar__item">
    <span class="glass-tab-bar__icon">
      <svg viewBox="0 0 24 24"><!-- Icon --></svg>
    </span>
    <span class="glass-tab-bar__label">Profile</span>
  </button>
</nav>
```

Плаваючий варіант з accessory:

```html
<div class="glass-tab-bar-dock">
  <nav class="glass-tab-bar glass-tab-bar--floating">
    <button class="glass-tab-bar__item is-active">
      <span class="glass-tab-bar__icon"><svg><!-- Icon --></svg></span>
      <span class="glass-tab-bar__label">Home</span>
    </button>
    <!-- more items -->
  </nav>
  <button class="glass-tab-bar__accessory glass-tab-bar__accessory--accent" aria-label="Compose">
    <svg><!-- Icon --></svg>
  </button>
</div>
```

- Потрібен `glass-bg--has-tab-bar` на фоновому контейнері (для плаваючого варіанта — `glass-bg--has-tab-bar-floating`).
- Активний пункт: `.glass-tab-bar__item.is-active`, і `aria-current="page"` поруч.
- `.glass-tab-bar__badge--dot` — крапка без числа (з 1.38.0). Причину пиши в `aria-label` елемента.
- Іконка-шрифт або `<img>`-маска кладеться прямо в `.glass-tab-bar__icon` (з 1.28.0), і вона підпорядковується станам. Додай `aria-hidden="true"`.
- Гострі місця: не став `transition: all` на елементи (лише `color`, `background-color`, `box-shadow`, `opacity`, `transform`). Не перевизначай `stroke` на `.glass-tab-bar__icon svg`. Використовуй токени: `--gl-tab-bar-color`, `--gl-tab-bar-hover-color`, `--gl-tab-bar-label-size` (10px), `--gl-tab-bar-icon-size` (24px), `--gl-tab-bar-z-index` (900).

**Droplet (з 1.27.0, рекомендовано):** `.glass-tab-bar--droplet` і `glasskit-droplet.js`:

```html
<nav class="glass-tab-bar glass-tab-bar--floating glass-tab-bar--droplet">
  <button class="glass-tab-bar__item is-active">…</button>
  <!-- more items -->
</nav>

<script type="module">
  import { attachDroplets } from '@jungherz-de/glasskit/glasskit-droplet.js';
  attachDroplets();   // every --droplet row in the page (or a shadow root: attachDroplets(root))
</script>
```

- Стилі малюють drop, модуль його рухає. Без скрипта бар лишається зі spotlight.
- Не задавай вручну `data-droplet*` і `--gl-droplet-left/-right/-top/-bottom`. Не перевизначай `transition` або `transform` drop.
- Таймінг задається токенами: `--gl-droplet-duration` (0.3s), `--gl-droplet-easing`, `--gl-droplet-trail-duration` (0.5s), `--gl-droplet-trail-delay` (40ms), `--gl-droplet-lift` (0.86), `--gl-droplet-settle-duration` (0.55s) та інші.
- Колонка (`--vertical` або `flex-direction: column`) рухає drop по осі y.
- Альтернатива: `<glk-tab-bar floating droplet>` у GlassKit Elements.

**Сайдбар, rail, top bar:** модифікатори `--vertical`, `--start` / `--end` (фіксація до краю), `--rail` (лише іконки, 72px), `--labels` (з `--rail`, підписи під іконками), `--top` (горизонтальний бар у потоці сторінки). Для плаваючого прямого бару: `.glass-tab-bar-dock--vertical`, `-dock--start` / `--end`.

#### Buttons (3.7)

```html
<!-- Primary: Color gradient, main action -->
<button class="glass-btn glass-btn--primary">
  <svg viewBox="0 0 24 24"><!-- Optional: Icon --></svg>
  Primary Action
</button>

<!-- Secondary: Milky white -->
<button class="glass-btn glass-btn--secondary">Secondary Action</button>

<!-- Tertiary: Subtle glass -->
<button class="glass-btn glass-btn--tertiary">Tertiary Action</button>

<!-- Sizes -->
<button class="glass-btn glass-btn--primary glass-btn--sm">Small (44px)</button>
<button class="glass-btn glass-btn--primary glass-btn--lg">Large (64px)</button>

<!-- Auto-width (instead of full-width) -->
<button class="glass-btn glass-btn--primary glass-btn--auto">Auto</button>
```

- Варіанти: `--primary` (градієнт кольору), `--secondary` (молочна, темний текст), `--tertiary` (прозора). Розміри: `--sm` (44px), `--lg` (64px), базово 56px.
- **Пастка:** `width: 100%` за замовчуванням. Для рядкових кнопок став `--auto`.
- Вимкнення: атрибут `disabled`, або `aria-disabled="true"` на `a.glass-btn` (посилання не вимикається, тож переходить далі, якщо сторінка цього не зупинить).
- Іконки: inline-`fill`/`stroke` атрибути не потрібні. Для суцільних брендових знаків додай `glass-icon--fill` на `<svg>`.
- `.glass-btn` працює і на `<a>`.
- Токени: `--gl-btn-radius` (форма), `--gl-btn-padding-x` (24px), `--gl-btn-primary-bg` (фон primary). Для AA на білому тексті затемнюй `--gl-btn-primary-bg`, а не `--gl-color-primary`.

#### Toggle Switch (3.18)

```html
<label class="glass-toggle">
  <input class="glass-toggle__input" type="checkbox" checked>
  <span class="glass-toggle__track">
    <span class="glass-toggle__thumb"></span>
  </span>
  <span class="glass-toggle__label">Notifications</span>
</label>
```

- Ієрархія обов'язкова: `.glass-toggle` > `__input` + `__track` > `__thumb`, плюс `__label`.
- Стан: `:checked` на input.
- Input невидимий, але лежить **поверх** track і сам приймає клік. Для ролі `switch` став `role="switch"` на input.
- Порожній `__label` не займає місця.
- Розташування перемикача в кінці рядка:

```html
<label class="glass-toggle glass-toggle--label-start glass-toggle--full">
  <input class="glass-toggle__input" type="checkbox">
  <span class="glass-toggle__track"><span class="glass-toggle__thumb"></span></span>
  <span class="glass-toggle__label">Notifications</span>
</label>
```

- У рядку списку перемикач став у `__trailing`.
- Токени треку: `--gl-toggle-track-bg` (вимкнено), `--gl-toggle-track-bg-checked` (увімкнено).

#### Select (3.16)

```html
<select class="glass-select">
  <option>Please select…</option>
  <option>Insurance</option>
  <option>Rental Agreement</option>
</select>
```

- Клас `.glass-select`. Стрілка — токен `--gl-select-chevron` (SVG `url(…)`), її можна перевизначити своїм `url(…)`.
- Плейсхолдер: перша опція з порожнім значенням, `disabled` і `hidden`, `selected`. Вона не обирається, `required` не дає відправити форму, поки вона показана.

```html
<select class="glass-select" required>
  <option value="" disabled hidden selected>Choose a kind…</option>
  <option value="facebook">Facebook</option>
</select>
```

- **Суперечність у джерелі:** текст 3.16 прямо забороняє використовувати першу реальну опцію на кшталт «Please select…» для «нічого не вибрано». Водночас приклади у каталозі та в «Form Page» саме так і роблять. Правило з тексту 3.16 тут вважаю правильним.
- Стан `:disabled` (0.4) і `:focus` (фокусне кільце).

#### Search (3.17)

```html
<div class="glass-search">
  <svg class="glass-search__icon" viewBox="0 0 24 24">
    <circle cx="11" cy="11" r="8"/>
    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
  </svg>
  <input class="glass-input" type="search" placeholder="Search contracts…">
</div>
```

- Обгортка `.glass-search` (position: relative), іконка `.glass-search__icon`, усередині — поле з класом `.glass-input`.
- Поле пошуку використовує звичайний `.glass-input`, а не окремий клас.

#### Input: поле, фокус і валідація (3.14)

Базова структура:

```html
<div class="glass-input-group">
  <label class="glass-label">Contract Name</label>
  <input class="glass-input" type="text" placeholder="e.g. Rental Agreement">
  <span class="glass-hint">Optional help text</span>
</div>
```

Стан помилки (валідація):

```html
<div class="glass-input-group">
  <label class="glass-label">Email</label>
  <input class="glass-input glass-input--error" type="email" value="invalid@">
  <span class="glass-hint glass-hint--error">Please enter a valid email address</span>
</div>
```

- Валідація задається лише класами. Червона рамка дає `.glass-input--error`, червона підказка — `.glass-hint--error`. JS-логіки в джерелі немає.
- Фокус: `:focus` дає фокусне кільце. Колір береться з `--gl-focus-ring`, а `--gl-border-focus` і `--gl-shadow-focus` його наслідують. Тінт у цих токенах дає менше 3:1, тож його не став.
- Дата й час (`type="date"`, `time`, `datetime-local`, `month`) мають той самий клас. Нативний вигляд знято, тож значення стоїть на початку.
- Префікс і суфікс: `.glass-input-wrap` з `__prefix` / `__suffix` та модифікаторами `--prefix` / `--suffix`.
- Посилання в рядку мітки (наприклад «Forgot password?»), записане **після** поля:

```html
<div class="glass-input-group glass-input-group--label-end">
  <label class="glass-label" for="password">Password</label>
  <input class="glass-input" id="password" type="password">
  <a class="glass-input-group__label-end" href="/reset">Forgot password?</a>
</div>
```

- Лічильник символів: `.glass-input-group__counter`, а з `.is-over` — повідомлення про перевищення. Прив'язуй його через `aria-describedby`.
- Гострі місця: не позиціонуй посилання абсолютно над рядком мітки. Не став `position` на `.glass-label` вручну.

#### Popover (3.25)

Базова структура: trigger всередині `.glass-popover-anchor`, поруч `.glass-popover`, з `.is-open` на popover:

```html
<div class="glass-popover-anchor">
  <button class="glass-btn glass-btn--secondary glass-btn--auto"
          onclick="gkTogglePopover(this, event)">
    Open menu
  </button>
  <div class="glass-popover">
    <ul class="glass-list glass-list--bare">
      <li class="glass-list__item glass-list__item--interactive">
        <div class="glass-list__content"><div class="glass-list__title">Duplicate</div></div>
      </li>
    </ul>
  </div>
</div>
```

JS-перемикач (фрагмент, його назва **`gkTogglePopover`**):

```js
// ⚠️ Do NOT name this function `togglePopover` — it collides with the
// native HTMLElement.togglePopover() method from the HTML Popover API.
function gkTogglePopover(btn, e) {
  const popover = btn.nextElementSibling;
  const wasOpen = popover.classList.contains('is-open');
  document.querySelectorAll('.glass-popover.is-open')
    .forEach(p => p.classList.remove('is-open'));
  if (!wasOpen) popover.classList.add('is-open');
  if (e) e.stopPropagation();
}
```

- Модифікатори: `.glass-popover--top` (угору), `--start` (ліве вирівнювання), `--end` (праве вирівнювання).
- Стан `.is-open` ставиться на `.glass-popover`, а не на тригер.
- Пастка: назва `togglePopover` кидає `NotSupportedError` в inline `onclick`.
- Пастка: звичайний абсолютний popover обрізається `overflow: hidden` і розширює сторінку, коли закритий. Для таких місць відкривай у top layer з атрибутом `popover`:

```html
<button class="glass-btn glass-btn--secondary glass-btn--auto" popovertarget="share-panel">Share</button>
<div class="glass-popover" id="share-panel" popover>
  <ul class="glass-list glass-list--bare">…</ul>
</div>
```

- Top layer сам не розміщує панель біля кнопки. Розміщення робить скрипт `gkPlace()` (3.25), і його треба викликати знову при скролі та зміні розміру, поки панель відкрита. `<glk-popover>` в GlassKit Elements робить це сам.
- `.glass-popover[popover][data-side="top"]` ставить скрипт, коли панель відкривається вгору.

#### Menu (3.37)

Фрагмент (скорочено) з базової структури:

```html
<button class="glass-btn glass-btn--secondary glass-btn--sm glass-btn--auto" id="view-button"
        aria-haspopup="menu" aria-expanded="false" popovertarget="view-menu">View</button>
<div class="glass-menu" id="view-menu" role="menu" aria-labelledby="view-button" popover>
  <button class="glass-menu__item" role="menuitem" tabindex="-1">
    <span class="glass-menu__check"><svg viewBox="0 0 24 24"><polyline points="5 12 10 17 19 7"/></svg></span>
    <span class="glass-menu__icon"><svg viewBox="0 0 24 24"><!-- Icon --></svg></span>
    <span class="glass-menu__label">Duplicate</span>
    <span class="glass-menu__trailing">⌘D</span>
  </button>
  <button class="glass-menu__item" role="menuitem" tabindex="-1">
    <span class="glass-menu__check"><svg viewBox="0 0 24 24"><polyline points="5 12 10 17 19 7"/></svg></span>
    <span class="glass-menu__label">Delete</span>
  </button>
</div>
```

- Панель — `.glass-menu` з `role="menu"`, названа своєю кнопкою через `aria-labelledby`. Ширина 180–320px.
- Пункти: `.glass-menu__item` з `role="menuitem"` (або `menuitemcheckbox` / `menuitemradio` з `aria-checked`). Небезпечна дія: `.glass-menu__item--danger`.
- Розділювачі: `.glass-menu__separator`. Заголовки груп: `.glass-menu__group-label` у `role="group"`.
- Відключені пункти: `aria-disabled="true"`, а не `disabled`. Вони лишаються досяжними стрілками.
- Якщо в меню є пункти з галочкою, **кожен** пункт має `.glass-menu__check`, інакше вирівнювання ламається.
- Для вмісту (форма, список посилань, текст) бери popover, а не меню. Меню — для команд.
- Клавіатура (WAI-ARIA menu button) сидить у скрипті; `<glk-menu>` робить її повністю. Пункти мають `tabindex="-1"`, одна точка табуляції.

#### Modal (3.12)

```html
<div class="glass-modal-overlay is-active">
  <div class="glass-modal">
    <div class="glass-modal__header">
      <h2 class="glass-modal__title">Delete contract?</h2>
    </div>
    <div class="glass-modal__body">
      <p>This action cannot be undone.</p>
    </div>
    <div class="glass-modal__footer">
      <button class="glass-modal__action">Cancel</button>
      <button class="glass-modal__action glass-modal__action--primary">Confirm</button>
    </div>
  </div>
</div>
```

Небезпечна дія: `<button class="glass-modal__action glass-modal__action--danger">Delete</button>`.

Відкриття і закриття через клас:

```js
// Open
document.querySelector('.glass-modal-overlay').classList.add('is-active');
// Close
document.querySelector('.glass-modal-overlay').classList.remove('is-active');
```

- **Пастка:** `is-active` ставиться на `.glass-modal-overlay`, **не** на `.glass-modal`.
- Рекомендовано нативний `<dialog class="glass-modal-overlay">` з `showModal()` (з 1.20.0). Він дає top layer, інертність фону, повернення фокусу і закриття по Escape. Структура всередині така сама. Для анімації закриття використовуй `is-active` і `close()` після 300 мс.
- Ширина за замовчуванням — `--gl-modal-max-width` (340px). Ширші діалоги перевизначай: `.my-dialog { --gl-modal-max-width: 560px; }`.
- Затемнення за діалогом розмиває `--gl-blur-overlay`, а без нього — `--gl-blur-soft`.
- Поки діалог відкритий, усе поза ним інертне: тост, показаний звідти, не клікається й не озвучується. Відгук давай всередині діалогу.

#### Card (3.6)

```html
<!-- Standard Card -->
<div class="glass-card">
  <p class="glass-card__text">Content</p>
</div>

<!-- Glow Card with Icon -->
<div class="glass-card glass-card--glow">
  <div class="glass-card__icon">
    <svg viewBox="0 0 64 64"><!-- Icon SVG --></svg>
  </div>
  <p class="glass-card__text">Description text goes here.</p>
</div>
```

- `.glass-card` — базовий скляний контейнер, `border-radius: 24px`.
- `.glass-card--glow` — градієнт скла з «світловою смугою».
- `.glass-card__icon` — центрована обгортка іконки 48×48px.
- `.glass-card__text` — опис, приглушений текст.
- Посилання на картці беруть `--gl-color-primary-on-glass`, а не `--gl-color-primary`.
- Список у картці: `.glass-list--bare` прибирає другу скляну поверхню.

#### Sheet (3.31)

```html
<div class="glass-sheet-overlay" hidden>
  <div class="glass-sheet" role="dialog" aria-modal="true" aria-labelledby="sheet-title">
    <div class="glass-sheet__grip" aria-hidden="true"></div>
    <h2 class="glass-sheet__title" id="sheet-title">Rebook to …</h2>
    <div class="glass-sheet__body">…</div>
    <div class="glass-sheet__actions"><button class="glass-btn glass-btn--secondary glass-btn--sm">Close</button></div>
  </div>
</div>
```

- Показ: прибери `hidden`, форсуй перерахунок (`void overlay.offsetHeight`), на наступному кадрі додай `.is-active`.
- Сховати: прибери `.is-active`, постав `hidden` після `transitionend` панелі (запасний варіант 400 мс). При зменшеному русі — одразу.
- Закриття: клік по затемненню і Escape.
- Модифікатори: `--inline` (без overlay, у потоці), `.glass-sheet-overlay--start` / `--end` (панель збоку на всю висоту, ширина 440px), `.glass-sheet-overlay--modeless` (без затемнення, відкривається через `show()`).
- Голова: `.glass-sheet__head` з `__leading`, `__heading` (`__eyebrow`, `__title`, `__subtitle`), `__trailing`, `__close`.
- Рекомендовано `dialog.glass-sheet-overlay` з `showModal()` (з 1.30.0). Назви його через `aria-labelledby`. Блокуй скрол сторінки (`overflow: hidden` на `<html>`), інакше колесо над затемненням і далі скролить сторінку.
- Пастки: `[hidden]` перебиває `display: flex`. З 1.39.0 `dialog.glass-sheet-overlay` має `overflow: clip`, а не `hidden`.
- `<glk-sheet>` у GlassKit Elements робить усе це сам.

#### Background, pill і tab bar знову не дублюю. Далі — ключові частини, які лишилися

Розділи 3.1–3.25 (крім перелічених) у цій відповіді не розписано, бо їх у завданні не просили.

---

#### Примітки щодо точності витягу

- Розділ (F) охоплює: Background, Pill Button, Tab Bar (з droplet), Buttons, Toggle, Select, Search, Input (фокус і валідація), Popover, Menu, Modal, Sheet, Card.
- Таблиці розділу (A) переписано дослівно. Прозові рецепти (AA, `contrast-color()`) у (A) пропущено.
- Розділи (B), (C), (D) та (E) переписано повністю, з українськими поясненнями і збереженими назвами класів.
