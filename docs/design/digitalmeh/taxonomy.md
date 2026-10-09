# digitalmeh.net — proposed taxonomy

Derived from the restored database, 2026-10-09. See
[post-manifest.csv](post-manifest.csv) for the per-post decisions this is based on.

## The problem

| | Count |
|---|---|
| Tags in WordPress | **499** |
| Used exactly once | **390** (78%) |
| Used zero times | 17 |
| Used 3+ times | 41 |
| Categories | 20 |

Tags were used as keywords — a phrase typed once while writing — rather than as a
navigational structure. Migrating them as-is would carry 390 tag pages with one post each.

The **categories are the opposite**: 20 of them, every one used, and they describe real
subject areas. They should survive largely intact.

## Proposal

### 1. Keep the categories, minus the obvious cleanup

`software` 55 · `mtg` 37 · `gnu/linux` 31 · `media` 31 · `hardware` 27 · `web` 24 ·
`sound` 22 · `oldschool` 15 · `vintage` 15 · `ubuntu` 12 · `image` 10 · `gentoo` 9 ·
`theState` 8 · `apple` 8 · `middle school` 6 · `n85` 5 · `food snob` 3 · `sport` 2 ·
`Uncategorized` 2

Cleanup needed:
- **`middle school` appears twice** (6 posts and 1 post) — a duplicate term to merge
- **`Uncategorized`** (2 posts) — assign them properly and drop it
- `n85` is a phone model; it is arguably a tag, not a category

### 2. Drop every tag that duplicates a category

Nine do: `food snob`, `gnu/linux`, `middle school`, `mtg`, `n85`, `oldschool`, `software`,
`ubuntu`, `vintage`. The category already carries that meaning.

### 3. Consolidate the rest into ~15–20 tags

The 41 tags that survive a 3× threshold still contain obvious synonym clusters:

| Cluster | Members | Suggested |
|---|---|---|
| Magic variants | `magic`, `mtgoldschool`, `middleschoolmtg`, `invintage`, `tsl`, `tsl:vintage`, `9394` | fold into categories; keep `tsl` only if the league matters |
| Deck archetypes | `combo`, `workshop`, `lich`, `dragon` | **keep** — genuinely finer than the category |
| Linux | `linux`, `gnu/linux` | fold into the `gnu/linux` category |
| Windows | `windows`, `windows 7`, `xp` | keep `windows`; drop version-specific |
| Microsoft dev | `.net`, `asp.net`, `IIS`, `sharepoint`, `sharepoint 2010` | keep `.net` and `sharepoint` |
| Nokia / Symbian | `nokia`, `symbian`, `s60`, `n85` | keep `symbian`; it dates the content usefully |
| Hardware | `dell`, `eeepc` | keep |
| Misc | `android`, `os x`, `google`, `review`, `libertarian`, `ec`, `Food Blog` | keep `android`, `os x`; review the rest |

**Target: 20 categories, 15–20 tags.** Down from 20 and 499.

This is a content-design judgement, not a scripting one — the table above is a starting
point for a human pass, not an answer.

## Rule for anything dropped

A dropped tag is not lost information: the words are still in the post body, and the site
will have search. Tags earn their place by being a route someone would actually navigate,
not by recording that a topic was mentioned.
