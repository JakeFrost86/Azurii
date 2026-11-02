#!/usr/bin/env python3
"""Builds data.json: the Azahar compatibility list with the games tested on Azurii on top.

Usage: python3 build.py path/to/azahar/compatibility_list.json
(source: https://github.com/azahar-emu/compatibility-list)

The Azurii Compat app edits azurii-tests.json and rebuilds data.json by itself when it
publishes; this script does the same job by hand.
- a test with "title" (and optional "ids") is a game missing from the Azahar list;
- "hidden" lists the title IDs of Azahar games removed from the page.
"""
import json
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
azahar = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
src = json.loads((here / "azurii-tests.json").read_text(encoding="utf-8"))
tests = {t["id"].upper(): t for t in src["tests"]}
hidden = {i.upper() for i in src.get("hidden", [])}

games, used = [], set()
for entry in azahar:
    ids = [r["id"].upper() for r in entry.get("releases", [])]
    test = next((tests[i] for i in ids if i in tests), None)
    if test:
        used.add(test["id"].upper())
    if any(i in hidden for i in ids):
        continue
    game = {"t": entry["title"], "ids": ids, "a": entry["compatibility"]}
    if test:
        game.update(s=test["status"], v=test["version"], en=test["en"], it=test["it"])
    games.append(game)

for key, test in tests.items():
    if key in used or "title" not in test:
        continue
    used.add(key)
    ids = [i.upper() for i in (test.get("ids") or [test["id"]])]
    games.append({"t": test["title"], "ids": ids, "a": test["status"],
                  "s": test["status"], "v": test["version"], "en": test["en"], "it": test["it"]})

missing = set(tests) - used
if missing:
    sys.exit(f"Tested games not in the Azahar list (give them a \"title\"): {sorted(missing)}")

games.sort(key=lambda g: g["t"].casefold())
(here / "data.json").write_text(json.dumps({"games": games}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"{len(games)} games, {len(used)} tested on Azurii")
