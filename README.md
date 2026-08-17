# standards-fabric

**Which standards apply where in a facility — ten years ago, now, ten years ahead — and a set of agents that keep a Swedish IoT consortium's standards & EU watch running every week without a secretariat.**

Two things in one repo, sharing one data core:

1. **Standards Twin** (`site/`) — pick a reality (a steel-frame plant, an underground test facility, a data centre, an office, a rental block), pick an epoch (2016 · 2026 · 2036), click a zone. You see the SEK/IEC/ISO documents, ontologies, MIMs and EU acts that govern that zone — with the *basis* for every entry (SEK dates, name-year heuristic, pipeline) and a *checked/assumed* flag on every curated reference.
2. **Agents** (`src/standards_fabric/agents/`) — six deterministic collectors mapped one-to-one on the consortium's core activities, plus a monthly radar over the eight optional efforts. GitHub Actions run them weekly and monthly and commit the digest to `reports/`. An LLM summary is optional and swappable (Anthropic / Ollama / none).

Measured, not written (`python -m standards_fabric gate` re-checks these numbers): **5** realities · **45** topics · **128** curated refs · **46** SEK committees snapshotted · **14104** catalogue documents time-sliced · **19** tests (5 of them prove the gate can say *no*).

## Why

The consortium proposal (of US, Aug 2026) names six core activities — Standardisation, the Standards & Platforms working group, EU engagement, County-wide IoT, Framework-agreement procurement, Municipal IoT — and eight options (ways of working IoT+AI, national case bank, national IoT device register, W3C, JTC 1, JTC 4, RefARK → ISO/IEC 30141, CitiVerse). Every one of them needs the same thing first: a **current, sourced picture of which standards, platforms and EU acts move — tied to where they bite in a real facility.** That picture is what this repo produces, on a schedule, in the open.

Method: [SMILE](https://doi.org/10.5281/zenodo.21757691) — reality emulation first (the zone map), then the standards as *data* on that reality, never as generic lists. Impact first, data last.

## Quick start

```bash
git clone https://github.com/winniio/standards-fabric && cd standards-fabric
python -m pip install -e ".[dev]"          # stdlib-only runtime; dev = pytest + ruff
python -m standards_fabric build           # twin from the committed SEK snapshot → site/index.html (open it)
python -m standards_fabric report weekly   # run the agents → reports/weekly/<YYYY-Www>/report.md
python -m standards_fabric gate            # acceptance gate, exit 0 = green
python -m standards_fabric snapshot        # refresh the SEK catalogue snapshot (46 committees, ~6 min)
```

Optional editorial summary: `SF_LLM=anthropic ANTHROPIC_API_KEY=… python -m standards_fabric report weekly` (default model `claude-haiku-4-5-20251001`; `SF_LLM=ollama` for a local model; prompt lives in `prompts/summarise.md`).

## Layout

```
data/realities/*.json     five facility instances (class = facility; add a sixth = one JSON, zero code)
data/topics/topics.json   45 topics → SEK committees + international committees + curated refs
data/topics/curated.json  128 refs the SEK catalogue does not carry: ISO/CEN via SIS, ETSI, W3C, OASC MIMs, EU acts, ontologies
data/sources/*.json       every feed / API the agents read (feeds, GitHub releases, EU F&T portal, TED, options keywords)
data/snapshots/sek/       SEK catalogue metadata per committee (all statuses incl. remiss/NWP) — refreshed monthly by CI
catalog/requirements.json procurement requirements catalogue; each line cites its standards; checked monthly against the snapshot
src/standards_fabric/     sek_client · timeslice · twin · site · agents/{activities,radar,orchestrator,llm} · gate · cli
site/template.html        the viewer (self-contained, theme-aware, keyboard-navigable)
reports/                  weekly/ monthly/ digests + state/ (dedupe baselines)
docs/                     PLAN.md · research/options-radar.md · strategy/swot-vpc-roadmap.md · playbooks/
.github/workflows/        ci · weekly-digest (Mon 05:17 UTC) · monthly-snapshot-and-radar (1st, 04:23 UTC) · pages
```

## The six agents ↔ the six activities

| Activity | Agent | What it does every run | Sources |
|---|---|---|---|
| Standardisation | `standards_watch` | diff of the SEK catalogue for 19 watchlist committees: new, withdrawn, remiss, NWP, status changes | elstandard.se API |
| Standards & Platforms WG | `platforms_overview` | new releases across 20 open IoT / twin / ontology projects | GitHub release feeds |
| EU engagement & monitoring | `eu_monitor` | DG CONNECT news filtered on IoT/twin/CRA/Data Act; open Funding & Tenders topics with deadlines | digital-strategy RSS, F&T search API |
| County-wide IoT | `county_iot` | Swedish IoT procurement notices; Internetstiftelsen news | TED v3 API (query still returns 0 — see sources.json), RSS |
| Framework agreement procurement | `procurement_catalog` (monthly) | every standard cited in `catalog/requirements.json` checked: withdrawn? new edition in pipeline? older than 10 years? | SEK snapshot |
| Municipal IoT | `municipal_iot` | OASC/MIMs news; dead-link check on the municipal playbook | RSS |
| Options (8) | `options_radar` (monthly) | keyword radar per option over all feeds | data/sources/options.json |

Every finding carries a source URL and a fetch date; a source that fails is reported as *"Källor som inte svarade"*, never silently dropped.

## Honesty labels

- `basis: sek-dates` — in-force verdict computed from SEK's own determination/annulment dates.
- `basis: name-year-heuristic` — international documents carry no withdrawal date in the catalogue; a 2013 edition withdrawn today is assumed to have been in force in 2016.
- `confidence: checked <date>` vs `assumed` on curated refs — assumed means "from working knowledge, verify before quoting externally".
- Counts on the map are *catalogue documents under the responsible committees* — the shortlist for a project is a subset.

## Adding a reality (the second-instance test)

Copy any file in `data/realities/`, change zones/systems and their `topics`. Run `build`. If it needs a topic that does not exist, add it to `topics.json` (committees + curated refs). No code changes — that is the point.

## Licence

MIT. Catalogue metadata © SEK Svensk Elstandard (titles, numbers, statuses only — no standard texts). Built by [WINNIIO](https://winniio.io) for the Standards & Platforms working group.
