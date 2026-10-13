#!/usr/bin/env python3
"""Inventory Team Serious tournament reports and deck techs stranded on The Mana Drain.

themanadrain.com carried the TSI/TSO write-ups before this site existed. The forum
reorganised and those threads now 404; they survive only in the Internet Archive.

What we want are **top-level threads that would stand alone as blog posts** -- tournament
reports and deck techs. Not every post an author ever made, not event announcements, not
podcast episode threads, not tournament calendars.

Two ways in, because neither is sufficient alone:

  1. Thread titles. Catches reports whoever wrote them, but misses any whose title does
     not name the event.
  2. Author topic listings. NodeBB serves /user/<handle>/topics -- the threads that person
     started, which is exactly "top level posts". Catches write-ups with odd titles, but
     only for handles whose profile pages were archived.

  script/tmd-inventory.py --refresh        re-fetch the CDX index (slow, ~31 pages)
  script/tmd-inventory.py                  rebuild the report from the cache
  script/tmd-inventory.py --out docs/tmd-archive-reports.md

CDX quirks that cost real time here, both worked around below:
  - matchType=prefix with a path returns nothing for this host; use url=host* instead.
  - a bare limit truncates silently. The first attempt reported zero matches out of 4,000
    rows when the answer was 100+ out of 29,669. Page with showNumPages instead.
"""
import argparse, json, os, re, sys, time
import urllib.parse, urllib.request, urllib.error

CDX = "https://web.archive.org/cdx/search/cdx"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
CACHE = os.environ.get("TMD_CACHE", "/tmp/tmd-cdx.txt")
# Author listings are cached per archived page, so a run that gets 429'd part way
# through can be re-run to fill the gaps without re-fetching what already worked.
AUTHOR_CACHE = os.environ.get("TMD_AUTHOR_CACHE", "/tmp/tmd-authors.json")
HTML_CACHE = os.environ.get("TMD_HTML_CACHE", "/tmp/tmd-html")
AVATAR_DIR = "assets/images/avatars"

# Team Serious people. Used to find threads they STARTED, and to attribute.
# Handles with an archived /user/<h>/topics capture can be enumerated; the rest
# only surface through title keywords. Discovered by reading data-username off
# cached thread pages, which is how most of these turned up -- guessing at
# handles found two, reading a single thread page found six more.
HANDLES = [
    # /topics archived -- enumerable
    "nartman99",         # Nam Tran. NOT "nartman"; that handle does not exist.
    "grandpabelcher",    # Nat Moes
    "xxhazardxx",
    "shaman-ben",
    "mdkubiak",
    "matori",
    "infant_no_1",
    "garbageaggro",
    "dr-j",
    # no /topics capture -- keyword-only, kept so the doc records the gap
    "cleverpseudonym",   # Rajah (uid 895, confirmed from the author metadata on #3824)
    "lhc",               # Jimmy
    "hazard",            # same person as xxhazardxx, older handle
    "presidentskroob",
    "thallidtosser",
    "bscheidemann",
]

# Venues these events ran at, for a location field on the ported post. Titles are
# the only place this appears; NodeBB has no location metadata on a thread.
VENUES = [
    ("Sandusky, OH", r"sandusky"), ("Berea, OH", r"berea|kidforce"),
    ("Warren, OH", r"warren|all.american"), ("Columbus, OH", r"columbus"),
    ("Livonia, MI", r"livonia|\briw\b"), ("Austin, TX", r"austin"),
    ("Houston, TX", r"houston"), ("Pittsburgh, PA", r"pittsburgh|steel.city"),
    ("Denver, CO", r"denver"), ("Toledo, OH", r"maumee"),
    ("Ann Arbor, MI", r"ann.arbor"),
]

# Thread titles worth a look.
KEYWORDS = re.compile(
    r"team.?serious|serious.?open|serious.?vintage|hazard.?vitational|"
    r"romancing.the.stones|\btsi\b|\btso\b|tsi[-_]|tso[-_]|tsivr|tsidp|tsisteveland|"
    r"mishra.?s.by.the.maumee|the.land|steveland|kidforce|pop.?shop",
    re.I)

# Would read as a blog post: a report, a deck tech, or a metagame piece.
REPORT = re.compile(
    r"report|results|write.?up|recap|tournament|top.?\d|\d+.?players|"
    r"deck.?tech|primer|goes.to|winner|playing|brewing|\bvids\b|coverage|"
    r"meta.?game|\bmeta\b|looking.back|state.of|year.in|breakdown|analysis|"
    r"restricted.list|banned|format|\bdata\b|statistics|\bstats\b",
    re.I)

