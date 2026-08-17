# Municipal IoT playbook — from plan to operation (v0.1)

*A checklist with sources. The `municipal_iot` agent verifies every link here still answers; dead links show up in the weekly digest.*

## 1. Decide what you want to change (SMILE: outcome first)
- Write the outcome in one sentence per case (fewer floods in cellars, warmer classrooms at lower cost, faster snow clearance). Data comes last.
- Check the case bank / IoT Sverige portfolio for someone who already did it: https://iotsverige.se/projekt/

## 2. Reuse a platform, do not build one
- County-wide precedent: Jönköping — https://iotjonkopingslan.se/om-satsningen/ (13 municipalities, region, länsstyrelse; contract with TH1NG "IoT Open", 2022)
- Open-source precedents: Sundsvall Diwise — https://www.diwise.se/ ; Denmark OS2iot — https://os2web.atlassian.net/wiki/spaces/OS2iot20/pages/2592211277
- Interoperability spine: OASC MIMs — https://mims.oascities.org/

## 3. Write requirements that cite standards
- Use `catalog/requirements.json` in this repo (checked monthly against the SEK catalogue).
- Reference architecture for procurement: RefARK IoT — https://inera.atlassian.net/wiki/spaces/AR/pages/4258005694/-How+RefARK+IoT+can+be+used+in+procurement
- International: ISO/IEC 30141:2024 — https://www.iso.org/standard/88800.html

## 4. Security and law before the first sensor
- Cyber Resilience Act (Reg. 2024/2847): https://eur-lex.europa.eu/eli/reg/2024/2847/oj — reporting duties 11 Sep 2026, full application 11 Dec 2027
- Consumer/municipal IoT baseline: ETSI EN 303 645 — https://www.etsi.org/deliver/etsi_en/303600_303699/303645/
- OT security: IEC 62443 (SS-EN IEC 62443 series via SEK) — https://elstandard.se/
- Public-space sensors: Amsterdam's mandatory register as a model — https://sensorenregister.amsterdam.nl/

## 5. Operate: keep the picture current
- Weekly digest: `reports/weekly/LATEST.md` in this repo (standards, platforms, EU calls, procurement notices)
- Standards Twin for your facility type: https://life-atlas.github.io/standards-fabric/
