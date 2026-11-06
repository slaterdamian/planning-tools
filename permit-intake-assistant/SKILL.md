---
name: permit-intake
description: >-
  Intake and completeness review for City of Beaverton Type 1 land use applications (sign permits,
  Design Review Compliance Letters/DRCL, Single-Detached & Middle Housing Design Review One/SDMHDR1,
  Legal Lot Determinations/LLD, landscape tree removals, and other Chapter 40 applications). Use this
  whenever a Beaverton planner describes or uploads an application and needs a zone-aware completeness
  checklist, a determination of what's missing, the applicable Development Code standards, or a draft
  incompleteness/deficiency letter. Trigger on prompts like "applicant submitting for 3 wall signs at
  [address] in [zone]", "sign permit", "completeness check", "is this application complete", "DRCL",
  "SDMHDR", "intake this application", "what's missing from this submittal", or any mention of the
  Beaverton Development Code (BDC). Reach for it even when the planner just pastes a proposal description.
---

# Beaverton permit intake

Help a City of Beaverton planner intake a **Type 1** land use application: figure out what it is, what
zone it's in, what the applicant must submit, what's missing, and which Development Code standards apply —
then draft an incompleteness letter. Type 1 = administrative, no public hearing (BDC 50.35).

The full Development Code (chapters 10–70) is bundled in `references/`. It is the source of truth — read it,
don't guess. The four most common applications on this desk are **Sign Permit, DRCL, SDMHDR1, and LLD**.

## Two standing facts about this desk
- **Fees are already paid** before the file arrives. Never list fee payment as a missing completeness item,
  even though every city form and approval-criteria list mentions fees.
- Applications **arrive electronically** (PDF uploads). If files are attached, read them first.

## Workflow — ask first, then checklist

The prompt usually looks like *"Applicant submitting for 3 wall signs, at [ADDRESS] in [ZONE]."* Work in order;
a checklist that isn't zone-aware will be wrong.

### 1. Understand the proposal
Read any uploaded PDFs. Confirm what's proposed, the site address, and the **zoning district**. If the zone
wasn't given and isn't in the documents, ask for it — sign and design standards diverge sharply by zone.

### 2. Determine the application type and confirm it's Type 1
Match the proposal to a Chapter 40 application (`references/application-types.md`, `references/00-index.md`).
Open the relevant `40.xx.15` section in `references/chapter-40-applications.txt` and read its **Threshold**,
**Procedure Type**, **Approval Criteria**, and **Submission Requirements**. If the procedure type is Type 2/3/4,
say so and recommend routing — it's outside this desk's Type 1 scope.

### 3. Resolve unclear terms — definition hierarchy
When unsure what a term means (e.g., "wall sign", "primary building wall", "gross floor area", "hazard tree"),
resolve it in this order and say which source you used:
1. **BDC Chapter 90 (Definitions)** — *check first, always.* The decision-critical definitions are bundled with
   full text in `references/definitions-key-terms.md`. The complete term→secid list is `references/secid-definitions.tsv`
   (566 terms) — for any term there, read it on encodePlus via its link (see Hyperlinking).
2. If Chapter 90 has no definition, use ***Webster's New International Dictionary, 3rd edition*** for the
   ordinary meaning.

### 4. Build the zone-aware checklist
Build the submittal checklist from the **city's own application form** for that type — these are transcribed in
`references/application-forms.md` (Sign, DRCL, SDMHDR1, LLD), which also lists the approval criteria and the
standards each worksheet flag pulls in. Then confirm against:
- the general completeness items in **BDC 50.25.1** (signed form + owner/agent authorization; written statement
  addressing the relevant criteria and standards), minus fees; and
- the **applicable standards** the approval criteria cross-reference into Chapters 20 (zoning/site standards),
  60 (e.g. 60.40 signs, 60.60 trees, 60.05 design), and 70 (downtown), **for the specific zone**. Read those
  sections and cite exact subsections.
Apply the corrections in `references/application-types.md` (signs never need Design Review; no engineer's stamp
as a planning item; DRCL threshold is 25% GFA / 2,500 sq ft, not an invented 500; no arborist letter or
fee-in-lieu for landscape removals). These encode real past mistakes — honor them.

### 5. Ask the planner what was actually submitted
Present the checklist and have the planner indicate, item by item, what the submittal includes. Use the
**AskUserQuestion tool with multiSelect** so they can check off everything present in one pass and note
partial/deficient items. If PDFs were uploaded, pre-fill what you can verify and ask them to confirm the rest.

### 6. Identify what's missing or deficient
Compare submitted vs. required. An item is a deficiency only if it's genuinely required information or an
unaddressed criterion (BDC 50.25.3) — never a quality judgment and never a comment on the likely outcome.

### 7. Produce the two deliverables (with hyperlinks)
1. **Internal completeness checklist** — every required item marked present / missing / deficient with its BDC
   citation, plus the applicable standards the proposal will be reviewed against.
2. **Draft incompleteness letter** — using `assets/incompleteness-letter-template.md`. List only missing items
   (with citations) and the applicable standards. If nothing is missing, don't force a letter: state the
   application appears complete and ready for review on the merits, and list the standards.

In **both** deliverables, hyperlink every cited code section and every defined term (see Hyperlinking). Save to
the outputs folder and present. Offer the letter as a Word document if the planner wants to send it (`docx` skill).

## Hyperlinking (required in all output)
The planner wants every code reference and every defined term linked back to encodePlus for cross-reference.
- **Link format:** `https://online.encodeplus.com/regs/beaverton-or/doc-viewer.aspx#secid-<ID>`
- **Code sections:** look up the section number in `references/secid-sections.tsv` and link it, e.g.
  `[BDC 60.40.35](https://online.encodeplus.com/regs/beaverton-or/doc-viewer.aspx#secid-290)`.
- **Defined terms:** when a Chapter 90 defined term appears in your output (it's listed in
  `references/secid-definitions.tsv`), link the first use, e.g.
  `[wall sign](https://online.encodeplus.com/regs/beaverton-or/doc-viewer.aspx#secid-502)`.
- If a section or term isn't in the bundled maps, you can resolve its secid live: the encodePlus tree loads via
  `toc-view.aspx?tocid=<id>&task=expand` and each node carries `id="secid-x<ID>"`; or open the doc viewer and
  read the `#secid-<ID>` in the URL. Don't fabricate an ID — omit the link if you can't verify it.

## Live resources (Chrome browser tool — JavaScript-rendered, not plain fetch)
- **Development Code & Chapter 90 Definitions:** https://online.encodeplus.com/regs/beaverton-or/doc-viewer.aspx
- **Application forms & checklists:** https://beavertonoregon.gov/777/Applications-Fees-Brochures
- **Engineering Design Manual** (vision/sight-clearance referenced by sign criteria):
  https://beavertonoregon.gov/814/Engineering-Design-Manual-Standard-Drawi

## Reference files
- `references/00-index.md` — chapter/section map; read first.
- `references/application-types.md` — Type 1 catalog + the required corrections.
- `references/application-forms.md` — submittal checklists & approval criteria transcribed from the city forms.
- `references/definitions-key-terms.md` — full text of decision-critical Chapter 90 definitions.
- `references/secid-sections.tsv` · `references/secid-definitions.tsv` — section/term → encodePlus secid for links.
- `references/chapter-20-zoning.txt` · `chapter-40-applications.txt` · `chapter-60-special-requirements.txt`
  · `chapter-70-downtown.txt` (+ ch.10/30/50) — full code text; grep by section number.
- `assets/incompleteness-letter-template.md` — the letter format.
