# lens-gh — конектор «Lens GitHub»

> живе доки: конектор lens-gh працює АБО його замінено іншим шляхом запису з чату (тоді — в archive/).
> дім: `lens-governance/tools/lens-gh/` · протокол використання: `kernel/Lens_github_push_protocol.md`
> версія: 1.2.0 · 27.09.2026 · сесія LGH-2

## Що це

Власний MCP-сервер на Cloudflare Workers, що дає чату Claude запис у GitHub-репо `Konst-Andre/*`.
Навіщо: з 16.09.2026 чат працює в контейнері з git-проксі, який пускає запис лише в репо,
підключені до сесії, а в чаті їх підключити нічим. Конектор викликається з боку Anthropic, а токен
GitHub живе в секреті воркера, тож у тексті чату й інструкції Project він не потрібен.

## Де живе

| Що | Де |
|---|---|
| Воркер | Cloudflare, акаунт Konst, скрипт `lens-gh` · `https://lens-gh.konstandre.workers.dev` |
| Точка MCP | `https://lens-gh.konstandre.workers.dev/mcp/<MCP_KEY>` (ключ — лише в налаштуваннях конектора) |
| Код | `tools/lens-gh/worker.js` у цьому репо (канон) ≡ живий воркер (звіряти md5) |
| Смоук | `tools/lens-gh/smoke.sh` (`local` · `live` · `docs`) + `smoke_local.mjs` (підроблений GitHub) — рецепти `CHAT_TOOLS.md` §2-б цитуються звідси |
| Доріжка нових версій | `https://next-lens-gh.konstandre.workers.dev` (aliased Version URL, ті самі секрети) · конектор «Lens GitHub next» |
| Підключення | claude.ai → Settings → Connectors → «Lens GitHub» |

## Змінні воркера

| Імʼя | Тип | Що |
|---|---|---|
| `GH_TOKEN` | секрет | fine-grained PAT GitHub (Contents: write; для `.github/workflows/*` — ще Workflows: write; для Actions — Actions: write) |
| `MCP_KEY` | секрет | випадковий ключ у шляху URL; хто не знає ключа — отримує 404 |
| `TICKET_KEY` | секрет | ≥ 32 символи; HMAC-підпис квитків `gh_ticket`. Окремий від `MCP_KEY`: витік квитка не дає доступу до MCP. Коротший — `gh_ticket` відмовляє |
| `OWNER` | змінна | `Konst-Andre` — запис лише в репо цього власника |
| `PROTECT` | змінна, необовʼязкова | гілки через кому, куди запис заборонено; зараз не задана |

Значення секретів вносить лише Konst у дашборді Cloudflare (П-LGH1). У цей файл, самері, репо — ніколи.

## Інструменти (7)

| Інструмент | Що робить |
|---|---|
| `gh_read` | файл, можна діапазоном рядків `start_line`/`end_line` |
| `gh_list` | тека (один рівень) або все дерево (`recursive`) |
| `gh_log` | останні коміти гілки |
| `gh_commit` | один коміт з багатьох змін: `edits` (фрагмент `old` рівно 1 раз) · `content` · `content_base64` · `blob` (sha з квитка `put`) · `from`(+`move`) · `delete`; `dry_run` (точний розмір); `create_from` для нової гілки |
| `gh_ticket` | квиток на 10 хв: `tar` · `get` · `put` → маршрут `/t/<квиток>` (опис і рецепти — `CHAT_TOOLS.md` §2-б) |
| `gh_branch` | `list` · `create` · `delete` (потрібен sha гілки) |
| `gh_actions` | `workflows` · `runs` · `jobs` · `log` · `dispatch` · `rerun` · `cancel` |

## Запобіжники в коді

- `expected_head` **обовʼязковий** для справжнього запису в наявну гілку; не збігся — коміт відхилено («гілка зрушила»).
- Лише репо власника `OWNER`; шляхи без `..` і `/` на початку.
- Без force-push: ref оновлюється з `force: false`.
- Гілку за замовчуванням (`main`) видалити неможливо ніколи.
- `edits`: фрагмент `old` має входити рівно 1 раз.
- Ліміт Workers Free: ≤ 50 зовнішніх запитів на виклик → ≲ 40 файлів на коміт.
- **Квиток** = `base64url(JSON{repo, op, ref, path, note, exp}).base64url(HMAC-SHA256)`. Одна функція `verifyTicket` для всіх маршрутів: підпис · `exp` (10 хв) · `op` ↔ метод (`put` = POST, `tar`/`get` = GET) · власник `OWNER`. Будь-яка помилка → 404 без пояснень; причина — у лог (`reject · sig|expired|method|repo|op|shape|no-key`).
- `ref` квитка закріплюється на sha коміту при видачі. `get` при видачі звіряє, що файл є, і називає його sha й розмір.
- Воркер нічого не кодує й не розпаковує (CPU 10 мс): `tar`/`get` — потік від GitHub; `put` — тіло без розбору в `git/blobs` (≤ 50 МБ, більше → 413).
- Лог: один рядок на використання квитка `lens-gh t · час · op · repo · path|sha · розмір · note` → Cloudflare Workers Logs (запити на `next` у логи не потрапляють; URL квитка Cloudflare показує як `REDACTED`).

