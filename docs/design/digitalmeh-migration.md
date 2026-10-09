# Design: digitalmeh.net → Jekyll

**Status:** phases 0 and 1 complete; phase 2 under way
**Goal:** move `digitalmeh.net` off WordPress onto Jekyll

**Not the goal:** retiring the AWS box. It also runs cheertime production and staging, which
deploy every 10 minutes — see [../impl/aws-box/inventory.md](../impl/aws-box/inventory.md).
Migrating this site removes one tenant, not the host.

---

## What we know

Measured from the public WordPress REST API, 2026-10-09:

| | |
|---|---|
| Published posts | **152** |
| Pages | 5 |
| Categories | 20 |
| **Tags** | **499** |
| Media items | 321 |
| Approved comments | 34 |
| Date range | **2006-04-20 → 2022-11-16** (16 years) |
| Stack | WordPress 6.5.13, PHP 8.3.4, openresty |
| Permalink structure | `/%postname%/` — flat, no date prefix |
| Content format | **classic HTML**, not Gutenberg blocks |
| DNS | GoDaddy (`domaincontrol.com`), A record → `3.139.113.70` |

### Three observations that shape everything below

**499 tags across 152 posts.** Roughly 3.3 tags per post with almost no reuse — a tag
per idea rather than a tag per category of idea. This is the real work in phase 2, and it
is a content-design problem, not a scripting one. Expect to end with 20–40 tags.

**Flat permalinks over 16 years.** URLs look like `/2022-11-05-the-magic-at-the-underground-lounge/`
— the date is inside the slug, not the path. Jekyll's default would be
`/:year/:month/:day/:title/`, which would break **every inbound link and search result**.
Preserving URLs is a hard requirement, not a nice-to-have.

**Classic HTML, not blocks.** Easier to convert than Gutenberg, but the content contains
hand-written anchors (`<a name="event">`), manual tables of contents and inline markup that
a naive HTML→Markdown pass will mangle.

---

## Phase 0 — Access — **DONE 2026-10-09**

The key already syncs to phatmyth via Dropbox at
`/files/data/nas/nas4-cloud/rajah/dropbox/awsKeys/rjPrivate`, so no key needed copying:

```bash
ssh -i /files/data/nas/nas4-cloud/rajah/dropbox/awsKeys/rjPrivate \
    ubuntu@ec2-3-139-113-70.us-east-2.compute.amazonaws.com
```

Using the key in place rather than reading it keeps the private material out of any
transcript. The original plan was to add a public key instead — kept below in case the
Dropbox path ever goes away:

1. Add phatmyth's public key to the box:
   ```
   ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBBWBXRTdE61wDjGFYgt4RVJUpQkZ7XEx7IXOej5nnjsoRKsfJXd/cPJQpfgScRoYxFICnpPK53f9bD7qYipgxII= mythuser@phatmyth
   ```
   Port 22 is reachable from here; the key above currently gets `Permission denied` for
   `ubuntu`, `ec2-user`, `admin`, `debian`, `bitnami` and `root`, so the username is
   something else.
2. Confirm the login user and whether it has `sudo`.
3. Confirm MySQL access (socket or credentials from `wp-config.php`).

---

## Phase 1 — Full archive — **DONE 2026-10-09**

Stored at **`/files/data/backups/digitalmeh.net/2026-10-09/`** on phatmyth. Streamed
directly over SSH rather than staged on the box, because that disk is at 82%.

| File | Size | Contents |
|---|---|---|
| `bitnami_wordpress.sql.gz` | 1.1 MB | full database |
| `swag.tar.gz` | 1.1 GB | WordPress files + uploads, 12,619 entries |
| `compose.tar.gz` | 595 B | compose definition |
| `npm-proxy-hosts.tar.gz` | 1.2 KB | Nginx Proxy Manager routing |

**Restore verified**, not just copied: the dump was loaded into a clean MariaDB container
and every count matched the live site — 152 published posts, 5 pages, 321 attachments,
499 tags, 20 categories, 25 tables.

**3,880 files under `wp-content/uploads/`** against 321 media items, because WordPress keeps
several resized variants per upload. Worth remembering when sizing the Jekyll site.

> ⚠️ `swag.tar.gz` contains `wp-config.php` with database credentials and salts. It lives
> outside any git repository and must stay there.

