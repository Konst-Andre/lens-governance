#!/usr/bin/env python3
# G-C · група Б, поправка · 2.13: мертве посилання на S32_FONT (у репо й ARCHIVE_INDEX немає) → адреса без імені файлу
# живе доки: G-C закрито й запушено
import sys, hashlib
W = "kernel/wsd/Work_Standard.md"; w = open(W, encoding="utf-8").read()
OLD = "Повний контекст — `EquipLens_session_summary_S32_FONT.md` §2.)*"
NEW = "Повний контекст — самері EquipLens S32 §2; у репо не архівоване (лежить на ПК), тому ім'я файлу як адреса не дається, 12.15.)*"
md5 = lambda s: hashlib.md5(s.encode()).hexdigest()[:8]
if NEW in w and OLD not in w: print("no-op", md5(w)); sys.exit(0)
assert w.count(OLD) == 1 and NEW not in w, "якір — стоп"
w = w.replace(OLD, NEW); open(W, "w", encoding="utf-8").write(w); print("після", md5(w))
