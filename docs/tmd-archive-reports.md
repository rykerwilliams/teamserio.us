# Team Serious write-ups stranded on The Mana Drain

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
| archived URLs for `themanadrain.com` | 63,496 |
| distinct forum threads among them | 2,920 |
| **candidate reports and deck techs** | **39** |
| other top-level threads worth a look | 6 |

## Found two ways

Neither is sufficient alone:

1. **Thread titles** — catches reports whoever wrote them, but misses any whose title does
   not name the event.
2. **Author topic listings** — NodeBB serves `/user/<handle>/topics`, the threads that
   person *started*, which is exactly "top level posts". Catches write-ups with odd titles,
   but only for handles whose profile pages were archived.

Handles checked: `nartman99`, `grandpabelcher`, `xxhazardxx`, `shaman-ben`, `mdkubiak`, `matori`, `infant_no_1`, `garbageaggro`, `dr-j`, `cleverpseudonym`, `lhc`, `hazard`, `presidentskroob`, `thallidtosser`, `bscheidemann`.

- `nartman99` — 2 listing(s) archived, not yet fetched (nartman99/topics, nartman99/best)
- `grandpabelcher` — 18 threads from 2 archived listing(s)
- `xxhazardxx` — 6 threads from 2 archived listing(s)
- `shaman-ben` — 2 listing(s) archived, not yet fetched (shaman-ben/topics, shaman-ben/best)
- `mdkubiak` — 2 listing(s) archived, not yet fetched (mdkubiak/topics, mdkubiak/best)
- `matori` — 2 listing(s) archived, not yet fetched (matori/topics, matori/best)
- `infant_no_1` — 2 listing(s) archived, not yet fetched (infant_no_1/topics, infant_no_1/best)
- `garbageaggro` — 2 listing(s) archived, not yet fetched (garbageaggro/topics, garbageaggro/best)
- `dr-j` — 2 listing(s) archived, not yet fetched (dr-j/topics, dr-j/best)
- `cleverpseudonym` — no archived profile listing; cannot enumerate
- `lhc` — no archived profile listing; cannot enumerate
- `hazard` — 1 listing(s) archived but no /topics among them (/best is unavailable in the archive); cannot enumerate
- `presidentskroob` — no archived profile listing; cannot enumerate
- `thallidtosser` — no archived profile listing; cannot enumerate
- `bscheidemann` — no archived profile listing; cannot enumerate

A handle with no archived `/topics` capture cannot be enumerated at all — its write-ups
only surface if the thread *title* happens to match a keyword, which is unreliable.
`xxhazardxx` started a thread called "Top 4 Finish - Paradoxical Outcome": a real report,
invisible to every keyword in the list, found only because that profile page was archived.

