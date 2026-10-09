# Roadmap

Moved out of `README.md` 2026-10-09. Items completed by the GitHub Pages migration are
marked; see [impl/gh-pages-migration/](impl/gh-pages-migration/).

---

## Migration follow-ups

These have ordering constraints or deadlines attached.

- [ ] **Read the box inventory in the private `aws-docker` repo before planning anything
      involving that host.** It runs other production services; decommissioning is not on
      the table.
- [ ] **Retire the obsolete `teamserio.us-prod` and `-dev` containers on the old host** and
      reclaim their space. Doing so permanently ends the DNS rollback to AWS, so make it a
      decision rather than an accident. Host details are in the private `aws-docker` repo.
- [ ] **The AWS box is not retired.** teamserio.us no longer depends on it, but other
      tenants do and the instance cannot be shut down. Details are in the private
      `aws-docker` repo rather than here — this repository is public, and a public
      inventory of an unpatched host's software versions is free reconnaissance.
- [ ] **Migrate `digitalmeh.net` off WordPress** — tracked in the **`digitalmeh.net` repo**,
      not here. Phases 0–2 done; phase 3 awaits content decisions. This is what finally allows the instance to be decommissioned.
- [ ] **Patch or replace `digitalmeh.net` in the meantime.** Tracked in that repo. A
      WordPress install that stopped being maintained because the box was "about to be
      decommissioned" deserves a deliberate decision rather than drift.
- [ ] **Decide what happens to the frozen teamserio.us copy on that box.** It stopped
      receiving deploys on 2026-10-09, so it holds a snapshot from that date. A DNS rollback
      still works but would serve that snapshot rather than anything published since — which
      gets staler and more misleading over time. Either refresh it deliberately, or delete
      it and accept that rollback is no longer an option.
- [ ] **Dump the reverse-proxy config off the old host.** Any redirects or headers it held
      for teamserio.us are invisible from this repo and would be lost.
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
      subdomain, including `dev`, to the old host. Verified safe to change: the other
      tenants use their own domains or explicit records, so nothing depends on the wildcard.
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
