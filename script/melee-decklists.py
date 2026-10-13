#!/usr/bin/env python3
"""Pull decklists for a melee.gg tournament into assets/files/YYYY/MM/DD/.

    script/melee-decklists.py 435351 --date 2026-06-12 --event "TSI7 MS"
    script/melee-decklists.py 435351 --date 2026-06-12 --event "TSI7 MS" --apply

Dry run by default; nothing is written without --apply.

Why this exists rather than Badaro's MTGODecklistCache.Tools: that project is
the reference implementation and its MtgMeleeConstants.cs is where the two
endpoints below came from. But it parses the deck page for a button with class
'decklist-builder-copy-button', and melee no longer renders that -- the page is
Mustache-templated now and the list text lives in #decklist-mtgo-text. The
tools were last updated 2025-09 and their data repo stopped at 2025-03, so they
do not work against the current site. This is the same approach with the
selector moved.

Two melee quirks worth knowing:
  * The archetype field is junk. Every deck in a FreeForm event comes back
    named "Colorless", so --event/--deck naming has to come from elsewhere.
  * A player can register a decklist and leave it empty. Those return a page
    with an empty #decklist-mtgo-text, and are skipped.

Card names are normalised against Scryfall, because players type them by hand
and the site links each card. Real examples from one event: "Sylvan Libary",
"floded strand", "Counter Spell", "Savannah Lion", and entire lists in
lowercase.
"""
import argparse, html, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
     "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
SCRYFALL_UA = "teamserio-decklist-import/1.0 (+https://teamserio.us)"

STANDINGS = "https://melee.gg/Standing/GetRoundStandings"
DECK_PAGE = "https://melee.gg/Decklist/View/{id}"
TOURNEY   = "https://melee.gg/Tournament/View/{id}"

COLS = ["Rank", "Player", "Decklists", "MatchRecord", "GameRecord", "Points",
        "OpponentMatchWinPercentage", "TeamGameWinPercentage",
        "OpponentGameWinPercentage", "FinalTiebreaker", "OpponentCount"]


def fetch(url, data=None, headers=None, tries=4):
    """GET/POST with backoff. A 404 is an answer; anything else is retried."""
    hdrs = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    hdrs.update(headers or {})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs)
            return urllib.request.urlopen(req, timeout=45).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 ** i)
        except Exception:
            time.sleep(2 ** i)
    return None


def round_ids(tournament_id):
    page = fetch(TOURNEY.format(id=tournament_id))
    if page is None:
        sys.exit(f"could not load tournament {tournament_id}")
    page = page.decode("utf-8", "replace")
    ids = re.findall(r'class="btn btn-gray round-selector" data-id="(\d+)"', page)
    if not ids:
        sys.exit("no rounds found -- is the tournament public?")
    return ids


