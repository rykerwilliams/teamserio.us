#!/usr/bin/env python3
"""Turn an archived Mana Drain thread into a teamserio.us post.

Reads a thread page cached by tmd-inventory.py and writes a Jekyll post matching
the conventions of the one that was ported by hand
(_posts/2022-07-23-tso-all-american-warren.md):

  - layout: default-with-decklists
  - <pre> blocks are written to assets/files/YYYY/MM/DD/ as .txt and
    referenced with {% deckfile %}; --inline-decklists keeps the old
    inline {% decklist %} form
  - the author block comes from AUTHORS, keyed by TMD handle
  - replies land in a "Replies and relevant bits" section, each marked
    "Reply from <handle>", while any decklist in a reply is absorbed above

  script/tmd-to-post.py --thread 1639
  script/tmd-to-post.py --thread 1639 --out _posts/2017-12-02-tsi-mishras.md
  script/tmd-to-post.py --thread 3824 --stdout      # compare against the hand port
"""
import argparse, html as htmllib, os, re, sys, time, urllib.parse

HTML_CACHE = os.environ.get("TMD_HTML_CACHE", "/tmp/tmd-html")
# Thread images -- standings screenshots, decklist photos, event shots -- are
# served from the forum's uploads and die with it, so they are pulled in here.
IMAGE_DIR = "assets/images/tmd"

# Keyed by TMD handle. Avatars already in the repo; see docs/tmd-archive-reports.md.
# Keys are matched case-insensitively via author_entry(); the forum reports
# handles inconsistently ("GrandpaBelcher" in a post header, "grandpabelcher"
# in a profile URL) and the thread authors are nartman99 and shaman-ben, which
# did not match the keys here at all.
AUTHORS = {
    "cleverpseudonym": {
        "name": "Rajah James", "avatar": "../assets/images/avatars/310221.jpg",
        "location": "Ohio, US",
        "links": [("https://bsky.app/profile/cleverpseudonym.bsky.social",
                   "fab fa-bluesky", "My personal bsky"),
                  ("https://x.com/rykerwilliams", "fab fa-twitter", "My personal X"),
                  ("https://www.facebook.com/rajah.james", "fab fa-facebook",
                   "My personal FB")],
    },
    # Both have written here under their own names already, so a ported post
    # must reuse the author block from their existing posts rather than a stub
    # -- otherwise the same person shows up twice with different avatars.
    # Nam: _posts/2026-02-07-HSI-9-Event-Report.md
    "nartman99": {"name": "Nam Tran",
                  "avatar": "../assets/images/avatars/namQ_277x325.png",
                  "location": "Ohio, US", "links": []},
    # Goes by "Shaman Ben" online rather than a full name, so the display name
    # is deliberately not expanded. Michigan Team Serious; the RIW Livonia
    # threads are his.
    "shaman-ben": {"name": "Shaman Ben", "location": "Leng", "links": []},
    # UNCONFIRMED -- Rajah's recollection, not verified against the forum
    # profile. Worth checking before this is published under his name.
    "infant_no_1": {"name": "Josh McCurley", "links": []},
    # None of these three have written here under their own name yet, so there
    # is no existing author block to match and no avatar in the repo. They get
    # a name and nothing else; tmd-inventory.py --avatars can pull their forum
    # avatar later if one was archived.
    "brassman": {"name": "Andy Probasco", "links": []},
    "lhc": {"name": "Jimmy McCarthy", "links": []},
    "cutlex": {"name": "Duane Haddix", "links": []},
    # Nat: _posts/2024-06-08-castmaster-season-1.md
    "grandpabelcher": {"name": "Nat Moes",
                       "avatar": "../assets/images/avatars/nat_400x400.jpg",
                       "location": "Ohio, United States",
                       "links": [("https://bsky.app/profile/grandpabelcher.bsky.social",
                                  "fab fa-bluesky", "My personal bsky"),
                                 ("https://x.com/GrandpaBelcher", "fab fa-twitter",
                                  "My personal Twitter")]},
}


def page_no(name):
    """The forum page number a cached filename represents. Page 1 has no suffix."""
    m = re.search(r"_(\d{1,3})\.html$", name)
    return int(m.group(1)) if m else 1


def find_thread(tid):
    """Every cached page of this thread, in page order.

    These threads are paginated -- 28 of the 45 candidates are archived across
    more than one page, and #2609 runs to 16. The write-up is on page 1 but the
    replies run across all of them, so a port needs the lot. Returns
    (list of (page_no, html), list of filenames).
    """
    hits = [n for n in os.listdir(HTML_CACHE) if re.search(rf"_topic_{tid}_", n)]
    if not hits:
        return [], []
    hits.sort(key=page_no)
    out = []
    for n in hits:
        body = open(os.path.join(HTML_CACHE, n), encoding="utf-8", errors="replace").read()
        out.append((page_no(n), body))
    return out, hits


ARCHIVE_PREFIX = re.compile(r"^(?:https?://web\.archive\.org)?/web/\d{14}(?:im_|if_)?/")

# nodebb renders emoji as <img>. The hand-ported post carries the character, so
# map the ones these threads actually use and drop the rest.
EMOJI = {"slight_smile": "\U0001F642", "smile": "\U0001F604", "wink": "\U0001F609",
         "grinning": "\U0001F600", "thumbsup": "\U0001F44D", "+1": "\U0001F44D",
         "frowning": "\U0001F641", "cry": "\U0001F622", "joy": "\U0001F602",
         "heart": "\u2764\ufe0f", "fire": "\U0001F525", "beers": "\U0001F37B",
         "beer": "\U0001F37A", "trophy": "\U0001F3C6"}


