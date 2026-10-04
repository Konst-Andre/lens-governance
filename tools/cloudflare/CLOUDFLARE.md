# Cloudflare — спільний акаунт Konst: бюджет, налаштування, актуалізація

> живе доки: проєкти Konst живуть на Cloudflare. Дім — `lens-governance:tools/cloudflare/` (поруч із каркасом `tools/claude-code/`).
> Народився: AE-Simulator S89, 03.10.2026. Блок `cf-limits` нижче — **єдине джерело** чисел і порогів для `cf_budget.sh`; правиш число — правиш блок.
> **Перевірено: 2026-10-03** (рядок читає `cf_budget.sh`; старше 30 днів — нагадує актуалізувати, §5).

**Навіщо.** Усі проєкти Konst — **один безкоштовний акаунт**. Ліміти спільні: бот AirLens, сайт AE, QR-Lens і кожен новий проєкт
їдять з тих самих 100 000 запитів на день і 500 збірок Pages на місяць. Сесія одного репо не бачить, що робить інший — тому бюджет
міряє скрипт на старті кожної сесії, а правила живуть тут, а не в чаті.

## 1. Бюджети (Free) — що рахувати

```cf-limits
workers_requests_day=100000
pages_builds_month=500
workers_builds_minutes_month=3000
alarm_share=70
fail_share=90
fresh_days=30
```
`workers_builds_minutes_month` — довідково: скрипт хвилин поки не міряє (API не перевірено); решту читає.

| ресурс | ліміт Free | на що скидається | хто їсть | що буде при переповненні | джерело (перевірено) |
|---|---|---|---|---|---|
| запити до воркерів + Pages Functions | 100 000 / добу на **акаунт** | опівночі UTC | бот (вебхук, крон), API сайтів, проксі моделі | помилка 1027 — воркер не відповідає до кінця доби | developers.cloudflare.com/workers/platform/limits (03.10.2026) |
| CPU на запит | 10 мс | — | важкий розбір, рендер | обрив запиту `exceededResources` | там само |
| статика Pages / `[assets]` воркера | без ліміту, безкоштовно | — | сайти, Mini App | — | developers.cloudflare.com/pages/functions/pricing (03.10.2026) |
| **збірки Pages** | **500 / місяць на акаунт**, 1 водночас | календарний місяць | **кожен push у будь-яку гілку будь-якого підключеного репо** (за замовчуванням) | нові деплої стоять: сайт живий, але зміни (і дані з редактора) не доїжджають | developers.cloudflare.com/pages/platform/limits (03.10.2026) |
| збірки воркерів (Workers Builds) | 3 000 хв / місяць, 1 водночас, 20 хв на збірку | місяць | push у репо з підключеним Workers Builds | викладка стоїть | developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing (03.10.2026) |
| крон-тригери | 5 на акаунт | — | боти | новий крон не створиться | workers/platform/limits (03.10.2026) |
| D1 | 5 млн читань · 100 тис. записів / добу | опівночі UTC | бот | — | кукбук том 6, T4 |

**Платні виходи** (на випадок, якщо Free стане тісно): Workers Paid $5/міс знімає денний ліміт запитів і дає 5 хв CPU, але **не піднімає
збірки Pages** (500 → 5 000 дає лише план Pro). Тому збірки бережемо налаштуванням, а не грошима.

## 2. Правила для кожного проєкту

1. **Збірка лише з теки сайту.** Pages → Settings → Builds → *Build watch paths*: include = `<тека сайту>/*` (напр. `site/*`), а не `*`.
   Документи, самері, інструменти, тести збірку не будять. Виключення перевіряються першими; `*` ловить і вкладені теки.
   Пропущена фільтром збірка лишає в API запис із `is_skipped: true` і стадіями `idle` (заміряно 03.10.2026) — це не збірка;
   `cf_budget.sh` її не рахує. Чи рахує її ліміт Cloudflare — у документації не сказано (не перевірено).
   Те саме є у Workers Builds (*Build watch paths*), але для воркера — **навпаки: include `*`, exclude документів** (`docs/*`, `tools/*`,
   `.claude/*`, `CLAUDE.md`, `README.md`): збірка воркера читає й сусідні теки (`[assets]`, `../data`), і перелік, що забув одну, мовчки
   не викладе зміну, а виключення, що забуло одну, дасть лише зайву збірку. Як і чим перевірити — кукбук том 6 · T13.
