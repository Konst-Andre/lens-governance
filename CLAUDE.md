# lens-governance — ядро Lens: як тут працювати

> живе доки: існує ядро. Це **двері** з маршрутами «звідки брати», не карта: карта — `kernel/Lens_INDEX.md`. Коротко; правило роботи з ядром змінилось — правиться тут, тим самим комітом (перед комітом — подвійний аудит, нижче).
> Claude Code вантажить цей файл сам у кожній сесії, де підключено ядро, — навіть коли сесія працює в іншому репо (перевірено 04.10.2026, AirLens S12).

**Що це.** Спільне ядро сімейства Lens і всіх репо Konst: протокол роботи (wsd), кукбук (iOS/PWA томи 1–5, бот на Workers — том 6), правила Cloudflare, каркас Claude Code, гейт `Lens_validate.py`. Продукти живуть у своїх репо; сюди — лише те, що потрібне **більш ніж одному** проєкту.

- **Репо публічне.** Секретів, токенів, переліку токенів, внутрішніх адрес — ніколи. Посилання на приватні репо — лише `Репо:шлях`, без вмісту.
- **Мова** — українська; код і ідентифікатори — англійською.
- **Старт роботи з ядром:** `kernel/Lens_INDEX.md` §1 (порядок читання) → §2 (чотири ролі — чотири доми) → потрібний файл **точково**. Wsd і томи кукбуку цілком не читати.
- **Гілка ядра:** `main` (у сесії іншого репо — його правило гілки, а це — лише для правок ядра); push + read-back (`git ls-remote origin refs/heads/main` ≡ локальний HEAD). Інші сесії теж пишуть у `main` → `git pull` перед правкою, ніколи force.
- **Гейт перед комітом:** `python3 kernel/Lens_validate.py --gov .` + `--repo <Репо>=../<Репо>` лише на репо, склоновані поруч (тека, якої нема, дає хибні ✗ на всі її `Репо:шлях` — заміряно 04.10: ✗ 20; без `--repo` вони — ⓘ) — ✗ не більше, ніж до правки; нове ⚠ від своєї правки — прибрати.

## Звідки брати, коли… (Claude Code)

Файл відкривати **точково** — за тригером рядка; що читати на старті — `kernel/Lens_INDEX.md` §1. Шляхи тут і скрізь в інструкціях — **у бектиках**: це назва; `@шлях` без бектиків вантажить файл цілком у кожну сесію (code.claude.com/docs/en/memory, 04.10.2026). Звірено з `git ls-files` 04.10.2026 (ревізія `CC-4`).

| коли | звідки брати |
|---|---|
| інтерфейс iOS / PWA, бот на Workers | `kernel/cookbook/Lens_cookbook_INDEX.md` → номер → том, точково |
| будую чи правлю стенд, харнес, компер, важелі | `kernel/Lens_stagebench_manifest.md` за § (буфер — `kernel/Lens_stagebench_delta_running.md`) |
| device-тест на синтетичних даних (пісочниця) | `kernel/Lens_sandbox_manifest.md` |
| суджу рендер, стенд, прев'ю, вирок пристрою | `kernel/wsd/Lens_verdict_protocol.md` — номер з маршруту на початку `Work_Standard.md` |
| пишу детектор, гейт, смоук; патч перед комітом; діагноз помилки | `kernel/wsd/Lens_patch_check_protocol.md` |
| прев'ю для Konst | `tools/PREVIEW.md` — повний текст (у профілі — стиснення); крок «квиток / `gh_commit`» тут = `git push` у `Konst-Andre/sandbox` |
| правило wsd за номером (`1.x`, `12.x`) | `kernel/wsd/Work_Standard.md` — «Зміст» і маршрут |
| веду канон: куди записати, правка вічного файла | `kernel/wsd/Lens_governance_protocol.md` (К1/К2 · 12.11 · 12.15–12.20) |
| питання з варіантами, форма 💡, двійне пояснення | `kernel/Lens_PROFILE.md` §7 (`13.1`–`13.3`) |
| зовнішній візуальний ефект · скло й острівець | `kernel/Lens_fx_candidates.md` · `products/Lens_glass_FINDINGS.md` |
| Excel, Power Query, VBA (KPI · QR Lens) | `kernel/Lens_excel_protocol.md` |
| порт блоку «Обслуговування» | `kernel/modules/Lens_module_1_maint_v1.md` (пара — кукбук A79) |
| Cloudflare · каркас репо під Claude Code | `tools/cloudflare/CLOUDFLARE.md` · `tools/claude-code/CLAUDE_CODE.md` |
| теки, імена, адресація `Репо:шлях` у ядрі | `kernel/Lens_REPO_LAYOUT.md` — формула ядра, **не** `docs/REPO_LAYOUT.md` продукту |
| архівне джерело · переїзд продуктів | греп по `archive/` (перейменування — `kernel/Lens_ARCHIVE_INDEX.md` §3-б) · `sessions/Lens_gov/Lens_MIGRATION_GW_ledger.md` |

**Ера Project — у Claude Code не читати:** `kernel/Lens_PROJECT_instruction.md` · `kernel/Lens_NEWPROJECT_bootstrap.md` · `kernel/Lens_github_push_protocol.md` · `tools/CHAT_TOOLS.md` · `tools/ADAPT.md` · `tools/lens-gh/`. Шапки «AUTO-READ» і штамп «KERNEL v2 … між Projects» тут не діють. **Правило ядра, що спирається на механіку чату Claude** (`present_files`, `ask_user_input_v0`, `/mnt/…`, project_knowledge_search, квиток / конектор): суть правила діє, механіка — відповідник Claude Code (файл у репо + коміт · AskUserQuestion · греп по клону · `git`).

## Знахідка з іншого репо → сюди (wsd 1.19)

Тест одним питанням: **«якщо репо продукту завтра забуде це — знання має загинути разом із ним?»** Ні → вічний файл ядра в **тій самій сесії**, у репо продукту — рядок-вказівник.

| знахідка про | дім у ядрі |
|---|---|
| Cloudflare: ліміти акаунта, збірки, прев'ю, токени (лише правило, без переліку) | `tools/cloudflare/CLOUDFLARE.md` |
| Telegram-бот на Workers + D1 + Mini App (і його адмін-частина) | `kernel/cookbook/Lens_bot_cookbook_6_telegram_workers.md` (серія `T`) |
| iOS / PWA / інтерфейс | томи 1–5 через `kernel/cookbook/Lens_cookbook_INDEX.md` |
| як влаштувати репо для Claude Code, профіль Konst, аудит | `tools/claude-code/` |
| протокол роботи (як ми працюємо) | `kernel/wsd/Work_Standard.md` — лише окремим ходом, це канон |
| не влізло в жодну | `kernel/Lens_INDEX.md` §2 — там рішення |

Новий рецепт кукбуку — рядки в `Lens_cookbook_INDEX.md` §2 і §3 тим самим комітом. Борг ядра, який не закрити зараз, — рядок у `kernel/Lens_governance_CHERGA.md`.

## Аудит правил і інша модель

Змінив файл інструкцій (цей файл, `tools/claude-code/PROFILE.md`, правило ядра, шаблон `CLAUDE.md`) — перед комітом `bash tools/claude-code/audit_prompts.sh <файл>`: **два** проходи, sonnet + opus `--effort high`. **Fable — лише за явним словом Konst** (підписка: за реальні кошти). Запуск будь-якої моделі — рядок у чаті до запуску: модель · effort · навіщо. Журнал аудиту ядра — `AE-Simulator:docs/AUDIT.md`.