### Discovered while verifying: the database container cannot be rebuilt

`bitnami/mariadb:11.1.4` **no longer exists in the registry** — pulling it fails with
`manifest unknown`. The running container survives only because its image is already on
disk. If it is ever removed, or the host is rebuilt, the compose file will not come back up.
The verification restore had to use the official `mariadb:11` image instead.

That turns this migration from housekeeping into something with a deadline attached.

### Original plan, for reference

The point is a **restorable** archive, not merely a copy. An untested backup is a guess.

1. `mysqldump` the WordPress database (single transaction, routines, triggers).
2. `wp-content/uploads/` in full — 321 media *items*, but WordPress generates several
   resized files per upload, so expect substantially more files on disk.
3. `wp-content/themes/` and `plugins/` — needed to understand rendering quirks later.
4. `wp-config.php`, the openresty vhost configs, PHP-FPM pool config, and any crontab.
5. **Verify the archive restores.** Stand the dump up in a local MySQL container, point a
   throwaway WordPress at it, confirm the post count matches and pages render.
6. Store off-box, on phatmyth. **`wp-config.php` contains database credentials and salts —
   it must not go into any git repository.**

---

## Phase 2 — Inventory and decide — **in progress**

### What the database shows that the public API could not

| | Published | Hidden |
|---|---|---|
| Posts | 152 | **84 draft**, 2 private |
| Pages | 5 | 4 draft, 1 private |

**84 drafts**, spanning 2006-05 to 2023-01 — but most are not really posts:

- **17** have more than 500 characters of content
- **16** are essentially empty (under 100 characters)
- the remaining ~51 sit in between

So the review set is realistically **17 substantive drafts**, not 84.

### The tag problem, measured

| Used | Tags |
|---|---|
| 0× | 17 |
| **1×** | **390** |
| 2× | 51 |
| 3× | 18 |
| 4×+ | 23 |

**390 of 499 tags are used exactly once** — 78%. These are not a taxonomy, they are
keywords typed once and never reused. Only about 16 tags are used five times or more:
`mtg` (16), `windows` (12), `oldschool` (12), `vintage` (10), `ec` (9), `linux` (9),
`ubuntu` (8), `combo` (8), `software` (8), `.net` (7), `gnu/linux` (6), `n85` (6).

**The 20 categories are already a working taxonomy** and need far less surgery:
`software` 55, `mtg` 37, `gnu/linux` 31, `media` 31, `hardware` 27, `web` 24, `sound` 22,
`oldschool` 15, `vintage` 15, `ubuntu` 12, `image` 10, `gentoo` 9, `theState` 8, `apple` 8,
`middle school` 6, `n85` 5, `food snob` 3, `sport` 2, `Uncategorized` 2, `middle school` 1.

**Suggested direction:** carry the categories across as Jekyll categories mostly as-is, and
rebuild tags from scratch from the ~16 that recur rather than migrating 499. Note the
cleanup already visible above: `middle school` exists twice, and `mtg`, `oldschool`,
`vintage`, `ubuntu`, `n85` and `gnu/linux` exist as *both* a category and a tag.

### Still to do in this phase

1. Traffic data from the access logs — which of the 152 posts anyone actually reads
2. Media usage — which of the 3,880 upload files surviving posts reference
3. The manifest: keep/drop, final slug, final tags, per post

### Original plan, for reference

Everything here is read-only analysis producing a written decision, not code.

1. **Post status breakdown** straight from `wp_posts`: `publish`, `draft`, `private`,
   `pending`, `future`, `trash`, plus `post_type` (posts vs pages vs attachments vs custom
   types vs revisions). The public API only shows the 152 published ones — **the hidden
   posts are precisely what the API cannot see**, which is why this step needs the DB.
2. **Taxonomy analysis:** every tag and category with its post count. Expect a long tail of
   single-use tags. Group synonyms, identify the 20–40 that earn their place.
3. **Traffic reality check:** pull the openresty access logs and count hits per URL. Sixteen
   years of posts will not be uniformly worth migrating, and real traffic beats memory for
   deciding what to keep. *(Not in the original outline; cheap and high-value.)*
