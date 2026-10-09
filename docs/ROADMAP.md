# Roadmap

Moved out of `README.md` 2026-10-09. Items completed by the GitHub Pages migration are
marked; see [impl/gh-pages-migration/](impl/gh-pages-migration/).

---

## Migration follow-ups

These have ordering constraints or deadlines attached.

- [ ] **Read [impl/aws-box/inventory.md](impl/aws-box/inventory.md) before planning anything
      involving that host.** It runs two production applications, not just WordPress:
      cheertime deploys to it **every 10 minutes**. Decommissioning is not on the table.
- [ ] **Reclaim disk — the box is at 82%** with a disk-alert cron running. ~1.8 G of stale
      digitalmeh backups in `~`, plus the now-obsolete `teamserio.us-prod` and `-dev`
      containers. Archive the backups off-box first; stopping those containers permanently
      ends the DNS rollback to AWS.
- [ ] ~~**The AWS box is NOT retired — it also hosts `digitalmeh.net`.**~~ teamserio.us no
      longer depends on it, but the instance cannot be shut down. That site is
      **WordPress 6.5.13 on PHP 8.3.4**, served by the same openresty, with DNS at GoDaddy
      (`domaincontrol.com`) rather than Namecheap. Its A record points straight at
      `3.139.113.70`.
- [ ] **Migrate `digitalmeh.net` off WordPress** — designed in
      [design/digitalmeh-migration.md](design/digitalmeh-migration.md). Blocked on SSH
      access to the box. This is what finally allows the instance to be decommissioned.
- [ ] **Patch or replace `digitalmeh.net` in the meantime.** WordPress 6.5.13 is well behind current, and
      a public WordPress that stopped being maintained because the box was "about to be
      decommissioned" is worth a deliberate decision: update it, move it to managed hosting,
      or retire it. Dynamic PHP has a far larger attack surface than the static site that
      just left this box.
- [ ] **Decide what happens to the frozen teamserio.us copy on that box.** It stopped
      receiving deploys on 2026-10-09, so it holds a snapshot from that date. A DNS rollback
      still works but would serve that snapshot rather than anything published since — which
      gets staler and more misleading over time. Either refresh it deliberately, or delete
      it and accept that rollback is no longer an option.
- [ ] **Dump the openresty config off the AWS box.** It now matters for two reasons: any
      redirects or headers it held for teamserio.us are invisible from this repo, and it
      also carries the vhost config for the WordPress site still running there.
- [x] ~~Align `dev` and remove the config-divergence guards~~ — 2026-10-09. `dev` was 35
      commits behind and held nothing worth keeping (its only unique files were two
      decklists renamed to incorrect spellings), so it was reset to `main` rather than
      merged. Recovery point if ever needed: `023bcef`. Both guards removed.
- [ ] **Delete the `preview` DNS record** at Namecheap (the only preview leftover).
- [ ] **Delete the five `DEPLOY_*` secrets** — `DEPLOY_HOST`, `DEPLOY_HOST_DIR`,
      `DEPLOY_HOST_PORT`, `DEPLOY_SSH_KEY`, `DEPLOY_USERNAME`. Unused now that the AWS
      workflow is gone; an unused SSH key in a public repo's secrets is worth retiring.
- [x] ~~Remove the preview scaffolding~~ — `deploy-pages-preview.yml`, `_config_staging.yml`
      and the `gh-pages-migration` branch deleted 2026-10-09
- [x] ~~Delete `jekyll-build-and-deploy-prod.yml`~~ — deleted 2026-10-09
- [ ] **Decide what `*.teamserio.us` should point at.** The wildcard still sends every
      subdomain, including `dev`, to the AWS box. Verified safe to change: `digitalmeh.net`
      is a separate domain with its own A record, so it does not depend on this wildcard.
- [ ] **Raise the apex TTL** back from 1 minute once the deployment is settled.

## Backend / build

- [x] ~~Upgrade chulapa 1.1.0 → 2.1.0~~ — 2026-10-09. Also uncovered a latent bug in
      `_plugins/mtg_autocard.rb`, which rewrote `((Card Name))` across *every* page
      including theme JavaScript assets; 2.x's search script contains
      `.map(([key, indices]) => ({...}))`, whose doubled parens matched, breaking search
      with a syntax error. The plugin is now scoped to HTML output.
- [x] ~~Add `width`/`height` to gallery images~~ — 2026-10-09. Measured with image bytes
      blocked, so the browser could only use declared dimensions: the gallery went from
      collapsing to 31px to reserving 332px. Applies to the six square includes; the
      proportional `image-gallery-no-caption-3-per-responsive` is left alone because each
      thumbnail has its own aspect ratio and Jekyll cannot read image dimensions without a
      plugin. One gallery uses it.
- [ ] *(optional)* Reserve space in the proportional gallery too, by having
      `prep-images.sh` emit a thumbnail-dimension map into `_data/` for the include to read.
      Only worth it if more galleries start using that layout.
- [ ] Open external links with `target="_blank"`
- [ ] Disqus comments
- [ ] Two posts contain hardcoded `https://teamserio.us/posts/...` cross-links; make relative
- [x] ~~Document how the site is built and the deployment architecture~~ — `docs/impl/`
- [x] ~~Consolidate build scripts to one instead of one per branch~~ — single
      `deploy-pages.yml`; the dev site is retired
- [x] ~~Build step to change `_config.yml` before the Jekyll build~~ — config overlays
      (`_config_preview.yml`, `_config_staging.yml`) instead of mutating the tracked file

## Cosmetic / layout / CSS

- [ ] Social media links on articles

## Content

- [ ] Media page for songs and videos
- [ ] Decklists locally
- [ ] Old posts from TMD
- [ ] **Bios collection** — Team Serious CV pages. Interview questions:
  - Favorite Team Serious member
  - Straight up: black licorice?
  - What Magic card looks most appetizing to you?
  - You can ask Richard Garfield any question. What would it be?
  - What percentage of your collection is old enough to drive? Drink? Rent a car?
  - Favorite Magic color, because it's corny AF
  - What's your favorite fruit-themed card?
  - Which Magic card would look better with a pentagram on it?
  - What would your cumulative upkeep be if you had one?
  - Who else in your family plays Magic? What do your parents think about it?
  - Sandwich punch? In?
  - How many hot dogs could you eat in under 10 minutes?
  - Hour Power or Edward 40 Hands?
  - Stadium mustard or ballpark mustard?
  - Notable finishes?