Rajah is `cleverpseudonym` (uid 895, confirmed from the author metadata on thread #3824)
and Nam Tran is `nartman`. **Neither has an archived profile page**, so neither can be
enumerated this way — which is the clearest argument for the `--meta` pass below: a thread
page states its own author, so authorship does not depend on whether somebody's profile
happened to get crawled.

## Candidate reports and deck techs (39)

| thread | snapshot | author | title |
|---|---|---|---|
| `#2347` | [2022-01-16](https://web.archive.org/web/20220116101516/http://www.themanadrain.com/topic/2347/1-13-19-team-serious-open-at-the-pop-shop-results/1?lang=en-US) | — | 1 13 19 team serious open at the pop shop results |
| `#702` | [2020-11-01](https://web.archive.org/web/20201101002038/http://www.themanadrain.com/topic/702/10-15-16-team-serious-open-results-sandusky-oh-top4/2) | — | 10 15 16 team serious open results sandusky oh top4 |
| `#1861` | [2019-08-25](https://web.archive.org/web/20190825231254/http://themanadrain.com/topic/1861/14-april-2018-romancing-the-stones-3-27-players-in-austin-tx) | — | 14 april 2018 romancing the stones 3 27 players in austin tx |
| `#2424` | [2019-08-18](https://web.archive.org/web/20190818094624/http://www.themanadrain.com/topic/2424/2-9-2019-proxy-vintage-team-serious-open-at-kidforce-berea-oh-results/) | — | 2 9 2019 proxy vintage team serious open at kidforce berea oh results |
| `#3824` | [2023-02-05](https://web.archive.org/web/20230205014206/http://themanadrain.com/topic/3824/2022-07-23-team-serious-open-all-american-cards-and-comics-warren-oh-results/1?lang=en-US) | — | 2022 07 23 team serious open all american cards and comics warren oh results |
| `#3862` | [2022-12-07](https://web.archive.org/web/20221207071535/http://www.themanadrain.com/topic/3862/2022-09-17-team-serious-open-all-american-cards-and-comics-warren-oh-results/1?lang=en-US) | — | 2022 09 17 team serious open all american cards and comics warren oh results |
| `#1776` | [2019-09-15](https://web.archive.org/web/20190915163412/http://themanadrain.com/topic/1776/24-february-2018-romancing-the-stones-pt-2-17-players/2) | — | 24 february 2018 romancing the stones pt 2 17 players |
| `#2106` | [2020-10-20](https://web.archive.org/web/20201020150233/http://www.themanadrain.com/topic/2106/25-august-2018-romancing-the-stones-6-23-players-in-austin-tx/4) | — | 25 august 2018 romancing the stones 6 23 players in austin tx |
| `#1952` | [2021-01-28](https://web.archive.org/web/20210128042816/http://www.themanadrain.com/topic/1952/27-may-2018-romancing-the-stones-4-24-players-in-austin-tx/5) | — | 27 may 2018 romancing the stones 4 24 players in austin tx |
| `#2172` | [2022-05-25](https://web.archive.org/web/20220525093419/http://www.themanadrain.com/topic/2172/29-september-2018-romancing-the-stones-7-18-players-in-austin-tx/1?lang=en-US) | — | 29 september 2018 romancing the stones 7 18 players in austin tx |
| `#2470` | [2021-09-22](https://web.archive.org/web/20210922025716/http://www.themanadrain.com/topic/2470/3-16-2019-m-tg-proxy-vintage-team-serious-open-at-pop-shop-sandusky-oh-results/1) | — | 3 16 2019 m tg proxy vintage team serious open at pop shop sandusky oh results |
| `#1089` | [2022-05-28](https://web.archive.org/web/20220528045839/http://www.themanadrain.com/topic/1089/4-1-17-berea-oh-team-serious-open-at-kidforce-collectibles-results/3?lang=en-US) | — | 4 1 17 berea oh team serious open at kidforce collectibles results |
| `#316` | [2017-12-22](https://web.archive.org/web/20171222021455/http://themanadrain.com/topic/316/5-22-berea-oh-team-serious-open-kidforce-collectibles-17-players-results/1) | — | 5 22 berea oh team serious open kidforce collectibles 17 players results |
| `#1192` | [2021-09-28](https://web.archive.org/web/20210928024809/http://www.themanadrain.com/topic/1192/5-6-17-sandusky-oh-team-serious-open-pop-shop-results/5?lang=en-US) | — | 5 6 17 sandusky oh team serious open pop shop results |
| `#1288` | [2020-09-28](https://web.archive.org/web/20200928051210/http://www.themanadrain.com/topic/1288/6-17-2017-team-serious-open-berea-ohio-kidforce-collectibles-results) | — | 6 17 2017 team serious open berea ohio kidforce collectibles results |
| `#2810` | [2020-09-27](https://web.archive.org/web/20200927205120/http://www.themanadrain.com/topic/2810/6-29-19-proxy-vintage-team-serious-open-at-kidforce-collectibles-berea-oh-results) | — | 6 29 19 proxy vintage team serious open at kidforce collectibles berea oh results |
| `#2053` | [2019-12-13](https://web.archive.org/web/20191213224740/http://www.themanadrain.com/topic/2053/7-14-18-m-tg-proxy-vintage-team-serious-open-at-the-pop-shop-results/1) | — | 7 14 18 m tg proxy vintage team serious open at the pop shop results |
| `#485` | [2017-07-06](https://web.archive.org/web/20170706210537/http://www.themanadrain.com:80/topic/485/7-16-team-serious-invitational-results/8?page=1) | — | 7 16 team serious invitational results |
| `#1441` | [2020-09-20](https://web.archive.org/web/20200920050332/http://www.themanadrain.com/topic/1441/8-19-17-team-serious-open-proxy-vintage-at-kidforce-collectibles-berea-oh-results) | — | 8 19 17 team serious open proxy vintage at kidforce collectibles berea oh results |
| `#577` | [2017-10-25](https://web.archive.org/web/20171025091935/http://themanadrain.com/topic/577/8-27-team-serious-open-results) | `grandpabelcher` | 8 27 team serious open results |
| `#616` | [2017-10-25](https://web.archive.org/web/20171025085746/http://themanadrain.com/topic/616/9-10-team-serious-open-results) | `grandpabelcher` | 9 10 team serious open results |
| `#2322` | [2020-09-26](https://web.archive.org/web/20200926061251/http://www.themanadrain.com/topic/2322/looking-back-on-vintage-2018-romancing-the-stones-2018-vintage-metagame-report) | — | looking back on vintage 2018 romancing the stones 2018 vintage metagame report |
| `#2266` | [2019-07-20](https://web.archive.org/web/20190720075134/http://themanadrain.com/topic/2266/romancing-the-stones-8-27-players-in-austin-texas/2) | — | romancing the stones 8 27 players in austin texas |
| `#2297` | [2022-07-01](https://web.archive.org/web/20220701004735/http://www.themanadrain.com/topic/2297/romancing-the-stones-invitational-vids/1?lang=en-US) | — | romancing the stones invitational vids |
| `#3152` | [2022-12-07](https://web.archive.org/web/20221207065221/http://www.themanadrain.com/topic/3152/team-serious-invitational-coverage/2?lang=en-US) | — | team serious invitational coverage |
| `#2296` | [2022-07-05](https://web.archive.org/web/20220705043211/http://themanadrain.com/topic/2296/team-serious-invitational-tsisteveland-14-players/2?lang=en-US) | `grandpabelcher` | team serious invitational tsisteveland 14 players |
| `#2653` | [2019-08-26](https://web.archive.org/web/20190826071148/http://themanadrain.com/topic/2653/team-serious-middle-school-chaos-draft-report/) | `grandpabelcher` | team serious middle school chaos draft report |
| `#2207` | [2022-05-23](https://web.archive.org/web/20220523185442/http://www.themanadrain.com/topic/2207/team-serious-open-10-20-18-at-the-kidforce-collectibles-berea-oh-results/14?lang=en-US) | — | team serious open 10 20 18 at the kidforce collectibles berea oh results |
| `#1738` | [2022-06-26](https://web.archive.org/web/20220626082216/http://www.themanadrain.com/topic/1738/team-serious-open-2-3-18-at-the-pop-shop-results/1?lang=en-US) | — | team serious open 2 3 18 at the pop shop results |
| `#1924` | [2021-01-19](https://web.archive.org/web/20210119123717/http://www.themanadrain.com/topic/1924/team-serious-open-5-19-18-at-the-kidforce-collectibles-berea-oh-results/14) | — | team serious open 5 19 18 at the kidforce collectibles berea oh results |
| `#2145` | [2022-05-28](https://web.archive.org/web/20220528051107/http://www.themanadrain.com/topic/2145/team-serious-open-9-8-18-at-the-kidforce-collectibles-berea-oh-results/1) | — | team serious open 9 8 18 at the kidforce collectibles berea oh results |
| `#1920` | [2018-05-28](https://web.archive.org/web/20180528123736/http://themanadrain.com:80/topic/1920/team-serious-open-report?page=1) | — | team serious open report |
| `#1026` | [2017-12-16](https://web.archive.org/web/20171216081505/http://themanadrain.com/topic/1026/team-serious-vintage-open-2-25-sandusky-oh-results/4?page=1) | — | team serious vintage open 2 25 sandusky oh results |
| `#1545` | [2019-04-23](https://web.archive.org/web/20190423201902/http://themanadrain.com/topic/1545/top-4-finish-paradoxical-outcome/2) | `xxhazardxx` | top 4 finish paradoxical outcome |
| `#1310` | [2021-04-14](https://web.archive.org/web/20210414205605/http://www.themanadrain.com/topic/1310/tsi-colorado-6-24-2017-results/4) | — | tsi colorado 6 24 2017 results |
| `#1763` | [2021-01-19](https://web.archive.org/web/20210119125812/http://www.themanadrain.com/topic/1763/tsi-hazard-s-birthday-3-0-2-17-2018-results/14) | — | tsi hazard s birthday 3 0 2 17 2018 results |
| `#2447` | [2022-01-19](https://web.archive.org/web/20220119082109/http://www.themanadrain.com/topic/2447/tsi-hazard-s-birthday-4-0-march-2nd-2019-results/9?lang=en-US) | — | tsi hazard s birthday 4 0 march 2nd 2019 results |
| `#1639` | [2020-10-01](https://web.archive.org/web/20201001202629/http://www.themanadrain.com/topic/1639/tsi-mishra-s-by-the-maumee-12-2-2017-results) | — | tsi mishra s by the maumee 12 2 2017 results |
| `#2786` | [2021-10-17](https://web.archive.org/web/20211017012424/http://www.themanadrain.com/topic/2786/tsi-the-land-6-15-2019-results/9?lang=en-US) | — | tsi the land 6 15 2019 results |

## Other top-level threads (6)

| thread | snapshot | author | title |
|---|---|---|---|
| `#1400` | [2022-01-20](https://web.archive.org/web/20220120231728/http://www.themanadrain.com/topic/1400/abrupt-decay-vs-abrade-decklist-included/26?lang=en-US) | `xxhazardxx` | abrupt decay vs abrade decklist included |
| `#1408` | [2021-09-26](https://web.archive.org/web/20210926224147/http://www.themanadrain.com/topic/1408/card-alters/10?lang=en-US) | `xxhazardxx` | card alters |
| `#106` | [2019-11-22](https://web.archive.org/web/20191122203947/http://themanadrain.com/topic/106/gencon-2016/8) | `xxhazardxx` | gencon 2016 |
| `#2816` | [2020-10-29](https://web.archive.org/web/20201029200536/http://themanadrain.com/topic/2816/middle-school-and-old-school-7-27-and-28-columbus-oh/2) | `grandpabelcher` | middle school and old school 7 27 and 28 columbus oh |
| `#2630` | [2022-01-17](https://web.archive.org/web/20220117015135/http://www.themanadrain.com/topic/2630/middle-school-and-old-school-with-scg-columbus-7-27-and-7-28/1?lang=en-US) | `grandpabelcher` | middle school and old school with scg columbus 7 27 and 7 28 |
| `#2609` | [2021-09-16](https://web.archive.org/web/20210916163356/http://www.themanadrain.com/topic/2609/ravenous-giant-aka-color-shifted-juzam/12?lang=en-US) | `xxhazardxx` | ravenous giant aka color shifted juzam |

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
| `<pre>` block | `{% decklist %}` … `{% enddecklist %}`, leading "Deck" line dropped |
| a line that is only bold text | an `##` heading — "**Standings**", "**Meta**" |
| tab-separated pasted rows | a Markdown table; rows arrive as separate paragraphs, so runs are gathered across blank lines |
| `web.archive.org/web/<ts>/…` links | the original target, unwrapped |
| nodebb emoji `<img>` | the character, or dropped |
| `/assets/uploads/files/…` images | downloaded to `assets/images/tmd/`, fetched **through the Wayback copy** since the live forum 404s them |

Front matter carries `tmd_thread` and `tmd_snapshot` so every ported post says where it
came from, plus `event_date`, `venue` and `players`.

Note the post `date:` is the day the write-up went up on **The Mana Drain**, not the day
the event was held, so the site's dates line up with the threads they came from. They
differ by a few days on every thread, and the site's URL is built from this date. The
event date is kept in `event_date`, and is what files the decklists under
`assets/files/YYYY/MM/DD`.

This reverses the earlier convention, which followed the hand port and used the event
date. Changing it moved every ported post's URL, including two that were already live;
there is no redirect plugin here, so those old URLs now 404.

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

## Threads the site already covers -- do not port these

Check before porting. Two candidate threads correspond to posts that already
exist, and porting either would publish a duplicate.

| thread | existing post | state |
|---|---|---|
| `#3824` | `_posts/2022-07-24-tso-all-american-warren.md` | Ported. Was the hand port; replaced by the converted version, verified 12 of 12 decklists identical at 464 card lines. |
| `#3862` | `_posts/2022-09-18-tso-all-american-warren.md` | Ported. Also a hand port -- every phrase of its prose traces back to the thread -- replaced by the converted version, verified 8 of 8 decklists identical at 321 card lines. |

Both carry a `tmd_thread` marker now, which is what lets a batch run skip them.
Rajah's rule: one post per event, and where a hand-written port and a converted
one both exist, keep the converted one -- its decklists are files.

Near misses that are NOT duplicates:

- `#2653` "team serious middle school chaos draft report" is dated three days
  before `2019-06-15-tsi-the-land.md`. Same weekend, different event. Port it.

## Things that look like bugs but are the source

- **`0 Mishra's Workshop`** leads Duane Haddix's list in #2786. It is deliberate:
  he usually plays Workshops and brought Karn Eldrazi instead, so he opened the
  list by saying he had none. The deck is 60/15 without it. Confirmed with
  Rajah; leave it. Do not add a pass that strips zero-quantity lines without
  checking for this.
- **58-card main deck** in James Crouch's list in #1483. Posted that way in
  2017, not a parse error.
- **61-card main decks** for Ben Perry and Frank Singel in #1639. Also as
  posted.

Totalling a decklist does not catch any of these -- the first sums to 60 and
the others are simply what someone wrote. They are only visible by reading the
list, which is the argument for a human reading each ported post before it
publishes.

## Dropbox is supporting material, not a source

Rajah's Dropbox has an event archive at `mtgo/ts/` -- roughly 940 files, with
folders matching several of the threads below (`land2`..`land6`, `hazard6`,
`KSI 2024`, `hsi7 - 2024`, `tsl`), including decklists already in text form and
event photos.

**It is secondary material only.** The scope of this work is what is stranded
on The Mana Drain; the inventory comes from the archive and nothing else. Do
not browse `mtgo/ts/` to discover events, and do not port a post because a
folder exists for it.

Consult it only for a thread already found on TMD, and only to fill a gap that
thread has -- a decklist the snapshot truncated, a photo the Archive never
captured. Reached live with `rclone` against the `dp:` remote; the NAS copy
under `nas4-cloud` is a mirror and may be stale.

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
