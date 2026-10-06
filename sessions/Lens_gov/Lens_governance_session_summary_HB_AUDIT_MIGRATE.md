# Lens — самері сесії H-B «Ціна аудиту · переїзд StockCheck і QR · воркер з гіта»

живе доки: наступна governance-сесія закрила або перенесла §0 — тоді в archive/summaries/Lens_gov/ (стеля 2 живих: це + GZ).
дім: lens-governance/sessions/Lens_gov/ · оголошено: `kernel/Lens_INDEX.md` §5, рядок «Lens (governance)».
сесія: 05–06.10.2026 · Claude Code (хмара), Opus 5.5, effort medium → high (Konst) · ядро + `add_repo`: stock-check · EquipLens · QR-Lens (запис) · режим — делеговано Konst. Попереднє самері H-A — `archive/summaries/Lens_gov/` (його §0 перенесено сюди).

## §0 · ВІДКРИТЕ

**0.1 · Перша робота — адаптація `QR-Lens` під каркас** (`QR-Lens:lens/QR_Lens_CHERGA.md` `QRL-3`, за `tools/claude-code/ADOPT.md`). Розкладка за Р-7 уже є (06.10), бракує каркаса: `CLAUDE.md`, хук, `env_check` (з перевіркою «живий сайт ≡ `docs/index.html`»), журнал аудиту. Аудит `CLAUDE.md` — клас 2.

**0.2 · Друга — розмова з Konst про дані QR** (`QRL-5` автоматизація KPI → Excel → `index` · `QRL-6` додати PSR Києва й Черкас за запитом керівника). Читати першим — `QR-Lens:lens/QR_Lens_export_contract_v1_1.md`; зразки вже в репо (`sources/KPI.xlsx`, `tools/` — xlsm і шаблон v2). Мапа «людина → область» захардкоджена в шаблоні (`SR_AREA`) — правити шаблон, не `index.html`.

**0.3 · QR — хостинг** (`QRL-1`): сайт — воркер з Workers Builds (коміт у `docs/` сам деплоїть, перевірено 06.10); Pages `qr-lens` (тека виводу `docs`) живе, доки люди переходять → **видаляє Konst** (знімає старі деплої зі списком PSR).

**0.4 · Черга ядра — 6 відкритих** (`kernel/Lens_governance_CHERGA.md`): пакети `ХІД-8` (індекс) · `GATE` (інструменти гейта, з `G19-1`) · `WSD` (канон) — **коли, вирішує Konst**; `CQ-2` (черги AE/AirLens — у їхніх сесіях) · `CC-5` (профіль ⟂ wsd 1.19 — вирок Konst).

**0.5 · Продукти, що чекають своїх сесій:** `stock-check` (`SC-1` сайт → `docs/` — прод · `SC-3` каркас · `SC-4` відтворити втрачене) · EquipLens («З ЯДРА»: `Г-11` `Г-13` `ADR-1`) · AE (переїзд на воркер — `AE-Simulator:docs/CHERGA.md` §0 п.5; правило — `CLOUDFLARE.md` §2 п.9–11).

**0.6 · Відкрите з GZ §0** (п.3 хід 8 + `GH-1` · п.4 `G19` · п.5–8, 11–12) — текст у GZ, не тут.

**Від Konst:**
- ⏳ видалити проєкт Pages `qr-lens` (тип Pages), коли всі перейдуть на `qr-lens.konstandre.workers.dev`.
- ✅ 06.10 профіль v10 вставлено · ✅ «так» на злиття stock-check · ✅ зразки Excel QR у репо · ✅ Pages QR — тека виводу `docs`.

## §1 · ЩО ЗРОБЛЕНО (ядро `main` ← `6db553a`)

