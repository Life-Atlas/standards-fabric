# SWOT · Value Proposition Canvas · 6–12-month roadmap

*For the Standards & Platforms working group and the national IoT consortium (lead: Internetstiftelsen). Drafted 2026-08-17 by WINNIIO as an input, not a position. Numbers marked (measured) come from this repo; the rest is judgement and says so.*

## 1. SWOT — the consortium's standards & platforms capability

| | Helpful | Harmful |
|---|---|---|
| **Internal** | **Strengths** · ten years of IoT Sverige projects and relationships in every county (eight regional nodes on the slide) · SEK TK IoT / SK 1–5 seats already held; delegates report from SC 41 plenaries · RefARK exists and is used in procurement · Jönköping's county-wide platform (13 municipalities + region + länsstyrelse + ~40 bolag, TH1NG "IoT Open", contract Nov 2022) and Sundsvall's open Diwise are running precedents | **Weaknesses** · no continuous market/standards overview — it is produced by volunteers when a meeting needs it · knowledge sits in people (key-person risk) and in PDFs · Sweden absent from the CitiVerse EDIC's 14 member states · TED/SIS/ISO have no open APIs — the "single entry point" promised on the slide has no data plumbing yet · funding for editorships (not attendances) is not budgeted |
| **External** | **Opportunities** · CRA (obligations 2027), Data Act (2025/26), AI Act (2026/27), EPBD/EED recasts create *demand* for exactly this overview from every municipality and supplier · JTC 4 is new — early drafts win editorships · CitiVerse EDIC calls (> €80 M so far) reward interoperable LDTs · MIMs Plus adopted EU-wide gives a ready spine · Danish OS2 shows a working open-source municipal model to copy | **Threats** · consortium becomes a meeting series with no artefacts (the IoT Sverige end-of-programme risk) · vendors define "the platform" through framework agreements before the requirements catalogue exists · EU acts land unread and municipalities buy non-compliant devices · fragmentation: eight nodes, eight platforms, eight data models |

**The one thing:** turn the working group's *knowledge* into a *repository that publishes weekly* — then every other activity (procurement catalogue, case bank, EU monitoring, JTC seats) has a home and a heartbeat. That is what `standards-fabric` is: the first instance, running.

## 2. Value Proposition Canvas

**Customer segments** (in order of who pays): (1) municipalities & regions buying IoT/twins, (2) the consortium secretariat/programme office, (3) Swedish suppliers who need to know what to build to, (4) standards delegates.

| Customer jobs | Pains | Gains |
|---|---|---|
| Buy an IoT platform / sensors / a twin that will still be legal and interoperable in five years | "Which standards apply to *this* building/plant?" answered by consultants, differently each time · CRA/Data Act deadlines discovered late · framework agreements written on yesterday's standards | One place that shows, per zone of a facility, what applied, applies, and is coming — with sources · a requirements catalogue that checks its own citations monthly |
| Run a working group / consortium without a paid secretariat | Overviews decay between meetings; the person who knew leaves | A weekly digest that arrives whether or not anyone had time; the git history *is* the institutional memory |
| Influence ISO/IEC/CEN work | Attend, do not shape; no draft to bring | RefARK/catalogue material shaped as NWP-ready inputs |

| Products & services | Pain relievers | Gain creators |
|---|---|---|
| **Standards Twin** (facility × epoch × zone) | replaces bespoke standards inventories; makes obligations spatial | reality-first (SMILE): the map is the client's own facility, not a generic list |
| **Weekly/monthly agents** (6 activities + 8-option radar) | no secretariat needed; sources cited; failures reported | market overview "for everyone" as the slide promises — actually delivered |
| **Requirements catalogue with self-checking citations** | stale references in framework agreements | one shared catalogue for the framework-agreement procurement activity |
| **Case bank schema + site** (proposed) | PDF graveyard | outcome-first cases linked to the standards they used |

**WINNIIO's role in one sentence:** the consortium owns the content and the seats; WINNIIO builds and runs the machinery (repo, agents, twin, catalogue), teaches the method (SMILE), and hands over — nothing in the stack is proprietary and every component is swappable.

## 3. Roadmap — six to twelve months (Sep 2026 → Aug 2027)

Owner codes: **WG** = Standards & Platforms working group · **SEC** = consortium secretariat (Internetstiftelsen) · **SEK** = SEK TK IoT delegation · **WIN** = WINNIIO. Each milestone has a *state* the day it ships (rules: a milestone leaving the house carries a state, not just a date).

| When | Milestone | State on delivery | Owner |
|---|---|---|---|
| **Sep 2026** | Weekly digest adopted as WG standing item; sources.json reviewed by WG (add/remove feeds) | repo running (VERIFIED today); WG review = decision at next meeting | WG · WIN |
| Sep | Fix TED query; add SIS + ISO/IEC work-programme collectors (monthly) | today: TED returns 0, SIS/ISO curated by hand | WIN |
| Sep–Oct | Requirements catalogue v0.2 co-edited with two procuring municipalities; every line cites standards; monthly self-check live | v0.1 seeded (25 lines) | WG · SEC |
| Oct | Case-bank schema + migration of the IoT Sverige portfolio into `cases/` (outcome-first, standards-linked) | schema proposed in options-radar.md | SEC · WIN |
| Oct | Standards Twin: first *real* datacenter reality + county-platform reality | reference model today | WIN + one host site |
| Nov | JTC 4 mirror participation decided; one draft (catalogue ↔ MIMs alignment) prepared as input | option only | SEK · SEC |
| Nov–Dec | RefARK v1.3 rewritten as NWP-shaped document for SC 41 (procurement patterns TR) | RefARK on Inera Confluence | SEK · WG |
| Dec | CitiVerse EDIC: national letter of intent drafted with the ministry route; one municipal LDT pilot named | Sweden not a member (verified) | SEC |
| Jan 2027 | Sensor-register pilot (Amsterdam-model, municipal installations) legal note + data model tied to MIM7 | idea | SEC · one municipality |
| Feb 2027 | Monthly options radar reviewed as a WG agenda item; first quarter of digests archived; ISO 30186 maturity self-assessment on two pilots | radar code exists, no review loop yet | WG |
| Mar 2027 | CRA readiness pack for municipalities (device requirements from catalogue + EN 303 645 + IEC 62443 mapping) — before reporting duties start (Sep 2027 is *not* the date; obligations 11 Sep 2026 reporting / 11 Dec 2027 full) | curated entries exist | WG · WIN |
| Apr–Jun 2027 | Second-instance test of everything: a new node (e.g. Halland) onboards with zero code — one reality JSON, one feed list, catalogue reuse | designed for | any node |
| Aug 2027 | Year review measured by the gate: digests shipped / period, catalogue lines with fresh citations, realities, drafts submitted, EDIC status | gate GREEN today | SEC |

**Budget shape (judgement, not a quote):** the machinery costs one part-time engineer-day per week to run and extend for a year; the political options cost delegates' time and one editorship. The expensive mistake is the reverse — many delegates, no machinery.

## 4. What is explicitly *not* proposed

- A new Swedish IoT platform. Jönköping, Sundsvall and OS2iot already exist; the consortium's job is requirements, interoperability and reuse.
- A national product register. CRA + EN 303 645 + DPP cover products; a *sensor installation* register (Amsterdam model) is the useful Swedish thing.
- Any component with lock-in. Every collector, model call and viewer in this repo is stdlib + JSON; the LLM is optional and swappable.
