# Фармастор Залишки v2 — REBUILD BRIEF (дизайн з нуля · логіку портуємо)
> Дата: 12.07.2026. Мета: чистий старт у свіжому чаті. **Джерело правди — `Фармастор_v2_MASTER_LOCK.md`.**
> Рішення Konst: старий v1.3-варіант дизайну — не годиться. Будуємо дизайн **повністю з нуля** за нашими стандартами; логіку (підрахунок/стан) **переносимо**.

---

## §0 · РІШЕННЯ + УРОК (з цього починати)
**Порт-на-legacy провалився двічі.** Причина одна: стратегія «мінімальний-diff порт на v1.3» **зберігає стару структуру** (teal-хедер, білі бари, плоскі картки, мертва xlsx-бібліотека, старий markup) — а це рівно те, що ми замінюємо. Тобто такий порт **за побудовою** дає напів-старий результат. Це не дрібниця, це неправильна стратегія.

**Нове правило (урок, кандидат у wsd):** коли існує **harness** (visual truth, device✓) + **MASTER_LOCK** (логіка+токени) → будувати **чистий шелл з harness + портувати логіку**. НЕ грати новий дизайн на старий scaffold. Перероблювати таке = марна втрата ресурсів.

---

## §1 · ПРИНЦИП РИБІЛДУ
- **Логіка = переносимо** (вирахування норм/дефіциту, стан, копія — під капотом, візуально не видно, але має бути точна). Донор — існуючий JS.
- **Дизайн = з нуля, повністю.** Кожна кнопка / прес / анімація / стан / іконка — за стандартами (Cookbook), максимальна якість, **device = арбітр**.
- **Locked-дизайн (що вже залучили) — беремо як є.** Не-зроблене — придумуємо/будуємо **harness-first**, не латаємо.

---

## §2 · ЛОГІКА — ПОРТУВАТИ (донор: `Фармастор_замовлення_v2_step1.html` / v1.3 — ЛИШЕ JS, не дизайн)
- **DATA: 83 SKU** — канон = `Farmastor_multibrand_harness_v1.html` DATA-блок (§2 MASTER_LOCK; device✓). НЕ дублювати, брати звідти.
- **getBrand** + **фікс §8** (р.408 `«містить Durex»` substring → точний матч бренду; інакше 12 гелів «Гель Durex…» ловляться хибно).
- **getMSLval = norm-resolver §3** (SKU.Category OTC|IW → тір аптеки `ph.oTC`|`ph.iW` A/B/C/D → MSL-колонка = норма). **Критична логіка, вже працює коректно — перенести дослівно.**
- **bKey, groupByBrand, getSubGroup** (детектори nested під-груп §2 — LOCKED).
- **Стейт-модель v2 §1:** `phs[phId].visits=[{date,vals,tier,transferred}]`; **A1 snapshot-on-copy** (📋→transferred=true; дубль того ж дня=перезапис; новий день=push); **absent≠0**; **міграція v1→v2** (обгорнути phId, історію не бекфілити, `farmstore_v1` недоторканий).
- **Copy-контракт §4:** `MSL.map(s=>d[s.k]!==undefined?d[s.k]:'').join('\n')` (83 by-kode, master-order); дуальний якір `M{X}·Proxima{ID}`; тост «✓ Скопійовано 83…»; CSV+share-sheet — тиха страховка в ••• (не герой).
- **filledCount / прогрес.**
- **ВИКИНУТИ НАЗАВЖДИ (не переносити):** `xlsx-js-style` (−425 КБ), legacy-міст `--teal→…`, увесь старий CSS/markup, білі бари (`.bot-bar background:#fff`), стильний .xlsx-експорт, колонка «→ Замовлення».

---

## §3 · ДИЗАЙН — БАЗА = HARNESS VERBATIM + §6 ТОКЕНИ
- **CSS-скелет lift з `Farmastor_multibrand_harness_v1.html`** (well/chip/eyebrow/settled/row/brand-card) — **dark співпаде 1:1**, бо піднімаємо дослівно (не переспівуємо).
- **Токени §6.1–6.3** з MASTER_LOCK: нейтрали §6.1, teal §6.2 (`hsl(162 82% 27%)`/`hsl(163 46% 46%)`, inkStr 14/15, tintMix 50, mutL 46), геометрія §6.3.
- **Хедер нейтральний** (НЕ teal-банер): `--bg` фон, заголовок `--text`, back/sub/прогрес нейтрал+accent. Емоджі-іконки геть (🏪/📥/🗑). Патерн уже відпрацьований у step2 — взяти звідти.
- **Auto-dark dual-selector + FOUC-скрипт §7.**

### FILL-рядок — застосувати ПОВНІСТЮ (у порті це пропущено — головний борг):
- **relabel-система SKU** (§2, лочили раундами): `.rv` назва + `.rpk` форма/№ окремим тегом + `.ck` ✓ — як `nameLine()` у harness. НЕ сирий `s.n`.
- **sub-eyebrows** (getSubGroup §2, sticky, tick+hairline-top §6.3) — nested форми в бренді.
- **well-комірка** 60×46 r15, input усередині (ghost-норма .34 / суцільне / «0»=дані).
- **δ-чіп** кутовий soft+55%border, hyphen, **silent-ok A59** (лише дефіцит).
- **settled-tint** (accent-soft 50%) на заповнених.
> *Що з порту вже вийшло правильно (взяти за основу):* well+ghost+settled+✓ рендеряться коректно; norm-resolver працює. Не так: relabel/sub-eyebrows відсутні, брак collapse-анім, білий bot-bar, dark-композит не harness.

