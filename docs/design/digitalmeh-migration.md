# Design: digitalmeh.net → Jekyll

**Status:** proposal, not started
**Goal:** move the last site off the AWS box, so `3.139.113.70` can finally be decommissioned

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

## Phase 0 — Access *(blocking everything else)*

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

## Phase 1 — Full archive

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

## Phase 2 — Inventory and decide

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
4. **Then decommission the instance** — which also retires the frozen teamserio.us copy and
   closes out the remaining AWS items on the roadmap.

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
