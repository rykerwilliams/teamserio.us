# Migration Plan: Self-Hosted AWS → GitHub Pages

**Status:** Investigation complete, awaiting decisions
**Date:** 2026-10-08
**Scope:** Move `teamserio.us` from the self-hosted AWS box to GitHub Pages

---

## 1. Executive summary

**The original blocker is gone, but it was never really the theme.** Chulapa builds fine;
what fails is GitHub Pages' *native* Jekyll build, which ignores `_plugins/` and refuses
non-allowlisted gem themes. That path is obsolete. GitHub Pages now deploys from a
**GitHub Actions artifact**, which runs arbitrary Ruby with arbitrary plugins — and this
repo *already* builds that way in CI today. The build is not the problem.

**The real blocker is size.** The site carries ~940 MB of assets against a **1 GB hard
limit** on published Pages sites. A lift-and-shift lands at roughly 945 MB — about 6%
headroom, consumed by one or two event write-ups.

**Verdict: migration is viable, but an image diet is a prerequisite, not a nice-to-have.**

---

## 2. Current state (measured)

### Hosting
| Item | Value |
|---|---|
| Live IP | `3.139.113.70` (AWS, us-east-2) |
| Server | `openresty`, header `X-Served-By: teamserio.us` |
| DNS | Namecheap (`dns1/dns2.registrar-servers.com`) — **not** Route 53 |
| A record TTL | **30 seconds** |
| `www` | A record to same IP |
| Prod path | `/prod-www` on the box |
| Dev path | `/dev-www`, served at `dev.teamserio.us` |

### Deployment (today)
- `.github/workflows/jekyll-build-and-deploy-prod.yml` — push to `main` → build → SCP to `/prod-www`
- `.github/workflows/jekyll-build-and-deploy.yml` — push to `dev` → build → SCP to `/dev-www`
- `.github/workflows/promote-dev-to-prod.yml` — manual merge `dev` → `main`, preserving `main`'s `_config.yml`
- `.github/workflows/calibreapp-image-actions.yml` — recompresses images on PR at quality 80

Both deploy workflows SSH in, `rm -Rf` the target dir, then SCP `_site`. Secrets used:
`DEPLOY_HOST`, `DEPLOY_USERNAME`, `DEPLOY_SSH_KEY`, `DEPLOY_HOST_PORT`.

### Repository
| Metric | Value |
|---|---|
| Visibility | **public** (so Pages is available at no cost) |
| `diskUsage` (GitHub) | 1,613,285 KB ≈ **1.58 GB** |
| Working tree | 940 MB (assets) + ~1 MB source |
| `.git` | 1.6 GB |
| Tracked files | 557 |
| Posts | 28 |
| `CNAME` file | **absent** |

### Asset breakdown — the crux
| Type | Size | Files |
|---|---|---|
| `.jpg` | **737.0 MB** | 370 |
| `.mp4` | **153.7 MB** | 3 (largest single file **85.6 MB**) |
| `.png` | 19.8 MB | 32 |
| **Total** | **~912 MB** | |

### Build output (verified in `ruby:3.2` container, assets excluded)
| Theme version | Result | HTML pages | Size (no assets) |
|---|---|---|---|
| chulapa-jekyll **1.1.0** (current lock) | **builds, exit 0** | 43 | 4.7 MB |
| chulapa-jekyll **2.1.0** as-is | **FAILS** | — | — |
| chulapa-jekyll **2.1.0** + `repository:` | **builds, exit 0** | 43 | 4.9 MB |

**Projected published site: ~917 MB (assets) + ~5 MB = ~922 MB against a 1 GB ceiling.**

---

## 3. GitHub Pages limits (from GitHub docs)

- Published site: **no larger than 1 GB** *(hard)*
- Source repository: **recommended limit 1 GB** *(we are at 1.58 GB)*
- Bandwidth: **100 GB/month** *(soft)*
- Builds: 10/hour *(soft; not applicable to Actions-based deploys)*
- Not permitted as a free web host for online business / e-commerce / SaaS *(a community
  site is fine; bulk video hosting invites scrutiny)*