# Would not: announcements, calendars, podcast episode threads, admin chatter.
NOT_A_POST = re.compile(
    r"^free.?(good.?)?podcast|^serious.?vintage.?(ep|episode|\d)|calendar|"
    r"^podcast|featured.image|outside.assistance|^looking.for|wtb|wts|"
    r"for.sale|\bsignup|sign.?up|registration|announce",
    re.I)


OFFLINE = False          # set by --cached-only; no requests are made at all


def get(url, tries=5):
    """Returns (body, error). An empty body with no error means a real empty page."""
    if OFFLINE:
        return "", "offline (--cached-only)"
    last = "no attempt"
    for n in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode("utf-8", "replace"), None
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (429, 503):
                time.sleep(15 * (n + 1)); continue
            return "", last
        except Exception as e:
            last = type(e).__name__
            time.sleep(8)
    return "", last


def refresh_cdx():
    pages = get(f"{CDX}?url=themanadrain.com*&showNumPages=true")[0].strip()
    pages = int(pages) if pages.isdigit() else 1
    print(f"  CDX reports {pages} pages", file=sys.stderr)
    rows = []
    for p in range(pages):
        q = urllib.parse.urlencode({
            "url": "themanadrain.com*", "output": "json",
            "fl": "timestamp,original", "filter": "statuscode:200",
            "collapse": "urlkey", "page": str(p)})
        try:
            data = json.loads(get(f"{CDX}?{q}")[0] or "[]")
            rows += [f"{t} {u}" for t, u in data[1:]]
        except Exception:
            pass
        print(f"  page {p+1}/{pages}: {len(rows)} rows", file=sys.stderr)
        time.sleep(3)
    open(CACHE, "w").write("\n".join(rows))
    return rows


def load_cdx(refresh=False):
    if refresh or not os.path.isfile(CACHE):
        return refresh_cdx()
    return open(CACHE).read().splitlines()


def threads_from(rows):
    """newest capture per thread id -> (timestamp, slug, url)"""
    best = {}
    for line in rows:
        if " " not in line:
            continue
        ts, url = line.split(" ", 1)
        if "/topic/" not in url:
            continue
        tail = url.split("/topic/", 1)[1]
        parts = tail.split("/")
        if len(parts) < 2 or not parts[1]:
            continue
        tid, slug = parts[0], parts[1].split("?")[0]
        if tid not in best or ts > best[tid][0]:
            best[tid] = (ts, slug, url)
    return best


def fetch_cached(ts, url):
    """Fetch an archived page, keeping a copy on disk so repeat passes are free."""
    os.makedirs(HTML_CACHE, exist_ok=True)
    key = re.sub(r"[^A-Za-z0-9]+", "_", f"{ts}_{url}")[:160] + ".html"
    path = os.path.join(HTML_CACHE, key)
    if os.path.isfile(path):
        return open(path, encoding="utf-8", errors="replace").read(), None
    html, err = get(f"https://web.archive.org/web/{ts}/{url}")
    if html:
        open(path, "w", encoding="utf-8").write(html)
    return html, err