def localise_image(url, tid, snapshot_ts="", fetch=True):
    """Download a forum upload into IMAGE_DIR and return its site path.

    Returns the original url untouched if it is not a forum upload, or if the
    download fails -- a broken remote link is better than a link to a file that
    is not there, and the caller's output stays honest either way.
    """
    import urllib.error
    import urllib.request
    raw = unarchive(url)
    m = re.search(r"/assets/uploads/files/([^/?#]+)$", raw)
    if not m:
        return url, None
    name = f"{tid}-{m.group(1)}"
    dest = os.path.join(IMAGE_DIR, name)
    web = "/" + dest
    if os.path.isfile(dest):
        return web, "already present"
    if not fetch:
        return url, "not fetched"
    # Pull it through the Wayback copy. The live forum 404s these -- that is the
    # whole reason this exists -- so fetching the de-archived url is pointless.
    if "web.archive.org" in url or url.startswith("/web/"):
        src = url if url.startswith("http") else "https://web.archive.org" + url
    elif snapshot_ts:
        src = f"https://web.archive.org/web/{snapshot_ts}im_/{raw}"
    else:
        src = raw
    try:
        req = urllib.request.Request(src, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
        if not body.startswith((b"\xff\xd8", b"\x89PNG", b"GIF8", b"RIFF")):
            return url, "not an image"
        os.makedirs(IMAGE_DIR, exist_ok=True)
        open(dest, "wb").write(body)
        return web, f"{len(body)//1024} KB"
    except urllib.error.HTTPError as e:
        return url, f"HTTP {e.code}"
    except Exception as e:
        return url, type(e).__name__


def unarchive(url):
    """Strip the Wayback wrapper so a link points at the real target again."""
    u = ARCHIVE_PREFIX.sub("", url)
    if u.startswith("//"):
        u = "https:" + u
    return u


def emoji_img(tag):
    """An emoji <img> becomes its character, or nothing."""
    name = re.search(r'(?:title|alt)="?:?([a-z0-9_+\-]+):?"?', tag, re.I)
    if name and name.group(1).lower() in EMOJI:
        return EMOJI[name.group(1).lower()]
    return ""


def tabbed_table(text):
    """Tab-separated lines become a Markdown table.

    The standings in these threads are pasted in as tab-separated text, not a
    <table>; the hand-ported post turned them into a Markdown table, so this does
    the same. The first row is the header.
    """
    rows = [l for l in text.splitlines() if "\t" in l]
    if len(rows) < 2:
        return None
    # "\u2022\tBig Fish, Little Fish" is a bulleted list that happens to use a tab
    # for indentation, not a two-column table. Treating it as one produced rows
    # of "| \u2022 | Big Fish, Little Fish |" with separator lines spliced through
    # the middle of the metagame breakdown.
    if all(BULLET.match(r) for r in rows):
        return None
    cells = [[c.strip() for c in r.split("\t")] for r in rows]
    width = max(len(c) for c in cells)
    cells = [c + [""] * (width - len(c)) for c in cells]
    head, body = cells[0], cells[1:]
    out = ["| " + " | ".join(head) + " |",
           "|" + "|".join("---" for _ in head) + "|"]
    for r in body:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


BULLET = re.compile(r"^\s*[\u2022\u00b7\u25aa\u25cf*]\s*\t?\s*")


def md_from(node):
    """Convert a post's HTML body to Markdown.

    Deliberately narrow: these are forum posts, so the tag vocabulary is small.
    <pre> is handled by the caller because it becomes a Liquid tag, not Markdown.
    """
    s = node
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</p>\s*<p[^>]*>", "\n\n", s, flags=re.I)
    s = re.sub(r"</?p[^>]*>", "\n\n", s, flags=re.I)
    s = re.sub(r"<(h[1-6])[^>]*>(.*?)</\1>",
               lambda m: "\n\n" + "#" * int(m.group(1)[1]) + " " + m.group(2).strip() + "\n\n",
               s, flags=re.S | re.I)
    s = re.sub(r"<a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a>",
               lambda m: f"[{m.group(2).strip()}]({unarchive(m.group(1))})",
               s, flags=re.S | re.I)
    s = re.sub(r"<(strong|b)[^>]*>(.*?)</\1>", r"**\2**", s, flags=re.S | re.I)
    s = re.sub(r"<(em|i)[^>]*>(.*?)</\1>", r"*\2*", s, flags=re.S | re.I)
    s = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", s, flags=re.S | re.I)
    s = re.sub(r"</?(ul|ol)[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<blockquote[^>]*>(.*?)</blockquote>",
               lambda m: "\n".join("> " + l for l in m.group(1).strip().splitlines()) + "\n",
               s, flags=re.S | re.I)
    # emoji first, so they do not become stray image links
    s = re.sub(r"<img[^>]*(?:nodebb-plugin-emoji|/emoji/)[^>]*>", lambda m: emoji_img(m.group(0)),
               s, flags=re.I)
    s = re.sub(r"<img[^>]+src=\"([^\"]+)\"[^>]*>",
               lambda m: f"\n![]({unarchive(m.group(1))})\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmllib.unescape(s)
    # A line that is nothing but bold text is a section heading in these posts --
    # "**Standings**", "**Meta**" -- and the hand port promoted them to h2.
    s = re.sub(r"^\*\*([^*\n]{2,60})\*\*\s*$", r"## \1", s, flags=re.M)

    # Pasted tab-separated standings become a real table. Each row arrives as its
    # own paragraph, so gather runs of tab-bearing lines across blank lines rather
    # than treating one paragraph as one table.
    lines, out, run = s.splitlines(), [], []

    def flush():
        if not run:
            return
        t = tabbed_table("\n".join(run))
        out.append(t if t else "\n".join(run))
        run.clear()

    for ln in lines:
        if BULLET.match(ln):
            flush()
            out.append("- " + BULLET.sub("", ln).strip())
        elif "\t" in ln:
            run.append(ln)
        elif ln.strip() == "" and run:
            continue                 # blank line inside a pasted table
        else:
            flush()
            out.append(ln)
    flush()
    s = "\n".join(out)

    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    # Bullets arrive as <br/>-separated lines inside one <p>, and paragraph
    # normalisation then puts a blank line between each, so a five-item
    # metagame breakdown rendered as five separate paragraphs. Close them up
    # so consecutive items are one list.
    s = re.sub(r"(?m)^(- .+)\n\n(?=- )", r"\1\n", s)
    s = re.sub(r"(?m)^(- .+)\n\n(?=- )", r"\1\n", s)
    return s.strip()


# TMD's own decklist widget. Eight of the cached threads use it instead of a
# <pre> block, and between them it holds 42 decklists -- which the <pre>-only
# reader did not see at all, keeping just the first card of each and dropping
# the rest. Those threads also report decks=0 in the inventory, because that
# counts <pre>, so they look like standings-only posts when they are not.
WIDGET = re.compile(r'<div class="tmd-decklist">(.*?)</div>\s*</div>', re.S | re.I)
CARDROW = re.compile(r'<div>\s*(\d+)\s*<a[^>]*class="tmd-cardname"[^>]*>(.*?)</a>', re.S | re.I)
H3 = re.compile(r'<h3[^>]*>(.*?)</h3>', re.S | re.I)


def widget_deck(block_html):
    """(title, lines) for one tmd-decklist widget, sideboard separated.

    Returned in the same shape as a <pre> block so the caller cannot tell them
    apart: card lines with a bare blank line before the sideboard.
    """
    heads = [htmllib.unescape(re.sub(r"<[^>]+>", "", t)).strip()
             for t in H3.findall(block_html)]
    # A widget whose first heading is "Sideboard:" has no title -- that word is
    # a section marker. Prepending it as the title made write_deckfile read it
    # as the separator and file the entire list as sideboard.
    title = heads[0] if heads and not SIDEBOARD.match(heads[0]) else ""
    # Walk the block in order so a "Sideboard:" heading switches sections.
    main, side, cur = [], [], None
    for m in re.finditer(r'<h3[^>]*>(.*?)</h3>|' + CARDROW.pattern,
                         block_html, re.S | re.I):
        if m.group(1) is not None:
            h = htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
            if SIDEBOARD.match(h):
                cur = side
            continue
        qty = m.group(2)
        name = htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(3) or "")).strip()
        if qty and name:
            (side if cur is side else main).append(f"{qty} {name}")
    # Emit the marker word, not a blank line: write_deckfile splits on the
    # marker and skips blanks, so a blank separator put the whole sideboard
    # into the main deck and every widget list came out 75/0.
    lines = main + (["Sideboard"] + side if side else [])
    return title, lines


