# Beaverton Development Code — bundled reference index

This folder contains the full text of the Beaverton Development Code (BDC), chapters 10–70,
extracted from the official encodePlus document viewer. Use it to resolve standards and
application requirements **without going to the web**. Grep these files for section numbers
(e.g. `grep -n "60.40.35" chapter-60-special-requirements.txt`) and read the surrounding lines.

## What's where

| Chapter | File | Covers |
|---|---|---|
| 10 | `chapter-10-general-provisions.txt` | Purpose, interpretation, general rules |
| 20 | `chapter-20-zoning.txt` | **Zoning districts** + site development standards. Use to identify the zone and its base standards. |
| 30 | `chapter-30-nonconforming.txt` | Nonconforming uses/structures/signs |
| 40 | `chapter-40-applications.txt` | **Applications** — thresholds, procedure type, approval criteria, submittal requirements for every application type |
| 50 | `chapter-50-procedures.txt` | Procedures. **50.25 = Application Completeness** (the general submittal list); 50.35 = Type 1 procedure |
| 60 | `chapter-60-special-requirements.txt` | **Standards** — design (60.05), parking (60.30), signs (60.40), trees (60.60), etc. |
| 70 | `chapter-70-downtown.txt` | Downtown Design District — zoning/streets (70.15), design standards (70.20) |

## Chapter 90 (Definitions) and supporting files

Chapter 90 didn't export to the chapter text files (the viewer renders it separately), so it's captured here as:
- `definitions-key-terms.md` — full text of the decision-critical definitions (signs, trees, floor area, etc.).
- `secid-definitions.tsv` — every Chapter 90 term → encodePlus secid, for hyperlinking and live lookup.

Other supporting files:
- `application-forms.md` — submittal checklists + approval criteria transcribed from the city's application forms.
- `secid-sections.tsv` — section number → encodePlus secid, for hyperlinking citations.

For any term not covered by `definitions-key-terms.md`, follow its secid link to read it on encodePlus; if
Chapter 90 has no definition, fall back to *Webster's New International Dictionary, 3rd ed.*

The ordinance-history appendix (zoning-map amendment tables) was omitted as not relevant to intake.

## Key section quick-map

### Sign permit (Type 1)
- `40.60.15` (ch.40) — Sign application: threshold, Type 1 procedure, approval criteria, submittal
- `50.25.1` (ch.50) — general completeness items
- `60.40` (ch.60) — sign regulations. Sub-sections:
  - `60.40.10` exempt from permit · `60.40.15` no-permit-but-regulated · `60.40.20` signs requiring a permit
  - `60.40.25` prohibited signs · `60.40.30` general size/location/measurement
  - `60.40.35` **Commercial / Industrial / Multiple-Use zones** (wall, awning, projecting, blade, freestanding; Tables A & B)
  - `60.40.40` **Residential zones** (MR, RMA, RMB, RMC, CM-MR, CM-RM)
  - `60.40.45` temporary · `60.40.50` electronic message centers · `60.40.55` nonconforming/illegal
- Downtown sign design/materials live in `60.40.35.6` (RC-BC/RC-MU/RC-DT/RC-OT) and the 40% window-sign allowance in `60.40.15.1`; Chapter 70 governs the broader downtown design context.

### Design Review Compliance Letter — DRCL (Type 1), 40.20.15.1
- Use DRCL (not DR Two/Three) only when the proposal is limited to the listed minor actions, OR:
  - GFA addition in residential/commercial/MU zones **≤ 25% of existing GFA and ≤ 2,500 sq ft**
  - GFA addition in industrial zones **≤ 15% of existing GFA and < 30,000 sq ft**
- Above those = Design Review Two (Type 2) or Three (Type 3) — outside Type 1 scope, flag for routing.

### Single-Detached & Middle Housing Design Review One — SDMHDR1 (Type 1), 40.21.15.1
- Applies to single-detached dwellings and middle housing (NOT commercial). Thresholds at 40.21.15.1
  (window/door changes per 60.05.60.2, floor-area additions in RMA/RMB/RMC/CM-RM, etc.).
- Design standards/guidelines for these housing types: `60.05.60` (ch.60).

### Legal Lot Determination — LLD (Type 1), 40.47
- 40.47 in ch.40 — threshold, criteria, submittal.

### Other ch.40 applications (broader scope)
Adjustment 40.10 · Conditional Use 40.15 · Design Review 40.20 · SDMHDR 40.21 · Downtown DR 40.23 ·
Director's Interpretation 40.25 · Zero Yard Setbacks 40.30 · Food Cart Pods 40.32 · Historic 40.35 ·
Home Occupation 40.40 · Land Division 40.45 · Legal Lot 40.47 · Loading 40.50 · Parking 40.55 ·
Sign 40.60 · Mass Shelter 40.65 · Resource Overlay 40.70 · Street Vacation 40.75 · Temporary Use 40.80 ·
Tree Plan 40.90 · Tree (Cooper Mtn) 40.91 · Variance 40.95 · Wireless 40.96.
Procedure type (Type 1/2/3/4) for each is stated in that section's ".15 Application → Procedure Type".
