#!/usr/bin/env python3
"""Builds data.json: the Azahar compatibility list with the games tested on Azurii on top.

Usage: python3 build.py path/to/azahar/compatibility_list.json [3dsdb list_XX.json ...]
(sources: https://github.com/azahar-emu/compatibility-list
          https://github.com/hax0kartik/3dsdb/tree/master/jsons)

The Azahar list often names a game only by the title ID of one region (usually the American
one). With the 3dsdb title lists, the other regions of the same game are added: they share the
three characters of the product code after "CTR-N-" (AG5E, AG5P, AG5J: Paper Mario Sticker Star).
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

here = Path(__file__).resolve().parent
azahar = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
tests = {t["id"].upper(): t for t in json.loads((here / "azurii-tests.json").read_text(encoding="utf-8"))["tests"]}

# Product code family (e.g. "AG5") of each application title ID, and the IDs of each family.
family_of, members = {}, defaultdict(set)
for path in sys.argv[2:]:
    for item in json.loads(Path(path).read_text(encoding="utf-8")):
        tid = str(item.get("TitleID", "")).upper()
        code = str(item.get("Product Code", ""))
        parts = code.split("-")
        if not tid.startswith("00040000") or len(parts) != 3 or len(parts[2]) != 4:
            continue
        family = parts[0] + "-" + parts[2][:3]
        family_of[tid] = family
        members[family].add(tid)

listed = {r["id"].upper() for e in azahar for r in e.get("releases", [])}

def siblings(entry):
    ids = {r["id"].upper() for r in entry.get("releases", [])}
    extra = set()
    for tid in ids:
        if tid in family_of:
            extra |= members[family_of[tid]]
    return extra - ids - listed

# Other regions of the same game, unless the list already names them, and never an ID that two
# entries would claim (two games of the same product code family: better no rating than a wrong one).
claims = defaultdict(int)
for entry in azahar:
    for tid in siblings(entry):
        claims[tid] += 1

games, used, added = [], set(), 0
for entry in azahar:
    ids = [r["id"].upper() for r in entry.get("releases", [])]
    extra = sorted(t for t in siblings(entry) if claims[t] == 1)
    added += len(extra)
    ids += extra
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
print(f"{len(games)} games, {len(used)} tested on Azurii, {added} title IDs of other regions added")
