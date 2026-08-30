> живе доки: назавжди (вічне, wsd 1.8) — реєстр портів Фармастор→StockCheck

# Фармастор v2 · ПОРТ-РЕЄСТР (щоб нічого не загубити)

**Ціль:** один індекс усього, що напрацьовано/залочено, але ще НЕ в продукті (`Фармастор_замовлення_v2_port_b12_3.html`), + відкриті рішення + борги. Джерело істини лишається MASTER_LOCK; це — карта-навігатор.
**Дата:** 19.07.2026 · **Продукт зараз:** b12_3 · **Наступний порт-таргет:** b13.

---

## A · DESIGN-LOCKED, але НЕ портоване в продукт (черга b13+)

Усе нижче — device✓ у харнесах, залочено в MASTER_LOCK, **BUILD у продукт pending**. Canon-merge лише ПІСЛЯ порту+device у продукті (compare-lock≠canon).

| # | Що | Джерело-харнес | §MASTER | Статус |
|---|---|---|---|---|
| A1 | **Верхівка Динаміки** (sumcard: Погіршилось/Покращилось + tally 3-плитки + date-pill, caption «відносно MSL», стан-іконки) | `dynamika_harness_v4_3.html` | §5.1 | design-lock 18.07, НЕ в проді |
| A2 | **Status-фільтр** (комбо-чіп band-swap біля області) | `status_filter_harness_v2.html` | §5.4 | device✓, НЕ в проді |
| A3 | **Перенесена-ринг** (тримаємо ринг, P1 ✓✓ в дузі, arcLift .82) | — | §5.2 | lock, port pending |
| A4 | **Home-картка** (3 стани, двоколірний fill, дуга-%, «не почато»=«—» без слова) | `harness v3.4` | §5.2/§6.4 | device✓ 14.07 — *звірити чи вже в b12_3* |
| A5 | **TopArea/Пікер-рядок** (L-A band-swap, прес місто.90/обл.88, пошук-well, addr street-led) | `toparea harness v4` | §5.3 | lock 15.07, stop-gap у b7_4 — *звірити стан* |
| A6 | **colhead-ДІМ + анатомія-гніздо Динаміки** (реальні назви v+pk+fd, дім full-scope, manifest per-тема, SKU-лейбл) | `colheaddim_v6 / v7` | §5.1 (pending-canon) | harness, sticky-фікс v7, **device-pick G/P pending** |
| A7 | **dark-tile / arcLift значення** (§6.5) | — | §6.5 | lock, застосувати при порті |
| A8 | **Δ-колір Динаміки = МОДЕЛЬ B** (недобір `s=max(0,MSL−V)`; **critK=0**=лише порожня→crit; labels «до/від норми»; tally=траєкторія, stuck→без-змін; Проблемні=СТАН `sT>0`; вердикт авто-з-tally) | `dynamika_deltacolor_harness_v1.html` | §5.1 | design-lock 19.07 (harness device✓), НЕ в проді |

> **Node 5 «Динаміка»-анатомія** гібрид: info(назва+fd+pk / MSL) + .dyn[well-було · well-стало · dbox-Δ]. Δ=T2-гніздо (світла глянець+drop / темна A66.1 tone-lift). Нурофен = 1 картка + nested eyebrow. **Δ-колір = Модель B (A8, §5.1) — реопен C1 RESOLVED.**

---

## B · NODE-ЧЕРГА (беквбон + екрани)

| Node | Що | Статус |
|---|---|---|
| 6 | Стан v2 `visits[]` + snapshot-on-copy (A1) + міграція v1→v2 | ✓ ГОТОВО |
| 7 | Home 3-станові картки | ✓ ГОТОВО (арка-філ лок b9) |
| 8 | Copy-контракт §4 (📋→M{X}, xlsx-стек знесено −86КБ) | ✓ переважно; **copy-toast Proxima-якір — звірити** |
| 5 | Пікер-оверлей (search-first, city sticky headers, tier mini-chips) | ⏳ harness-first pending |
| §5.1 | Екран порівняння (Динаміка) UI | 🔨 В РОБОТІ (harness colheaddim_v7) |

---

## C · ВІДКРИТІ РІШЕННЯ (потребують твого device-picks / реопену)

- **C1 · ✅ [RESOLVED 19.07 → МОДЕЛЬ B] Δ-колір: дистанція ⇄ недобір.**
  Реопен закрито (harness device✓). **Обрано B — недобір `s=max(0,MSL−V)`:** нижче норми=дія=warn/crit; дистанція фарбувала падіння під норму зеленим (не читалось). **critK=0** (лише порожня=crit). **labels «до/від норми».** Δ-колір=траєкторія; нижче-норми-зараз ловлять Проблемні (СТАН) + сире число. → **A8** (порт b13). Значення в §5.1 MASTER_LOCK.
- **C2 · [DEVICE-PICK] G-дім ⇄ per-brand.** Тест: довгий Нурофен в обох. Claude-бет = G. Konst-схил = P. **Pending.**
- **C3 · [LOCK-pending] Матеріал дому** (світла Lbg/Lbord/Ldrop · темна Dbg/DbordC/DridgeC/Ddip · геом chH/chRad). Важелі є, copy не знято. Device→copy→лок ОКРЕМО світла+темна.
- **C4 · [РЕОПЕН] Вхід у Динаміку / discoverability.** Footer-афорданс «📈 Динаміка» (visits≥2) ризикує бути невидимим. Пропозиція 16.07: **чіп-банд на Home** (активні/перенесені/усі/Динаміка) біля лічильника+області — вирішує і видимість, і швидкий перегляд перенесених. **Обговорення pending.**
- **C5 · Де «живе» Динаміка (макро-IA).** Залочено: лінійна IA, екран ③, per-аптека, вхід з Home. Пов'язано з C4.

---

## D · ПРОДУКТ-ЗАГЛУШКИ (immediate, поза Динамікою)

- **D1 · «Експорт CSV»** у ••• — dead stub, треба onclick + context-aware лейбл («ця аптека» з FILL / «усі дані (N аптек)» з Home).
- **D2 · «Про додаток»** — About-sheet (APP_BUILD, автор, Telegram, патерн A58).
- **D3 · Excel deep-link** — кнопка SharePoint-форми (FILL post-copy + ••• Home), лейбл «Excel», Universal Links, split 2.5:1. Device pending.
- **D4 · Date-пікер Динаміки** — зараз заглушка, свідомо відкладено на після §5.1-кроків.

---

## E · БОРГИ / ДЕФЕРНУТЕ

- **E1 · Арка «ring hidden by its own success»** — анімаційний борг (дуга ховається коли 100%).
- **E2 · getBrand баг** (§8/§2) — STEP1-«не чіпати» скасовано.
- **E3 · Абандонні un-transferred знімки** — маркер у порівнянні (деталь, не блокер).

---

## F · ПОЗА ЦИМ РЕЄСТРОМ (окрема governance-сесія)

Крос-продуктові хвости (QR Lens A58-motion/canon-борг B52–B57, Drive Lens dead-code audit, KPI category-integration, wsd Cluster 6, Cookbook uncanonized) — **НЕ тут**, живуть у cross-product governance-борзі. Цей реєстр — тільки Фармастор.

---

*Оновлювати після кожного порту в продукт (переносити рядок A→ виконано, canon-merge).*