Bandwidth math worth noting: the 85.6 MB video alone reaches the 100 GB soft limit in
**~1,200 plays**.

---

## 4. Why it failed before, and what actually changed

| | Then (native Pages build) | Now (Actions → Pages) |
|---|---|---|
| `_plugins/*.rb` | Silently ignored | **Executed normally** |
| Gem theme `chulapa-jekyll` | Not allowlisted → fails | **Installed via Bundler** |
| Jekyll version | Pinned to `github-pages` gem | **Any** (we use 4.3.x) |
| `jekyll-feed`, `jekyll-sitemap` | Allowlist only | Any plugin |

The five custom plugins — `calendar_fetcher.rb`, `deckfile_tag.rb`, `decklist_tag.rb`,
`grouptag.rb`, `mtg_autocard.rb` — are the reason native Pages was impossible. Under
Actions they are ordinary code. `calendar_fetcher.rb` even makes a live HTTPS call to
Google Calendar during build; verified working in the container (fetched 4,225 bytes).

**So the theme update is not what unblocks this.** It was already unblocked the moment
`actions/deploy-pages` existed. The theme upgrade is a separate, optional change.

---

## 5. Issues found, with fixes

### 5.1 Site size — BLOCKER (strategy decided)
~917 MB of assets vs a 1 GB hard limit. **Measured breakdown:**

| Set | Size | Files | Disposition |
|---|---|---|---|
| `DSC_*` DSLR shots | **384.6 MB** | 52 | resize + archive originals |
| Other gallery/event photos | ~310 MB | ~300 | resize |
| Videos (`.mp4`) | **153.7 MB** | 3 | move to YouTube |
| Decklist photos (`deck-*`) | 25.2 MB | 17 | **exempt — keep full res** |
| Headers / splash | 16.6 MB | 11 | **exempt — keep full res** |
| PNGs (non-header) | ~20 MB | 32 | leave |

JPEG dimensions across the library: **76 files >5000px, 181 at 3000–5000px**, 13 at
2048–3000px, 141 at ≤2048px. The large ones are unresized camera originals.

**Key context:** gallery thumbnails are already proxied through `images.weserv.nl`
(`w=350&h=350&q=50`), so the site only serves a full-size image on *click-through*.
Original resolution is storage weight, not page-load weight.

#### Decision: three-way split

**(1) Exempt — decklist photos and headers (~42 MB, 28 files).** Left completely alone.
Decklist photos (`deck-*`, 3024×4032 phone shots) must stay readable when zoomed; they are
referenced as direct markdown links, not through galleries, and sit *above* the gallery
subfolders (`gameplay/`, `candids/`, …) so the includes never sweep them in. Headers are
full-width hero backgrounds and must remain published at their current paths. At 42 MB
against a 1 GB budget, shrinking these buys nothing and risks the one thing users zoom in on.

**(2) Resize — the gallery/event bulk (~695 MB).** Max edge **2560px, quality 85, EXIF
stripped, `-auto-orient`**. Benchmarked on a 35-file sample:

| Setting | Before | After | Reduction |
|---|---|---|---|
| **2560px q85 jpg (chosen)** | 59.5 MB | 17.8 MB | **70.0%** |
| 2048px q82 jpg | 59.5 MB | 12.0 MB | 79.8% |
| 2048px q82 webp | 59.5 MB | 8.5 MB | 85.7% |
| 1600px q80 jpg | 59.5 MB | 8.0 MB | 86.6% |

WebP was **rejected** despite the better ratio: all 7 `image-gallery*.html` includes filter
explicitly on `.jpg`/`.jpeg`/`.JPG`/`.JPEG`, so WebP files would be invisible to every
gallery; `calibreapp/image-actions` cannot convert formats (confirmed — it only recompresses
in place), so every future post would need a permanent conversion step; and every `.jpg`
reference across all posts would need rewriting. That is a recurring tax on authoring for
~50 MB on a 1 GB budget. Staying on JPEG also means the target can be tightened to 2048px
later with a one-line script change and **zero reference edits**.

