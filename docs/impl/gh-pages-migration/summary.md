# Sprint Summary — AWS to GitHub Pages Migration

**Dates:** 2026-10-08 → 2026-10-09
**Branch:** `gh-pages-migration`
**Detail:** [gh-pages-migration-plan.md](plan.md)

---

## Goal

Move `teamserio.us` off the self-hosted AWS box onto GitHub Pages. The site had been
self-hosted because the Chulapa theme "wouldn't build properly on GitHub Pages", and the
theme had since been updated, so it seemed worth retrying.

## Outcome

Migration is prepared, verified and staged. **Production has not moved** — `teamserio.us`
still resolves to AWS, and `main` still deploys there. Everything below is on a branch.

| | Before | After |
|---|---|---|
| Published site | **905 MB** | **293 MB** |
| Headroom under the Pages 1 GB cap | 8% | **71%** |
| Images on disk | 743.8 MB | 274.6 MB |
| Self-hosted video | 153.7 MB | 0 (on YouTube) |
| Third-party services in the render path | 1 (weserv proxy) | 0 |
| Deploy method | SSH + SCP, non-atomic | Pages artifact, atomic |
| Environments | prod + dev site | prod only |

---

## The main finding

**The original decision to self-host was correct.** Chulapa is a non-allowlisted gem theme,
and this site carries five custom Ruby plugins (`calendar_fetcher`, `deckfile_tag`,
`decklist_tag`, `grouptag`, `mtg_autocard`). GitHub Pages' *native* Jekyll build ignores
`_plugins/` and rejects themes outside its allowlist, so the site genuinely could not be
published there. That was a hard stop, not a misdiagnosis.

**What changed is the deployment mechanism, not the theme.** Pages now publishes a
**GitHub Actions artifact**, which runs arbitrary Ruby with arbitrary plugins — and this
repo already built that way in CI, then SCP'd the result to AWS. So the constraint lifted
when Actions-based publishing arrived, and the theme update that prompted this attempt was
not what made it possible. Worth knowing for the next "we tried that and it didn't work":
check whether the thing that blocked you still exists, rather than whether the subject of
the blockage has changed.

**The actual blocker was size.** ~917 MB of assets against a 1 GB hard limit — about 8%
headroom, which one event write-up would have consumed.

---

## What changed

### Image library (commit `c4d8628`)
`script/prep-images.sh` sorts every image three ways:

- **Exempt** — decklist photos (`deck-*`) and post headers. 37 files. Decklists are phone
  shots people need to *read* when zoomed; headers render full-width. At ~42 MB against a
  1 GB budget, shrinking them buys nothing and risks the one thing users zoom in on.
- **Archive** — 45 DSLR originals (331.8 MB) copied to `assets/originals/`, excluded from
  the build, so they cost nothing against the cap and stay downloadable via jsDelivr
  (verified: a 15.2 MB original serves fine).
- **Resize** — everything else capped at 2560px q85. 236 files.

WebP was considered and rejected: all 7 gallery includes filter on `.jpg`/`.jpeg`, so WebP
would be invisible to every gallery; `calibreapp/image-actions` cannot convert formats, so
every future post would need a manual conversion step; and every `.jpg` reference would
need rewriting — a permanent tax on authoring for ~50 MB on a 1 GB budget.

### Video (commits `adacdce`, `c10f0a9`, `696af99`)
All three MP4s moved to the Full Warning YouTube channel, embedding verified via oEmbed
before any markup changed. Re-encoding was measured first and rejected: CRF 24 recovered
only 32% (153.7 MB → 104.5 MB), and those bytes would still stream from the Pages bandwidth
allowance on every play.

### Gallery thumbnails (commit `9938ab8`)
Galleries previously branched on `jekyll.environment`: production routed every thumbnail
through `images.weserv.nl`, a third-party proxy that fetched each photo *from the live
site*; development used local files at a fixed size. A local build therefore never showed
what production showed, and on a freshly published post the proxy would fetch before the
image was reachable, cache the miss and serve a placeholder.

Replaced with 123 real thumbnails generated at prep time (`assets/thumbs/sq/` 700×700
cropped, `assets/thumbs/fit/` proportional). Gallery folders are read from the posts, so new
galleries are picked up automatically. All 7 includes now use one code path.

### Workflows (commits `c492821`, `c8dd362`)
- `deploy-pages.yml` — builds on `main`, publishes via Pages artifact. Size guard (fails
  >900 MB) and gallery-integrity check (every thumbnail and click-through URL must resolve).