def split_pres(body_html):
    """Split a post body into (markdown, decklist) chunks in document order.

    Decklists arrive either as a <pre> block or as TMD's own widget; both are
    yielded as ("deck", text), with the widget carrying its <h3> title so the
    caller can name the file from it.
    """
    spans = []
    for m in re.finditer(r"<pre[^>]*>(.*?)</pre>", body_html, re.S | re.I):
        spans.append((m.start(), m.end(),
                      ("deck", htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(1))))))
    widgets = []
    for m in WIDGET.finditer(body_html):
        title, lines = widget_deck(m.group(1))
        if not lines:
            continue
        # Some posts split a list across two widgets, the second titled
        # "Sideboard:" or "SB". On its own that reads as a deck with no main
        # board, so fold it into the one before it.
        if widgets and SIDEBOARD.match(title or ""):
            ws, _, wlines = widgets[-1]
            widgets[-1] = (ws, m.end(), wlines + ["Sideboard"] + lines)
            continue
        widgets.append((m.start(), m.end(),
                        ([title] if title else []) + lines))
    for ws, we, wlines in widgets:
        spans.append((ws, we, ("deck", "\n".join(wlines))))
    spans.sort()

    parts, last = [], 0
    for start, end, chunk in spans:
        if start > last:
            parts.append(("md", body_html[last:start]))
        parts.append(chunk)
        last = max(last, end)
    if last < len(body_html):
        parts.append(("md", body_html[last:]))
    return parts


DECK_DIR = "assets/files"
NAME_CACHE = os.environ.get("TMD_NAME_CACHE", "/tmp/tmd-cardnames.json")

# Player shorthand, resolved before Scryfall sees it. Fuzzy search would get
# some of these wrong rather than fail -- "DT" is not a near-miss for "Demonic
# Tutor", it is a different string entirely -- so guessing here is safer than
# letting the API guess. Keyed loosely: case and punctuation are folded.
ALIASES = {
    "dcon": "Demonic Consultation",
    "dconsult": "Demonic Consultation",
    "dt": "Demonic Tutor",
    "xantid": "Xantid Swarm",
    "sadsac": "Sadistic Sacrament",
    # Standard Vintage shorthand, from a list written entirely this way.
    "acall": "Ancestral Recall",
    "vamp": "Vampiric Tutor",
    "mystical": "Mystical Tutor",
    "mental": "Mental Misstep",
    "tendrils": "Tendrils of Agony",
    "petal": "Lotus Petal",
    "jet": "Mox Jet",
    "sapphire": "Mox Sapphire",
    "sea": "Underground Sea",
    "delta": "Polluted Delta",
    "hurkyls": "Hurkyl's Recall",
    "catacobs": "Verdant Catacombs",
    "tropcial": "Tropical Island",
    # "chain" is Chain of Vapor here, confirmed. Worth re-checking if a red
    # deck ever ports: Chain Lightning is the other candidate for that word.
    "probe": "Gitaxian Probe",
    "lotus": "Black Lotus",
    "crypt": "Mana Crypt",
    "chain": "Chain of Vapor",
    # Read as Yawgmoth's Will from context -- an Ad Nauseam list. Not
    # confirmed; the alternative readings are all far less likely in Vintage.
    "will": "Yawgmoth's Will",
}

