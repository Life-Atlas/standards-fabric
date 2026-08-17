# PLAN — Standards Twin: the same facility ten years ago, now, ten years ahead

*Written 2026-08-17. Status column is measured against the repo at the time of writing; anything not marked VERIFIED is a plan.*

## The question

Take a model of a facility — a factory, a data centre, an office, a rental block — and show **which standards governed it in 2016, govern it in 2026, and are heading for 2036, tied to WHERE in the facility they bite**. Not a generic list: the steel plant's welding portal, the data centre's UPS room, the office's electrical central.

## Reality-defined, SMILE-ordered

| SMILE phase | What it means here | Status |
|---|---|---|
| Reality emulation | a zone/system map per facility (JSON), anonymised from real twins where we have them | VERIFIED — 5 realities; steel-frame plant built from the client's own station export (9 stations), underground lab from the 2026 twin; datacenter/office/housing are reference models |
| Concurrent engineering | topics as the shared vocabulary between the facility and the standards world | VERIFIED — 45 topics → 46 SEK committees + 128 curated refs |
| Collective intelligence | live catalogue data + ontologies/MIMs on the map | VERIFIED — 14 104 SEK documents time-sliced; SAREF, Brick, RealEstateCore, NGSI-LD, MIM1/2/4/6, IFC/CoClass/bSDD, AAS/OPC UA, ISA-95 in curated.json |
| Contextual intelligence | pipeline (remiss/NWP) + EU acts as the future layer; aging flags | VERIFIED — 88 pipeline docs; CRA/Data Act/EPBD/EED-DC/Machinery Reg/Battery Reg carried as curated future entries |
| Continuous intelligence | weekly/monthly agents keep the picture current | VERIFIED — workflows committed; first weekly run 2026-W34 with 136 sourced findings |
| Perpetual wisdom | published, open, reusable by anyone | VERIFIED — MIT, https://life-atlas.github.io/standards-fabric/ |

## How the three epochs are computed

- **Past (2016)** — Swedish documents: `determination_date ≤ 2016-12-31 and (annulment_date is null or > 2016-12-31)` from SEK's own dates. International documents: publication year from the number (`:2013`) — a heuristic, labelled as such.
- **Now (2026)** — status *publicerad*, no annulment.
- **Future (2036)** — now + pipeline (*remiss*, *new work proposal*, *under bearbetning*) + curated expected acts; documents ≥ 20 years old by 2036 without a new edition are flagged *aging*.

Every rule ships with a test and a mutation that makes the test fail (`tests/test_timeslice.py`).

## What a zone shows (worked example — steel plant, Stn 14.1 welding portal)

Topics: welding · machines-electrical · emc · emf-exposure · industrial-networks · digital-twin-manufacturing · aas-opcua.
2016 → SS-EN 60974 series (arc welding), SS-EN 60204-1 ed.5, EMC 61000-6, ISA-95, OPC UA (2010 edition), RAMI 4.0 as DIN SPEC.
2026 → same families revised, + IEC 63278-1 (AAS), ISO 23247 (manufacturing twin), IEC 62443 horizontal, OPC UA companion specs, EU Machinery Regulation adopted (applies 2027).
2036 → Machinery Regulation in force, Digital Product Passport via ESPR (AAS/EPCIS as carriers), CRA in force for the welding-cell controllers, aging flags on 2016-era editions.

## Where the twin should go next (ranked by impact for the consortium)

1. **Real datacenter reality** — the current one is a reference model. One Swedish colocation site with its DCIM zone map turns "EED Art. 12 reporting" from a curated line into a zone-by-zone obligation. Effort: one JSON + one workshop.
2. **ISO/IEC work-programme collector** — the future layer is thin on international drafts because SEK's catalogue only lists open Swedish remisser (88). ISO's SC 41 / JTC 4 work programmes and IEC's project pages have no open API; a monthly scrape with a stable parser is the missing piece. Effort: 1–2 days.
3. **SIS catalogue** — non-electrotechnical (ISO 50001, EN 15232/52120, IFC, ISO 37120) are curated by hand today. SIS has no public API either; a monthly scrape or a purchased data feed closes it. Effort: 1–2 days or a licence.
4. **Zone → requirement export** — click a zone, get the procurement requirement lines that cite its standards (`catalog/requirements.json` already carries citations). Effort: half a day.
5. **3D/BIM anchoring** — the zone JSON has grid coordinates; the same topics can hang off IFC spaces (`IfcSpace`) or the existing Godot/Unity twins. Effort: mapping table only — the twin viewer stays 2D on purpose.
6. **County-wide instance** — a "county IoT platform" reality (network, platform, applications, municipal endpoints) so the consortium's own architecture is treated as a facility. Effort: one JSON.

## Known limits (stated so nobody has to discover them)

- Counts on the map are *catalogue documents under the responsible committees*; a project's shortlist is a subset. The map is a starting inventory, not a compliance verdict.
- `assumed` curated refs (most of the 128) come from working knowledge and are dated; each needs a primary-source check before it is quoted externally. The `checked` ones were verified 2026-08-17 against SEK's catalogue or EUR-Lex.
- SEK's search API is undocumented; the client is written defensively (retries, status inheritance for drafts) and the monthly snapshot is committed so a broken API never blanks the site.