def standings(round_id):
    d = {"draw": "1", "start": "0", "length": "500", "roundId": round_id,
         "order[0][column]": "0", "order[0][dir]": "asc",
         "search[value]": "", "search[regex]": "false"}
    for i, c in enumerate(COLS):
        d[f"columns[{i}][data]"] = c
        d[f"columns[{i}][name]"] = c
        d[f"columns[{i}][searchable]"] = "true"
        d[f"columns[{i}][orderable]"] = "true"
        d[f"columns[{i}][search][value]"] = ""
        d[f"columns[{i}][search][regex]"] = "false"
    raw = fetch(STANDINGS, urllib.parse.urlencode(d).encode(),
                {"X-Requested-With": "XMLHttpRequest",
                 "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                 "Accept": "application/json, text/javascript, */*; q=0.01"})
    if raw is None:
        sys.exit("standings request failed")
    return json.loads(raw).get("data", [])


def deck_text(deck_id):
    """The MTGO-format list, read out of #decklist-mtgo-text."""
    page = fetch(DECK_PAGE.format(id=deck_id))
    if page is None:
        return None, None
    page = page.decode("utf-8", "replace")
    m = re.search(r'<[^>]*id="decklist-mtgo-text"[^>]*>(.*?)</(?:div|pre|textarea|span)>',
                  page, re.S)
    if not m:
        return None, None
    text = re.sub(r"<[^>]+>", "", html.unescape(re.sub(r"<br\s*/?>", "\n", m.group(1))))
    main, side, cur = [], [], None
    for line in (l.strip() for l in text.splitlines()):
        if not line:
            continue
        if line.lower().startswith("sideboard"):
            cur = side
            continue
        if re.match(r"^\d+\s", line):
            (side if cur is side else main).append(line)
    return (main, side) if main else (None, None)


def canonical_names(names):
    """Map each submitted name to Scryfall's spelling. Bulk first, fuzzy for the rest."""
    names = sorted(names)
    mapping, unresolved = {}, []
    for i in range(0, len(names), 75):
        chunk = names[i:i + 75]
        body = json.dumps({"identifiers": [{"name": n} for n in chunk]}).encode()
        raw = fetch("https://api.scryfall.com/cards/collection", body,
                    {"User-Agent": SCRYFALL_UA, "Content-Type": "application/json",
                     "Accept": "application/json"})
        if raw is None:
            unresolved.extend(chunk)
            continue
        r = json.loads(raw)
        found = {c["name"].lower(): c["name"] for c in r.get("data", [])}
        missing = {(x.get("name") or "").lower() for x in r.get("not_found", [])}
        for n in chunk:
            if n.lower() in missing:
                unresolved.append(n)
            else:
                hit = found.get(n.lower())
                if hit is None:
                    key = n.lower().replace("'", "").replace(",", "")
                    hit = next((v for k, v in found.items()
                                if k.replace("'", "").replace(",", "") == key), None)
                if hit:
                    mapping[n] = hit
                else:
                    unresolved.append(n)
        time.sleep(0.15)
    for n in unresolved:
        raw = fetch("https://api.scryfall.com/cards/named?fuzzy=" + urllib.parse.quote(n),
                    headers={"User-Agent": SCRYFALL_UA, "Accept": "application/json"})
        if raw:
            got = json.loads(raw).get("name")
            if got:
                mapping[n] = got
        time.sleep(0.2)
    return mapping


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tournament", help="melee tournament id, e.g. 435351")
    ap.add_argument("--date", required=True, help="event date, YYYY-MM-DD")
    ap.add_argument("--event", required=True, help='short label, e.g. "TSI7 MS"')
    ap.add_argument("--apply", action="store_true", help="actually write files")
    ap.add_argument("--out", default="assets/files", help="base output directory")
    args = ap.parse_args()

    y, m, d = args.date.split("-")
    outdir = os.path.join(args.out, y, m, d)

    rounds = round_ids(args.tournament)
    print(f"  {len(rounds)} rounds; using the last ({rounds[-1]}) for final standings")
    rows = standings(rounds[-1])
    print(f"  {len(rows)} players")

    decks = []
    for r in rows:
        team = r.get("Team") or {}
        players = team.get("Players") or []
        name = (players[0].get("DisplayName") if players else None) or team.get("Name") or "?"
        dls = r.get("Decklists") or []
        if not dls:
            continue
        main_b, side_b = deck_text(dls[0]["DecklistId"])
        if not main_b:
            print(f"    {name:<24} registered a list but it is empty -- skipped")
            continue
        decks.append({"rank": r.get("Rank"), "name": name, "main": main_b, "side": side_b})
        time.sleep(1.5)          # be polite
    print(f"  {len(decks)} usable decklists\n")

    submitted = {re.match(r"^\d+\s+(.+)$", c).group(1).strip()
                 for dk in decks for c in dk["main"] + dk["side"]}
    cmap = canonical_names(submitted)
    fixed = {k: v for k, v in cmap.items() if k != v}
    print(f"  {len(submitted)} unique cards, {len(fixed)} names corrected")
    for k, v in sorted(fixed.items())[:15]:
        print(f"    {k!r} -> {v!r}")
    missing = sorted(submitted - set(cmap))
    if missing:
        print(f"  !! {len(missing)} unresolved, left as submitted: {missing}")

    def norm(card):
        q, n = re.match(r"^(\d+)\s+(.+)$", card).groups()
        return f"{q} {cmap.get(n.strip(), n.strip())}"

    print()
    for dk in decks:
        fn = f"{dk['name']} - {args.event}.txt"
        path = os.path.join(outdir, fn)
        body = "\n".join(norm(c) for c in dk["main"]) + \
               "\n\nSideboard\n" + "\n".join(norm(c) for c in dk["side"]) + "\n"
        if args.apply:
            os.makedirs(outdir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(body)
        print(f"    {'wrote' if args.apply else 'would write'}  {path}")

    if not args.apply:
        print("\n  Dry run -- nothing written. Re-run with --apply.")
    print("\n  Deck names are NOT set: melee reports every FreeForm deck as "
          "'Colorless'. Rename each file to the archetype from the standings, "
          "then reference them with {% deckfile %}.")


if __name__ == "__main__":
    main()
