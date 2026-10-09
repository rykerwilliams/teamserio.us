# Roadmap

Moved out of `README.md` 2026-10-09. Items completed by the GitHub Pages migration are
marked; see [impl/gh-pages-migration/](impl/gh-pages-migration/).

---

## Migration follow-ups

These have ordering constraints or deadlines attached.

- [ ] **Decommission the AWS box.** It no longer receives deploys, so it holds a frozen
      copy of the site as of 2026-10-09. A DNS rollback still works but would serve that
      snapshot, not anything published since.
- [ ] **Dump the openresty config off the AWS box before decommissioning.** If it holds
      redirects or headers beyond extension handling, that is invisible from the repo and
      lost permanently.
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
      subdomain, including `dev`, to the AWS box.
- [ ] **Raise the apex TTL** back from 1 minute once the deployment is settled.

## Backend / build

- [ ] **Upgrade chulapa 1.1.0 → 2.1.0.** Needs `repository: rykerwilliams/teamserio.us` in
      `_config.yml` (verified: it fails to build without it), deleting the now-obsolete
      `_plugins/grouptag.rb`, and renaming `search.lunr_maxwords` to `search.maxwords`.
      Check the custom includes and `_layouts/default-with-decklists.html` afterwards.
- [ ] **Add `width`/`height` to gallery images.** They are `loading="lazy"` with no
      dimensions, so they reserve no space and the page shifts as thumbnails load. Every
      square thumbnail is 700×700, so this is a one-line change.
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
