# Start here — handover to the next agent

You are taking over `standards-fabric`. Read this and `README.md`. Together they
take ten minutes and save a day.

Everything below was measured on **2026-08-19** with the command shown next to it.
Where a number has no command, it is marked as such.

---

## 1 · The one idea

> **The standards are data on a reality. Never a generic list.**

A list of standards is unusable: nobody can tell which of 14 824 documents bites
where. A *facility* with zones, where each zone carries the documents that govern
it in a given decade, is usable — a procurer, a WG delegate and a plant engineer
can each point at the same zone and see their own answer.

That is the SMILE order (DOI 10.5281/zenodo.21757691): emulate the reality first,
then hang the data on it. Impact first, data last. Every design decision in this
repo follows from it, and the ones that look odd usually follow from it too.

The deep link Nicolas uses is the shortest demonstration:

```
https://life-atlas.github.io/standards-fabric/?reality=steel-fabrication-plant&epoch=now&zone=z:stn-13-1
```

Reality, epoch, zone — three parameters, one view, shareable into a meeting
minute. It exists because a view you cannot link to cannot be cited in a decision,
and a decision citing the twin is MVT criterion M8.

---

## 2 · Run it

```bash
git clone https://github.com/Life-Atlas/standards-fabric && cd standards-fabric
python -m pip install -e ".[dev]"
```

**Two Windows gotchas that cost time on 19 Aug 2026:**

| Symptom | Cause | Fix |
|---|---|---|
| `No module named standards_fabric` | the package lives in `src/`, editable install not always picked up | `PYTHONPATH=src python -m standards_fabric …` |
| `UnicodeEncodeError: 'charmap' … '\u2264'` | cp1252 console, the MVT scorecard prints `≤` | `PYTHONIOENCODING=utf-8` |

Combined, which is how every command below was run:

```bash
PYTHONPATH=src PYTHONIOENCODING=utf-8 python -m standards_fabric <cmd>
```

| Command | What it does | Measured 2026-08-19 |
|---|---|---|
| `build` | twin from the committed SEK snapshot → `site/index.html` | — |
| `report weekly` | run the six agents → `reports/weekly/<YYYY-Www>/report.md` | — |
| `gate` | acceptance gate, exit 0 = green | **`gate: GREEN`** |
| `mvt` | MVT scorecard, exit 0 = MVT reached | **`MVT NOT REACHED`, 2/7 owned green** |
| `snapshot` | refresh the SEK catalogue (53 committees, ~8 min) | — |

No secrets are needed for any of them. The LLM summary is optional and swappable:
`SF_LLM=anthropic|ollama|none`, prompt in `prompts/summarise.md`.

---

## 3 · Where everything is, and why it is there

```
data/realities/*.json     six facility instances
data/topics/topics.json   topics → SEK committees + international committees + refs
data/topics/curated.json  refs the SEK catalogue does not carry
data/sources/*.json       every feed / API the agents read
data/snapshots/sek/       SEK catalogue metadata per committee, refreshed monthly by CI
catalog/requirements.json procurement requirements; each line cites its standards
src/standards_fabric/     sek_client · timeslice · twin · site · agents/ · gate · cli
site/template.html        the viewer — self-contained, theme-aware, keyboard-navigable
reports/                  weekly/ monthly/ digests + state/ (dedupe baselines)
docs/                     MVT.md · PLAN.md · research/ · strategy/ · playbooks/
.github/workflows/        ci · weekly-digest (Mon 05:17 UTC) · monthly (1st 04:23 UTC) · pages
```

**Why data and code are separated the way they are.** Adding a seventh reality is
one JSON file and zero code. That is deliberate: the class is *facility*, and the
domain — steel, hydro, data centre, office — is data. A reality that needed a code
change would mean the class was drawn wrong. If you find yourself editing
`twin.py` to add a facility type, stop and fix the model instead.

**Why the snapshot is committed.** `ci.yml` builds and gates from the committed
snapshot, with no network and no secrets. A clean clone therefore reproduces the
site byte-for-byte, which is MVT criterion M9 and the only reason an outside
contributor can verify anything (M6).

**Why every entry carries a *basis* and a checked/assumed flag.** The time-slice
uses three different mechanisms — SEK publication dates, a name-year heuristic,
and the pipeline — and they are not equally trustworthy. Showing which one
produced a given row is the difference between a twin and a plausible-looking
list. The flag is also the thing M5 measures.

---

## 4 · The agents, and what each one is for

Six deterministic collectors mapped one-to-one on the consortium's six core
activities, plus a monthly radar over the eight optional efforts. The mapping is
not decorative: the consortium proposal names those six, and an agent that does
not serve one of them does not belong in this repo.