- `build-check.yml` — same build and checks on PRs and non-main branches, publishes nothing.
- `deploy-pages-preview.yml` — temporary, publishes this branch to `preview.teamserio.us`.
- Deleted the dev-site deploy. **Kept the AWS prod deploy** so both targets stay current
  until DNS moves and rollback stays a pure DNS change.

---

## Decisions and why

| Decision | Rationale |
|---|---|
| Resize to 2560px q85, not WebP or 2048px | Keeps the authoring habit unchanged (drop JPEGs in, commit) and can be tightened later with no reference edits |
| Keep decklist photos and headers full-size | Readability matters more than 42 MB |
| Archive DSLR originals in-repo, excluded from build | Full resolution stays available at zero cost against the cap |
| Videos to YouTube, not re-encoded | Re-encoding recovered only 32% and kept the bandwidth cost |
| **Retire the dev site** | It existed to work around deploy flakiness, not to preview content — see below |
| Generate thumbnails rather than proxy them | Removes a third-party runtime dependency and makes local match production |
| Validate on `preview.teamserio.us` | Exercises the real Pages host at a real domain before the apex moves |

### Why retiring the dev site is safe

Dev existed because "the deployed site was sometimes wonky". Four identifiable causes:

1. **Non-atomic deploys** — `rm -Rf /dev-www/**` then SCP left the site empty in between.
   *Fixed by Pages' atomic artifact swap.*
2. **The build was mutated after Jekyll ran** — "Clean Extensions for S3" renamed every
   `.html`, including `404.html`, which broke the custom 404. *Step deleted.*
3. **Galleries rendered differently in production** via the weserv proxy. *Fixed by
   generating thumbnails.*
4. **`calendar_fetcher.rb` rescues HTTP failures to `nil`** — a transient blip yields a
   successful build with the calendar silently missing. **Still outstanding.**

Replacement: the `dev` branch for work, `jekyll serve` for preview, and `build-check.yml`
so a broken build cannot reach `main`.

---

## Bugs found and fixed

- **Collapsed YouTube embeds.** The embeds used Bootstrap 5's `.ratio`, but the site loads
  **Bootstrap 4.5.0**, where the equivalent is `.embed-responsive`. The class did nothing,
  so videos laid out 157px tall instead of 360px and 640px — while the build stayed green.
  Replaced with a framework-independent include that also survives the chulapa 2.x upgrade.
- **Previews loaded production's CSS.** chulapa emits absolute URLs from `site.url` — ~1,918
  per build — so any preview pulled its stylesheet from, and navigated to, `teamserio.us`.
  Fixed with `_config_preview.yml` (`url: ""`). This would also have made staging
  validation on a `github.io` URL nearly meaningless.
- **A corrupt JPEG.** `DSC_5360-angelo.jpg` has a JFIF density of 65000 dots/cm, which makes
  ImageMagick exceed its time limit or abort on an assertion. libvips reads it in ~1 s. The
  script now falls back to libvips automatically.
- **Config edits on `dev` are silently discarded on promote** (`merge=ours` plus
  `git checkout HEAD -- _config.yml`). Not yet removed — see Open items.

## Incident: calibreapp/image-actions destroyed the originals archive

Opening the PR triggered `calibreapp/image-actions`, which recompressed 52 files and pushed
the result as a bot commit. 32 of them were in `assets/originals/`:

| | Before | After |
|---|---|---|
| Archived originals | **337.0 MB** | **72.6 MB** |
| `DSC_5387.jpg` | 13.8 MB | 3.2 MB |

About 78% of the archived full-resolution data, destroyed automatically, with no signal that
anything was lost — the commit message simply read "Optimised images". It also took a
further 5–8% off images `prep-images.sh` had already compressed at a chosen quality, and 76%
off one PNG.

Reverted, and the workflow deleted. It was redundant as well as harmful: once the prep
script resizes and compresses deliberately, a second unaware compressor can only
double-compress. Replaced by `prep-images.yml`, which runs the prep script in CI and commits
the result, so image handling has one owner.

**Worth remembering:** an automation that silently rewrites committed binaries is only safe
while nothing in the repo treats those binaries as masters. Introducing `assets/originals/`
changed that, and the existing workflow had no way to know.

## Verification performed