**(3) Archive originals — the 52 DSLR photos (384.6 MB).** Full-resolution copies move to
`assets/originals/`, which is added to `exclude:` in `_config.yml`. They stay versioned in
git but **never enter `_site`, so they cost nothing against the 1 GB cap**, and are served
for download via jsDelivr:

```
https://cdn.jsdelivr.net/gh/rykerwilliams/teamserio.us@main/assets/originals/<path>
```

Verified against this repo: a **15.2 MB original returns 200 through jsDelivr**. No new
accounts, no object storage, no AWS. Note jsDelivr **rejects the 85.6 MB video with 403**,
so this route is for images only.

**Videos → YouTube.** 153.7 MB in 3 files, and the 85.6 MB one reaches the 100 GB/month
soft bandwidth limit in roughly 1,200 plays. There are already two YouTube channels.

#### Projected result

| | Before | After |
|---|---|---|
| Published site | ~922 MB | **~255 MB** |
| Headroom under 1 GB cap | 8% | **~75%** |

*Caveat: resizing rewrites tracked files, so `.git` keeps the old blobs and repo size does
not shrink. Only the published artifact matters for the hard limit; shrinking `.git` would
need a history rewrite (optional, separate, destructive).*

### 5.2 Extension stripping must be removed — VERIFIED SAFE
Both deploy workflows run a "Clean Extensions for S3" step:
```bash
for i in `find -name '*.html'` ; do mv $i ${i%%.html} ; done
for i in `find -name 'index' -type f` ; do mv $i ${i}.html ; done
```
This strips `.html` from every non-index page to suit openresty. Verified: the build
produces **33 non-index `.html` files**, including every post
(`_site/posts/20220723_tso-all-american-warren.html`), because the permalink
`/posts/:year:month:day_:title` has no trailing slash.

On Pages this step must be **deleted**. Extensionless files would be served without a
usable content type, and renaming `404.html` → `404` **breaks the custom 404 page**, which
Pages keys off the filename.

**Verified empirically (2026-10-08):** GitHub Pages does resolve extensionless paths to
`.html` files, so removing the step preserves every live URL exactly. Tested against two
independent Pages sites (`server: GitHub.com`):

| URL | Status | `<title>` |
|---|---|---|
| `dieghernan.github.io/chulapa/search.html` | 200 | `Search \| Chulapa` |
| `dieghernan.github.io/chulapa/search` | 200 | `Search \| Chulapa` |
| `dieghernan.github.io/chulapa/definitely-not-a-real-page-xyz` | 404 | — |
| `jekyll.github.io/minima/about` | 301 → canonical | — |

Same page served both ways, and genuinely missing paths still return a correct 404 — so
the behavior is real pretty-URL resolution, not a blanket 200. **Current live URLs such as
`/posts/20220723_tso-all-american-warren` will keep working untouched.** No redirects
needed, no permalink changes needed.

### 5.3 Theme upgrade 1.1.0 → 2.1.0 — separate workstream
`chulapa-jekyll` 2.1.0 hit RubyGems **2026-10-08** (today). Published versions: 1.1.0
(2023-12-13), 2.0.0 (2025-02-24), 2.0.1 (2025-02-26), 2.1.0 (2026-10-08).

Verified failure and fix:
```
Liquid Exception: No repo name found. Specify using PAGES_REPO_NWO environment
variables, 'repository' in your configuration, or set up an 'origin' git remote
pointing to your github.com repository. in /_layouts/default-with-decklists.html
```
2.1.0 adds a **`jekyll-github-metadata`** dependency (via `octokit`). Fix is one line in
`_config.yml`:
```yaml
repository: rykerwilliams/teamserio.us
```
With that, 2.1.0 builds clean and produces the same 43 pages. Also consider exporting
`JEKYLL_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}` in CI so metadata API calls are
authenticated rather than subject to anonymous rate limits.

Other v1→v2 breaking changes to handle:
- `search.lunr_maxwords` → **`search.maxwords`** (currently set but empty, so harmless; rename anyway)
- **`_plugins/grouptag.rb` is no longer required** as of 2.0.1 — delete it after upgrading
- Twitter → X renaming and iconography; Mastodon sharing replaced by Bluesky
- `cloudtag2` / `cloudcategory2` approaches deprecated
- Seven new skins; current skin is `twitter-dim` — confirm it still exists in 2.x