4. **Media usage:** which uploads are actually referenced by surviving posts. Orphans do
   not need migrating, and this directly controls the final site size — the teamserio.us
   migration ran into the Pages 1 GB cap, so size gets designed in from the start here.
5. **Output a manifest** — a checked-in file listing every post with: keep/drop, final
   slug, final tags. That manifest is the contract phase 3 executes against, and it is
   reviewable before anything is converted.

---

## Phase 3 — Build the Jekyll site

1. **New repository.** One repo serves exactly one GitHub Pages site, and this repo's Pages
   site is `teamserio.us`. `digitalmeh.net` needs its own.
2. **Conversion.** Either `wp-cli export` to WXR then a converter, or read the DB directly.
   The DB route is better here because we need drafts and private posts, and we already
   need DB access for phase 2.
3. **URL preservation.** Set `permalink: /:title/` to match `/%postname%/`. For any URL that
   must change, add `jekyll-redirect-from`. Note GitHub Pages cannot do server-side
   redirects — these are meta-refresh stubs, so keep the list short by not changing slugs.
4. **Media.** Download, then resize with the same approach as `script/prep-images.sh`
   (exempt anything that must stay readable), and rewrite in-content URLs from
   `/wp-content/uploads/...` to the new paths.
5. **Comments.** 34 of them. Small enough to render statically into each post rather than
   adopting Disqus or giscus — preserves the history with no third-party dependency.
6. **Feed continuity.** `/feed/` must keep working for existing subscribers.
7. **The 5 pages**, plus menus and any sidebar content worth keeping.

---

## Phase 4 — Theme and idiosyncrasies

1. **Theme.** Chulapa is the known quantity — we now understand its config, its quirks and
   its 2.x behaviour. Worth considering even if digitalmeh wants a different look.
2. **Content oddities:** hand-written `<a name="...">` anchors, manual tables of contents,
   any shortcodes the classic editor left behind, inline styles, and `<table>` markup.
3. **Link checking**, three separate problems:
   - *internal* links between posts — must survive slug decisions from phase 2
   - *media* links — must survive the path rewrite in phase 3
   - *external* links — 16 years means significant link rot; produce a report and decide
     per link whether to fix, annotate or leave
4. **Search**, if wanted — lunr, as on teamserio.us.

---

## Phase 5 — Cutover and decommission *(not in the original outline)*

Without this the project does not achieve its actual goal.

1. DNS at **GoDaddy** (not Namecheap): apex A records → the four Pages IPs, `www` → CNAME.
2. Lower the TTL first. Set the custom domain, then **remove and re-add it** if the
   certificate stalls at `not yet requested` — see
   [../impl/gh-pages-migration/cutover-runbook.md](../impl/gh-pages-migration/cutover-runbook.md).
3. Soak, with the WordPress site still running as rollback.
4. **Retire the WordPress containers** (`swag`, `digitalmehnet-mariadb-1`) and reclaim
   their disk. The host itself stays — cheertime lives there.

---

## Gaps in the original four-phase outline

Recorded so the additions are visible rather than smuggled in:

| # | Gap | Why it matters |
|---|---|---|
| 1 | **URL preservation and redirects** | Jekyll's default permalink would break every one of 16 years' inbound links |
| 2 | **Media migration** | 321 items, path rewriting, and the size budget that bit us on teamserio.us |
| 3 | **Comments** | 34 of them; they vanish silently unless someone decides otherwise |
| 4 | **Repo and hosting target** | One repo = one Pages site, so this needs its own; plus GoDaddy DNS and the certificate dance |
| 5 | **Archive *verification*** | "Full archive" must mean restore-tested, or it is a guess |
| 6 | **Traffic data** | The best input for "what do we actually migrate" |
| 7 | **Feed continuity** | Existing subscribers |
| 8 | **Decommissioning** | The actual goal; phases 1–4 stop one step short of it |
| 9 | **Post status handling** | Drafts, private, pending and scheduled all need an explicit decision, not a default |
| 10 | **Secrets hygiene** | `wp-config.php` holds DB credentials and must never reach a repo |

## Open questions

- Is `digitalmeh.net` staying at that domain, or folding into teamserio.us?
- Should the hidden posts be published as part of this, or migrated as drafts?
- Does anything else on that box matter — cron jobs, mail, other vhosts?