- Built in a `ruby:3.2` container matching CI; 43 pages, build clean
- 617 local references audited, 0 broken
- Rendered in headless Chrome via Puppeteer with lazy images forced and console captured:
  **0 broken images**, galleries rendering, decklists and autocards working
- Embed geometry measured: **640×360** and **360×640**, both exact
- Preview isolation confirmed: **0 requests to teamserio.us, 0 links to it**
- Console errors present are **identical on the live site** — pre-existing, not regressions
- GitHub Pages' extensionless URL resolution verified empirically against two live Pages
  sites, so current URLs survive removing the extension-stripping step

---

## Open items

1. ~~**`calendar_fetcher.rb` fails silently**~~ — **FIXED 2026-10-09.** It was worse than
   silent: a failed fetch produced a *successful* build whose calendar page told visitors
   "Calendar data not available. Please rebuild the site." Loud on the live site, invisible
   in CI. Now it fetches with timeouts, validates the response is a real VCALENDAR, falls
   back to a committed snapshot at `_data/calendar.ics` (warning in GitHub Actions format
   with the snapshot's age), and fails the build only when there is neither. Verified in all
   three states.
2. **Config divergence guards** — remove `merge=ours` and the promote workflow's
   `git checkout HEAD -- _config.yml`, but **only after** aligning `dev`'s `_config.yml` to
   the production `url:`. Removing them first would push the dev URL into production.
3. **chulapa 1.1.0 → 2.1.0** — needs `repository: rykerwilliams/teamserio.us` in
   `_config.yml` (verified: it fails to build without it), plus deleting the now-obsolete
   `_plugins/grouptag.rb` and renaming `search.lunr_maxwords` to `search.maxwords`.
4. **Gallery images have no `width`/`height`** with `loading="lazy"`, so they reserve no
   space and the page shifts as thumbnails load. Every square thumb is 700×700 now, so this
   is a one-line fix.
5. **Wildcard DNS** — `*.teamserio.us` points at the AWS box, so `dev.teamserio.us` and
   every other subdomain keep resolving there. Revisit carefully: the box also hosts an old
   WordPress site, which may be reached through one of those names.
5b. **The AWS box is not being retired.** It also hosts `digitalmeh.net`
   (WordPress 6.5.13 / PHP 8.3.4, DNS at GoDaddy), so "decommission the instance" was never
   the right end state — only teamserio.us moved off it.
6. **Two hardcoded `https://teamserio.us` cross-links** in post bodies.
7. **Dump the openresty config** before decommissioning — if it holds redirects or headers
   beyond extension handling, that is invisible from the repo and would be lost.

## Preview is live — 2026-10-09

**https://preview.teamserio.us** is serving the migration branch from GitHub Pages, with
HTTPS. Verified against the real host:

| Check | Result |
|---|---|
| `/`, `/posts/`, `/all`, `/search`, `/tags`, `/categories`, `/404` | 200 |
| `/calendar`, `/full-warning` | 301 (directory redirect, as in production) |
| **Extensionless post URLs** (all three sampled) | **200** |
| `sitemap.xml`, `feed.xml`, `atom.xml`, `rss.xml` | 200 |
| CSS, gallery thumbnails | 200 |
| Old self-hosted `.mp4` path | 404 (correctly gone) |
| Nonexistent path | 404 (correct) |

That settles the central bet: GitHub Pages resolves `/posts/foo` to `posts/foo.html` on
this site, so removing the extension-stripping step preserves every live URL.

**Ordering lesson for cutover: set the custom domain, then re-run the deployment.** Setting
the domain on an already-published site left the edge serving "Site not found" for the root
while other paths worked. A redeploy bound it immediately and the certificate issued within
a couple of minutes. Expect the same sequence when switching the domain to `teamserio.us`.

Also expect DNS flapping during propagation: the existing `*.teamserio.us` wildcard keeps
answering from resolver caches until its TTL expires, and requests that land on AWS fail TLS
because that box has no certificate for the new hostname. It settles on its own.

## Remaining steps

1. ~~Add Namecheap CNAME `preview`~~ — done 2026-10-09
2. Validate on `preview.teamserio.us`, **including on a phone** for the portrait embeds
3. Set the custom domain to `teamserio.us`, repoint the apex to the four Pages IPs, enable
   Enforce HTTPS
4. Leave AWS running at least a week — with a 30-second TTL, rollback is a DNS change
5. Then: delete the AWS workflow, the four `DEPLOY_*` secrets, the preview workflow and
   `_config_staging.yml`; decommission the box