_names = {}


def _card_name(card):
    """The name to write into a decklist file.

    A transforming card is imported by its FRONT FACE: "Delver of Secrets",
    not "Delver of Secrets // Insectile Aberration", which is what Scryfall
    reports as its name and what MTGO will not accept. Split cards are the
    other way round -- "Wear // Tear" and "Fire // Ice" are the real names and
    both halves belong in the file.
    """
    name = card.get("name") or ""
    if card.get("layout") in ("transform", "modal_dfc", "flip", "reversible_card"):
        faces = card.get("card_faces") or []
        if faces and faces[0].get("name"):
            return faces[0]["name"]
    return name


def _fuzzy_ok(written, card):
    """Is a fuzzy match safe enough to accept unseen?

    Scryfall's fuzzy search returns its best guess, not a confident one, and on
    player shorthand that guess can be a different card entirely: "crypt" came
    back as Cryptex rather than Mana Crypt, and "lotus" as a token named Lotus
    rather than Black Lotus. Both would have gone into a decklist looking
    perfectly ordinary.

    So accept only when the written form appears as a whole word in the
    result -- "xantid" in "Xantid Swarm" passes, "crypt" in "Cryptex" does not
    -- and never accept a token. Anything else wants a human in ALIASES.
    """
    name = card.get("name") or ""
    if card.get("layout") == "token" or "Token" in (card.get("type_line") or ""):
        return False
    w = re.sub(r"[^a-z0-9 ]", " ", written.lower()).split()
    words = re.sub(r"[^a-z0-9 ]", " ", name.lower()).split()
    if not w:
        return False
    # Every written word must at least begin a word of the result, and one of
    # them must match a whole word. "dark rit" -> Dark Ritual passes on "dark";
    # "imp seal" -> Imperial Seal passes on "seal"; "crypt" -> Cryptex has only
    # the one word and it is a prefix, not a match, so it fails.
    def close(a, b):
        """One edit apart, for words long enough that it is a typo not a guess."""
        if min(len(a), len(b)) < 6 or abs(len(a) - len(b)) > 1:
            return False
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            for j, cb in enumerate(b, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                               prev[j - 1] + (ca != cb)))
            prev = cur
        return prev[-1] <= 1

    def strong(x):
        return any(x == y or close(x, y) for y in words)

    # Every written word must at least begin a word of the result, or be one
    # typo away from it. And one word must match strongly -- exactly, or as a
    # typo -- so a bare prefix alone is never enough: "dark rit" -> Dark Ritual
    # passes on "dark", "Enginnered Explosives" passes on "explosives", but
    # "crypt" -> Cryptex has only the one word and only prefixes it.
    if not all(strong(x) or any(len(x) >= 3 and y.startswith(x) for y in words)
               for x in w):
        return False
    if not any(strong(x) for x in w):
        return False
    # A single short word that merely appears somewhere in a longer card name
    # is not evidence: "sea" matches Sea Serpent exactly, while in a Vintage
    # list it means Underground Sea. Require a one-word result, or that the
    # word is distinctive enough and leads the name.
    if len(w) == 1 and len(words) > 1:
        return len(w[0]) >= 6 and words[0] == w[0]
    return True


def resolve_names(names):
    """Map each submitted card name to Scryfall's spelling.

    Forum posters type these by hand, so a ported thread carries whatever they
    wrote: 144 distinct names across the first five threads start lowercase,
    and one list was typed entirely that way. Scryfall matches case
    insensitively so nothing was broken, but "4 black lotus" next to
    "4 Black Lotus" in the next deck reads like a transcription error.

    Bulk endpoint first (75 per request), fuzzy only for what it misses. Cached
    on disk so re-running a port is free.
    """
    import json as _json
    import urllib.error
    import urllib.request
    global _names
    if not _names:
        try:
            _names = _json.load(open(NAME_CACHE, encoding="utf-8"))
        except Exception:
            _names = {}
    for n in names:
        a = ALIASES.get(re.sub(r"[^a-z0-9]", "", (n or "").lower()))
        if a:
            _names[n] = a
    todo = sorted({n for n in names if n and n not in _names})
    if not todo:
        return _names
    ua = {"User-Agent": "teamserio-tmd-import/1.0 (+https://teamserio.us)",
          "Accept": "application/json"}

    def req(url, data=None):
        h = dict(ua)
        if data:
            h["Content-Type"] = "application/json"
        for i in range(4):
            try:
                r = urllib.request.Request(url, data=data, headers=h)
                return _json.loads(urllib.request.urlopen(r, timeout=40).read())
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                time.sleep(2 ** i)
            except Exception:
                time.sleep(2 ** i)
        return None

    missed = []
    for i in range(0, len(todo), 75):
        chunk = todo[i:i + 75]
        r = req("https://api.scryfall.com/cards/collection",
                _json.dumps({"identifiers": [{"name": n} for n in chunk]}).encode())
        if not r:
            missed.extend(chunk)
            continue
        # Key on both the full name and the importable one: a transforming
        # card comes back as "Delver of Secrets // Insectile Aberration" while
        # the list says "Delver of Secrets", and without the second key every
        # one of them would fall through to a needless fuzzy lookup.
        found = {}
        for c in r.get("data", []):
            importable = _card_name(c)
            found[c["name"].lower()] = importable
            found.setdefault(importable.lower(), importable)
        nf = {(x.get("name") or "").lower() for x in r.get("not_found", [])}
        for n in chunk:
            if n.lower() in nf:
                missed.append(n)
            else:
                hit = found.get(n.lower())
                if hit is None:
                    key = re.sub(r"[^a-z0-9]", "", n.lower())
                    hit = next((v for k, v in found.items()
                                if re.sub(r"[^a-z0-9]", "", k) == key), None)
                if hit:
                    _names[n] = hit
                else:
                    missed.append(n)
        time.sleep(0.15)
    for n in missed:
        r = req("https://api.scryfall.com/cards/named?fuzzy=" + urllib.parse.quote(n))
        got = _card_name(r) if r else None
        if got and _fuzzy_ok(n, r):
            _names[n] = got
        else:
            # Leave it exactly as posted rather than guess. A wrong card in a
            # decklist is worse than an unprettified one.
            why = f" (rejected {got!r})" if got else ""
            print(f"    card name unresolved, left as written: {n!r}{why}",
                  file=sys.stderr)
        time.sleep(0.2)
    try:
        _json.dump(_names, open(NAME_CACHE, "w", encoding="utf-8"))
    except Exception:
        pass
    return _names