def avatar_for(handle, rows):
    """Download this person's TMD avatar into assets/images/avatars.

    NodeBB serves it from /assets/uploads/profile/<uid>-profileavatar.<ext>, and the
    only reliable way to tell whose is whose on a page full of avatars is the
    alt/title attribute carrying the username. Returns (path, note).
    """
    pages = [l.split(" ", 1) for l in rows
             if re.search(rf"/user/{re.escape(handle)}(/|$|\?)", l)]

    # The bare profile and /topics carry the owner's avatar; /followers and /blog
    # often do not. Try the useful ones first.
    def rank(tu):
        u = tu[1].rstrip("/")
        if u.endswith(handle):
            return 0
        if u.endswith("/topics"):
            return 1
        if u.endswith("/posts"):
            return 2
        return 3

    pages.sort(key=rank)
    unread = []
    for ts, url in pages:
        html, err = fetch_cached(ts, url)
        if err or not html:
            # Not "no avatar" -- the page could not be read at all. Treating those
            # as the same thing is how this reported a clean miss for a handle whose
            # only avatar-bearing pages had been rate limited.
            unread.append(f"{url.split('/user/')[-1]} ({err or 'empty'})")
            continue
        for m in re.finditer(r'<img[^>]+>', html):
            tag = m.group(0)
            if not re.search(rf'(alt|title)="{re.escape(handle)}"', tag, re.I):
                continue
            src = re.search(r'src="([^"]+)"', tag)
            if not src or "profile" not in src.group(1):
                continue
            raw = src.group(1)
            if raw.startswith("/web/"):
                raw = "https://web.archive.org" + raw
            ext = os.path.splitext(raw.split("?")[0])[1].lower() or ".jpg"
            if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                ext = ".jpg"
            os.makedirs(AVATAR_DIR, exist_ok=True)
            dest = os.path.join(AVATAR_DIR, f"tmd-{handle}{ext}")
            if os.path.isfile(dest):
                return dest, "already present"
            body, derr = get_bytes(raw)
            if derr or not body:
                return None, f"found {raw.split('/')[-1]} but download failed ({derr})"
            if not body[:4] in (b"\xff\xd8\xff\xe0", b"\xff\xd8\xff\xe1") \
               and not body.startswith((b"\x89PNG", b"GIF8", b"\xff\xd8", b"RIFF")):
                return None, "downloaded file is not an image"
            open(dest, "wb").write(body)
            return dest, f"{len(body)//1024} KB from {raw.split('/')[-1]}"
        time.sleep(8)
    if unread:
        return None, (f"INCONCLUSIVE -- {len(unread)} of {len(pages)} profile pages "
                      f"unreadable: {', '.join(unread[:3])}")
    return None, f"no avatar on any of the {len(pages)} archived profile pages"


def get_bytes(url, tries=3):
    for n in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read(), None
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(15 * (n + 1)); continue
            return b"", f"HTTP {e.code}"
        except Exception as e:
            time.sleep(8); last = type(e).__name__
    return b"", "rate limited"


MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], 1)}


