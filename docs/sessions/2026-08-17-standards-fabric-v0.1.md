# Session log — 2026-08-17 · standards-fabric v0.1.0

Repo created and shipped in one session, during and after the IoT Sverige Standards & Platforms working-group meeting (17 Aug, 13:00–15:30, SEK Solna / Zoom).

| | |
|---|---|
| Branch | `main` |
| Live site | https://life-atlas.github.io/standards-fabric/ |
| CI | ci · weekly-digest (Mon 05:17 UTC) · monthly-snapshot-and-radar (1st 04:23 UTC) · pages |
| Gate | GREEN · 28 tests · ruff clean |
| MVT | **NOT REACHED** — 2/7 owned criteria green, 3 blocked on people (`python -m standards_fabric mvt`) |

## Commits

| Commit | What |
|---|---|
| `c528fc2` | v0.1.0 — facility standards twin + six consortium agents |
| `a7d85e9` | repo URL → Life-Atlas/standards-fabric |
| `5a12c35` | docs: PLAN, options radar, SWOT·VPC·roadmap, municipal playbook |
| (picker) | reality picker as large cards; CONTRIBUTING + issue templates; pages on docs |
| (viewer) | basis chip in words + tooltips, every doc links to its catalogue page; hydro power plant reality |
| (embed) | deep links `?reality/&epoch/&zone`, embed mode, copy-link button; 3D roadmap |
| (mvt) | MVT contract as a command with a blocker clause; 9 new tests |
| (this) | scheduled runs self-record MVT evidence (M3/M10) |

## What was built

- **SEK catalogue client** — the public search API behind elstandard.se, reverse-engineered from the site bundle (`POST /api/search/standard`, 0-based pages, status keys, `/standard/<id>` detail route). Metadata only, never standard texts.
- **Standards twin** — 6 realities × 3 epochs (2016 / 2026 / 2036) × zones, 56 topics, 144 curated refs, 53 committees snapshotted, 14 824 documents time-sliced, every verdict carrying a *basis* label.
- **Six agents** mapped to the consortium's six core activities + a monthly radar over the eight options. First digest: `reports/weekly/2026-W34` (136 sourced findings).
- **Gate** (G1–G6) and **MVT scorecard** (M1–M10), each with mutations that prove they can fail.
- **Docs** — PLAN, options radar (steal-with-pride / cautionary tales, sourced), SWOT·VPC·roadmap, municipal playbook, 3D + embed roadmap, MVT contract, CONTRIBUTING + issue templates.

## Files changed

| Path | Status |
|---|---|
| `src/standards_fabric/{sek_client,timeslice,twin,site,gate,mvt,cli}.py` | new |
| `src/standards_fabric/agents/{base,activities,radar,orchestrator,llm}.py` | new |
| `data/realities/*.json` (6) · `data/topics/{topics,curated}.json` · `data/sources/*` · `data/mvt_evidence.json` | new |
| `data/snapshots/sek/*.json` (53 committees) | new, refreshed monthly by CI |
| `catalog/requirements.json` (25 lines) | new, seed |
| `site/template.html` → `site/index.html` + `site/data/twin.json` | new, built |
| `tests/` (28 tests) · `.github/workflows/` (4) · `docs/` (6) | new |

## Open items

1. **M1 tiers** — median zone shows 1 304 references; that is an inventory, not a shortlist. Critical path.
2. **M4 golden set** — 10 hand-verified documents to pin the time-slice.
3. **M5** — 23 load-bearing curated refs still `assumed`.
4. **M7 consent** — two realities derived from real client twins (anonymised) have no publish consent on record. Owner: Nicolas.
5. TED query returns 0; SEK newsroom URL is not a feed; ISO/CEN work programmes not collected (future epoch stays thin and labelled thin).
6. Next S&P meeting date unknown — nothing after 17 Aug in the calendar.
