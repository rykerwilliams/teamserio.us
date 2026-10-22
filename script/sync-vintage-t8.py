#!/usr/bin/env python3
"""Pull the Vintage championship Top 8 decklists out of the type1 repo into _data/.

The lists live in https://github.com/rykerwilliams/type1 under decks/, one file
per event, each card already resolved to its Scryfall oracle_id and original
printing. This copies what the pages need into _data/vintage_t8.json, the same
way sync-vintage-br.py does for the B&R list: the site builds with no network
dependency and a data change arrives as a reviewable diff.

    python3 script/sync-vintage-t8.py /path/to/type1

Re-run it when type1's decks/ changes (once a year per championship, plus
corrections) and commit the result.
"""
import glob, gzip, io, json, os, re, sys, unicodedata

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "_data", "vintage_t8.json")
EVENT_KEYS = ("event", "label", "date", "date_precision", "date_range",
              "location", "players", "source", "partial", "notes")
DECK_KEYS = ("finish", "seed", "player", "player_native", "archetype",
             "source", "notes")


def states(repo):
    """(effective, {oracle_id}) for every B&R snapshot, oldest first."""
    out = []
    adir = os.path.join(repo, "archive")
    for fn in sorted(os.listdir(adir)):
        if fn.endswith(".json"):
            st = json.load(io.open(os.path.join(adir, fn), encoding="utf-8"))
            out.append((st["effective"], {c["oracle_id"] for c in st["restricted"]}))
    return out


def in_force(date, sts):
    r = set()
    for eff, ids in sts:
        if eff <= date:
            r = ids
    return r


def layouts(repo, oids):
    """Scryfall's layout for each oracle_id in oids, from the bulk data that
    type1's script/resolve-decks.py caches in .cache/scryfall/."""
    found = sorted(glob.glob(os.path.join(repo, ".cache", "scryfall", "default-cards-*.jsonl.gz")))
    if not found:
        sys.exit("no Scryfall bulk data in type1's .cache/scryfall/: "
                 "run script/resolve-decks.py there first")
    out = {}
    with gzip.open(found[-1], "rt", encoding="utf-8") as f:
        for line in f:
            if '" // ' not in line and "' // " not in line and " // " not in line:
                continue
            c = json.loads(line)
            if c.get("oracle_id") in oids:
                out.setdefault(c["oracle_id"], c["layout"])
    return out


def mtgo_name(name, layout):
    """The name Magic Online's .txt import takes: a split card's halves joined
    by a slash ("Wear/Tear", as mtgo.com prints it), any other two-part card by
    its front face, and no accents ("Lorien Revealed", "Lim-Dul's Vault")."""
    if " // " in name:
        name = "/".join(name.split(" // ")) if layout == "split" else name.split(" // ")[0]
    return "".join(ch for ch in unicodedata.normalize("NFD", name)
                   if unicodedata.category(ch) != "Mn")


def main(repo):
    sts = states(repo)
    ddir = os.path.join(repo, "decks")
    cards, events = {}, []

    def slim(part):
        # [count, key] -- or with the source's spelling, where it differs, as
        # a third element. The key is the oracle_id's first 8 characters: there
        # are 13,000 card entries, so the full id on each one doubled the file,
        # and the full id and the card detail live once in `cards` instead.
        if part is None:
            return None
        out = []
        for c in part:
            oid = c["oracle_id"][:8]
            if cards.get(oid, {}).get("oracle_id", c["oracle_id"]) != c["oracle_id"]:
                sys.exit(f"oracle_id prefix {oid} is shared; lengthen the key")
            if oid not in cards:
                op = c["original_printing"]
                cards[oid] = {"oracle_id": c["oracle_id"], "name": c["name"], "set": op["set"],
                              "set_name": op["set_name"],
                              "released_at": op["released_at"],
                              "image": op["image"],
                              "scryfall_uri": op["scryfall_uri"].split("?")[0]}
            out.append([c["count"], oid] + ([c["printed_as"]] if c.get("printed_as") else []))
        return out

    for fn in sorted(os.listdir(ddir)):
        if not fn.endswith(".json"):
            continue
        d = json.load(io.open(os.path.join(ddir, fn), encoding="utf-8"))
        ev = {"slug": fn[:-5]}
        ev.update({k: d[k] for k in EVENT_KEYS if d.get(k) not in (None, [], False)})
        ev["players"] = d.get("players")
        restricted = {i[:8] for i in in_force(d["date"], sts)}
        decks, used = [], set()
        for x in d["decks"]:
            deck = {k: x[k] for k in DECK_KEYS if x.get(k) not in (None, [])}
            deck["main"] = slim(x.get("main"))
            deck["sideboard"] = slim(x.get("sideboard"))
            for part in (deck["main"], deck["sideboard"]):
                used |= {c[1] for c in part or []}
            decks.append(deck)
        ev["decks"] = decks
        # only the restricted cards someone actually played: enough to badge
        # them, without shipping the whole list 48 times
        ev["restricted"] = sorted(used & restricted)
        events.append(ev)

    multi = {c["oracle_id"] for c in cards.values() if " // " in c["name"]}
    lay = layouts(repo, multi) if multi else {}
    for c in cards.values():
        m = mtgo_name(c["name"], lay.get(c["oracle_id"]))
        if m != c["name"]:
            c["mtgo"] = m

    out = {"generated_from": "https://github.com/rykerwilliams/type1",
           "events": events, "cards": cards}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        # indented so a resync reads as a diff, but with each card entry
        # collapsed onto its own line rather than spread over four
        text = json.dumps(out, ensure_ascii=False, indent=1)
        text = re.sub(r'\[\n\s*(\d+),\n\s*("[0-9a-f]{8}")(?:,\n\s*("(?:[^"\\]|\\.)*"))?\n\s*\]',
                      lambda m: "[" + ",".join(g for g in m.groups() if g) + "]", text)
        f.write(text + "\n")
    ndecks = sum(len(e["decks"]) for e in events)
    print(f"wrote {OUT}")
    print(f"  events {len(events)}, decks {ndecks}, cards {len(cards)}")
    print(f"  {os.path.getsize(OUT)/1024:.0f} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip() + "\n\nGive the path to a checkout of "
                 "https://github.com/rykerwilliams/type1")
    main(sys.argv[1])
