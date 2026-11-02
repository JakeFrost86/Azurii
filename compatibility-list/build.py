#!/usr/bin/env python3
"""Builds data.json: the Azahar compatibility list with the games tested on Azurii on top.

Usage: python3 build.py path/to/azahar/compatibility_list.json
(source: https://github.com/azahar-emu/compatibility-list)
"""
import json
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
azahar = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
tests = {t["id"].upper(): t for t in json.loads((here / "azurii-tests.json").read_text(encoding="utf-8"))["tests"]}

games, used = [], set()
for entry in azahar:
    ids = [r["id"].upper() for r in entry.get("releases", [])]
    test = next((tests[i] for i in ids if i in tests), None)
    game = {"t": entry["title"], "ids": ids, "a": entry["compatibility"]}
    if test:
        used.add(test["id"].upper())
        game.update(s=test["status"], v=test["version"], en=test["en"], it=test["it"])
    games.append(game)

missing = set(tests) - used
if missing:
    sys.exit(f"Tested games not in the Azahar list: {sorted(missing)}")

games.sort(key=lambda g: g["t"].casefold())
(here / "data.json").write_text(json.dumps({"games": games}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"{len(games)} games, {len(used)} tested on Azurii")
