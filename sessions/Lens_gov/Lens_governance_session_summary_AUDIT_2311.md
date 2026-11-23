# Lens — самері сесії ядра «Пакет аудиту — закрити борг» · 23.11.2026

живе доки: борг аудиту ядра закрито й рядок у `kernel/Lens_AUDIT.md` записано — тоді в archive/summaries/Lens_gov/.
дім: lens-governance/sessions/Lens_gov/ · сесія: 23.11.2026 · Claude Code (хмара), **основний акаунт**, лише ядро · слово Konst: «закрити аудити, поки не скінчиться тижневий ліміт» (тиждень на старті 96 %, overage вимкнено).

## §0 · ВІДКРИТЕ

**0.1 · ДЛЯ ПАРАЛЕЛЬНОЇ СЕСІЇ (EquipLens, резервний акаунт) — прочитай.** Ядро зараз паралельно веде ЦЯ сесія за запитом Konst: пакет аудиту боргу (коміти в інструкціях після `6b2d03f`). Поле цієї сесії: `kernel/Lens_AUDIT.md` (новий рядок зверху) і правки **за аудитом** у файлах пакета — `CLAUDE.md` ядра · `tools/claude-code/CLAUDE_CODE.md` · `tools/PREVIEW.md` · `tools/claude-code/SHOTS.md` · `tools/claude-code/ADOPT.md` · `tools/claude-code/ACCOUNT_MOVE.md` · `tools/cloudflare/CLOUDFLARE.md` · `kernel/wsd/Lens_patch_check_protocol.md` · `kernel/Lens_stagebench_manifest.md` · `tools/claude-code/templates/env_check_template.sh` · `tools/claude-code/templates/SUMMARY_template.md` · `tools/claude-code/templates/CLAUDE_template.md` · `tools/claude-code/templates/BRIEF_template.md`. Проси: перед правкою цих файлів — `git pull`, правка малими комітами, ніколи force; рядок у `kernel/Lens_AUDIT.md` не пиши — його веде ця сесія. Аудит (`claude -p`) у тебе не запускати — він іде тут, на ліміті основного акаунта.

**0.2 · Пакет аудиту** — у роботі. Клас 2: `CLAUDE.md` ядра (opus high + sonnet high). Клас 1 (opus high): решта файлів 0.1, малі першими, великі (CLAUDE_CODE · stagebench · patch_check) — наостанок. Звіти — скретчпад сесії (не в репо, ядро публічне). Застосування знахідок — лише після «так» Konst.

**Від Konst:** вирок на знахідки пакета (буде тут).

## §1 · ХОДИ

| хід | коміт | що |
|---|---|---|
| 1 | `4abdc7e` | самері народжено; нотатка для паралельної сесії (§0.1); старт пакета аудиту |
| 2 | (цей) | H-C «двоє дверей» → `archive/summaries/Lens_gov/` (G10), `kernel/Lens_INDEX.md` §5 — нове самері; стартове повідомлення; повні шляхи в §0 |

## Стартове повідомлення (переїзд)

```text
Ядро lens-governance, гілка main. Сесія «пакет аудиту боргу» 23.11.2026: самері — sessions/Lens_gov/Lens_governance_session_summary_AUDIT_2311.md, §0 — що відкрито. Журнал аудиту — kernel/Lens_AUDIT.md (верхній рядок). Звіти аудиту були в скретчпаді попередньої сесії — якщо їх нема, синтез береться з рядка журналу.
```
