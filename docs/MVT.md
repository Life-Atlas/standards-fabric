# MVT — goal, Definition of Done, and where it stands today

*Written 2026-08-17, the day the repo went live. Measured with `python -m standards_fabric mvt` — the numbers below are that command's output, not prose.*

## What MVT means here

**Minimum Viable Twin: the smallest artefact that a named person outside WINNIIO uses to answer a real question, and that stays true next month without anyone touching it.**

Two halves, and both are load-bearing:

- *Used to answer a real question* — not "looks impressive in a demo". A delegate or a procurer gets an answer they act on.
- *Stays true without a human* — the agents update it on schedule and the gate refuses to publish when the picture drifts. A twin that needs me every month is a consultancy deliverable, not a twin.

Today it satisfies neither. It is a **working prototype with a live site and a green build** — which is a good place to be on day one, and not the MVT.

## Goal

> **MVT reached before the September Standards & Platforms meeting**, so the working group's first look is at something that already ran a month unattended and answers a procurement question in under a minute.
>
> Date to confirm — Tobbe's mail of 31 Jul 2026 says invitations run to January 2027, but no S&P meeting after 17 Aug is in the calendar. Ask.

The first *user* is deliberately not "everyone". It is one procuring municipality or region choosing an IoT platform or a substation refurbishment, and one WG delegate who wants the standards picture without asking anyone. If those two are served, the rest follows.

## Definition of Done

`python -m standards_fabric mvt` returns **0**. Ten criteria; seven are mine, three depend on named people.

```
DONE:      python -m standards_fabric mvt returns 0
BLOCKED:   when the only red criteria are M6, M7, M8 — report who is blocking, what was asked,
           and when; do not invent work to look busy, and do not mark them green from my side.
```

| # | Criterion | Why it is the *minimum* | Measured 2026-08-17 |
|---|---|---|---|
| **M1** | A zone yields a shortlist a human can act on — every topic carries a `tiers` block, core tier ≤ 25 documents | 1 304 references is an inventory. Nobody procures against 1 304. This is the difference between a curiosity and a tool | **RED** — 0/56 topics tiered, median zone shows **1 304** refs |
| **M2** | Every displayed document resolves to its catalogue page | A reference you cannot open is a claim, not a source | **GREEN** — 14 824 documents carry a URL; 12/12 sampled returned 200 *and* contained the document number |
| **M3** | A **scheduled** run has produced a digest without a human | "It updates weekly" is ASSUMED until a cron has fired and committed. The whole value proposition rests on this line | **RED** — 0 scheduled runs; first fires Mon 05:17 UTC / 1st 04:23 UTC |
| **M4** | A hand-verified golden set (≥10 real documents with known 2016/2026 status) pins the time-slice | The epoch rules are tested against synthetic documents. Rules can be self-consistently wrong | **RED** — `tests/golden_timeslice.json` missing |
| **M5** | Every load-bearing curated reference is `checked <date>`, not `assumed` | Load-bearing = used by ≥3 topics or cited in the requirements catalogue. These are the ones that end up in a procurement document | **RED** — 6/23 critical checked (11/144 overall) |
| **M6** | Someone outside WINNIIO has contributed and CI accepted it | Open source with one contributor is a private repo with extra steps | **BLOCKED** — 0. Owner: WG delegates / any node |
| **M7** | Realities derived from real sites have publish consent on record | Two realities are anonymised from client twins. Anonymised is not the same as cleared | **BLOCKED** — 0/2. Owner: Nicolas → site owners |
| **M8** | A real decision cites a view from the twin (permalink in a minute, a procurement doc, a committee comment) | The only proof that it answered a real question | **BLOCKED** — 0. Owner: WG / a procuring municipality |
| **M9** | A clean clone builds and gates without secrets | Key-person risk: it must survive me | **GREEN** — CI builds from the committed snapshot and runs the gate |
| **M10** | Runs fit the free Actions budget (weekly < 10 min, monthly < 25 min) | An MVT that eats the org's CI minutes gets switched off | **RED** — unmeasured until a scheduled run happens |

**Score: 2 of 7 mine are green. 3 blocked on people. MVT NOT REACHED.**

## What MVT is *not* (scope fence)

Out of scope until the ten are green — each of these is a good idea that would delay the only thing that matters:

- 3D anchors in Godot/Unreal/Hagerbach (`docs/ROADMAP-3D-AND-EMBED.md`) — the 2D view already answers the question; 3D makes it beautiful.
- ISO/CEN/SIS scrapers — the future epoch stays thin and *labelled* thin.
- More realities beyond the six. Six is already more than the MVT needs; two would do.
- An API, a database, user accounts, a hosted service.
- The case bank, the sensor register, the EDIC work — those are consortium activities the repo *supports*, not MVT scope.

## The critical path, in order

1. **M1 tiers** — the one thing. Without it the tool is not usable, so M8 can never happen. Estimated: a `tiers` block per topic (core / context / archive), a rule to auto-tier by committee-primary + document type, hand curation for the top 10 topics. 1–2 days.
2. **M3 + M10** — wait for Monday's cron, then record the run and its duration in `data/mvt_evidence.json`. Zero work, one week of calendar.
3. **M4 golden set** — 10 documents whose Swedish fastställande/upphävande dates I read by hand from the catalogue page. Half a day.
4. **M5** — 23 references to open and date-stamp. Half a day.
5. **M7** — two conversations (the plant CEO, the underground facility). Nicolas.
6. **M6, M8** — follow from showing it to the WG in September.

Everything else in the backlog waits behind these six lines.