Local overrides that need eyeballing after the upgrade (they hook theme internals):
`_includes/custom/custom_head.html`, `_includes/custom/custom_bottomscripts.html`,
`_includes/components/indexcardspodcast.html`, `_layouts/default-with-decklists.html`,
plus 7 `image-gallery*.html` includes.

**Recommendation: do not bundle this with the hosting move.** Migrate on 1.1.0 (a known-good
build), then upgrade the theme as its own PR on `dev`. One variable at a time.

### 5.4 Dev environment needs a new home — DECISION REQUIRED
One repo serves exactly one Pages site, so `dev.teamserio.us` cannot coexist with prod in
this repo. Options:
- **(a) Second public repo** (`teamserio.us-dev`) with its own Pages site + `dev.teamserio.us`. Deploy via PAT. Closest to current behavior.
- **(b) Cloudflare Pages for dev.** Free, no 1 GB cap, real preview URLs per branch. Adds a second platform.
- **(c) PR artifact previews only.** Reviewer downloads `_site`. No public dev URL — changes the review habit.
- **(d) Keep dev on the AWS box.** Simplest, but the box (and its cost) stays.

### 5.5 Smaller items
- **`CNAME` file absent** — Pages needs `teamserio.us` in a root `CNAME`. Setting the custom domain in repo settings commits this for you; pull it afterward.
- **Repo is 1.58 GB**, over GitHub's 1 GB *recommendation* (not enforced). Resizing images fixes the working tree; only history rewrite shrinks `.git`.
- **404 status semantics change:** openresty currently serves unknown paths as **HTTP 200** with the 404 page; Pages will return a correct **404** status. An improvement, but worth knowing.
- **`/all.html` and `/all` both work today**; both will continue to work on Pages.
- **`/calendar` 301-redirects** today; Pages does the same for directory paths.
- **Both `/feed.xml` and `/atom.xml` exist** (jekyll-feed and the theme). Footer links `./atom.xml`. Unchanged by migration.
- **Relative asset refs:** 25 use `/assets/`, 8 use `assets/`, 1 uses `./assets/`. Behavior is identical on Pages, so not a migration risk — but the relative ones are fragile and would break if permalinks ever gain trailing slashes. Pre-existing hygiene item.
- **Sass deprecation warnings** from chulapa 1.1.0's Bootstrap 5 SCSS (71 suppressed). Noise, not failure.
- **`json 3.0` encoding warnings** appear under 2.1.0 (`UTF-8 string passed as BINARY, this will raise an encoding error in json 3.0`). Will become an error in a future json release; track it.
- **Pin Ruby in CI.** Workflows request `3.2.4` and also run a redundant `gem install jekyll bundler` before `bundle install` — drop that line; Bundler already manages both.

---

## 6. Target architecture

```
  push to main
       │
       ▼
  GitHub Actions
   ├─ actions/checkout
   ├─ ruby/setup-ruby (3.2.4, bundler-cache)
   ├─ bundle exec jekyll build      ← custom _plugins run here
   ├─ actions/upload-pages-artifact
   └─ actions/deploy-pages          ← no SSH, no secrets, no server
       │
       ▼
  GitHub Pages CDN  ←── teamserio.us (Namecheap A/AAAA → Pages IPs)
```

What disappears: the EC2 instance, openresty, four deploy secrets, the `rm -Rf` step, and
the extension-rewriting hack.

### Proposed production workflow
```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2.4'
          bundler-cache: true
      - uses: actions/configure-pages@v5
      - name: Build site
        env:
          JEKYLL_ENV: production
          JEKYLL_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: bundle exec jekyll build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```
Note: **no "Clean Extensions" step**, and no `jekyll build --baseurl` override —
`baseurl: ""` with a custom apex domain is already correct.

### DNS cutover (Namecheap)
Replace the A record to `3.139.113.70` with four A records:
```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```
Optionally the AAAA set:
```
2606:50c0:8000::153   2606:50c0:8001::153
2606:50c0:8002::153   2606:50c0:8003::153
```
`www` → CNAME to `rykerwilliams.github.io` (Pages auto-redirects between apex and www).
Then enable **Enforce HTTPS** in repo settings once the certificate is issued (can take up
to 24 h; the option is greyed out until then).

