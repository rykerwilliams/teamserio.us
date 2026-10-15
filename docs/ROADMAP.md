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
- [ ] **Add AAAA records for the apex.** `teamserio.us` resolves to four A records and no
      AAAA, so the apex has no IPv6 path at all; `www` has one only because it is a CNAME to
      the `github.io` host. GitHub publishes four Pages addresses for apex domains:
      `2606:50c0:8000::153` through `:8003::153`. Low priority — IPv6-only clients reach the
      site today through carrier NAT64/DNS64, and this explains no observed failure.
      `digitalmeh.net` has the identical gap, so do both or neither.

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
- [x] ~~**Outbound links open in a new tab**~~ — 2026-10-13 (#35).
      `_plugins/external_links.rb` adds `target="_blank" rel="noopener noreferrer"` to
      every external link at render time, so contributors need not remember it. It also
      normalised what was there by hand: **41 anchors said `noreferer`**, one `r`, which
      is not a real rel token, so those links were still sending a referrer. A
      `:post_render` hook rather than a Generator, because at generator time the content
      is still Markdown and holds no `<a>` tags. Trap worth remembering: the first version
      rescued `URI.parse` failures and treated the link as internal — several hrefs end in
      an invisible U+2060 WORD JOINER and one has a trailing space, so they were skipped
      silently. Failing open is the wrong default for a security attribute.
- [x] ~~**MTGO download buttons pointed at a host called `assets`**~~ — 2026-10-13 (#36).
      `deckfile_tag.rb` built the href as `"/" + rel_path`, so a tag argument written with
      a leading slash produced `href="//assets/files/..."`. A browser reads a leading `//`
      as **protocol-relative**, resolving it to `https://assets/...` — a host that does not
      exist — so every download button on the HSI-9 post was dead on the live site. Eight
      posts use the leading-slash form and eight do not, which is why it went unnoticed,
      and all five examples in the contributor templates teach the broken form. Normalised
      to exactly one leading slash, so both spellings work.
- [ ] **Port `?v=` cache-busting from `digitalmeh.net`.** Asset URLs here are unversioned,
      so a browser holding an old `main.css` against new HTML has nothing to invalidate it.
      That site appends `?v={{ modified_time }}` to its asset links. Note this guards the
      **browser** cache only — query strings proved to have no effect on the CDN; see below.
- [ ] **Know the gzip-variant CDN failure mode.** On 2026-10-13 `digitalmeh.net` served every
      visitor an unstyled site: GitHub's CDN held a stale 404 for the *gzip-compressed*
      variant of two asset paths, cached before those files existed. `vary: Accept-Encoding`
      keeps a separate cache entry per encoding, so `curl` — which sends no `Accept-Encoding`
      by default — returned a healthy 200 from the uncompressed entry while every browser got
      the 404. Query strings get no separate cache key and the CDN ignores client
      `Cache-Control: no-cache`, so nothing client-side can clear it. **The remedy is a fresh
      Pages deploy**, which purges the CDN; a `workflow_dispatch` run is enough. When checking
      a live asset, always send `-H 'Accept-Encoding: gzip, deflate, br'`.

## Cosmetic / layout / CSS

- [x] **Rotate the site tagline on each deploy.** Done, with one tagline in the
      list. The home page title fell through to the GitHub repository's
      description field, which read **"testing"**, so every browser tab and
      every shared link said `TeamSerio.us | testing`. It was invisible from a
      checkout, which is why it lasted.

      `_data/taglines.yml` holds the list and `_plugins/tagline.rb` picks one at
      build time, so adding taglines needs no code change. The choice is
      deterministic, seeded from the commit SHA, so rebuilding a commit does
      not quietly change what a shared link says.

      Still wanted: more taglines. Rajah has some.


- [ ] Social media links on articles

## Content

- [x] ~~**Merch showcase**~~ — 2026-10-13 (#31). A `_merch` collection, a gallery at
      `/merch/`, and a copy-to-clipboard enquiry cart. Not a store: no checkout, no payment,
      and no email addresses in public files — visitors collect items, copy a list grouped by
      maker, and message that person on Slack or Discord. Prices are free text, so `$25`,
      `trade` and `ask` all work; only numeric ones are totalled.
- [x] ~~**First contributor-kit submission published**~~ — 2026-10-13 (#33). Mike
      Klements' Middle School Intercontinental Championship report from TSI7, the first
      write-up to come back through the template kit.

      **What to expect from a returned kit.** It arrived as two zips. The newer one's
      Markdown read cleanly but was a condensed rewrite that had lost roughly half the
      piece — the standings cut from 27 players to 11, the guest round-by-round report
      dropped entirely, placeholders left unfilled, and the author recorded as a deck name
      rather than a person. The older zip was faithful but had been through a
      Word-to-Markdown converter that escaped everything, including the `---` front matter
      delimiter. **Prefer the author's original document**, which that zip also contained,
      and verify the result against it rather than against either Markdown file.

      Worth adding to the kit READMEs: say plainly that sending the original Word document
      alongside is welcome, and that a Markdown export is not required.
- [ ] **Get the first real merch item.** `/merch/` ships **empty** — the one example is
      `published: false`, so nothing appears until a real item lands. The member kit is
      `templates/merch-item/`.
- [x] ~~**Contributor Templates v2**~~ — 2026-10-13. All four fill-in-the-blank kits published
      as release assets: the three write-up kits refreshed from `main`, plus the new
      `merch-item` kit. v1 stays up for anyone part-way through one; the format is unchanged.
      Kits live in `templates/`, which `_config.yml` excludes from the build, so they are
      distributed by release rather than served from the site.
- [ ] Media page for songs and videos
- [ ] Decklists locally
- [ ] **Port the TSI/TSO write-ups off The Mana Drain.** The forum reorganised and those
      threads now 404; they survive only in the Internet Archive. **39 candidate reports,
      deck techs and metagame pieces**, inventoried with snapshot links in
      [tmd-archive-reports.md](tmd-archive-reports.md), rebuildable with
      `script/tmd-inventory.py`. Several are other people's write-ups — Nat Moes
      (`grandpabelcher`), Jimmy (`lhc`), `presidentskroob`, `thallidtosser` — so check the
      author on each thread and credit them. **Coverage is incomplete**: only
      `grandpabelcher` and `xxhazardxx` have archived `/topics` listings, so for everyone
      else a write-up is only found if its title happens to match a keyword. Rajah's and
      Nam Tran's own TMD handles are not identified yet; adding them would help more than
      more keywords. Once a report lands here, the five `digitalmeh.net` posts linking
      these threads should point at the new post instead of the archive snapshot.
- [ ] **"What was legal when" — a date-driven Vintage card pool.** Given a date, show the
      Banned and Restricted list as it stood, and a Scryfall query for the legal pool, so a
      throwback tournament can be run off a link.

      **The problem with the existing sources.** Eternal Central's
      [Timeline of Vintage](https://www.eternalcentral.com/timeline-of-vintage/) and
      [Schools of Magic: History of Vintage](https://www.eternalcentral.com/history-of-vintage-schools-of-magic-an-alternative-history-of-the-banned-and-restricted-list/)
      publish the *changes* — this card restricted, that one unrestricted — but never the
      **state** on a given day. Working out what was actually legal in, say, spring 1999
      means replaying every announcement from 1994 forward and hoping none were missed.

      ⚠️ **Do not use the Schools of Magic piece as a source.** It is Menendian's
      *alternative* history: counted mechanically it carries **23 "should have been
      restricted/banned" statements against 3 describing what actually happened**. Scraping
      it would silently blend the real list with the author's counterfactual one, and
      people would be building tournament decks from the result. It is worth reading for
      the reasoning behind each decision; it is not a record of them. Take the actual
      actions from the timeline page, cross-checked against WotC's own B&R announcements.

      **Data model.** One append-only list of events — `{date, card, action}` where action is
      restrict / unrestrict / ban / unban — replayed to any date to get the state. Kept as a
      reviewable JSON file in the repo, not scraped at page load, so corrections are a diff
      and the provenance of each entry can carry a source link.

      **The Scryfall part works** — tested:

      | query | result |
      |---|---|
      | `date<=1994-12-31 game:paper` | 981 cards |
      | `date<=2003-12-31 game:paper -is:funny -is:digital` | 6,512 cards |
      | same, with banned cards excluded by name | works; 20 exclusions is a 478-char query |

      Vintage's *banned* list is short — ante cards, Chaos Orb, Falling Star, Shahrazad,
      conspiracies — so excluding by name is practical. Restricted cards stay legal at one
      copy, so they are a displayed list rather than a filter.

      **Open questions before building.**
      - `date<=` matches a *printing*, so a card reprinted later still matches on its early
        printing — needs checking that this does not let a card in before it existed.
      - Which sets were ever Vintage-legal needs stating explicitly (Un-sets, Alchemy and
        other digital-only sets, Portal-era oddities).
      - Announcement date vs effective date differ, especially in the 1990s; the list should
        key off whichever one a tournament would have used.
      - Cards renamed or errata'd since would need mapping to current Scryfall names.
      - Verification: reconstruct the state at a handful of known dates and diff against
        archived copies of WotC's B&R page. Without that the page is guesswork, and people
        would be building decks from it.

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