SIDEBOARD = re.compile(r"^\s*(side\s*board|sideboard|sb)\s*:?\s*$", re.I)
MAINDECK = re.compile(r"^\s*(main\s*deck|maindeck|deck|md)\s*:?\s*$", re.I)


def _key(x):
    """Fold a handle or display name to something comparable."""
    return re.sub(r"[^a-z0-9]+", "", (x or "").lower())


def author_entry(handle):
    """AUTHORS lookup by handle OR display name.

    The forum reports whichever it feels like: a thread by "shaman-ben" has
    author "Shaman Ben", and Nat appears as both "grandpabelcher" and
    "GrandpaBelcher". Matching the raw string missed all of those, so Shaman
    Ben's ported post came out with his name but no location.
    """
    if not handle:
        return {}
    if handle in AUTHORS:
        return AUTHORS[handle]
    k = _key(handle)
    for key, v in AUTHORS.items():
        if _key(key) == k or _key(v.get("name")) == k:
            return v
    return {}


def deck_lines(text):
    """The card lines of a <pre> block, with the source's leading 'Deck' dropped."""
    lines = [l.rstrip() for l in text.strip().splitlines()]
    while lines and (not lines[0].strip() or MAINDECK.match(lines[0])):
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


MONTHS = ["January","February","March","April","May","June","July",
          "August","September","October","November","December"]

ORDINALS = {"first":1,"second":2,"third":3,"fourth":4,"fifth":5,"sixth":6,"seventh":7,
            "eighth":8,"ninth":9,"tenth":10,"eleventh":11,"twelfth":12,
            "thirteenth":13,"fourteenth":14,"fifteenth":15,"sixteenth":16}


def deck_owner(md_before, lines):
    """Work out whose deck this is, and what it was called.

    Three shapes turn up across the threads, so all three are tried before
    falling back to a positional name:

      1. a tab-separated standings row in the text ABOVE the block --
         "1\tDave Ketterer\tRavager Shops\t12"      (#3824)
      2. a prose placing line as the FIRST LINE INSIDE the block --
         "First place - Joe Reuschel - Ravager Shops" (#1738)
      3. markdown headers inside the block --
         "# BUGstill (1st)" then "## Kevin Cron"      (#1483)

    Returns (rank, player, deck, body_lines) -- body_lines has any consumed
    header lines removed, so they do not end up in the decklist file.
    """
    # Keep the source index alongside each non-blank line: these blocks put a
    # blank line between "First place" and the player, so inspecting lines[:4]
    # directly made head[1] the blank and every deck fell back to "Deck N".
    idx = [(i, l) for i, l in enumerate(lines[:8]) if l.strip()][:4]
    head = [l for _, l in idx]

    def rest(n):
        """Everything after the nth non-blank header line."""
        if len(idx) < n:
            return lines
        body = lines[idx[n - 1][0] + 1:]
        while body and (not body[0].strip() or MAINDECK.match(body[0])):
            body = body[1:]
        return body

    # 2. "First place - Player - Deck" / "1st - Player - Deck"
    if head:
        first = head[0].strip()
        parts = [c.strip() for c in re.split(r"\s+[-\u2013\u2014]\s+", first) if c.strip()]
        if len(parts) >= 3:
            word = parts[0].lower().replace(" place", "").strip()
            rank = ORDINALS.get(word)
            if rank is None:
                m = re.match(r"(\d+)", word)
                rank = int(m.group(1)) if m else None
            if rank:
                return str(rank), parts[1], parts[2], rest(1)

    # 2b. placing on its own line, player and deck on the next --
    #     "First place" / "Andy Probasco - \"Death Survives\""   (#2786)
    if len(head) >= 2:
        word = head[0].strip().lower().replace(" place", "").strip()
        rank = ORDINALS.get(word)
        if rank is None and re.fullmatch(r"\d+(?:st|nd|rd|th)?", word):
            rank = int(re.match(r"\d+", word).group(0))
        if rank:
            parts = [c.strip() for c in
                     re.split(r"\s+[-\u2013\u2014]\s+", head[1].strip()) if c.strip()]
            if len(parts) >= 2:
                return (str(rank), parts[0], parts[1].strip('"\u201c\u201d'),
                        rest(2))
            if parts:
                return str(rank), parts[0], None, rest(2)

    # 2c. "Nam Tran - 2 Card Monte" with no placing. This is the <h3> of a TMD
    #     decklist widget, which names the deck but does not rank it. Only
    #     accepted when the line splits cleanly in two and neither half looks
    #     like a card line, so prose above a <pre> cannot be mistaken for it.
    if head:
        parts = [c.strip() for c in
                 re.split(r"\s+[-\u2013\u2014]\s+", head[0].strip()) if c.strip()]
        if (len(parts) == 2 and not re.match(r"^\d+\s", parts[0])
                and all(len(x) < 60 for x in parts)):
            return None, parts[0], parts[1], rest(1)

    # 3. "# Deck (1st)" + "## Player"
    if len(head) >= 2 and head[0].lstrip().startswith("#"):
        deck = re.sub(r"^#+\s*", "", head[0]).strip()
        rank = None
        m = re.search(r"\((\d+)(?:st|nd|rd|th)\)\s*$", deck, re.I)
        if m:
            rank = m.group(1)
            deck = deck[:m.start()].strip()
        player = re.sub(r"^#+\s*", "", head[1]).strip() if head[1].lstrip().startswith("#") else None
        body = rest(2) if player else rest(1)
        # A lone "## Dragon 2018?" with no player under it still names the deck;
        # the caller falls back to the posting handle for who.
        return rank, player, deck, body

    # 1. tab-separated standings row above the block
    for line in reversed((md_before or "").strip().splitlines()):
        if not line.strip():
            continue
        cells = [c.strip() for c in line.split("\t") if c.strip()]
        if len(cells) >= 3 and re.fullmatch(r"\d+", cells[0]):
            return cells[0], cells[1], cells[2], lines
        break

    return None, None, None, lines

