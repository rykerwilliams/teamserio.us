#!/usr/bin/env python3
"""Pull the Vintage B&R history out of the type1 repo into _data/.

The authoritative data lives in https://github.com/rykerwilliams/type1, where
each B&R announcement is one backdated commit. This copies what the page needs
into _data/vintage_br.json so the site builds with no network dependency and a
data change arrives as a reviewable diff.

    python3 script/sync-vintage-br.py /path/to/type1

Re-run it when the B&R list changes (a few times a year) and commit the result.
"""
import io, json, os, sys

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "_data", "vintage_br.json")


def main(repo):
    doc = json.load(io.open(os.path.join(repo, "events.json")))
    events, sources = doc["events"], doc["sources"]
    current = json.load(io.open(os.path.join(repo, "current.json")))
    # the era chart: not every change to the format is a B&R action, and the
    # errata and rules changes explain why some of the B&R ones happened
    try:
        eradoc = json.load(io.open(os.path.join(repo, "eras.json")))
    except FileNotFoundError:
        eradoc = {"eras": [], "change_kinds": {}}

    # Card detail, keyed by name, gathered from every snapshot so that cards
    # which were unrestricted along the way are still described.
    cards = {}
    adir = os.path.join(repo, "archive")
    for fn in sorted(os.listdir(adir)):
        if not fn.endswith(".json"):
            continue
        st = json.load(io.open(os.path.join(adir, fn)))
        for c in st["restricted"] + st.get("banned_cards", []):
            if c["name"] not in cards:
                op = c.get("original_printing") or {}
                cards[c["name"]] = {
                    "type_line": c.get("type_line"),
                    "mana_cost": c.get("mana_cost"),
                    "set": op.get("set"),
                    "set_name": op.get("set_name"),
                    "released_at": op.get("released_at"),
                    "rarity": op.get("rarity"),
                    "scryfall_uri": op.get("scryfall_uri"),
                    # carried so the page can show art without a Scryfall
                    # request per card
                    "image": op.get("image"),
                    "total_paper_printings": c.get("total_paper_printings"),
                }

    # Trim events to what the page renders: the replay plus provenance.
    slim = []
    for e in events:
        acts = []
        for a in e["actions"]:
            act = {"card": a["card"], "action": a["action"],
                   "from": a.get("resolved_from")}
            if a.get("note"):
                act["note"] = a["note"]
            acts.append(act)
        slim.append({
            "seq": e["seq"], "date": e["date"],
            "precision": e["date_precision"],
            "effective": e.get("effective") or e["date"],
            "announced": e.get("announced"),
            "era": e.get("era"), "era_name": e.get("era_name"),
            # the announcement itself, with an archived copy where one exists
            "announcement": e.get("announcement"),
            "actions": acts, "sources": e.get("sources", []),
        })

    out = {
        "generated_from": "https://github.com/rykerwilliams/type1",
        "format": "Vintage",
        "sources": sources,
        "categories": current.get("banned_categories", []),
        "pool_exclusions": current.get("pool_exclusions", []),
        "events": slim,
        "cards": cards,
        "change_kinds": eradoc.get("change_kinds", {}),
        # only the eras that say something: a date range with no recorded
        # change is not worth shipping to the browser
        "eras": [
            {k: v for k, v in e.items()
             if k in ("era", "range_text", "start", "end", "name", "changes",
                      "notable_printings", "citation", "change_kinds")}
            for e in eradoc.get("eras", [])
            if e.get("changes") or e.get("notable_printings")
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w").write(json.dumps(out, indent=1, sort_keys=False) + "\n")
    print(f"wrote {OUT}")
    print(f"  events {len(slim)}, cards {len(cards)}, "
          f"categories {len(out['categories'])}")
    print(f"  {os.path.getsize(OUT)/1024:.0f} KB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/files/docs/git/type1-build")
