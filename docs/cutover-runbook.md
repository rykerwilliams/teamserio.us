# Cutover Runbook — AWS to GitHub Pages

Ordered steps to publish `teamserio.us` from GitHub Pages. Each step says who does it.
Rollback is available at every point until step 7.

**Facts this runbook depends on** (measured 2026-10-09):

- Apex `A` record TTL is **1799 s (~30 min)**, not 30 s. Lower it before cutover or rollback
  is slow.
- The live site sends **no HSTS header**, so a brief HTTPS gap degrades to HTTP rather than
  hard-failing in browsers.
- `*.teamserio.us` wildcard points at the AWS box and stays that way.
- A custom domain must be bound by a **deployment**: setting it on an already-published site
  left the edge serving "Site not found" until a redeploy.

---

## Step 0 — Lower the TTL (you, Namecheap) — at least 30 min ahead

Set the apex `A` record TTL to **1 min** (Namecheap's minimum). This only makes the *next*
change propagate fast; it has to be in place before the change you want to roll back from.
Raise it again after the soak.

## Step 1 — Merge the branch to `main` (me, on your go-ahead)

`gh-pages-migration` is 15 commits ahead. Merging triggers two workflows:

- `jekyll-build-and-deploy-prod.yml` -> deploys the new build **to AWS**, so the content
  changes (thumbnails, YouTube embeds, no weserv) go live on infrastructure you already
  trust, with nothing depending on Pages yet.
- `deploy-pages.yml` -> publishes the production build to the Pages site.

Side effect: `preview.teamserio.us` starts serving a build whose links point at
`teamserio.us`. Cosmetic, and only we look at it.

**Rollback:** `git revert` and let the AWS workflow redeploy.

## Step 2 — Verify the content on the real site (you)

`https://teamserio.us` is still AWS. Check galleries, the three YouTube embeds, decklists,
search, calendar. This separates "did the content changes work" from "did the hosting move
work", so only one variable is in play at a time.

## Step 3 — Point Pages at the apex (me)

1. Set the Pages custom domain to `teamserio.us`
2. **Re-run `deploy-pages.yml`** — required, see the note above
3. `preview.teamserio.us` stops working at this point. Expected.

Pages is now ready to serve the apex, but DNS still sends visitors to AWS, so nothing
changes for them yet.

## Step 4 — Flip DNS (you, Namecheap)

Replace the apex `A` record (`3.139.113.70`) with four `A` records:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

Optionally also `AAAA`: `2606:50c0:8000::153`, `8001::153`, `8002::153`, `8003::153`.

Change `www` from its current CNAME-to-apex into `CNAME www -> rykerwilliams.github.io`.

Leave the `*` wildcard alone for now; it still catches `dev.teamserio.us`.

## Step 5 — Watch it land (me)

Propagation, then a URL sweep: pages, feeds, sitemap, extensionless post URLs, assets, 404
behaviour. Expect brief flapping between AWS and Pages while caches expire, and HTTPS
errors on requests that still land on AWS (that box has no cert for a Pages-issued domain).

Once the certificate issues — minutes in the preview's case, up to 24 h worst case — turn on
**Enforce HTTPS** in Settings > Pages.

## Step 6 — Soak, at least a week

Leave the AWS box running and the AWS workflow in place. Both targets stay current, so
**rollback is restoring one `A` record**.

## Step 7 — Cleanup (only after the soak)

1. **Dump the openresty config off the box before touching it.** If it holds redirects or
   headers beyond extension handling, that is invisible from the repo and lost forever.
2. Delete `jekyll-build-and-deploy-prod.yml` and the four `DEPLOY_*` secrets
3. Delete `deploy-pages-preview.yml`, `_config_staging.yml`, and the `preview` DNS record
4. Delete the `gh-pages-migration` branch
5. Align `dev`'s `_config.yml` to the production `url:`, **then** remove `merge=ours` from
   `.gitattributes` and `git checkout HEAD -- _config.yml` from the promote workflow
   (in that order, or the next promote pushes the dev URL into production)
6. Decide what `*.teamserio.us` should point at once the box is gone
7. Raise the apex TTL back to something normal
8. Decommission the EC2 instance

---

## How publishing works afterwards

One workflow, `deploy-pages.yml`: **any push to `main` builds and publishes.** There is no
separate upload step, no SSH, no secrets.

| You want to | You do |
|---|---|
| Publish a change | Merge to `main` — publishing is automatic |
| Publish without a code change | Actions > *Deploy to GitHub Pages* > **Run workflow** (`workflow_dispatch`) |
| Check a change before publishing | Push a branch or open a PR — `build-check.yml` runs the same build and checks, publishing nothing |
| Preview locally | `bundle exec jekyll serve --config _config.yml,_config_preview.yml` |
| Promote `dev` | `promote-dev-to-prod.yml` still works, but see Step 7.5 — `dev` is far behind and needs reconciling first |

### Adding a new event write-up

1. Drop photos in `assets/images/<year>/<month>/<day>/...` as you do now
2. Write the post, commit, push **to a branch** (not `main`)
3. `prep-images.yml` runs automatically: it resizes, archives DSLR originals, generates
   thumbnails and commits the result back to your branch. Pull before continuing.
4. Merge to `main` — publishing is automatic

You can still run `script/prep-images.sh --apply` locally if you prefer; the script is
idempotent, so CI will simply find nothing to do.

The workflow deliberately does not run on `main`, because a bot commit there would trigger a
publish mid-flight. If unprepped images ever do reach `main`, the gallery-integrity check
fails the build rather than publishing a page with missing thumbnails.

> **`calibreapp/image-actions` was removed.** It recompressed images that `prep-images.sh`
> had already compressed at a chosen quality — including `assets/originals/`, where it
> destroyed about 78% of the archived full-resolution data (337 MB → 72.6 MB) as an
> automatic bot commit. Do not reinstate it without excluding every path the prep script
> manages.

### The guardrails that now exist

- **Size guard** — build fails over 900 MB, warns over 500 MB (currently ~293 MB)
- **Gallery integrity** — every thumbnail and full-size link must resolve
- **Calendar** — falls back to the committed snapshot and warns; fails the build only if
  there is no snapshot at all
- **Oversized images** — warns on anything over 3 MB still in `assets/images/`
- **Image prep** — runs automatically on branches and PRs, committing the result back