def write_deckfile(lines, event_date, event_label, player, deck, seq):
    """Write a decklist as its own .txt and return the path to reference.

    Preferred over an inline {% decklist %} block: the list stays a plain text
    file someone can download and import, and the post just points at it.

    Main and sideboard are separated by a bare blank line. Do NOT write the
    word "Sideboard" -- deckfile_tag.rb emits that heading for either a blank
    line or a line reading "Sideboard", so including it renders it twice."""
    y, m, d = (event_date or "0000-00-00").split("-")[:3]
    out_dir = os.path.join(DECK_DIR, y, m, d)
    who = player or f"Deck {seq}"
    name = f"{who} - {event_label} - {deck}.txt" if deck else f"{who} - {event_label}.txt"
    name = re.sub(r"[/\\]", "-", name)
    path = os.path.join(out_dir, name)

    main, side, cur = [], [], None
    for l in lines:
        if SIDEBOARD.match(l):
            cur = side
            continue
        if not l.strip():
            continue
        m = re.match(r"^(\d+)\s+(.+?)\s*$", l.strip())
        if m:
            qty, nm = m.group(1), m.group(2)
            (side if cur is side else main).append(f"{qty} {_names.get(nm, nm)}")
        else:
            (side if cur is side else main).append(l.strip())
    os.makedirs(out_dir, exist_ok=True)
    body = "\n".join(main) + ("\n\n" + "\n".join(side) if side else "") + "\n"
    open(path, "w", encoding="utf-8").write(body)
    return "/" + path.replace(os.sep, "/")


def decklist_block(text):
    """A {% decklist %} block. The source's leading 'Deck' line is dropped -- the
    hand-ported post does not carry it, and the tag supplies its own heading."""
    lines = [l.rstrip() for l in text.strip().splitlines()]
    while lines and lines[0].strip().lower() in ("deck", "deck:", ""):
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "{% decklist %}\n" + "\n".join(lines) + "\n{% enddecklist %}"


def front_matter(meta):
    a = author_entry(meta["author"]) or {"name": meta["author"] or "Unknown", "links": []}
    out = ["---", "layout: default-with-decklists",
           f'title:  "{meta["title"]}"',
           f'date:   {meta["date"]}',
           "categories: tournament-writeup",
           f'tags: {meta["tags"]}']
    for k in ("include_on_feed", "show_author", "show_bottomnavs", "show_categories",
              "show_comments", "show_date", "show_related", "show_sociallinks", "show_tags"):
        out.append(f"{k:<18}: true")
    out += ["author:", f'  name: {a["name"]}']
    if a.get("avatar"):
        out.append(f'  avatar: {a["avatar"]}')
    if a.get("location"):
        out.append(f'  location: {a["location"]}')
    if a.get("links"):
        out.append("  links:")
        for url, icon, label in a["links"]:
            out.append(f"    - url: {url}")
            out.append(f'      icon: "{icon}"')
            out.append(f'      label: "{label}"')
    # Where this came from. These threads are gone; the snapshot is the only record.
    out.append(f'tmd_thread: {meta["tid"]}')
    out.append(f'tmd_snapshot: {meta["snapshot"]}')
    if meta.get("event_date"):
        out.append(f'event_date: {meta["event_date"]}')
    if meta.get("venue"):
        out.append(f'venue: {meta["venue"]}')
    if meta.get("players"):
        out.append(f'players: {meta["players"]}')
    out.append("---")
    return "\n".join(out)


