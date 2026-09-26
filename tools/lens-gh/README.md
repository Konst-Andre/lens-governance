# lens-gh — конектор «Lens GitHub»

> живе доки: конектор lens-gh працює АБО його замінено іншим шляхом запису з чату (тоді — в archive/).
> дім: `lens-governance/tools/lens-gh/` · протокол використання: `kernel/Lens_github_push_protocol.md`
> версія: 1.1.0 · 25.09.2026 · сесія LGH-1

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
| Підключення | claude.ai → Settings → Connectors → «Lens GitHub» |

## Змінні воркера

| Імʼя | Тип | Що |
|---|---|---|
| `GH_TOKEN` | секрет | fine-grained PAT GitHub (Contents: write; для `.github/workflows/*` — ще Workflows: write; для Actions — Actions: write) |
| `MCP_KEY` | секрет | випадковий ключ у шляху URL; хто не знає ключа — отримує 404 |
| `OWNER` | змінна | `Konst-Andre` — запис лише в репо цього власника |
| `PROTECT` | змінна, необовʼязкова | гілки через кому, куди запис заборонено; зараз не задана |

Значення секретів вносить лише Konst у дашборді Cloudflare (П-LGH1). У цей файл, самері, репо — ніколи.

## Інструменти (6)

| Інструмент | Що робить |
|---|---|
| `gh_read` | файл, можна діапазоном рядків `start_line`/`end_line` |
| `gh_list` | тека (один рівень) або все дерево (`recursive`) |
| `gh_log` | останні коміти гілки |
| `gh_commit` | один коміт з багатьох змін: `edits` (фрагмент `old` рівно 1 раз) · `content` · `content_base64` · `from`(+`move`) · `delete`; `dry_run`; `create_from` для нової гілки |
| `gh_branch` | `list` · `create` · `delete` (потрібен sha гілки) |
| `gh_actions` | `workflows` · `runs` · `jobs` · `log` · `dispatch` · `rerun` · `cancel` |

## Запобіжники в коді

- `expected_head` **обовʼязковий** для справжнього запису в наявну гілку; не збігся — коміт відхилено («гілка зрушила»).
- Лише репо власника `OWNER`; шляхи без `..` і `/` на початку.
- Без force-push: ref оновлюється з `force: false`.
- Гілку за замовчуванням (`main`) видалити неможливо ніколи.
- `edits`: фрагмент `old` має входити рівно 1 раз.
- Ліміт Workers Free: ≤ 50 зовнішніх запитів на виклик → ≲ 40 файлів на коміт.

## Деплой нової версії

1. Правка `worker.js` тут → локальний смоук на підробленому GitHub.
2. `PUT https://api.cloudflare.com/client/v4/accounts/<acc>/workers/scripts/lens-gh` (multipart):
   `metadata = {"main_module":"worker.js","compatibility_date":"2026-09-01","keep_bindings":["secret_text","plain_text"]}` + файл `worker.js`.
   `keep_bindings` зберігає секрети й змінні — без нього вони зникнуть.
3. Перевірка: `GET https://lens-gh.konstandre.workers.dev/` → `lens-gh <версія>`.
4. Нові/змінені інструменти видно в чаті лише після перепідключення конектора.
5. ⚠ Файл `wrangler.jsonc` для цього воркера не заводимо: його `vars` перезаписують змінні з дашборду.

Відкат: задеплоїти попередню версію `worker.js` з історії цього файлу тим самим запитом.

## Ротація `MCP_KEY`

1. Новий ключ — випадковий рядок ≥ 32 символи (напр. менеджер паролів, «лише літери й цифри»).
2. Cloudflare → Workers → `lens-gh` → Settings → Variables and Secrets → `MCP_KEY` → Edit → вставити → Deploy.
3. claude.ai → Settings → Connectors → «Lens GitHub» → видалити й додати заново з URL `https://lens-gh.konstandre.workers.dev/mcp/<новий ключ>`.
4. Старий URL одразу дає 404. Робити між чатами.

## Історія

- 1.0.0 · 25.09.2026 (LGH-0) — read · list · log · commit; `PROTECT=main`.
- 1.1.0 · 25.09.2026 (LGH-1) — `expected_head` обовʼязковий · `gh_branch` · `gh_actions`; `PROTECT` знято.
