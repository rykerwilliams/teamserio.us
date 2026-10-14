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
import argparse, html as htmllib, os, re, sys

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
    cells = [[c.strip() for c in r.split("\t")] for r in rows]
    width = max(len(c) for c in cells)
    cells = [c + [""] * (width - len(c)) for c in cells]
    head, body = cells[0], cells[1:]
    out = ["| " + " | ".join(head) + " |",
           "|" + "|".join("---" for _ in head) + "|"]
    for r in body:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


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
        if "\t" in ln:
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
    return s.strip()


def split_pres(body_html):
    """Split a post body into (markdown, decklist) chunks in document order."""
    parts, last = [], 0
    for m in re.finditer(r"<pre[^>]*>(.*?)</pre>", body_html, re.S | re.I):
        if m.start() > last:
            parts.append(("md", body_html[last:m.start()]))
        inner = re.sub(r"<[^>]+>", "", m.group(1))
        parts.append(("deck", htmllib.unescape(inner)))
        last = m.end()
    if last < len(body_html):
        parts.append(("md", body_html[last:]))
    return parts


DECK_DIR = "assets/files"


def author_entry(handle):
    """AUTHORS lookup that tolerates the forum's inconsistent handle casing."""
    if not handle:
        return {}
    if handle in AUTHORS:
        return AUTHORS[handle]
    low = handle.lower()
    for k, v in AUTHORS.items():
        if k.lower() == low:
            return v
    return {}


def deck_lines(text):
    """The card lines of a <pre> block, with the source's leading 'Deck' dropped."""
    lines = [l.rstrip() for l in text.strip().splitlines()]
    while lines and lines[0].strip().lower() in ("deck", "deck:", ""):
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


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
    head = [l for l in lines[:4]]

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
                return str(rank), parts[1], parts[2], lines[1:]

    # 3. "# Deck (1st)" + "## Player"
    if len(head) >= 2 and head[0].lstrip().startswith("#"):
        deck = re.sub(r"^#+\s*", "", head[0]).strip()
        rank = None
        m = re.search(r"\((\d+)(?:st|nd|rd|th)\)\s*$", deck, re.I)
        if m:
            rank = m.group(1)
            deck = deck[:m.start()].strip()
        player = re.sub(r"^#+\s*", "", head[1]).strip() if head[1].lstrip().startswith("#") else None
        body = lines[2:] if player else lines[1:]
        while body and body[0].strip().lower().rstrip(":") in ("main deck", "maindeck", "deck"):
            body = body[1:]
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
        if l.strip().lower().rstrip(":") == "sideboard":
            cur = side
            continue
        if not l.strip():
            continue
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

    if replies:
        body += "\n\n## Replies and relevant bits\n"
        for r in replies:
            # Someone posting their list in a reply is still a decklist, and
            # dropping it loses content the thread had -- #1738 has one that
            # belongs to nobody in the top five. Write it as a file like any
            # other, credited to whoever posted it.
            reply_decks = []
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
                reply_decks.append("{%% deckfile %s %%}" % rpath)
            prose = md_from(re.sub(r"<pre[^>]*>.*?</pre>", "", r["html"], flags=re.S | re.I))
            if not prose.strip() and not reply_decks:
                continue
            body += f'\n**Reply from {r["username"]}:**\n\n'
            if prose.strip():
                body += f"{prose}\n"
            for d in reply_decks:
                body += f"\n{d}\n"
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

    return front_matter(meta) + "\n\n" + body + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--thread", required=True)
    ap.add_argument("--out")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--title")
    ap.add_argument("--tags", default="vintage tournament-writeup")
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
    meta, err = inv.thread_meta(a.thread, ts, _url_from_cache(name))
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
    meta["tags"] = a.tags

    if a.event_date:
        meta["event_date"] = a.event_date
        # The post date drives the URL; the forum posting date stays in
        # tmd_snapshot as provenance.
        meta["date"] = a.event_date + meta.get("date", "")[10:]
    text = build(meta, owner["html"], replies, fetch_images=not a.no_images,
                 deckfiles=not a.inline_decklists, event_label=a.event)
    if a.stdout or not a.out:
        print(text)
    else:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"  wrote {a.out}: {len(text)} chars, "
              f"{text.count('{% decklist %}')} decklist(s), {len(replies)} reply/replies",
              file=sys.stderr)


def _url_from_cache(name):
    """Rebuild the archived url from the cache filename tmd-inventory.py wrote."""
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