## Деплой нової версії (з 1.2.0: через доріжку `next`, прод не чіпається до зеленого смоуку)

Потрібні: Cloudflare API-токен (Workers Scripts: Edit) і Account ID — від Konst на сесію; `npm i wrangler@4` у контейнері.

1. Правка `worker.js` → `bash smoke.sh local` зелений.
2. Завантажити версію **без деплою** на `next`:
   `wrangler versions upload worker.js --name lens-gh --compatibility-date 2026-09-01 --no-bundle --keep-vars --preview-alias next --tag v<версія>`
   `--no-bundle` — у Cloudflare іде рівно цей файл (md5 ≡ репо); `--keep-vars` — інакше wrangler видалить змінні з дашборду (`OWNER`). Секрети версія бере поточні.
3. `GET https://next-lens-gh.konstandre.workers.dev/` → нова версія; `GET https://lens-gh.konstandre.workers.dev/` → стара.
4. Konst вмикає конектор «Lens GitHub next» (перепідключає, якщо змінився список інструментів) → чат видає квитки через нього → `bash smoke.sh live` + пункти, які скрипт перелічує наприкінці.
5. Зелено → коміт `worker.js` (+ смоук) у репо → у прод **ту саму** версію через API (не `wrangler versions deploy`: він підставляє свою конфігурацію й може вимкнути Workers Logs):
   `POST /accounts/<acc>/workers/scripts/lens-gh/deployments` · `{"strategy":"percentage","versions":[{"version_id":"<id>","percentage":100}]}`.
6. Звірка: `GET /` прод → нова версія · md5 коду з `GET …/scripts/lens-gh/content/v2` ≡ md5 `worker.js` у репо · Workers Logs увімкнено (`…/settings` → `observability.logs.enabled`).
7. Konst перепідключає основний «Lens GitHub» (нові інструменти видно лише після цього); «next» — вимкнути до наступної версії.
8. ⚠ Файл `wrangler.jsonc` для цього воркера не заводимо: його `vars` перезаписують змінні з дашборду.

⚠ **Будь-яка зміна секрету чи змінної в дашборді (Deploy) створює нову версію з ОСТАННЬОЇ ЗАВАНТАЖЕНОЇ і ставить її в прод** — навіть якщо остання завантажена лише на `next` і ще не перевірена (LGH-2: так 1.2.0 потрапила в прод до живого смоуку). Тому: секрети міняти **до** кроку 2 або після кроку 5; якщо довелось між ними — одразу крок 6 і, якщо смоук ще не зелений, відкат.

Відкат: `POST …/deployments` з `version_id` попередньої версії (список — `GET …/scripts/lens-gh/versions`); або завантажити `worker.js` з історії цього файлу кроками 2 і 5.

## Ротація `MCP_KEY`

1. Новий ключ — випадковий рядок ≥ 32 символи (напр. менеджер паролів, «лише літери й цифри»).
2. Cloudflare → Workers → `lens-gh` → Settings → Variables and Secrets → `MCP_KEY` → Edit → вставити → Deploy.
3. claude.ai → Settings → Connectors → «Lens GitHub» → видалити й додати заново з URL `https://lens-gh.konstandre.workers.dev/mcp/<новий ключ>`.
4. Старий URL одразу дає 404. Робити між чатами.

## Історія

- 1.0.0 · 25.09.2026 (LGH-0) — read · list · log · commit; `PROTECT=main`.
- 1.1.0 · 25.09.2026 (LGH-1) — `expected_head` обовʼязковий · `gh_branch` · `gh_actions`; `PROTECT` знято.
- 1.2.0 · 27.09.2026 (LGH-2) — «квиток»: `gh_ticket` (tar · get · put) + маршрут `/t/` · `gh_commit {blob}` · точний розмір `content_base64` у `dry_run` · секрет `TICKET_KEY` · `smoke.sh`/`smoke_local.mjs` · деплой через доріжку `next`. ТЗ: `SPEC_v1.2.md`. Смоук §7: локально 38/38, живий 6/6. Прод = версія `cbe01d9e`.
