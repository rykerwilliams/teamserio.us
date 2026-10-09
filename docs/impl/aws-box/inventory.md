# AWS box — what is actually on it

**Host:** `ec2-3-139-113-70.us-east-2.compute.amazonaws.com` (`3.139.113.70`), internal
`ip-172-31-20-44`
**OS:** Ubuntu 20.04.6 LTS · **Disk: 24 G of 29 G used (82%)**, Docker alone is 12 G
**Access:** `ssh ubuntu@...` with the key in Dropbox (`awsKeys/rjPrivate`)
**Surveyed:** 2026-10-09

Written because the box was repeatedly assumed to be nearly empty. It is not. Three times
during the teamserio.us migration the plan said "decommission this" and three times that
turned out to be wrong.

---

## Architecture

Everything is Docker. There is no nginx or openresty on the host — `systemctl` reports both
inactive.

```
Internet :80 :443
      │
      ▼
nginx-proxy-app-1          Nginx Proxy Manager (openresty)   ← the front door
      │                     admin on :81, manager.rajahjames.net
      ├─► swag                    :5000/:5001   nginx + php-fpm → WordPress (digitalmeh.net)
      │     └─► digitalmehnet-mariadb-1          MariaDB 11.1.4, internal only
      ├─► teamserio.us-prod       :6200/:6201   static nginx  ← now obsolete
      ├─► teamserio.us-dev        :6000/:6001   static nginx  ← now obsolete
      ├─► cheertime-competition-web-1  :8090    production app
      └─► cheertime-staging-web-1      :8091    staging app
                └─ cheertime-staging-{rest,auth,db}  PostgREST / GoTrue / Supabase Postgres

openssh-server             container SSH on :2222, separate from the host sshd
```

`Server: openresty` on every response comes from Nginx Proxy Manager, not from a hand-rolled
openresty install. That matters: **there is no `/etc/nginx` to dump.** The routing config
lives in the NPM container at `/data/nginx/proxy_host/*.conf`, and each service's config
lives in its own compose directory.

## Domains routed by NPM

| Domain | Backend | Status |
|---|---|---|
| `cheertime.rajahjames.net` | cheertime-competition-web | **active production** |
| `dev-cheertime.rajahjames.net` | cheertime-staging-web | active staging |
| `digitalmeh.net` | swag → WordPress | active, the migration target |
| `manager.rajahjames.net` | NPM itself | admin UI |
| `phase.teamserio.us` | phase-server | **unknown — HTTPS returns nothing** |
| `teamserio.us` | teamserio.us-prod | **obsolete**, DNS now points at GitHub Pages |
| `dev.teamserio.us` | teamserio.us-dev | **obsolete**, dev site retired |

## Compose projects in `~/aws-docker`

`cheertime-competition`, `cheertime-staging`, `clevelandrocs.net` *(no running container —
retired?)*, `digitalmeh.net`, `nginx-proxy`, `phase-server`, `teamserio.us-docker`

## Cron

Deployment is **automated and frequent**:

- `cheertime-competition/deploy.sh` — **every 10 minutes**
- `cheertime-staging/deploy.sh` — every 10 minutes, offset by 5
- nightly `backup-db.sh` for both, 03:17 and 03:23
- `disk-alert.sh` every 15 minutes — which exists for a reason, see below

---

## Corrections to earlier assumptions

| Assumed | Actually |
|---|---|
| The box only served teamserio.us | It serves two production applications and several domains |
| "Decommission after the soak" | **cheertime production deploys to it every 10 minutes** |
| Only WordPress remains | WordPress plus cheertime prod and staging, plus `phase-server` |
| There is an openresty config to dump | There is no host nginx; config is inside NPM and per-project compose |

**The box is not a candidate for decommissioning in any near timeframe.** Migrating
`digitalmeh.net` removes one tenant, not the need for the host.

## Reclaimable right now

Disk is at 82% with 5.3 G free, and a cron job watches it — so this is worth doing.

| Item | Size | Note |
|---|---|---|
| `~/digitalmeh.net.bak` | 958 M | stale backup |
| `~/digitalmehnet_20220207_..._archive.zip` | 869 M | 2022 archive |
| `teamserio.us-prod` + `-dev` containers and their content | — | obsolete; teamserio.us is on GitHub Pages |

Stopping the two teamserio containers also settles the "frozen copy" question from the
migration: once they go, the DNS rollback to AWS is gone for good. Do that deliberately,
not by accident. **Take the archive first** — those 1.8 G of backups are the only copies of
pre-migration digitalmeh state that we know of, and they should be moved off the box rather
than deleted.

## Open questions

- ~~**`phase.teamserio.us`**~~ — confirmed misconfigured (2026-10-09). Routed by NPM with
  its own explicit A record, but serving nothing.
- **`clevelandrocs.net`** — compose project present, nothing running. Retired?
- **Ubuntu 20.04** reached end of standard support in April 2025. This is the underlying
  reason the host needs rebuilding, not a footnote — but one step at a time.
- **`bitnami/mariadb:11.1.4` no longer exists in the registry.** The digitalmeh database
  container cannot be recreated from its compose file; it survives only because the image
  is already on disk. Discovered while verifying the archive. This gives the digitalmeh
  migration a deadline it did not previously appear to have.