def build(meta, owner_html, replies, fetch_images=True, deckfiles=True,
          event_label=None):
    # One batch for the whole post, before anything is written: 500-odd names
    # across a thread, and the bulk endpoint takes 75 at a time.
    all_names = []
    for src in [owner_html] + [r["html"] for r in replies]:
        for kind, text in split_pres(src):
            if kind != "deck":
                continue
            for l in deck_lines(text):
                m = re.match(r"^\d+\s+(.+?)\s*$", l.strip())
                if m:
                    all_names.append(m.group(1))
    if all_names:
        resolve_names(all_names)

    chunks = []
    seq = 0
    nonlocal_seq = [0]
    label = event_label or meta.get("event_label") or "TMD"
    for kind, text in split_pres(owner_html):
        if kind != "deck":
            chunks.append(md_from(text))
            continue
        seq += 1
        nonlocal_seq[0] = seq
        lines = deck_lines(text)
        if not deckfiles:
            chunks.append("{% decklist %}\n" + "\n".join(lines) + "\n{% enddecklist %}")
            continue
        # The introducing line is the last thing in the markdown chunk above.
        rank, player, deck, lines = deck_owner(chunks[-1] if chunks else "", lines)
        path = write_deckfile(lines, meta.get("event_date") or meta.get("date", "")[:10],
                              label, player, deck, seq)
        # When the placing line lived inside the block it has just been consumed
        # into the filename, so without this the post loses who finished where.
        # When it came from a standings row above, that row is still on the page
        # and a second heading would only repeat it.
        if player and rank and not (chunks and "\t" in (chunks[-1] or "")):
            head = f"### {rank}. {player}"
            if deck:
                head += f" \u2014 {deck}"
            chunks.append(head)
        chunks.append("{%% deckfile %s %%}" % path)
    body = "\n\n".join(c for c in chunks if c.strip())

    from_decks = []
    if replies:
        body += "\n\n## Replies and relevant bits\n"
        for r in replies:
            # Someone posting their list in a reply is still a decklist, and
            # dropping it loses content the thread had -- #1738 has one that
            # belongs to nobody in the top five. The list goes up with the other
            # decklists rather than down here, since that is where a reader
            # looking for decklists will be; the reply keeps whatever it said.
            for kind, text in split_pres(r["html"]):
                if kind != "deck":
                    continue
                dl = deck_lines(text)
                if not dl:
                    continue
                nonlocal_seq[0] += 1
                _, rp, rd, dl = deck_owner("", dl)
                who = rp or author_entry(r["username"]).get("name") or r["username"]
                rpath = write_deckfile(
                    dl, meta.get("event_date") or meta.get("date", "")[:10],
                    label, who, rd, nonlocal_seq[0])
                head = f"### {who}" + (f" \u2014 {rd}" if rd else "")
                # Naming the handle as well is only worth it when it is a
                # different person from the one the deck is filed under --
                # "Rajah James ... posted as a reply by cleverpseudonym" is
                # the same person twice.
                by = "" if _key(who) == _key(r["username"]) or \
                     _key(author_entry(r["username"]).get("name")) == _key(who) \
                     else f" by {r['username']}"
                from_decks.append(
                    f'{head}\n\n*Posted as a reply{by}.*\n\n'
                    f'{"{%% deckfile %s %%}" % rpath}')
            # Strip BOTH decklist forms from the prose. <pre> was handled; the
            # widget was not, so its cards rendered as a wall of inline links
            # immediately above the very deckfile block they had become.
            stripped = re.sub(r"<pre[^>]*>.*?</pre>", "", r["html"], flags=re.S | re.I)
            stripped = WIDGET.sub("", stripped)
            prose = md_from(stripped)
            if not prose.strip():
                continue
            body += f'\n**Reply from {r["username"]}:**\n\n'
            if prose.strip():
                body += f"{prose}\n"

    if from_decks:
        marker = "\n\n## Replies and relevant bits\n"
        block = "\n\n" + "\n\n".join(from_decks)
        body = (body.replace(marker, block + marker, 1) if marker in body
                else body + block)

    # Rewrite forum uploads to local copies, reporting what happened to each.
    notes = []
    snap_ts = re.search(r"/web/(\d{14})", meta.get("snapshot", "") or "")
    def swap(m):
        new, note = localise_image(m.group(1), meta["tid"],
                                   snap_ts.group(1) if snap_ts else "", fetch_images)
        notes.append((m.group(1).split("/")[-1][:48], note or "left remote"))
        return f"![]({new})"
    body = re.sub(r"!\[\]\(([^)]+)\)", swap, body)
    for name, note in notes:
        print(f"    image {name}: {note}", file=sys.stderr)

    # Say where this came from, in the post itself rather than only in front
    # matter. These threads 404 on the live forum, so the Wayback copy is the
    # only thing a reader can check the port against.
    snap = meta.get("snapshot")
    if snap:
        posted = (meta.get("posted") or "")[:10]
        when = ""
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", posted):
            y, m, d = posted.split("-")
            when = f" on {int(d)} {MONTHS[int(m) - 1]} {y}"
        body = (f"*Originally posted to The Mana Drain{when}. The forum has since "
                f"reorganised and the thread is gone; this is ported from the "
                f"[archived copy]({snap}).*\n\n") + body

    return front_matter(meta) + "\n\n" + body + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--thread", required=True)
    ap.add_argument("--out")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--title")
    ap.add_argument("--tags", default="vintage tournament-writeup")
    ap.add_argument("--no-archive-tag", action="store_true",
                    help="omit the tmd-archive tag this script otherwise adds")
    ap.add_argument("--event", help='short label for decklist filenames, '
                    'e.g. "TSO Warren 2022.07.23"')
    ap.add_argument("--event-date", help="YYYY-MM-DD the event was held. Sets the "
                    "post date and the assets/files/ folder. The site's URLs are "
                    "built from the post date and the hand port uses the event "
                    "date, not the day it was posted to the forum -- slug parsing "
                    "only recovers it for some threads, so pass it explicitly.")
    ap.add_argument("--inline-decklists", action="store_true",
                    help="emit inline decklist blocks instead of writing .txt "
                         "files and referencing them with the deckfile tag")
    ap.add_argument("--no-images", action="store_true",
                    help="leave image urls remote instead of downloading them")
    a = ap.parse_args()

    pages, names = find_thread(a.thread)
    if not pages:
        sys.exit(f"no cached page for thread {a.thread} in {HTML_CACHE} "
                 f"-- fetch it with tmd-inventory.py first")
    html, path = pages[0][1], names[0]
    have = sorted(p for p, _ in pages)
    print(f"  cached pages for #{a.thread}: {have}", file=sys.stderr)
    if 1 not in have:
        sys.exit(f"page 1 is not cached, and it holds the write-up. Cached: {have}. "
                 f"Every candidate thread does have a page 1 archived -- fetch it.")

    # Reuse the inventory's scraper so there is one definition of this parsing.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "inv", os.path.join(os.path.dirname(__file__), "tmd-inventory.py"))
    inv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inv)

    name = os.path.basename(path)
    m = re.match(r"(\d{14})_(.*)\.html$", name)
    ts, url = m.group(1), m.group(2).replace("_", "/")
    # recover the real url from the cached filename's shape
    url = re.sub(r"^http/", "http://", url)
    meta, err = inv.thread_meta(a.thread, ts, _url_from_cache(name, a.thread))
    if err:
        sys.exit(f"could not parse cached page: {err}")

    # Merge every cached page, de-duplicating by post id: captures overlap.
    posts, seen = [], set()
    for _, body in pages:
        for post in inv.posts_in(body):
            if post["pid"] and post["pid"] in seen:
                continue
            seen.add(post["pid"])
            posts.append(post)
    posts.sort(key=lambda p: int(p["index"] or 0))
    owner = next((p for p in posts if p["owner"]), posts[0] if posts else None)
    if not owner:
        sys.exit("no posts found on any cached page")
    replies = [p for p in posts if p is not owner]
    print(f"  merged {len(posts)} post(s) across {len(pages)} page(s)", file=sys.stderr)

    slug = _slug_from_cache(name)
    meta = dict(meta)
    meta["tid"] = a.thread
    meta["title"] = a.title or _title_from_slug(slug, meta)
    meta["date"] = (meta["posted"][:19].replace("T", " ") + " +0000") if meta["posted"] else ""
    # Every post this script produces is a thread rescued from The Mana Drain,
    # and they should be findable as a group. Deliberately NOT the existing
    # "tmd" tag: that is already in use on posts which merely cite a TMD thread
    # (tsi-the-land-2, tsi-the-land-3, serious-champ-na-vintage-2022), none of
    # which are ports. "tmd-archive" means the post IS one.
    if not a.no_archive_tag:
        tags = (a.tags or "").split()
        if "tmd-archive" not in tags:
            tags.append("tmd-archive")
        a.tags = " ".join(tags)
    meta["tags"] = a.tags

    if a.event_date:
        meta["event_date"] = a.event_date
        # The post date drives the URL; the forum posting date stays in
        # tmd_snapshot as provenance.
        #
        # Fixed at midday UTC rather than carrying the forum's posting time.
        # The site renders in America/New_York, so a thread posted at 01:04 UTC
        # became the previous day locally and the post built as
        # /posts/20171201_... for an event held on the 2nd.
        meta["date"] = a.event_date + " 12:00:00 +0000"
    text = build(meta, owner["html"], replies, fetch_images=not a.no_images,
                 deckfiles=not a.inline_decklists, event_label=a.event)
    if a.stdout or not a.out:
        print(text)
    else:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"  wrote {a.out}: {len(text)} chars, "
              f"{text.count('{% decklist %}')} decklist(s), {len(replies)} reply/replies",
              file=sys.stderr)