---

## 7. Decisions required before execution

1. ~~**Image strategy**~~ — **DECIDED 2026-10-08:** exempt decklists + headers, resize the
   bulk to 2560px q85, archive the 52 DSLR originals to `assets/originals/` + jsDelivr. See §5.1.
2. ~~**Videos**~~ — **DECIDED:** move the 3 MP4s to YouTube (jsDelivr 403s above ~50 MB).
2a. **Which photos get "full resolution" links?** The 52 `DSC_*` files are archived either
   way; open question is which posts surface the link in their text.
3. **Dev environment** — second repo, Cloudflare Pages, PR artifacts, or keep on AWS?
4. **Theme upgrade timing** — after the migration (recommended) or as part of it?
5. **History rewrite** — leave `.git` at 1.6 GB (harmless) or shrink it later?
6. **AWS box** — decommission after cutover, or does it serve anything else?

---

## 8. Phased plan

### Phase 0 — Staging proof (no production impact)
1. Branch `gh-pages-migration` off `main`.
2. Add the workflow above, triggered on that branch only.
3. Enable Pages (Source: GitHub Actions) — site appears at `rykerwilliams.github.io/teamserio.us`.
   Note: at that URL `baseurl: ""` makes root-relative `/assets/...` paths 404. Either set
   `baseurl: /teamserio.us` for staging only, or validate on a temporary subdomain instead.
4. Confirm it builds and deploys at all. **Stop here if the artifact exceeds 1 GB.**

### Phase 1 — Image diet (the actual work)
1. ~~Script a resize pass~~ **DONE — `script/prep-images.sh`** (2026-10-08). Dry run by
   default, `--apply` to write, `--path <dir>` to scope. Auto-builds a small ImageMagick
   container since the dev box has no ImageMagick and no passwordless sudo. Per-file
   timeouts and resource limits, so one malformed image cannot stall or abort a 300-file
   batch. Idempotent: files already within the cap are skipped and an archived original is
   never overwritten.

   **Validated on two folders:**
   - `assets/images/2025/08/16/KSI2` **applied**: 52.8 MB → 13.6 MB (74.2% smaller),
     7 originals archived, long edge exactly 2560px, portrait orientation preserved.
   - `assets/images/2023/02/19` dry run: **8 `deck-*` files correctly exempted**, 3 already
     within cap, 16 resized, 29.7% smaller.
   - Build verified: `_site` contains **0** files from `assets/originals/`, `script/` or `docs/`.

   **One file needs manual repair:** `assets/images/2025/08/16/KSI2/DSC_5360-angelo.jpg`
   has a malformed JFIF header (negative density, `-536x-536`) that makes ImageMagick hang.
   The script times out and leaves it untouched. It is still 9.6 MB at 4016x4741.
2. ~~Run it~~ **DONE 2026-10-08 — full `--apply` across the library:**

   | Result | Value |
   |---|---|
   | Images on disk | **743.8 MB → 274.6 MB** (61.9% smaller) |
   | Resized | 236 files |
   | Exempt (decklists, headers, logos, avatars) | 37 files |
   | Already within cap | 170 files |
   | Originals archived to `assets/originals/` | 45 files, 331.8 MB |
   | **Published `_site` (verified build)** | **905 MB → 436 MB** |
   | Originals leaked into `_site` | **0** |
   | Pages built | 43 (unchanged) |

   Re-running is a no-op (verified: second full pass reports 0 resized, 0 failed), so this
   is safe to run again after each new event.

   **The 436 MB still includes the 153.7 MB of video.** Once those move to YouTube the
   published site lands at roughly **282 MB — about 72% headroom** under the 1 GB cap.

   One corrupt file was found and repaired: `DSC_5360-angelo.jpg` had a JFIF density of
   65000 dots/cm (`fd e8`, which `file` reports as `-536`). ImageMagick either exceeded its
   time limit or aborted on an assertion and dumped core; neutralising the density with
   exiftool did not help. **libvips read it in 1.1 s.** The script now falls back to
   `vipsthumbnail` whenever ImageMagick fails, and the repaired file is 9.6 MB → 577 KB with
   no visible quality loss.
