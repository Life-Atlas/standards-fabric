# Contributing

Everything that matters here is **data, not code**. Most contributions are a JSON edit and a pull request; CI runs the tests, rebuilds the twin and runs the gate. If the gate is green, a maintainer merges and Pages redeploys.

## Four ways to contribute (easiest first)

| I want to… | Edit | Rules |
|---|---|---|
| **Add or correct a reference** (a standard, ontology, MIM, EU act) | `data/topics/curated.json` | one entry per ref; three epochs (`past/now/future`) with a state from `absent · draft · in-force · superseded · expected · aging`; a `confidence` — write `checked YYYY-MM-DD` only if you opened the primary source that day, otherwise `assumed`; a `url` when one exists |
| **Add a topic** (a class of concern, e.g. "district heating substations") | `data/topics/topics.json` | map it to SEK committees (`sek`), international committees (`intl`) and curated refs. Then run `python -m standards_fabric snapshot --committee "TK 57"` for any new committee |
| **Add a reality** (your facility: a hospital, a water plant, a school) | `data/realities/<slug>.json` — copy an existing one | zones on a grid (`x,y,w,h`) that do not overlap; every zone/system lists topics; `reality_basis` says honestly whether it is a reference model or anonymised from a real twin; **no client names, no personal data** |
| **Add a source the agents should read** | `data/sources/sources.json` / `options.json` | RSS/Atom feed URLs, GitHub `owner/repo`, keywords per option. Note the date you verified the feed answers |
| **Edit the requirements catalogue** | `catalog/requirements.json` | every line cites its standards by number; the monthly agent will tell you when a citation goes stale |
| **Fix a rule or add a collector** | `src/standards_fabric/` | Python 3.11+, stdlib only at runtime; every new check ships with a test that can fail (see `tests/test_gate.py`) |

## Ground rules

- **No standard texts.** Numbers, titles, statuses, dates and links only. The catalogue metadata belongs to SEK/ISO/CEN; the texts are theirs to sell.
- **Every finding has a source URL.** The gate (`G5`) rejects a report with a sourceless finding.
- **Numbers are measured.** README figures are checked by `G6`; do not hand-edit a count.
- **No domain nouns in shared code.** "steel", "datacenter", "apartment" live in `data/`, never in `src/` (a test enforces it).
- **Swedish or English** — both are fine in data and docs; the weekly digest is Swedish.

## Local loop

```bash
python -m pip install -e ".[dev]"
python -m pytest -q && ruff check src tests
python -m standards_fabric build && python -m standards_fabric gate
```

Open `site/index.html` in a browser to see your change.

## Governance (proposed — to be confirmed by the working group)

- Maintainers: WINNIIO (machinery) + two named delegates from the Standards & Platforms working group (content). Merges need one content review for `data/**` and `catalog/**`, one code review for `src/**`.
- Monthly: the working group reviews `reports/monthly/LATEST.md` and the open PRs in one agenda item.
- Anyone can open an issue with the templates in `.github/ISSUE_TEMPLATE/`.
