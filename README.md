A Jekyll site for [teamserio.us](https://teamserio.us), hosted on GitHub Pages.

## Running it locally

```bash
bundle install
bundle exec jekyll serve --config _config.yml,_config_preview.yml
```

The `_config_preview.yml` overlay matters: without it the theme builds absolute URLs from
`site.url`, so a local preview loads its CSS from the live site and navigates there on the
first click.

## Publishing

**Push to `main` and it publishes.** `deploy-pages.yml` builds and deploys to GitHub Pages;
there is no upload step.

Adding a post with photos: drop them in `assets/images/<year>/<month>/<day>/`, write the
post, and commit **to a branch**. CI resizes them, archives DSLR originals and generates
gallery thumbnails, committing the result back. Then merge.

You can run `script/prep-images.sh --apply` yourself if you prefer; it is idempotent.

## Special markup from plugins

`((Tezzeret, Cruel Captain))` renders as a Scryfall link with a hover preview, via the
autocard plugin.

## Documentation

See [docs/](docs/) — [roadmap](docs/ROADMAP.md), [implementation records](docs/impl/),
[designs](docs/design/).