3. Replace the 3 MP4s with YouTube embeds (or move to object storage).
4. Add a **resize guardrail** — `calibreapp/image-actions` has no resize or
   max-dimension option and cannot convert formats (verified: its only settings are
   `jpegQuality`, `jpegProgressive`, `pngQuality`, `webpQuality`, `avifQuality`,
   `ignorePaths`, `compressOnly`, `minPctChange`, `minAbsChange`). So the cap needs either
   a custom ImageMagick/libvips step in a PR workflow that resizes and commits, or a local
   `script/prep-images.sh` run before committing a new event. Keep image-actions for
   compression on top.
5. Sort the 52 `DSC_*` originals into `assets/originals/`, add `assets/originals/` to
   `exclude:`, and add "download full resolution" jsDelivr links where wanted.
6. **Gate: published artifact must be ≤ 400 MB** (projection is ~255 MB). Add a CI check
   that fails the build if `_site` exceeds it, so this cannot silently recur.

### Phase 1b — Video rehome to YouTube

The three MP4s are the largest published files by an order of magnitude and the only
remaining bandwidth hazard.

| File | Resolution | Duration | Bitrate | Size | Used in |
|---|---|---|---|---|---|
| `2026/02/07/1000010024.mp4` "The Icebox" | 1280x720 **landscape** | 3:11 | 3750 kb/s | **85.6 MB** | `_posts/2026-02-07-castmaster-at-hsi.md:119` |
| `2024/06/08/8-n4xc8Fk.mp4` "Sort Video" | 720x1280 **portrait** | 1:00 | 5979 kb/s | **42.8 MB** | `_posts/2024-06-08-castmaster-season-1.md:121` |
| `2024/06/08/5-wyoZN7z.mp4` "Jimmy and JR Paint" | 720x1280 **portrait** | 1:00 | 3538 kb/s | **25.3 MB** | `_posts/2024-06-08-castmaster-season-1.md:159` |

All three are plain HTML5 `<video>` tags — no player library to replace.

#### Why not just re-encode and keep self-hosting?

Measured (H.264 CRF 24, preset medium, AAC 128k):

| | Before | After | Saving |
|---|---|---|---|
| Sort Video | 42.8 MB | 26.6 MB | 38% |
| Jimmy and JR Paint | 25.3 MB | 16.7 MB | 34% |
| The Icebox | 85.6 MB | 61.2 MB | 29% |
| **Total** | **153.7 MB** | **104.5 MB** | **32%** |

Not enough. 104 MB still sits in the published site and, more importantly, still streams out
of the 100 GB/month soft bandwidth allowance on every play. YouTube removes the storage
*and* the bandwidth, and gives seeking, captions, mobile playback and adaptive quality for
free. **Recommendation: YouTube.**

#### Tooling: is there an MCP for this?

**No.** Connected servers are Gmail, Google Drive, Google Calendar and Claude Docs — none
covers YouTube, and there is no `yt-dlp` or `gcloud` on this box. Options:

1. **Manual upload via YouTube Studio — recommended.** Three one-off files, roughly ten
   minutes total. No setup, no credentials, no new trust boundary.
2. **YouTube Data API v3 script.** Needs a Google Cloud project, an OAuth client and a
   consent flow. Quota is not the constraint (the default allocation covers far more than
   three uploads); the setup effort is. Worth building only if video becomes a per-event
   habit, in which case it belongs in the same script as the image prep.
3. **A third-party YouTube MCP server.** Community-maintained, and would need write access
   to the YouTube account. For three one-off uploads the setup and trust cost exceeds the
   benefit.

Note that under every option the upload authenticates as the account owner, so this step
needs a human either way.

#### Shape matters for the embeds

Two of the three are **720x1280 portrait, exactly 1:00** — i.e. YouTube Shorts shape. A
standard 16:9 iframe would letterbox them into thin slivers. Use a 16:9 wrapper for The
Icebox and a 9:16 wrapper with a sane max-width for the two portrait clips, or they will
dominate the page on desktop.

