# Options radar — what the world has done with the eight optional efforts

*Research pass 2026-08-17 for the Standards & Platforms working group / the coming national IoT consortium. Each option: what exists elsewhere, what to steal with pride, cautionary tales, and what it costs to start. Sources are linked; statements without a link are labelled ASSUMED and should be verified before they go into a funding application.*

Reading order matters: **the six core activities are secretariat work that a repo can automate; the eight options are political and standards-body positions that need named people.** This document is about the second kind.

---

## 1. Ways of working and structure for IoT + AI

**What exists.** OASC's MIMs Plus (adopted by the EU's Living-in.EU movement) already frame the IoT→AI hand-off as interoperability mechanisms: MIM1 context (NGSI-LD), MIM2 shared data models, MIM4 personal-data management, MIM5 fair AI (transparency), MIM7 places, MIM8 indicators. Denmark's OS2iot was procured with the MIMs written into the requirements ([Interoperable Europe country report](https://interoperable-europe.ec.europa.eu/sites/default/files/inline-files/Denmark%202024%20-%20Country%20Intelligence%20Report.pdf)). The EU AI Act's transparency obligations started to be enforced 2 August 2026 ([DG CONNECT, 31 Jul 2026](https://digital-strategy.ec.europa.eu/en/news/commission-starts-enforcing-ai-act-rules-and-new-transparency-requirements-2-august) — picked up by our `eu_monitor` agent this week).

**Steal with pride.** Do not write a Swedish "IoT+AI method". Adopt MIMs Plus as the spine, add the three things the MIMs do not say: (a) data-quality contracts at the sensor edge (what a value means, its unit, its uncertainty — SAREF/SSN vocabulary), (b) an "AI-ready" checklist per data set (provenance, consent basis, retention) mapped to Data Act Art. 4/5 and AI Act Annex IV, (c) a decision log — every AI-supported decision recorded with the data version it used. This repo's twin already carries the vocabulary; the checklist is one JSON per data set.

**Cautionary tale.** Sidewalk Toronto (2017–2020) built the technology first and lost the city on data governance — the project was cancelled before anything was built, with privacy concerns named as the main cause by most post-mortems ([Marketplace 2024](https://www.marketplace.org/episode/2024/12/04/why-googles-smart-city-failed), [Wikipedia](https://en.wikipedia.org/wiki/Sidewalk_Toronto)). The lesson for "IoT + AI": governance is the deliverable, the model is the by-product.

**Cost to start.** Two workshops + a checklist. Zero new infrastructure.

## 2. National case bank for IoT

**What exists.** IoT Sverige's own project portfolio (ten years of funded projects, e.g. [Regiongemensam IoT Jönköpings län](https://iotsverige.se/projekt/regiongemensam-iot-jonkopings-lan), [Sundsvall accessibility](https://iotsverige.se/projekt/sundsvall-kommun/)) is a case bank in all but name; the final technical report being written now (Tobbe & Elias, programme office) is the moment to structure it. Internationally: OASC's case pages, the EU LDT4SSC knowledge hub ([CitiVerse related initiatives](https://knowledgehub.ldt4ssc.eu/communities_content/CitiVerse_Related_Initiatives/)), and Living-in.EU's community pages ([RISE's page](https://living-in.eu/smartcommunities/rise-research-institute-sweden)).

**Steal with pride.** Denmark's OS2 model — the case *is* the code plus the business case: OS2iot is used by 25 municipalities and offered by five commercial operators on their own stacks ([Interoperable Europe](https://interoperable-europe.ec.europa.eu/sites/default/files/inline-files/Denmark%202024%20-%20Country%20Intelligence%20Report.pdf)). A Swedish case bank should require every case to carry: outcome first (SMILE order: impact → action → insight → information → data), the standards it relied on (link into this twin), the procurement documents, and the reusable artefacts (data models, dashboards, contracts). Cases without a measured outcome are stories, not cases.

**Cautionary tale.** Case banks die when they are PDF libraries maintained by a project that ends. The Chicago Array of Things — a well-funded, well-documented sensor programme — was superseded by SAGE and its earlier nodes replaced ([MIT Technology Review 2022](https://www.technologyreview.com/2022/08/19/1057848/array-of-things-goes-global/)); the *documentation* survived because it was in a public repo, not a portal. Put the case bank in git, publish it as a site, let the weekly agent check that every link still answers (our `municipal_iot` agent already does this for the playbook).

**Cost to start.** A schema (one JSON), the IoT Sverige portfolio migrated, a Pages site. Weeks, not months.

## 3. Central national register for IoT devices

**What exists.** Three different things travel under this name and must not be confused:
- *Consumer-security labels/registers*: Singapore's CLS (voluntary since 2020, four levels, mutual recognition with Finland's Traficom label since 2021; UK PSTI compliance recognised as CLS level 1) ([CSA Singapore](https://www.csa.gov.sg/our-programmes/certification-and-labelling-schemes/cybersecurity-labelling-scheme/about/)). Basis: ETSI EN 303 645.
- *Public-space sensor registers*: Amsterdam's Sensorenregister — mandatory since 1 Dec 2021 for any professional sensor in public space, shown on a public map ([Cities Today](https://cities-today.com/amsterdam-introduces-mandatory-register-for-sensors/), [register](https://sensorenregister.amsterdam.nl/)).
- *Product conformity under EU law*: the Cyber Resilience Act (Reg. 2024/2847) — reporting obligations from 11 Sep 2026, full application 11 Dec 2027 — makes manufacturers responsible and market surveillance authorities the enforcers; there is no EU device register, only conformity and the coming Digital Product Passport under ESPR.

**Steal with pride.** For the totalförsvar motive on the slide, the Amsterdam model (where are the sensors, who owns them, what do they collect) is the one that maps to Swedish municipal reality — and it is a *register of installations*, not of products. For the product side, do not build a register: reference CRA + EN 303 645 + (for OT) IEC 62443, and use the coming CRA harmonised standards. Sweden already has the vehicle: SEK TK IoT and the CEN-CENELEC JTC 13 mirror.

**Cautionary tale.** Voluntary labels stay small unless procurement demands them — Singapore kept CLS voluntary and had to grow it through mutual recognition. A Swedish register with no procurement pull will be a list nobody updates. Tie it to the framework-agreement catalogue: a device that is not in the register cannot be called off.

**Cost to start.** Legal analysis (municipal mandate for a sensor register, GDPR), then a data model reusing Amsterdam's fields and MIM7 places. The register itself is a table with a map.

## 4. W3C

**What exists.** W3C Web of Things: Thing Description 1.1 and Architecture 1.1 Recommendations (2023); the WoT WG continues (TD 2.0 work) — ASSUMED, verify on w3.org. There is a *W3C Smart Cities Nordic community group* with hybrid meetings ([w3.org community page, Aug 2024](https://www.w3.org/community/smartcity-nordic/2024/08/07/hybrid-meeting-the-19th-of-august)). Swedish W3C membership is thin (RISE? — ASSUMED).

**Steal with pride.** WoT TD is the cheapest bridge from "our sensors" to "ISO/IEC 21823 semantic interoperability" and to MIM1/2 (NGSI-LD carries TDs). Put a TD requirement in the framework catalogue (`INT-03` already there) and let one Swedish organisation hold the pen in the WoT WG.

**Cautionary tale.** W3C work without deployments becomes a spec nobody implements; the group must bring one real device catalogue (e.g. the county platform's) to the table.

**Cost to start.** One W3C membership + one delegate + one implementation.

## 5. JTC 1

**What exists.** ISO/IEC JTC 1/SC 41 (IoT and digital twin) — SEK TK IoT mirrors it and has 113 catalogue documents (103 published, 5 in pipeline; measured 2026-08-17). SC 41 has produced the twin family: 30173 (concepts), 30186 (maturity), 30188 (reference architecture, 2026), and 30141:2024 (IoT RA revision, ISO/IEC/IEEE 42010-conformant). Swedish delegates report from plenaries (Berlin Nov 2025, SEK newsroom).

**Steal with pride.** Sweden's asset is the *procurement lens* (RefARK) — most SC 41 members bring vendor architecture. Keep RefARK's procurement patterns flowing into 30141's implementation patterns and into 30188.

**Cautionary tale.** Delegations that only attend do not shape; the countries that shape hold editorships. Fund one editorship (a person-year over three years), not ten attendances.

**Cost to start.** Already running through SEK; the marginal cost is an editorship.

## 6. JTC 4

**What exists.** ISO/IEC JTC 4 *Smart and sustainable cities and communities* — proposed by an ISO/IEC joint task force (2024), circulated for member vote and established; scope covers resilience, sustainable mobility, community infrastructure, climate adaptation, and digitalisation as it serves cities ([ISO committee page](https://www.iso.org/committee/11064026.html), [ANSI notice](https://www.ansi.org/standards-news/all-news/12-16-24-smart-and-sustainable-cities-and-communities-ansi-seeks-comments-on-proposed-iso-iec-jtc)). It absorbs work that lived in ISO/TC 268 and IEC SyC Smart Cities.

**Steal with pride.** Enter early with one concrete Swedish input: the county-platform requirements catalogue + MIMs Plus alignment. New committees give editorships to whoever brings drafts.

**Cautionary tale.** Smart-city standardisation has produced many indicator standards (ISO 37120 family) and few interoperability ones; do not spend the seat on more indicators.

**Cost to start.** SIS/SEK mirror committee participation; one delegate; one draft.

## 7. RefARK → ISO/IEC 30141

**What exists.** RefARK IoT (Inera's Arkitekturgemenskap, v1.3, "how RefARK IoT can be used in procurement" — [Inera Confluence](https://inera.atlassian.net/wiki/spaces/AR/pages/2835054927), [procurement page](https://inera.atlassian.net/wiki/spaces/AR/pages/4258005694/-How+RefARK+IoT+can+be+used+in+procurement)); the WG's own earlier *Slutrapport Arbetsgrupp Standarder och IoT-Plattformar v0.9*. ISO/IEC 30141:2024 replaced the 2018 edition with implementation-pattern support ([ISO](https://www.iso.org/standard/88800.html)); SS-ISO/IEC 30141 utg 1:2024 exists in the SEK catalogue (measured).

**Steal with pride.** Germany's RAMI 4.0 → IEC PAS 63088 route: a national reference model became an IEC publicly available specification within ~2 years by arriving as a finished draft with industry backing. RefARK's procurement patterns can take the same route into 30141's next amendment or a new TR ("IoT reference architecture — procurement patterns").

**Cautionary tale.** National architectures that stay national get overwritten by the international one at the next procurement round.

**Cost to start.** Editorial: rewrite RefARK v1.3 as an NWP-shaped document; SEK TK IoT submits.

## 8. Citiverse

**What exists.** The *LDT CitiVERSE EDIC* was announced by the Commission on 7 Feb 2025 with 11 founding member states; 14 member states by 2025, seat in Valencia, target 100 cities by 2026, > €80 M invested via Digital Europe ([Living-in.EU](https://living-in.eu/news/ldt-citiverse-edic-fact), [EDIC site](https://ldtcitiverse-edic.eu/), [Eurocities](https://eurocities.eu/latest/launch-of-european-funding-instrument-to-upscale-digital-twins-towards-the-citiverse-through-living-in-eu/)). Sweden is **not** among the listed founding or 2025 members (Belgium, Croatia, Czechia, Estonia, France, Ireland, Italy, Latvia, Luxembourg, Netherlands, Portugal, Slovakia, Slovenia, Spain) — this is exactly the gap the option names.

**Steal with pride.** Join the EDIC through the ministry route (Digital Europe national contact), and bring the two things Sweden already has: local digital twins in Gothenburg/Stockholm/Helsingborg (ASSUMED list — verify) and the SMILE reality-first method as the twin-maturity story (ISO/IEC 30186 maturity model is the standards hook). The sandbox on the slide should be a *federated* node on the EDIC's infrastructure, not a Swedish clone.

**Cautionary tale.** Songdo/Masdar-style greenfield twins and "metaverse" city pilots (2021–23) collapsed with the hype cycle; the EDIC deliberately anchors on interoperable, reusable LDTs and MIMs. Join for the interoperability, not the XR.

**Cost to start.** A government letter of intent + a municipal pilot. The EDIC's calls fund the rest.

---

## Cross-cutting: what the six core activities can already lean on (measured this week)

- `standards_watch`: 4 645 documents tracked across 19 watchlist committees; 28 open remisser/NWPs right now.
- `platforms_overview`: 90 releases in the last periods across 20 open projects (Orion-LD 1.12, OS2iot 1.12, ChirpStack 4.19, ThingsBoard 4.3, Ditto 3.9, Home Assistant 2026.8 …).
- `eu_monitor`: 29 open Funding & Tenders topics matching IoT / digital twin / smart cities / CitiVerse, with deadlines; AI Act enforcement news.
- `county_iot`: TED query returns 0 — the query grammar needs tuning; Internetstiftelsen's Dataverkstaden annual report surfaced as context.
- Full report: `reports/weekly/2026-W34/report.md`.