---

## §4 · ЩО ЩЕ НЕ ЗРОБЛЕНО — ПРИДУМАТИ/ПОБУДУВАТИ (harness-first, per standards)
- **Home-картки:** 3 стани §5 (не почато / X/83 📋 / перенесено ✓✓), тір-профіль `OTC B·IW C`, дуальний якір, «📈 Динаміка» (visits≥2), «Очистити» сховати з-під ока + гард. **Press-механіка A67** (card = slow inertial).
- **Пікер:** знести нативний `<select>`; пошук-перш (назва/адреса/Proxima); групування по місту (реюз FILL-акордеона, sticky); layout рядка §5 (addr сильний ellipsis, тір=2 міні-чіпи).
- **Bottom-bar / кнопки / FAB / session-bar:** нейтрал+accent, press per-standard (A67 chip short/sharp).
- **Brand collapse-анім + винагородження** при done-бренді (зараз миттєвий `display:none`) — **motion-bench** (slow-mo × bake).
- **Comparison §5.1** — fast-follow (дата-контракт локнутий, UI harness-first).
- Кожен інтерактив: **A67 press-ladder** (chip short/sharp; card slow inertial), **reduced-motion guard** обовʼязково.

---

## §5 · REFERENCE (READ-FIRST у свіжому чаті)
1. `Фармастор_v2_MASTER_LOCK.md` — **джерело правди** (токени/логіка/IA).
2. `Farmastor_multibrand_harness_v1.html` — **visual truth**: CSS-компоненти + relabel `nameLine`/eyebrow + 83 SKU DATA + getSubGroup.
3. `Фармастор_замовлення_v2_step1.html` — **ЛИШЕ донор логіки** (getBrand/getMSLval/state/copy). **Дизайн звідти НЕ брати.**
4. `Work_Standard.md` → `Lens_iOS_cookbook.md` — стандарти/патерни (A45/A48/A59/A67 …).

---

## §6 · MISTAKES-LOG (щоб не повторити)
1. Не викинув xlsx-lib попри §4 + власну заяву «не потрібна».
2. Відклав **локнуте** мовчки (relabel, sub-eyebrows, collapse-анім) → напів-готовий екран.
3. Порт-на-legacy замість чистого шелла → напів-старий результат.
4. Не перефарбував bot-bar (білий на dark).
**Anti-патерн → правило:** лок = буквальний чекліст; є harness+лок → чистий шелл + порт логіки; не відкладати локнуте мовчки; §4-видалення робити одразу.

---

## §7 · ПЛАН СВІЖОГО ЧАТУ
1. READ-FIRST (§5) → підтвердити токени/relabel/geometry з MASTER_LOCK+harness.
2. Побудувати **чистий шелл**: index-структура (лінійна IA §5), §6-токени, нейтральний хедер, auto-dark+FOUC. Порожній, без екранів.
3. **Порт логіки** (§2) на чистий скелет: DATA+getBrand(fix)+norm-resolver+state+copy — під валідацію (`node --check`, grep-anchors).
4. **FILL екран** з harness verbatim + relabel + sub-eyebrows + δ-чіп + settled (§3) → device.
5. Далі per-screen: Home-картки → пікер → collapse-анім/press → comparison §5.1. Кожен: harness/bench → device → ship.

---

```
Привіт, бро. Фармастор v2 — БУДУЄМО З НУЛЯ (дизайн повністю новий, логіку портуємо).
Рішення прийнято минулого чату: порт-на-legacy — тупик, старий v1.3-дизайн викидаємо.

READ-FIRST:
1. Фармастор_v2_MASTER_LOCK.md — джерело правди (токени §6 / логіка / IA §5).
2. Farmastor_multibrand_harness_v1.html — visual truth: CSS-компоненти (well/chip/eyebrow/settled),
   relabel nameLine + sub-eyebrows (getSubGroup) + 83 SKU DATA. Дизайн беремо ЗВІДСИ.
3. Фармастор_замовлення_v2_step1.html — ЛИШЕ донор ЛОГІКИ (getBrand+fix §8, getMSLval=norm-resolver §3,
   state v2 §1, copy §4). Дизайн звідти НЕ чіпати.
4. Work_Standard.md → Lens_iOS_cookbook.md — стандарти.
Повний контекст + чекліст + mistakes-log: Фармастор_session_summary_v2_REBUILD_brief.md

Принцип: логіку переносимо (вирахування норм/дефіциту, стан, копія — точність критична);
дизайн будуємо з нуля за стандартами — кожна кнопка/прес/анімація harness-first, device-арбітр.
ВИКИНУТИ: xlsx-lib (−425КБ), legacy-міст, весь старий CSS/markup, білі бари.

Старт: план чистого шелла (структура IA §5 + §6-токени + нейтральний хедер + auto-dark/FOUC),
план → confirm → code (wsd 1.5). НЕ грати на старий scaffold. Погнали.
```
