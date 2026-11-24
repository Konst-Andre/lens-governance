# Lens — самері сесії ядра «Пакет аудиту — закрити борг» · 23.11.2026

живе доки: борг аудиту ядра закрито й рядок у `kernel/Lens_AUDIT.md` записано — тоді в archive/summaries/Lens_gov/.
дім: lens-governance/sessions/Lens_gov/ · сесія: 23.11.2026 · Claude Code (хмара), **основний акаунт**, лише ядро · слово Konst: «закрити аудити, поки не скінчиться тижневий ліміт» (тиждень на старті 96 %, overage вимкнено).

## §0 · ВІДКРИТЕ

**0.1 · ДЛЯ ПАРАЛЕЛЬНОЇ СЕСІЇ (EquipLens, резервний акаунт) — прочитай.** Ядро зараз паралельно веде ЦЯ сесія за запитом Konst: пакет аудиту боргу (коміти в інструкціях після `6b2d03f`). Поле цієї сесії: `kernel/Lens_AUDIT.md` (новий рядок зверху) і правки **за аудитом** у файлах пакета — `CLAUDE.md` ядра · `tools/claude-code/CLAUDE_CODE.md` · `tools/PREVIEW.md` · `tools/claude-code/SHOTS.md` · `tools/claude-code/ADOPT.md` · `tools/claude-code/ACCOUNT_MOVE.md` · `tools/cloudflare/CLOUDFLARE.md` · `kernel/wsd/Lens_patch_check_protocol.md` · `kernel/Lens_stagebench_manifest.md` · `tools/claude-code/templates/env_check_template.sh` · `tools/claude-code/templates/SUMMARY_template.md` · `tools/claude-code/templates/CLAUDE_template.md` · `tools/claude-code/templates/BRIEF_template.md`. Проси: перед правкою цих файлів — `git pull`, правка малими комітами, ніколи force; рядок у `kernel/Lens_AUDIT.md` не пиши — його веде ця сесія. Аудит (`claude -p`) у тебе не запускати — він іде тут, на ліміті основного акаунта.

**0.2 · Пакет аудиту — хвиля 1 (23.11) готова, хвиля 2 (24.11) іде.** Хвиля 1: `CLAUDE.md` ядра opus+sonnet ($2,89; спільне — речення агентові в HTML-коментарі `CLAUDE.md:3-4`, зрізається; sonnet — `motion_lint` названо, приладу нема) · `tools/claude-code/templates/SUMMARY_template.md` (5 знахідок, $1,14) · `tools/claude-code/templates/CLAUDE_template.md` (3, $1,45) · `tools/claude-code/templates/BRIEF_template.md` (8, $1,53) · `tools/claude-code/templates/env_check_template.sh` (9, $1,37). `tools/PREVIEW.md` — порожній (тиждень 100 % 23.11 00:15 UTC), повтор у хвилі 2. Хвиля 2 (ліміти відновились): `PREVIEW` · `ADOPT` · `ACCOUNT_MOVE` · `SHOTS` · `CLOUDFLARE` · `patch_check` · `CLAUDE_CODE` · `stagebench`. Далі — синтез → вирок Konst → правки → рядок `kernel/Lens_AUDIT.md`. Попутно: старий борг `REV-5` (36 знахідок 19.11, рядок `kernel/Lens_AUDIT.md` AE S156) — у той самий синтез.

**0.3 · Посилання й маркер (запит Konst 24.11, скріни Routes).** SHA і `файл:рядок` у звітах — клікабельні permalink GitHub (на коміт, не на гілку; `.md` — з `?plain=1#L`), маркер — в інлайн-коді з кольором стану. План — у чаті 24.11, 💡 чекає вироку Konst. Аналог уже є в Routes (`Routes:tools/handoff_check.py` `--md`, коміт Routes 28e7051) — прочитати не вдалось (add_repo відхилено класифікатором).

**Від Konst:** вирок на знахідки пакета (буде тут).

## §1 · ХОДИ

| хід | коміт | що |
|---|---|---|
| 1 | `4abdc7e` | самері народжено; нотатка для паралельної сесії (§0.1); старт пакета аудиту |
| 2 | `d9be410` | H-C «двоє дверей» → `archive/summaries/Lens_gov/` (G10), `kernel/Lens_INDEX.md` §5 — нове самері; стартове повідомлення; повні шляхи в §0 |
| 2-б | `f18c2aa` | журнал гачків — вердикти сесії (handoff_check справжній) |
| 3 | `01ca6a8` | хвиля 1 аудиту — підсумок у §0.2; хвиля 2 запущена 24.11 |
| 4 | (цей) | запит Konst 24.11: посилання замість голих SHA / `файл:рядок` + маркер в інлайн-коді — план показано, чекає «так» (§0.3) |

## Стартове повідомлення (переїзд)

```text
Ядро lens-governance, гілка main. Сесія «пакет аудиту боргу» 23.11.2026: самері — sessions/Lens_gov/Lens_governance_session_summary_AUDIT_2311.md, §0 — що відкрито. Журнал аудиту — kernel/Lens_AUDIT.md (верхній рядок). Звіти аудиту були в скретчпаді попередньої сесії — якщо їх нема, синтез береться з рядка журналу.
```