- `AUD-2` ✅ формула ціни аудиту (клас правки → проходи, пакетом) — `tools/claude-code/templates/AUDIT_template.md` «Коли і скільки» · `audit_prompts.sh` (по черзі, стоп на ліміті, вартість, stderr окремо) · детектори `frame_check` (копія скрипта) і `env_check` (борг аудиту).
- `AUD-3` ✅ wsd 2.42 — премортем «усі справжні, найсильніша першою» (Klein 2007).
- Експеримент Konst «sonnet на high» — підтверджено; клас 2 = sonnet high + opus high (`kernel/Lens_AUDIT.md`, 06.10).
- Переїзд: StockCheck (журнал GW крок 3 ✅, `stock-check` `e2463c3`) · QR (крок 4 ✅, `QR-Lens` `99484fc`) · `Lens_glass_FINDINGS` → `kernel/`, `products/` зникла.
- QR → воркер з гіта: `qr-lens.konstandre.workers.dev` (Київстар і Vodafone ✓) · Workers Builds через API · `CF-1` ✅ правила в `tools/cloudflare/CLOUDFLARE.md` §2 п.9–12.
- Прополка черги ядра: 28 → 6 відкритих (закрито зроблене, 3 → EquipLens, пакети).
- `.claude/settings.json` ядра — дозвіл на команди читання.

## §2 · УРОКИ (рядок + дім)

- Покриття правила шукати за ознакою, не за іменем інструмента (греп `audit_prompts` пропустив «подвійний аудит» у 6 файлах) → `kernel/Lens_AUDIT.md`, рядок 05.10 `AUD-2`.
- Ціна аудиту — читання посилань, не холодний старт; sonnet без `--effort` думає в 7 разів менше → `tools/claude-code/templates/AUDIT_template.md` «Коли і скільки» · `kernel/Lens_AUDIT.md` 06.10.
- Старі деплої Pages вічні, кеш краю — 7 днів; ручний деплой воркера ≠ сайт оновлюється сам → `tools/cloudflare/CLOUDFLARE.md` §2 п.10–11.
- Завантаження з GitHub web іде без `[CF-Pages-Skip]` → Pages зібрав корінь без сайту → `CLOUDFLARE.md` §2 п.11 (тека виводу = тека сайту на час переходу).
- Премортем журналу GW справдився: G19 худне з корпусом → `GATE` (`G19-1`).

## §3 · ЧИСЛА БАЗИ

`--gov` ✓25 ⚠18 ✗0 (було ✓25 ⚠21 на старті) · відкритих у черзі ядра 6 (стеля 12; старші 30 дн. — 3 пакети) · Cloudflare 06.10: збірки Pages 55/500 · аудит сесії: 05.10 6 проходів $5,80 · 06.10 wsd 2 проходи $3,85 · CLOUDFLARE $1,04.

## Стартове повідомлення наступної сесії

```text
Сесія ядра Lens (репо Konst-Andre/lens-governance, main; ПУБЛІЧНЕ — секретів ніколи). Відповідай українською, простою мовою.
Старт: env_check (хук) → самері sessions/Lens_gov/Lens_governance_session_summary_HB_AUDIT_MIGRATE.md §0 → kernel/Lens_governance_CHERGA.md.
ПЕРША РОБОТА — адаптація QR-Lens під каркас (QR-Lens:lens/QR_Lens_CHERGA.md QRL-3, за tools/claude-code/ADOPT.md; репо підключити add_repo).
ДРУГА — розмова про дані QR: QRL-5 (автоматизація KPI → Excel → index) і QRL-6 (додати PSR Києва й Черкас). Спершу прочитати QR-Lens:lens/QR_Lens_export_contract_v1_1.md, потім слухати мене.
Пакети ХІД-8 / GATE / WSD — лише за моїм словом.
Аудит інструкцій — за класом, пакетом перед самері (tools/claude-code/templates/AUDIT_template.md «Коли і скільки»); перед запуском — rate_limit_info. Fable — лише за моїм словом. Маркер контексту — get_session щоразу. Делегування: вирішуй сам, пояснюй простою мовою.
```
