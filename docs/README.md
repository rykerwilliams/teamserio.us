# Documentation

| | |
|---|---|
| [ROADMAP.md](ROADMAP.md) | What's planned and what's outstanding |
| [impl/](impl/) | How things were built — one folder per project |
| [design/](design/) | Proposals, written before building |

Work on other systems lives in their own repos: the **digitalmeh.net** WordPress migration
in the `digitalmeh.net` repo, and the **AWS box inventory** in `aws-docker`.

Nothing here is published: `docs/` is in the `exclude:` list in `_config.yml`.

## Layout

```
docs/
├── ROADMAP.md
├── design/                     proposals, before the work
└── impl/                       records, during and after the work
    └── gh-pages-migration/
        ├── plan.md             investigation, measurements, decisions
        ├── summary.md          narrative of what happened and why
        └── cutover-runbook.md  the steps, and how to publish afterwards
```

**`impl/` is for work that happened.** One folder per project. Keep the measurements and the
rejected options in it, not just the outcome — the numbers behind a decision are what make
it reviewable later, and the option you rejected is the one someone will propose again.

**`design/` is for work that hasn't happened yet.** Move a design into `impl/` when it ships,
or delete it when it doesn't.

## Start here

New to the deployment? Read
[impl/gh-pages-migration/cutover-runbook.md](impl/gh-pages-migration/cutover-runbook.md) —
the "How publishing works afterwards" section covers day-to-day: adding a post, what CI does
for you, and the guardrails that will fail a build.