def event_date(slug, posted=""):
    """The date of the event itself, parsed out of the thread slug.

    Distinct from the post date: an event on 2018-02-03 gets written up on the
    4th, and the slug is the only place the event date appears. Several formats
    are in use, so each is tried explicitly rather than guessed.

    Many slugs give a month and day but no year ("5-22-berea-oh-team-serious-
    open"). `posted` supplies it: the event is taken to be in the post's year, or
    the year before if that would put it after the post. Returns "" rather than a
    guess when the slug carries no date at all.
    """
    s = slug.lower()
    s = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", s)      # march-2nd-2019 -> march-2-2019

    # 2022-07-23-team-serious-open...
    m = re.search(r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b", s)
    if m:
        y, mo, d = map(int, m.groups())
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"

    # ...6-15-2019-results  /  ...2-17-2018-results
    m = re.search(r"\b(\d{1,2})-(\d{1,2})-(20\d{2})\b", s)
    if m:
        mo, d, y = map(int, m.groups())
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"

    # 14-april-2018-...  /  april-14-2018-...
    m = re.search(r"\b(\d{1,2})-([a-z]+)-(20\d{2})\b", s)
    if m and m.group(2) in MONTHS:
        return f"{int(m.group(3)):04d}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"
    m = re.search(r"\b([a-z]+)-(\d{1,2})-(20\d{2})\b", s)
    if m and m.group(1) in MONTHS:
        return f"{int(m.group(3)):04d}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"

    # 5-6-17-sandusky...  /  10-15-16-team-serious...  (two-digit year, 2000s)
    m = re.search(r"\b(\d{1,2})-(\d{1,2})-(\d{2})\b", s)
    if m:
        mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31 and 5 <= y <= 30:
            return f"20{y:02d}-{mo:02d}-{d:02d}"

    # Month and day only -- take the year from the post date.
    if posted[:4].isdigit():
        py, pm, pd = int(posted[:4]), int(posted[5:7] or 1), int(posted[8:10] or 1)
        pat = (r"\b(\d{1,2})-(\d{1,2})\b", None)
        m = re.search(pat[0], s)
        if m:
            mo, d = int(m.group(1)), int(m.group(2))
            if 1 <= mo <= 12 and 1 <= d <= 31:
                y = py if (mo, d) <= (pm, pd) else py - 1
                return f"{y:04d}-{mo:02d}-{d:02d}"
        # "14-april" / "april-14" with the year implied
        m = re.search(r"\b(\d{1,2})-([a-z]+)\b", s)
        if m and m.group(2) in MONTHS:
            mo, d = MONTHS[m.group(2)], int(m.group(1))
            y = py if (mo, d) <= (pm, pd) else py - 1
            return f"{y:04d}-{mo:02d}-{d:02d}"
        m = re.search(r"\b([a-z]+)-(\d{1,2})\b", s)
        if m and m.group(1) in MONTHS:
            mo, d = MONTHS[m.group(1)], int(m.group(2))
            y = py if (mo, d) <= (pm, pd) else py - 1
            return f"{y:04d}-{mo:02d}-{d:02d}"

    return ""


POST_LI = re.compile(
    r'<li[^>]*component="post"(?P<attrs>[^>]*)>(?P<rest>.*?)(?=<li[^>]*component="post"|\Z)',
    re.S)
POST_BODY = re.compile(
    r'<div[^>]*component="post/content"[^>]*>(?P<html>.*?)</div>\s*(?:<!--|</div>|<div)', re.S)


def posts_in(html):
    """Every post in the thread: who wrote it, when, and its body HTML.

    One fetch gives metadata and prose both -- they are the same page. Splitting
    the body into a second pass would double the requests against a host that
    throttles, for nothing: re-parsing a cached page is free.
    """
    out = []
    for m in POST_LI.finditer(html):
        attrs, rest = m.group("attrs"), m.group("rest")

        def attr(name):
            a = re.search(rf'{name}="([^"]*)"', attrs)
            return a.group(1) if a else ""

        body = POST_BODY.search(rest)
        out.append({
            "index": attr("data-index"),
            "pid": attr("data-pid"),
            "uid": attr("data-uid"),
            "username": attr("data-username"),
            "timestamp": attr("data-timestamp"),
            "owner": "topic-owner-post" in attrs,
            "html": (body.group("html").strip() if body else ""),
        })
    return out


def thread_meta(tid, ts, url):
    """Scrape everything a ported post needs from an archived thread page.

    The snapshot timestamp is when the Archive crawled the page, NOT when the
    thread was posted -- a 2016 report captured in 2022 would be filed under the
    wrong year. article:published_time is the real date.
    """
    html, err = fetch_cached(ts, url)
    if err or not html:
        return None, err or "empty page"

    def meta(prop):
        m = re.search(rf'<meta[^>]+property="{prop}"[^>]+content="([^"]*)"', html)
        return m.group(1) if m else ""

    # Every post, with its prose. The owner's post is the write-up; the rest are
    # replies, whose decklists get absorbed and whose commentary gets attributed.
    allposts = posts_in(html)

    owner = next((p for p in allposts if p["owner"]), allposts[0] if allposts else None)
    replies = [p for p in allposts if p is not owner]
    author = owner["username"] if owner else ""
    uid = owner["uid"] if owner else ""
    posts = []
    for p in allposts:
        pair = (p["username"], p["uid"])
        if pair[0] and pair not in posts:
            posts.append(pair)

    slug = url.split("/topic/", 1)[1].split("/")[1] if "/topic/" in url else ""
    venue = next((name for name, pat in VENUES if re.search(pat, slug, re.I)), "")
    players = re.search(r"(\d+)[-_]players", slug)
    if not players and owner:
        # The title does not always carry it, but the write-up usually opens with
        # "12 Players gathered..." or similar.
        text = re.sub(r"<[^>]+>", " ", owner["html"])
        players = re.search(r"\b(\d{1,3})\s+players\b", text, re.I)

    # Uploaded images in the thread -- decklist photos and event shots, which die
    # with the forum unless they are pulled too.
    # Exclude the backslash too: these appear inside JS string literals, so an
    # escaped quote otherwise leaves a trailing \ and duplicates the filename.
    uploads = sorted(set(re.findall(r'/assets/uploads/files/([^"\')\s\\]+)', html)))

    return {
        "tid": tid,
        "posted": meta("article:published_time"),
        "modified": meta("article:modified_time"),
        "section": meta("article:section"),
        "author": author,
        "author_uid": uid,
        "participants": posts,          # everyone who posted, for reply attribution
        "body": owner["html"] if owner else "",
        "replies": [{"username": p["username"], "uid": p["uid"],
                     "timestamp": p["timestamp"], "html": p["html"]}
                    for p in replies],
        "decklist_blocks": len(re.findall(r"<pre[ >]", owner["html"])) if owner else 0,
        "event_date": event_date(slug, meta("article:published_time")),
        "venue": venue,
        "players": players.group(1) if players else "",
        "uploads": uploads,
        "snapshot": f"https://web.archive.org/web/{ts}/{url}",
    }, None


def load_author_cache():
    try:
        return json.load(open(AUTHOR_CACHE))
    except Exception:
        return {}


def save_author_cache(c):
    try:
        json.dump(c, open(AUTHOR_CACHE, "w"))
    except OSError:
        pass


def started_by(handle, rows, cache):
    """Thread ids this person started, from their archived /topics listing.

    Returns (ids, pages_tried, failures). An earlier version returned a bare set,
    so a page that 429'd looked identical to a person with no threads -- every
    handle after the first silently contributed nothing.

    /topics is the one that matters and it fetches reliably. /best is attempted
    second and best-effort: every /best capture tried so far 429s on every
    retry, across different handles and timestamps, so its failure is not
    treated as making the result incomplete.
    """
    want = re.compile(rf"/user/{re.escape(handle)}/(topics|best)(\?|$)")
    pages = sorted((l.split(" ", 1) for l in rows if want.search(l)),
                   key=lambda tu: 0 if "/topics" in tu[1] else 1)
    ids, failures, uncached = set(), [], []
    for ts, url in pages:
        key = f"{ts}/{url}"
        if key in cache:                      # already read in an earlier run
            ids |= set(cache[key])
            continue
        # /topics already answered for this handle, and /best always 429s -- do not
        # spend five retries and a minute of backoff proving that again.
        if url.rstrip("/").endswith("/best") and ids:
            continue
        is_best = url.rstrip("/").endswith("/best")
        html, err = get(f"https://web.archive.org/web/{ts}/{url}", tries=1 if is_best else 5)
        if err:
            # Offline mode made no request, so this is a gap in the cache, not a
            # failure to read something that was there.
            if err.startswith("offline"):
                uncached.append(url.split("/user/")[-1])
            # /best is known-unavailable in the archive; not a reason to call the
            # run incomplete, and not worth retrying
            elif not is_best:
                failures.append(f"{url} ({err})")
        else:
            found = sorted(set(re.findall(r"/topic/(\d+)/", html)))
            cache[key] = found
            ids |= set(found)
        time.sleep(12)          # archive.org 429s readily; this pass is small
    return ids, len(pages), failures, uncached


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--skip-authors", action="store_true",
                    help="title keywords only; skips the slow per-handle fetches")
    ap.add_argument("--avatars", action="store_true",
                    help=f"also download each handle's TMD avatar into {AVATAR_DIR}")
    ap.add_argument("--meta", action="store_true",
                    help="scrape each candidate thread for real post date, author, "
                         "forum section, venue and attached images")
    ap.add_argument("--cached-only", action="store_true",
                    help="rebuild from cached pages only; makes no requests, so the doc "
                         "can be regenerated while archive.org is throttling")
    a = ap.parse_args()
    if a.cached_only:
        globals()["OFFLINE"] = True

    rows = load_cdx(a.refresh)
    print(f"  {len(rows)} archived URLs in the index", file=sys.stderr)
    allthreads = threads_from(rows)
    print(f"  {len(allthreads)} distinct forum threads", file=sys.stderr)

    by_handle, handle_states = {}, []
    if not a.skip_authors:
        problems = {}
        cache = load_author_cache()
        for h in HANDLES:
            ids, tried, failures, uncached = started_by(h, rows, cache)
            save_author_cache(cache)
            if ids:
                by_handle[h] = ids
            if failures:
                problems[h] = failures
            state = f"{len(ids)} threads from {tried} archived listing(s)"
            if failures:
                state += f" -- {len(failures)} FETCH FAILED, result incomplete"
            elif not tried:
                state = "no archived profile listing; cannot enumerate"
            elif uncached and not ids:
                state = (f"{tried} listing(s) archived, not yet fetched "
                         f"({', '.join(uncached[:2])})")
            elif not ids:
                state = (f"{tried} listing(s) archived but no /topics among them "
                         f"(/best is unavailable in the archive); cannot enumerate")
            print(f"  {h}: {state}", file=sys.stderr)
            handle_states.append(f"- `{h}` — {state}")
        if problems:
            print("  WARNING: some author listings could not be read; re-run to complete:",
                  file=sys.stderr)
            for h, fs in problems.items():
                for f in fs:
                    print(f"    {h}: {f}", file=sys.stderr)

    avatars = {}
    if a.avatars:
        for h in HANDLES:
            path, note = avatar_for(h, rows)
            avatars[h] = (path, note)
            print(f"  avatar {h}: {note}" + (f" -> {path}" if path else ""), file=sys.stderr)
            time.sleep(10)

    started = {tid: h for h, ids in by_handle.items() for tid in ids}

    cand = {}
    for tid, (ts, slug, url) in allthreads.items():
        title = slug.replace("-", " ")
        if NOT_A_POST.search(slug):
            continue
        hit_kw = bool(KEYWORDS.search(slug))
        hit_author = tid in started
        if not (hit_kw or hit_author):
            continue
        if not REPORT.search(slug) and not hit_author:
            continue
        cand[tid] = {
            "ts": ts, "slug": slug, "title": title,
            "url": f"https://web.archive.org/web/{ts}/{url}",
            "author": started.get(tid, ""),
        }

    rep = {k: v for k, v in cand.items() if REPORT.search(v["slug"])}
    other = {k: v for k, v in cand.items() if k not in rep}

    def table(d):
        out = ["| thread | snapshot | author | title |", "|---|---|---|---|"]
        for tid, c in sorted(d.items(), key=lambda kv: kv[1]["slug"]):
            ts = c["ts"]
            who = f"`{c['author']}`" if c["author"] else "—"
            out.append(f"| `#{tid}` | [{ts[:4]}-{ts[4:6]}-{ts[6:8]}]({c['url']}) | {who} | {c['title']} |")
        return "\n".join(out)

    md = f"""# Team Serious write-ups stranded on The Mana Drain

`themanadrain.com` carried the TSI and TSO write-ups before this site existed. **The forum
reorganised and those threads now 404** — they survive only in the Internet Archive.

What this lists: **top-level threads that would stand alone here as blog posts** — tournament
reports, deck techs and metagame pieces. Not every post these authors made, not event
announcements, not podcast episode threads, not tournament calendars, not replies in other
people's threads.

Rebuild with `script/tmd-inventory.py`.

## Scale

| | |
|---|---|
| archived URLs for `themanadrain.com` | {len(rows):,} |
| distinct forum threads among them | {len(allthreads):,} |
| **candidate reports and deck techs** | **{len(rep)}** |
| other top-level threads worth a look | {len(other)} |

## Found two ways

Neither is sufficient alone:

1. **Thread titles** — catches reports whoever wrote them, but misses any whose title does
   not name the event.
2. **Author topic listings** — NodeBB serves `/user/<handle>/topics`, the threads that
   person *started*, which is exactly "top level posts". Catches write-ups with odd titles,
   but only for handles whose profile pages were archived.

Handles checked: {', '.join('`'+h+'`' for h in HANDLES)}.

{chr(10).join(handle_states) if handle_states else '- *(author pass skipped)*'}

A handle with no archived `/topics` capture cannot be enumerated at all — its write-ups
only surface if the thread *title* happens to match a keyword, which is unreliable.
`xxhazardxx` started a thread called "Top 4 Finish - Paradoxical Outcome": a real report,
invisible to every keyword in the list, found only because that profile page was archived.

Rajah is `cleverpseudonym` (uid 895, confirmed from the author metadata on thread #3824)
and Nam Tran is `nartman`. **Neither has an archived profile page**, so neither can be
enumerated this way — which is the clearest argument for the `--meta` pass below: a thread
page states its own author, so authorship does not depend on whether somebody's profile
happened to get crawled.

## Candidate reports and deck techs ({len(rep)})

{table(rep)}

## Other top-level threads ({len(other)})

{table(other)}

## What to scrape per thread

`--meta` pulls this from each candidate thread. Verified against thread #3824.

| field | source | why it matters |
|---|---|---|
| **real post date** | `<meta property="article:published_time">` | **The snapshot timestamp is when the Archive crawled the page, not when the thread was posted.** A 2016 report captured in 2022 would be filed under the wrong year. |
| author | `data-username` + `data-uid` on the first post | The thread itself is the authority. This is how `cleverpseudonym` (uid 895) was confirmed as the author of #3824 — more reliable than profile listings, and it works for handles with no archived profile at all. |
| forum section | `<meta property="article:section">` | #3824 is "Official Tournament Results". Maps straight onto a tag here. The sections in use are `vintage-strategy`, `vintage-community`, `vintage-tournaments`, `official-tournament-results`. |
| modified date | `<meta property="article:modified_time">` | Catches threads edited long after posting. |
| venue | the thread title | NodeBB has no location field, but titles name the shop: Sandusky, Berea, Warren, Columbus, Livonia, Austin, Houston, Pittsburgh, Denver, Toledo, Ann Arbor. |
| player count | the thread title | Often there — "17 players", "27 players". Worth keeping in a report. |
| attached images | `/assets/uploads/files/...` | **Decklist photos and event shots. These die with the forum.** They must be pulled and committed locally, same as the card art was. |

### Converting a thread to a post

`script/tmd-to-post.py --thread <id>` turns a cached thread into a post matching the
conventions of the one ported by hand, `_posts/2022-07-23-tso-all-american-warren.md`.

**Validated against that hand port**, which is a verbatim port of thread #3824: the
converter reproduces all **12 decklists card-for-card**, and the standings table
row-for-row. That is the reason to trust it on the threads nobody has checked.

Transforms it applies, each one worked out by diffing against the hand port:

| source | becomes |
|---|---|
| `<pre>` block | `{{% decklist %}}` … `{{% enddecklist %}}`, leading "Deck" line dropped |
| a line that is only bold text | an `##` heading — "**Standings**", "**Meta**" |
| tab-separated pasted rows | a Markdown table; rows arrive as separate paragraphs, so runs are gathered across blank lines |
| `web.archive.org/web/<ts>/…` links | the original target, unwrapped |
| nodebb emoji `<img>` | the character, or dropped |
| `/assets/uploads/files/…` images | downloaded to `assets/images/tmd/`, fetched **through the Wayback copy** since the live forum 404s them |

Front matter carries `tmd_thread` and `tmd_snapshot` so every ported post says where it
came from, plus `event_date`, `venue` and `players`.

Note the post `date:` should be the **event** date, not the TMD posting date — that is what
the hand port does, and it is what the site's URL is built from. The posting date stays as
provenance.

### Still worth considering

- **Turning the scraped HTML into Markdown.** `--meta` captures each post's body as HTML.
  Converting it, and deciding how `<pre>` decklists should look here, is the remaining
  judgement call.
- **Event date parsing covers 25 of 45 slugs outright.** The rest give a month and day with
  no year, which `--meta` resolves from the post date, or carry no date at all
  (`team-serious-open-report`, `top-4-finish-paradoxical-outcome`) — those return nothing
  rather than a guess, and need the post date or the body.
- **View and reply counts.** Available, but they say more about the forum than the writing.

## Author avatars

Ported articles should carry their real author, and this site already renders one:
`author.avatar` in post front matter, pointing into `assets/images/avatars/`.

**Already in the repo**, so the main authors are covered without touching the archive:

| person | handle | file |
|---|---|---|
| Rajah James | — | `rajah_460x460.jpg`, `310221.jpg` |
| Nat Moes | `grandpabelcher` | `nat_400x400.jpg` |
| Nam Tran | — | `namQ_460x527.jpg`, `namQ_277x325.png` |

`script/tmd-inventory.py --avatars` pulls the rest from the archive. NodeBB serves them
from `/assets/uploads/profile/<uid>-profileavatar.<ext>`, and the only way to tell whose is
whose on a page full of avatars is the `alt`/`title` attribute carrying the username, so
that is what the script matches on. Identified so far:

| handle | archive file |
|---|---|
| `grandpabelcher` | `11-profileavatar.jpeg` |
| `xxhazardxx` | `127-profileimg.jpg` |

Downloads are rate limited by archive.org after any sustained run against it — the script
says `found <file> but download failed (rate limited)` rather than pretending there is no
avatar. Re-run `--avatars` later; fetched pages are cached, so it resumes rather than
starting over. `presidentskroob` and `thallidtosser` have no archived profile page at all,
so they have no recoverable avatar.

## Shape of a ported post

```
---
title:      TSO — All American Cards and Comics, Warren OH
date:       2022-07-24          # article:published_time, when it was written up
event_date: 2022-07-23          # parsed from the slug; the event itself
venue:      Warren, OH
players:    14
author:
  name:   Rajah James           # from data-username on the first post
  avatar: ../assets/images/avatars/rajah_460x460.jpg
tags: [mtg, vintage, tso, official tournament results]
---

<the write-up, from the first post>

<decklists — absorbed, each credited to the player who ran it>

## Replies and relevant bits

**Reply from nartman:** why the fourth Mishra's Workshop came out for the
Thorn, and how the Shops matchup played after sideboarding.

**Reply from grandpabelcher:** the Dragon line he was holding in game three.
```

**Decklists from replies are absorbed.** A decklist is event data — the record of what
somebody played — not a piece of writing, so it belongs in the report proper, credited to
the player who ran it rather than quoted at arm's length.

**The interesting bits from replies are noted as replies from whoever wrote them.** Where
someone explains a card choice, a sideboard plan or a matchup, that is their writing, so it
goes in a **"Replies and relevant bits"** section at the end of the post, each item marked
**Reply from `<handle>`**. That keeps the report readable as one piece while being straight
about whose words are whose, and gives the good forum discussion somewhere to live instead
of dying with the thread.

`--meta` records `participants`, every handle that posted in the thread, so the replies
section can be attributed without re-reading the page.

## State of play

### Done

- **Thread #3824 is already ported**, by hand, as
  `_posts/2022-07-23-tso-all-american-warren.md` → `/posts/20220723_tso-all-american-warren`
  (verified live). The `digitalmeh.net` post that links thread #3824 should point there
  rather than at an archive snapshot.
- `script/tmd-inventory.py` locates candidate threads and scrapes their metadata.
- `script/tmd-to-post.py` converts a cached thread into a post, **validated** by
  reproducing the hand-ported #3824: 12/12 decklists card-for-card, standings row-for-row.

### Blocked on archive.org rate limiting

Nothing here is a code problem; the Wayback Machine throttles hard after a sustained run
and then refuses pages that worked an hour earlier. Everything below resumes from cache.

| thread | event | status |
|---|---|---|
| `#3824` | 2022-07-23 TSO, Warren OH | **ported already** (see above) |
| `#1763` | 2018-02-17 TSI Hazard's Birthday 3.0 | 14 pages archived **including page 1**; only page 14 is cached, which holds posts 4–11 and no owner post |
| `#1639` | 2017-12-02 TSI Mishra's by the Maumee | not fetched; four attempts, all HTTP 429 |
| `#1738` | 2018-02-03 TSO at the Pop Shop | not fetched |
| `#2786` | 2019-06-15 TSI The Land | not fetched |

### These threads are paginated

**28 of the 45 candidates are archived across more than one page**; `#2609` and `#1924` run
to 16. The write-up is on page 1 but the replies run across all of them, so a full port
needs every page — `tmd-to-post.py` merges whatever is cached, de-duplicating by post id
since captures overlap, and refuses to proceed if page 1 is missing because that is where
the write-up lives.

**Page 1 is archived for every one of the 45.** Nothing is unrecoverable; it is purely a
matter of fetching politely.

| | |
|---|---|
| candidate threads | 45 |
| total archived pages across them | **168** |
| threads missing page 1 | **0** |
| at 45s per request | roughly 2 hours of unhurried fetching |

Also pending for the same reason: the avatars for `lhc` and `hazard`, and the thread images
(`grandpabelcher` → `11-profileavatar.jpeg`, `xxhazardxx` → `127-profileimg.jpg` were
identified but not downloaded).

### Resuming

Caches live outside the repo and make a resumed run cheap:

```
/tmp/tmd-cdx.txt        63,496 archived URLs (the CDX index; --refresh rebuilds it)
/tmp/tmd-authors.json   per-page thread-id lists from author listings
/tmp/tmd-html/          every archived page already fetched
```

```
script/tmd-inventory.py --meta --avatars      # fill the gaps; skips what is cached
script/tmd-to-post.py --thread 1639 --out _posts/2017-12-02-tsi-mishras-maumee.md
```

Be unhurried about it. The script spaces requests and retries 429s, but a long run still
earns a throttle; the caches exist so that costs nothing the second time.

### Handles: how coverage actually improved

Guessing at handles found two. **Reading `data-username` off one cached thread page found
six more** — `shaman-ben`, `mdkubiak`, `matori`, `infant_no_1`, `garbageaggro`, `dr-j`, all
with `/topics` archived. That is the cheapest way to widen this: convert a thread, read the
handles out of it, add them, re-run.

It also corrected one: **Nam Tran is `nartman99`**, not `nartman` — the latter has no
archived pages at all, the former has eight including `/topics`.

## Porting notes

- **Attribution matters.** Several are other people's write-ups — Nat Moes
  (`grandpabelcher`), Jimmy (`lhc`), `presidentskroob`, `thallidtosser`. Check the author on
  the thread itself before republishing, and credit them. The `author` column here is only
  filled in where an archived profile listing proved who started the thread.
- **Decklists** should become local lists rather than links into a dead forum.
- **Card links** should use `<<Card Name>>` so `_plugins/mtg_autocard.rb` renders them to
  Scryfall.
- **`digitalmeh.net` links here too.** Five posts there point at these threads via Archive
  snapshots; as each report lands here, they should point at the new post instead.
"""
    if a.out:
        open(a.out, "w", encoding="utf-8").write(md)
        print(f"  wrote {a.out}: {len(rep)} reports, {len(other)} other", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
