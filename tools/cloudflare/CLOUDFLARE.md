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
`workers_builds_minutes_month` — довідково: скрипт хвилин поки не міряє — Builds API працює (журнал 03.10, QR 06.10), але чи віддає він тривалість збірок — не перевірено; решту читає.

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

9. **Новий сайт — воркер з `[assets]`, не Pages; наявні Pages — переїзд** (`CF-1`). `*.pages.dev` не відкривається в мобільних мережах Київстар
   і Vodafone, `*.workers.dev` — відкривається (вирок пристрою Konst 05–06.10.2026; публічного джерела нема). Воркер без коду віддає лише
   теку сайту: `wrangler.toml` → `[assets] directory = "./docs"` (тека за правилом 3) і `not_found_handling = "single-page-application"` —
   як Pages без `404.html` (старі ярлики PWA лишаються робочими). Зразок — `QR-Lens:wrangler.toml`.
10. **Воркер під'єднаний до гіта (Workers Builds) з першого дня.** Ручний `wrangler deploy` з сесії — лише перший раз: інакше файл,
   завантажений з телефона (GitHub web), до сайту не доходить (QR 06.10). Фільтр — правило 1 (include `*`, exclude документів).
   Під'єднати може й сесія через API: `builds/repos/connections` → `builds/triggers` (06.10, QR-Lens) — токеном з правом Workers Builds
   Configuration Edit (токен середовища сесії ядра його має, перевірено 06.10), не токеном лише на читання з §4. Перевірка — два коміти: лише
   документ → нового запису в `builds/workers/<tag>/builds` нема; конфіг або сайт → збірка `success`, md5 сайту ≡ репо.
11. **Після переїзду проєкт Pages видаляється.** Старі деплої живуть вічно за `<hash>.<проєкт>.pages.dev` і віддають прибрані файли;
   кеш краю тримає голу адресу до 7 днів (`s-maxage=604800`, QR 06.10). Порядок: на час переходу людей тека виводу Pages = тека сайту
   (інакше Pages збирає корінь і віддає 404) → люди перейшли → видалити (правило 5: «так» Konst).
12. **Порада, не правило — свій домен** (Konst 06.10): коли всі сайти на воркерах — домен на акаунт (`qr.<домен>` як Custom Domain
   воркера): блок оператора на `workers.dev` не вб'є сайти, адреса людська й стала. Ціна ≈ $10/рік + DNS разово; ризик — не продовжити домен.

