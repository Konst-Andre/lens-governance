---
# живе доки: діє tools/claude-code/NIGHT_SHIFT.md; ставить у ~/.claude/skills/ диспетчер ядра (hooks/lens-hooks.sh, SessionStart)
name: night
description: Нічна зміна Konst — агент працює сам за планом самері §0, поки Konst спить. Викликає лише Konst командою /night (або словом «нічна зміна»); модель сама не вмикає.
disable-model-invocation: true
---
Konst увімкнув **нічну зміну** командою `/night`. Аргументи (план, пороги, «до ранку», «з аудитом»): $ARGUMENTS

1. Прочитай `lens-governance:tools/claude-code/NIGHT_SHIFT.md` цілком — це правило зміни (що можна, чого ніколи, пороги, ранковий звіт).
2. Заміряй: `get_session` (контекст, `autocompact_state`) і `list_events` з `kinds: ["rate_limit_event"]` (5 год і тиждень, скид — у київському часі).
3. Одним повідомленням підтверди: план (з аргументів або самері §0), пороги, чого **не** робитимеш, коли зупинишся. Далі працюй, не чекаючи відповіді.