| Activity | Agent | Source |
|---|---|---|
| Standardisation | `standards_watch` | elstandard.se API, 19 watchlist committees |
| Standards & Platforms WG | `platforms_overview` | GitHub release feeds, 20 projects |
| EU engagement | `eu_monitor` | digital-strategy RSS, Funding & Tenders search API |
| County-wide IoT | `county_iot` | TED v3 API, Internetstiftelsen RSS |
| Framework procurement | `procurement_catalog` (monthly) | the SEK snapshot |
| Municipal IoT | `municipal_iot` | OASC/MIMs RSS + dead-link check |
| The eight options | `options_radar` (monthly) | `data/sources/options.json` |

**Known defect, written down rather than hidden:** the TED v3 query in
`county_iot` returns 0 results. The query is in `data/sources/*.json` with a note.
It is a query problem, not a plumbing problem — the agent runs and reports zero,
which is honest but useless. Fixing it is cheap and high value.

---

## 5 · Where it actually stands

`PYTHONPATH=src PYTHONIOENCODING=utf-8 python -m standards_fabric mvt`

| | Criterion | State |
|---|---|---|
| M1 | Zone yields an actionable shortlist (core tier ≤ 25 per topic) | **RED** — 0 of 56 topics carry a `tiers` block; median zone shows 1304 refs |
| M2 | Every displayed document resolves to its catalogue page | GREEN — 14 824 documents all carry a URL |
| M3 | A scheduled run has produced a digest without a human | **RED** — 0 scheduled runs recorded |
| M4 | Hand-verified golden set pins the time-slice to reality | **RED** — `tests/golden_timeslice.json` missing |
| M5 | Load-bearing curated refs verified, not assumed | **RED** — 6/23 critical refs checked, 11/144 overall |
| M6 | Someone outside WINNIIO has contributed | BLOCKED — owner: WG delegates |
| M7 | Realities from real sites have publish consent on record | BLOCKED — owner: Nicolas → site owners |
| M8 | A real decision cites a view from the twin | BLOCKED — owner: WG / a procuring municipality |
| M9 | Clean clone builds and gates without secrets | GREEN |
| M10 | Runs fit the free Actions budget | **RED** — no scheduled run measured yet |

**`gate: GREEN` and `MVT NOT REACHED` are both true at the same time, and that is
the point.** The gate proves the build is consistent with its own data. The MVT
scorecard asks whether the thing is useful to anyone yet. Do not let a green gate
be read as a finished product; the README says *working prototype, not the MVT*
for that reason.

---

## 6 · The critical path, in order

1. **M1 — tiers.** A zone showing 1304 references is an inventory. Add a `tiers`
   block to `data/topics/topics.json` so each topic separates a core tier from the
   long tail, and make the viewer show core first. This is the single change that
   turns the twin from impressive into usable, and it unblocks M8, because nobody
   cites a view they cannot act on.
2. **M4 — golden set.** The epoch rules are tested against synthetic documents
   only. Hand-verify a set of real documents into `tests/golden_timeslice.json`.
   Until then the time-slice is asserted, not proven.
3. **M5 — verify the load-bearing refs.** 6 of 23 critical refs are `checked`.
   The other 17 are assumptions carrying weight.
4. **M3 and M10 close themselves** once the crons have fired once and recorded
   their own evidence (commit `19d41dd` made scheduled runs record it).
5. **M6, M7, M8 are not yours.** They need a human decision or an outside party.
   Report them as blocked with the owner named; do not engineer around them.

---

## 7 · Rules that apply here

- **Every number that leaves this repo comes from a command.** The README's counts
  are re-checked by `gate`. If you write a number by hand, `gate` should be able
  to fail on it — and if it cannot, that is a hole to close, not a number to keep.
- **A check that has never said no is not a check.** 5 of the 19 tests exist to
  prove the gate can fail. Any check you add ships with a fixture that breaks it,
  and you run that fixture and observe the failure.
- **Unverified is a state, not a gap to fill.** `assumed` is a legitimate value.
  A guess dressed as `checked` is the failure this repo is built to avoid.
- **Iterate narrow.** `gate` and `mvt` are fast, but the full agent run is not.
  Run the one thing you changed; run everything once at the end.

---

## 8 · Context outside this repo

| Where | What |
|---|---|
| https://life-atlas.github.io/standards-fabric/ | the published viewer (GitHub Pages, redeploys on `docs` changes) |
| `docs/MVT.md` | the contract: what MVT means, and the blocker clause |
| `docs/PLAN.md`, `docs/strategy/`, `docs/research/options-radar.md` | why this shape, what was considered and rejected |
| `docs/playbooks/` | the municipal playbook the `municipal_iot` agent link-checks |
| `docs/sessions/` | session logs; read the newest before assuming anything is stale |
| `C:\Users\ceo\OneDrive - Winniio AB\WINNIIO 2026\Repos\winniio-unikom-portal` | related work: municipal digitalisation training package, same principle applied to a customer |

---

Written 2026-08-19. Every figure above came from `gate`, `mvt` or `git log` on
that date. If you are reading this much later, re-run both before trusting a
single one of them.