13. **Довідка, не правило — preview-адреса воркера («флажок» в адресі; Konst 07.10).** Нова версія воркера має свою адресу поруч із продом:
   `<префікс версії або аліас>-<воркер>.<субдомен>.workers.dev` — прод при цьому не змінюється. Аліас: `wrangler versions upload --preview-alias <ім'я>`;
   Workers Builds для не-продакшн гілки сам дає аліас з імені гілки (developers.cloudflare.com/workers/versions-and-deployments/preview-urls, перевірено 07.10.2026).
   Коли згодиться: показати зміну сайту на телефоні з реальними даними, не публікуючи їх у sandbox. Адреса публічна для того, хто її знає;
   увімкнення гілкових збірок чи завантаження версії — налаштування Cloudflare, лише з «так» Konst. **Перевірено наживо 08.10.2026 (QR-Lens CC-2):** `npx wrangler@4 versions upload --preview-alias zvit` з тимчасової копії `docs/` + `wrangler.toml` → `https://zvit-<воркер>.<субдомен>.workers.dev`, прод ≡ (md5 головної не змінився), повторне завантаження з тим самим аліасом переписує його за ~10 с; статика `[assets]` переадресовує `/x.html` → `/x` (307) — посилання давати без `.html`. Увімкненість preview на воркері — API `workers/scripts/<воркер>/subdomain` → `previews_enabled`. Тригер — `tools/PREVIEW.md` §3 п.8 (прев'ю з реальними даними). **Бюджет:** це не збірки Pages (500/міс, §1) — гілкова збірка воркера їсть хвилини Workers Builds (3000/міс, §1; збірка QR ≈ 1 хв), а `wrangler versions upload` з сесії чи Action — збірок не їсть зовсім (Konst 07.10 перепитав саме це).
    *Read-back прев'ю (QR-Lens CC-3, 08.10.2026):* одразу після `versions upload` адреса-аліас якийсь час віддає **попередню** версію (4 з 5 сторінок ≠, за хвилину — усі ≡). Звіряти з адресою версії `<id8>-<воркер>…` (вона незмінна) або повторити з `?r=<випадкове>` — не робити висновку з першого читання аліаса.
    *Не публікувати файл з теки сайту (QR-Lens CC-4, 08.10.2026):* `.assetsignore` у корені `[assets] directory` (формат `.gitignore`; developers.cloudflare.com/workers/static-assets/binding «Ignoring assets»): wrangler не вантажить збіги — перевірено наживо з зубами на версії-прев'ю (фіктивний `zvit.html`: з файлом 0, без — 1; сам `.assetsignore` теж не віддається). Зразок — `QR-Lens:docs/.assetsignore` (звіт воріт у `docs/`, на проді не видно). **Перевірка «не видно» — лише `curl -L`:** через редирект 307 `/x.html` → `/x` перший тест без `-L` дав 0 і без захисту (сліпий детектор). **Гілкові збірки (доки 10.2026):** команда прев'ю Workers Builds за замовчуванням тепер `npx wrangler preview` (Worker Previews, свій Preview URL), а не `versions upload` (developers.cloudflare.com/workers/ci-cd/builds/configuration «Preview command») — перед увімкненням звірити адресу наживо.
    *Прев'ю з реальними даними — лише за Cloudflare Access (QR-Lens CC-4, 08.10.2026):* Workers → воркер → Settings → Domains & Routes → Access: Scope **Previews only**, політика **Cloudflare account** (не «Email domain»: для `gmail.com` пустить будь-кого з Gmail); вхід пам'ятається до **7 дн.** (максимум дашборду; за замовчуванням 24 год). Політика одна на всі прев'ю акаунта. Перевірка — **поведінкою**: прев'ю → 302 на `*.cloudflareaccess.com`, прод → 200 (у дашборді біля прод-адреси теж показується замок — це не вхід на проді). **Перемикач `workers.dev` не чіпати:** вимкнений → прод 404 (Cloudflare 1042); увімкнути — API `POST workers/scripts/<воркер>/subdomain {"enabled":true,"previews_enabled":true}` або дашборд. Токен сесії Access-застосунків не бачить (`access/apps` → 0).
    *Вхід Access у застосунку з «Додому» на iOS (QR-Lens CC-4, 09.10.2026 — попередньо, тест «Revoke session» чекає Konst):* воркер `qr-admin` цілком за Access («All traffic», та сама політика, що прев'ю) + маніфест (`display: standalone`, `<link rel=manifest crossorigin="use-credentials">` — інакше маніфест без cookie, Access його не пустить) → додано на «Додому» зі сторінки адмінки (не зі сторінки входу) → **застосунок відкрився без рядка адреси, звіт є** (сесія вже була — вхід у Safari для прев'ю). Відкрите: чи завершиться новий вхід усередині застосунку (iOS тримає дані «Додому» окремо від Safari; запасний — passkey у воркері). Шапка під годинником у standalone — мета `apple-mobile-web-app-status-bar-style: black-translucent` (кукбук A1/A10).
    *Тригер прев'ю Workers Builds через API (QR-Lens CC-4, 08.10.2026):* приймається лише форма **`branch_includes ["*"]` + `branch_excludes ["<продакшн-гілка>"]`** (на одну гілку — 12042 «A trigger already exists for this configuration»; додаткові виключення чи складна команда з `if`/`$` — 12002 «Invalid request body»). Фільтр гілки — у скрипті команди за `WORKERS_CI_BRANCH` (зразок — `QR-Lens:tools/qr_preview.sh`: лише `qr-data` → `versions upload --preview-alias qr-data`, інші гілки — нічого). Воркер, підключений до Builds до Worker Previews, лишається на старій моделі (`versions upload`), доки не зроблено незворотний перехід.
14. **Workers Builds — стан збірки і тест перед деплоєм (QR-Lens CC-5, 09.10.2026, перевірено наживо).** (а) Кожна збірка пише в GitHub **перевірку (check run) `Workers Builds: <воркер>`** на коміт (застосунок `cloudflare-workers-and-pages`; `completed` + `success`/`failure`) — це джерело правди «сайт зібрався» для сторінки чи гейта: `GET /repos/<репо>/commits/<sha>/check-runs?check_name=…` (токен GitHub уже є; токена Cloudflare в сторінці не треба). Заміряно: злиття → success за 37 с. Комбінований `/status` при цьому `pending` без записів — дивитись саме check-runs. (б) **Тест перед деплоєм** — `build_command` тригера (напр. `node smoke.mjs`; червоний → деплою нема): API `PATCH /accounts/<id>/builds/triggers/<trigger_uuid>` `{"build_command": …}`, read-back `GET …/builds/workers/<script_tag>/triggers`. Це налаштування Cloudflare — лише з «так» Konst.

## 3. Реєстр проєктів акаунта (оновлює агент, коли бачить зміну; джерело — API)

| проєкт | тип | репо | що будить збірку | прев'ю | стан |
|---|---|---|---|---|---|
| `ae-simulator` | Pages (`site/`) | AE-Simulator | `site/*` | `claude/*` | налаштовано S89 (03.10) |
| `ae-edit` · `ae-proxy` | воркери | AE-Simulator (`ae-proxy` — лише дашборд) | CI GitHub (`deploy-edit.yml`) | — | — |
| `airlens` | воркер + `[assets]` (бот і Mini App: `airlens.konstandre.workers.dev`) | AirLens | Workers Builds: include `*`, exclude `docs/*` `tools/*` `.claude/*` `CLAUDE.md` `README.md` (жовтень: 13 з 25 комітів — без збірки) | — | налаштовано 03.10 (AirLens S12, Р-80) через Builds API; перевірено — коміт лише з `docs/` збірки не дав; детектор «прод ≡ репо» в `env_check` ✓; тривога власнику про запити **акаунта** з півночі UTC — Р-79 |
| ~~`airlens`~~ | ~~Pages (`airlens-8bd.pages.dev`)~~ | AirLens | — | — | **видалено 03.10** (AirLens S11, Р-78): перевірено — доменів нема, 404, посилань у репо нема; 131 деплой + проєкт через API; бот і Mini App живі (воркер) |
| `qr-lens` | **воркер** `[assets]`=`docs/` (`qr-lens.konstandre.workers.dev`) + Pages (тека `docs`, на час переходу людей) | QR-Lens | воркер: Workers Builds `main`, include `*`, exclude `lens/*` `archive/*` `sessions/*` `tools/*` `.claude/*` `CLAUDE.md` `README.md` (06.10, перевірено двома комітами) | Pages: усі гілки | ⚠ Pages: старі деплої віддають список PSR — видалити, коли люди перейдуть (`QR-Lens` `QRL-1`) |
| ~~`drive-lens-preview`~~ | Pages | Drive-Lens-preview | — | — | видалено Konst 05.10 (репо поки лишається) |
| `lens-gh` | воркер | lens-governance (`tools/lens-gh/`) | — (деплой руками) | — | сервер конектора «Lens GitHub» для Project — **живий, не сирітка** (Project працює: Routes та ін., Konst 06.10) |

## 4. Як репо підключається (раз)

У `tools/env_check.sh` репо — рядок (див. `tools/claude-code/templates/env_check_template.sh`):
```bash
if cfb=$(curl -sSf -m 20 https://raw.githubusercontent.com/Konst-Andre/lens-governance/main/tools/cloudflare/cf_budget.sh 2>/dev/null); then
  printf '%s\n' "$cfb" | bash; else echo "cloudflare: — (cf_budget не завантажено)"; fi
```
⚠ Не `curl … | bash || echo …`: на 404 `bash` отримує порожній вхід і виходить з 0 — збій мовчить.
і абзац у `CLAUDE.md` репо (зразок — `tools/claude-code/templates/CLAUDE_template.md`): рядки `cloudflare:` і `⚠` в `env_check` —
читати, тривога — у звіті одразу після «що ти побачиш»; зміна налаштувань Cloudflare — прод-крок, лише після «так» Konst. Потрібні змінні середовища `CLOUDFLARE_API_TOKEN` (права на читання: Pages,
Workers, Account Analytics) і `CLOUDFLARE_ACCOUNT_ID`. Скрипт лише читає, токен не друкує; береться з `main` ядра свідомо — щоб
актуалізація (§5) доїжджала до всіх репо без правок у них. Ціна: довіра до `main` ядра (той самий власник).

## 5. Актуалізація — щоб цей файл не протух (замкнений цикл)

**Коли.** (а) `cf_budget.sh` друкує «перевірено N дн. тому» при N > 30; (б) реальність суперечить числу тут (помилка 1027, збірка не
пішла, ліміт у дашборді інший); (в) Cloudflare змінив план чи назву налаштування.
**Звірку агент робить сам, без запиту Konst, окремим ходом у будь-якому репо, де помітив; ПРАВКУ — пропонує й застосовує після
«так» Konst** (це файл правил ядра: зміна тексту §2 — ще й аудит класу 1, `CLAUDE.md` ядра «Аудит правил» · `tools/claude-code/audit_prompts.sh`; зміна лише чисел, дат, реєстру чи
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
