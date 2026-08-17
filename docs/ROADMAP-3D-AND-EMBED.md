# Roadmap — 3D twins (Godot / Unreal / Hagerbach) and embedding on winniio.io

*Written 2026-08-17. The 2D viewer is deliberately the first surface: it renders in any browser, on a phone, in a meeting, from a link. 3D is the same data with a different renderer — not a different product.*

## What already exists that makes this cheap

The whole twin is one JSON (`site/data/twin.json`) with a stable shape:

```
realities[<id>].zones[] : {id, name, x, y, w, h, topics[], counts:{past,now,future}}
topics[<id>].epochs[e]  : {sek:[docId…], curated:[refId…]}
docs[<docId>]           : {n(ame), t(itle), y(ear), s(tatus), c(ommittee), u(rl), b(asis), pipe, age}
```

Nothing in it is 2D except `x,y,w,h`. A 3D client needs exactly one thing added: a mapping from a zone id to something in the 3D scene.

## Step 1 — anchor ids (the only real work)

Add an optional `anchor` block per zone, filled per renderer. Data, not code:

```json
{"id": "stn-14-1", "name": "Welding portal", "anchor": {
   "godot": "res://factory/Halls/Hall14/Station14_1",
   "unreal": "/Game/Factory/Stations/Stn_14_1",
   "ifc":    "3vB2Yo$KX0kugbUWHB5Ffv",
   "usd":    "/World/Factory/Stn_14_1",
   "gis":    {"lat": 58.5039, "lon": 13.1573}}}
```

- **Godot factory twin** (`C:/Users/ceo/factory-twin-godot`, branch `work/vsab-phase1`): station nodes already exist in `layout-vsab.json`; the anchor is the node path. A small autoload fetches `twin.json`, indexes by anchor, and shows a panel on click. ~150 lines of GDScript.
- **Unreal** (Anupaul/Priyanshu's build): same idea via a DataTable of anchor → zone id, or a `GameplayTag` per station actor.
- **Hagerbach / underground lab twin** (`underground-lab-twin`, FROZEN): the reality `underground-test-facility` already exists here with 9 zones — portal, main tunnel, fire gallery, labs, event hall, electrical/UPS, server room, workshop, outdoor. Anchors map to the existing tunnel geometry; the standards panel becomes a station in the visitor tour ("this gallery is governed by IEC 60695 fire testing, IEC 60079 Ex, IEC 62305 lightning — here is what changed since 2016").
- **IFC/USD** anchors give the same trick to any BIM viewer and to Omniverse without touching either engine.

## Step 2 — the runtime contract

Both engines consume the *published* JSON, never a private copy:

```
GET https://life-atlas.github.io/standards-fabric/data/twin.json   (5.5 MB, cacheable, CORS-open on Pages)
```

Refresh once per session, cache to disk, fall back to the last good copy. That means the 3D twin's standards layer updates every month **without a rebuild of the game binary** — the monthly workflow commits the new snapshot and both engines see it on next launch.

## Step 3 — what the 3D view shows that 2D cannot

- **Elevation and adjacency**: cable routes crossing a fire compartment, the switchyard's clearance envelope, a tunnel's ventilation path. Standards that are about *distance and separation* (IEC 61936 clearances, IEC 62305 protection zones, EN 50174 separation of power and data cabling) only make sense in 3D.
- **Walkthrough as an audit**: stand in the relay room, see the 15 documents that govern what you are looking at, with the 2016→2026 delta and the pipeline.
- **Time as a slider in space**: the same room in 2016 / 2026 / 2036, with the aging documents highlighted on the equipment they govern.

## Step 4 — WINNIIO site

Two ways, both live off the same build:

1. **Embed** (shipped today): `?embed=1` hides the page chrome; `?reality=…&epoch=…&zone=…` deep-links a view. So winniio.io can carry, e.g. on the digital-twin page:

```html
<iframe src="https://life-atlas.github.io/standards-fabric/?embed=1&reality=hydro-power-plant&epoch=future"
        title="Standards Twin" loading="lazy" style="width:100%;height:820px;border:1px solid #e5e7eb;border-radius:12px"></iframe>
```

2. **Own domain later**: point `standards.winniio.io` (or a path on the site) at the same Pages artefact via CNAME, so the tool is WINNIIO-branded while the repo stays neutral and open. Requires a DNS record and one line in the Pages settings.

Copy for the site (draft, one paragraph): *"Which standards apply where in your facility — ten years ago, today, and ten years ahead. Open source, sourced from SEK Svensk Elstandard's public catalogue, updated weekly by agents you can read. Built with SMILE: impact first, data last."* With a link to the repo and to the weekly digest.

## Step 5 — order of work (proposal)

| # | Work | Effort | Unlocks |
|---|---|---|---|
| 1 | `anchor` field + schema note + one filled example per renderer | half a day | everything below |
| 2 | Godot autoload + click panel on the VSAB factory twin | 1–2 days | the demo Nicolas can show in a meeting |
| 3 | Hagerbach: anchors for the 9 zones + a "standards station" in the tour | 1 day | a second instance, proving the pattern is not factory-specific |
| 4 | winniio.io embed on one page | hours | public shop window |
| 5 | Unreal DataTable mapping | 1–2 days | parity with the UE build |
| 6 | IFC/USD anchors + a Speckle/Omniverse demo | 2 days | BIM-side conversation with property owners |

Nothing here needs a new backend. If the 3D layer ever needs queries the JSON cannot answer (e.g. "every document that governs a cable route crossing two zones"), that is the moment to add a small API — not before.