CDX_CACHE = os.environ.get("TMD_CACHE", "/tmp/tmd-cdx.txt")
_cdx_urls = None


def _cdx_lookup(ts, tid):
    """The real archived url for a thread, from the CDX index.

    The cache filename cannot be reversed into a url: tmd-inventory.py builds it
    with re.sub(r"[^A-Za-z0-9]+", "_", ...), which collapses "/", "?", "=" and
    "-" all into the same character. Reconstructing from it produced
    ".../topic-1738-team-serious-open-...-1-lang-en-US", which 404s, and that
    string was going into every ported post as its provenance link.
    """
    global _cdx_urls
    if _cdx_urls is None:
        _cdx_urls = {}
        try:
            with open(CDX_CACHE, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    m = re.search(r"(\d{14})\s+(\S*?/topic/(\d+)/[^\s]*)", line)
                    if m:
                        _cdx_urls.setdefault((m.group(1), m.group(3)), m.group(2))
        except OSError:
            pass
    return _cdx_urls.get((ts, str(tid)))


def _url_from_cache(name, tid=None):
    """The archived url for a cached page, from the CDX index where possible."""
    ts = re.match(r"^(\d{14})_", name)
    if ts and tid:
        hit = _cdx_lookup(ts.group(1), tid)
        if hit:
            return hit
    # Last resort, and known to be unreliable -- see _cdx_lookup.
    body = re.sub(r"^\d{14}_", "", name)[:-len(".html")]
    body = body.replace("http_www_themanadrain_com_", "http://www.themanadrain.com/")
    body = body.replace("http_themanadrain_com_", "http://themanadrain.com/")
    return body.replace("_topic_", "topic/", 1).replace("_", "-")


def _slug_from_cache(name):
    m = re.search(r"_topic_\d+_(.*)\.html$", name)
    return m.group(1).replace("_", "-") if m else ""


def _title_from_slug(slug, meta):
    words = slug.replace("-", " ").strip()
    return words[:1].upper() + words[1:]


if __name__ == "__main__":
    main()