2. **Прев'ю лише для робочих гілок агента.** Pages → Settings → Builds → *Branch control*: preview = *Custom*, include `claude/*`.
   Інші гілки прев'ю не дають. Не потрібні прев'ю — *None*.
3. **Тека виводу — лише те, що публікується** (`site/`, `public/`; у продуктах Lens сайт — `docs/`, Р-7), не корінь репо — інакше
   документація, самері, `CLAUDE.md` доступні за адресою. Перевірка — за ВМІСТОМ, не кодом: Pages без `404.html` віддає головну з 200
   (`tools/claude-code/REPO_FRAME.md` §3).
4. **Фільтр збірок може мовчки не доставити зміну** → у `env_check` репо — детектор «файл на живому сайті ≡ `main`» (хеш одного
   файла даних або `index.html`). Без нього правило 1 небезпечне.
5. **Сирітки.** Проєкт Pages/воркер без дому в документах репо — кандидат на видалення: він їсть збірки й нічого не віддає.
   Видалення — лише з «так» Konst, після перевірки, що на нього не посилається жоден бот, домен чи Mini App.
6. **Ім'я `<проєкт>.pages.dev` може бути зайняте чужим** — тоді Cloudflare дає `<проєкт>-xxx.pages.dev`. Справжня адреса — API
   `pages/projects/<name>` → `subdomain`, не здогад з імені (так було з AirLens: `airlens.pages.dev` — чужий сайт, свій був `airlens-8bd`; видалено 03.10, §3).
7. **Міряти, потім казати.** Число в чаті чи документі — з `cf_budget.sh` або API, з датою; без заміру — «≈» або «не перевірено».
8. **Фільтра ще нема, а коміт не про сайт** — повідомлення коміту **починається** з `[CF-Pages-Skip]` (також `[CI Skip]` · `[Skip CI]`; регістр не важить) — Pages цей коміт не збирає (developers.cloudflare.com/pages/configuration/git-integration/github-integration, оновлено 21.04.2026). Чи рахує Cloudflare такий пропуск у 500 і що збирає push із кількох комітів — не перевірено. Це латка до правила 1, не заміна.

## 3. Реєстр проєктів акаунта (оновлює агент, коли бачить зміну; джерело — API)

| проєкт | тип | репо | що будить збірку | прев'ю | стан (03.10.2026) |
|---|---|---|---|---|---|
| `ae-simulator` | Pages (`site/`) | AE-Simulator | `site/*` | `claude/*` | налаштовано S89 |
| `ae-edit` · `ae-proxy` | воркери | AE-Simulator (`ae-proxy` — лише дашборд) | CI GitHub (`deploy-edit.yml`) | — | — |
| `airlens` | воркер + `[assets]` (бот і Mini App: `airlens.konstandre.workers.dev`) | AirLens | Workers Builds: include `*`, exclude `docs/*` `tools/*` `.claude/*` `CLAUDE.md` `README.md` (жовтень: 13 з 25 комітів — без збірки) | — | налаштовано 03.10 (AirLens S12, Р-80) через Builds API; перевірено — коміт лише з `docs/` збірки не дав; детектор «прод ≡ репо» в `env_check` ✓; тривога власнику про запити **акаунта** з півночі UTC — Р-79 |
| ~~`airlens`~~ | ~~Pages (`airlens-8bd.pages.dev`)~~ | AirLens | — | — | **видалено 03.10** (AirLens S11, Р-78): перевірено — доменів нема, 404, посилань у репо нема; 131 деплой + проєкт через API; бот і Mini App живі (воркер) |
| `qr-lens` · `drive-lens-preview` | Pages | QR-Lens · Drive-Lens-preview | `*` | усі гілки | ⚠ заводські — правило 1–2 у їхній сесії |
| `lens-gh` | воркер | lens-governance | — | — | — |

## 4. Як репо підключається (раз)