Landscape (Bootstrap 5, which Chulapa already ships):
```html
<div class="ratio ratio-16x9">
  <iframe src="https://www.youtube.com/embed/VIDEO_ID" title="The Icebox"
          frameborder="0" allowfullscreen loading="lazy"></iframe>
</div>
```

Portrait:
```html
<div class="ratio mx-auto" style="--bs-aspect-ratio: 177.78%; max-width: 360px;">
  <iframe src="https://www.youtube.com/embed/VIDEO_ID" title="Sort Video"
          frameborder="0" allowfullscreen loading="lazy"></iframe>
</div>
```

#### Decisions needed

1. **Which channel** — `@FullWarningPodcast` or `@SeriousVintageCast`? These are Castmaster
   event clips, not episodes, so neither is an obvious home.
2. **Visibility** — **unlisted** is suggested: embeds work normally and the clips stay off
   the channel's public feed, which suits incidental event footage. Public if you want them
   discoverable.
3. **Shorts or regular** for the two portrait 1:00 clips.
4. **Keep the source files?** Suggested: `git mv` them into `assets/originals/` rather than
   deleting. They leave the published site (that directory is excluded) but stay archived in
   the repo. Note `.git` will not shrink either way, since history already contains them,
   and jsDelivr will not serve files this large, so YouTube is the only serving path.

#### Steps

1. Upload the three clips; record the video IDs.
2. Replace each `<video>` block with the matching iframe wrapper above.
3. `git mv` the three MP4s into `assets/originals/` (or delete, per decision 4).
4. Rebuild and confirm the published site drops to roughly **282 MB**.
5. Check both posts render correctly on mobile, where the portrait embeds matter most.

### Phase 2 — Validation on staging
1. Deploy the slimmed site to staging.
2. Verify (extensionless resolution is already proven, but confirm for this site): post
   URLs resolve **without** `.html`; the custom 404 returns 404 with the themed page; `/all`, `/search`, `/posts/`, `/calendar`, `/tags`,
   `/categories`, `/full-warning` all load; `sitemap.xml`, `feed.xml`, `atom.xml` present;
   lunr search works; the Google Calendar block renders; decklist and `<<Card Name>>`
   autocard tags render.
3. Crawl staging for broken links and diff the URL inventory against the live site.

### Phase 3 — Cutover
1. Set custom domain `teamserio.us` in repo settings; pull the generated `CNAME`.
2. Lower TTL if needed (already 30 s) and update Namecheap A/AAAA records.
3. Watch propagation; verify HTTPS; enable **Enforce HTTPS** once available.
4. **Leave the AWS box running and untouched** for at least a week.

### Phase 4 — Cleanup
1. Delete the SSH/SCP deploy steps and the four `DEPLOY_*` secrets.
2. Re-point or retire `dev.teamserio.us` per decision #3.
3. Decommission the EC2 instance once prod is stable (decision #6).
4. Separately: upgrade to chulapa 2.1.0 on `dev` (`repository:` line, `maxwords` rename,
   delete `_plugins/grouptag.rb`, review the custom includes/layout), then promote.

### Rollback
At any point before Phase 4, revert the Namecheap A record to `3.139.113.70`. With a 30 s
TTL, recovery is effectively immediate, and the AWS box still holds a complete copy of the
site. This is the cheapest rollback story available — worth preserving by not rushing Phase 4.

---

## 9. Not verified / open questions

- **openresty config** — no access to the box; if it contains rewrites, redirects, or custom headers beyond extension handling, those are invisible to this investigation and would be silently lost. **Worth dumping the nginx/openresty config before decommissioning.**
- **Actual traffic volume** — unknown, so the 100 GB/month soft limit cannot be assessed. Check whatever analytics or server logs exist before cutover.
- **Anything else on that EC2 instance** — other sites, mail, cron jobs?
- **Visual fidelity of chulapa 2.1.0** — page *count* is identical (43), but no rendering comparison has been done.
- **`dev.teamserio.us` DNS** — not inspected; assumed to point at the same box.
