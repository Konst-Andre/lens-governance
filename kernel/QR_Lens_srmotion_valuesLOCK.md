> живе доки: назавжди (вічне, wsd 1.8) — значення sr-motion QR Lens

# QR Lens — SR-motion values LOCK (device✓ Konst)

Джерело: harness `QR_Lens_srmotion_harness_v4.html` → device-арбітраж (12.9).
База для порту: `QR_Lens_preview_batch57_1.html` (batch57/rev1/phase4) → ціль B58.
Статус: **E1-каскад + E3a settle-glow ЗАЛОЧЕНО**. A/D + frame-gap — pending device.

---

## E1 каскад появи рядків (device✓)
```
off   140 ms
step   90 ms      // не 80 (хедер-дефолт був стале сміття; staggerRows+timing = 90)
dur   540 ms      // не 560
dist   26 px      // §3.2 діапазон 24-28
ease  spring  cubic-bezier(.34,1.56,.64,1)
```
`staggerRows(rows,{step:90,off:140,dur:540,dist:26,ease:'cubic-bezier(.34,1.56,.64,1)'})`

## E3a settle-glow (device✓) — механіка «glow + whisper-pop» (гібрид, НЕ чистий (d))
```
glowDur    760 ms   // <700 читається як flash/glitch (decel front-load); 760 = bloom встигає прочитатись навмисним
glowSize     8 px   // тісний halo, обіймає ring, не прожектор — character-consistent (тихий planning-tool)
glowInt     45 %    // opacity піку
glowScale  112 %    // whisper-pop: kinetic-відгук робить announce живим (стеля важеля; «гучніше» не треба)
```
**Тригер (ключове рішення):** `transitionend('transform')` саме `.sel`-рядка у стаггері
(self-sync зі slow-mo/ease, без re-mul) + safety-fallback `setTimeout(off+selIdx*step+dur+80)`.
→ glow бʼє КОЛИ обраний аватар приземлився (~950ms при selIdx3/step90/dur540), НЕ посеред каскаду.
**Матеріал:** base accent-ring НЕ чіпається; outer-glow — additive шар поверх (bloom→gone),
scale 1.12→1.0 на тому ж glowDur. `reduced-motion` → glow skip.
**Розвʼязана проблема:** E3a на E1-каскаді НЕ було видно (1-shot пульс проходив поки рядки ще їхали).

## Вибір A (harness-дефолт, НЕ device-lock)
```
aGrow 90 % · aRingDur 260 ms · aSettle 420 ms (settle→close, A18.1)
```

## Спільне (device✓)
```
openDur 240 ms (A18 slide) · press scale 92 % · press down 70 ms
```

---

## PENDING device (до повного lock перед B58-портом)
- [ ] **A vs D** — раніше «лишити обидва, розсудить device»; чекаю device-вердикт (character тихого tool → схил до D)
- [ ] **frame-gap** glow на N12 `Повна` — paint-вартість (glowSize8 малий blur → ризик низький, але зміряти)

## Канон-борг (після A58-арки, разом з B52→B57)
- Precept: **ring-after-cascade** — announce-glow привʼязувати до `transitionend` .sel-рядка, НЕ до фіксованого offset (інакше 1-shot тоне в каскаді)
- Precept: **glow+whisper-pop** гібрид — коли announce секвенсовано ПІСЛЯ руху, малий scale не шум, а пунктуація
- Precept: E1 **spring/dist26** каскад як дефолт SR-selector
- Cookbook A71-extension: settle-glow як announce-патерн (base-ring preserved, additive outer-glow)