У `tools/env_check.sh` репо — рядок (див. `tools/claude-code/templates/env_check_template.sh`):
```bash
if cfb=$(curl -sSf -m 20 https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/tools/cloudflare/cf_budget.sh 2>/dev/null); then
  printf '%s\n' "$cfb" | bash; else echo "cloudflare: — (cf_budget не завантажено)"; fi
```
⚠ Не `curl … | bash || echo …`: на 404 `bash` отримує порожній вхід і виходить з 0 — збій мовчить.
і абзац у `CLAUDE.md` репо (зразок — `tools/claude-code/templates/CLAUDE_template.md`): рядки `cloudflare:` і `⚠` в `env_check` —
читати, тривога — першою в звіті; зміна налаштувань Cloudflare — прод-крок, лише після «так» Konst. Потрібні змінні середовища `CLOUDFLARE_API_TOKEN` (права на читання: Pages,
Workers, Account Analytics) і `CLOUDFLARE_ACCOUNT_ID`. Скрипт лише читає, токен не друкує; береться з `main` ядра свідомо — щоб
актуалізація (§5) доїжджала до всіх репо без правок у них. Ціна: довіра до `main` ядра (той самий власник).

## 5. Актуалізація — щоб цей файл не протух (замкнений цикл)

**Коли.** (а) `cf_budget.sh` друкує «перевірено N дн. тому» при N > 30; (б) реальність суперечить числу тут (помилка 1027, збірка не
пішла, ліміт у дашборді інший); (в) Cloudflare змінив план чи назву налаштування.
**Звірку агент робить сам, без запиту Konst, окремим ходом у будь-якому репо, де помітив; ПРАВКУ — пропонує й застосовує після
«так» Konst** (це файл правил ядра: зміна тексту §2 — ще й подвійний аудит, `CLAUDE.md` ядра «Аудит правил» · `tools/claude-code/audit_prompts.sh`; зміна лише чисел, дат, реєстру чи
журналу — дані, без аудиту):
1. Відкрити джерела з колонки «джерело» (developers.cloudflare.com: `workers/platform/limits` · `workers/platform/pricing` ·
   `pages/platform/limits` · `pages/configuration/build-watch-paths` · `pages/configuration/branch-build-controls` ·
   `workers/ci-cd/builds/limits-and-pricing`) — і пошук «Cloudflare Workers free plan limits <рік>» на випадок переїзду сторінок.
2. Звірити кожне число й назву налаштування; змінене — поправити в таблиці **і** в блоці `cf-limits`, дату джерела — сьогоднішня.
3. Оновити «Перевірено:» у шапці; рядок у журнал нижче (навіть «змін нема» — це теж результат).
4. Новий урок із роботи репо (щось зламалось / зекономилось) — у §2 правилом або в реєстр §3, з репо й датою.
5. Після «так» — коміт у `lens-governance` `main`; у сесії, яка не має ядра, — дифф Konst у чат для governance-сесії.

| дата | хто (репо, сесія) | що звірено | що змінилось |
|---|---|---|---|
| 2026-10-03 | AirLens S12 | developers.cloudflare.com/workers/ci-cd/builds/build-watch-paths (29.05.2026) · …/builds/api-reference (22.09.2026); Builds API: тригер і список збірок воркера airlens | §2 п.1: для воркера — виключення, а не перелік тек (перелік мовчки пропускає `../data`, `[assets]`); watch paths airlens поставлено через API (`PATCH builds/triggers`), коміт лише з `docs/` — без збірки (до фільтра — збірка за ~3 с); шляхи фільтра — від кореня репо при корені збірки `/worker` |
| 2026-10-03 | AirLens S11 | API акаунта: запити по днях 26.09–03.10 за скриптами; проєкт Pages airlens (домени, деплої); developers.cloudflare.com/workers/ci-cd/builds/api-reference (22.09.2026) · …/configuration (API token) | заміряно: ≤ 2 027 запитів/добу, бот 97 %; Pages airlens видалено (131 деплой + проєкт, `DELETE …?force=true` без збоїв); Builds API — лише токен користувача (права: Workers Builds Configuration Edit + Workers Scripts Read); build token Workers Builds — окремий, автостворений, не чіпати |
| 2026-10-03 | AE-Simulator S89 | developers.cloudflare.com/pages/platform/known-issues (06.05.2026) | проєкт Pages із >100 деплоями дашборд не видаляє: спершу деплої (`wrangler pages deployment delete <id> --project-name <p> --force` у циклі, скрипт на тій сторінці; або API `DELETE …/pages/projects/<p>/deployments/<id>?force=true`), активний продакшн-деплой лишається — потім видалити проєкт |
| 2026-10-03 | AE-Simulator S89 | усі джерела §1; API акаунта: проєкти, збірки за 30 днів, запити за 7 днів | файл створено; заміряно: запити ≤ 2 000/добу (~2 %), збірки Pages ~305 за 30 днів (AE ~173, AirLens-Pages 132) |
