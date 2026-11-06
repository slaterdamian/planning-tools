# Development code intake assistant (Beaverton Type 1)

**[Live demo →](https://slaterdamian.github.io/planning-tools/permit-intake-assistant/)**

A completeness-review assistant that helps a planner check whether a City of
Beaverton Type 1 land use application is complete. It covers sign permits, Design Review
Compliance Letters, Single-Detached & Middle Housing Design Review One, Legal Lot Determinations,
landscape tree removals and other Chapter 40 applications.

It comes in two versions:

- **Web tool (`index.html`, the live demo).** A rule-based version that runs in any browser with no
  AI and no account. Pick the application type and zone, answer the threshold questions, and mark
  each submittal item as received, missing or deficient. It returns the Type 1 scope decision (or
  where to route the application instead), the zone-specific checklist, preliminary review math
  such as the 20% wall-sign allowance or tree replacement inches, the applicable standards, and a
  draft incompleteness letter you can copy or print. It covers the five most common paths: Sign
  Permit, DRCL, SDMHDR One, Legal Lot Determination and Landscape Tree removal.
- **AI version (`SKILL.md` + `references/`).** A Claude skill that reads a free-text proposal or
  uploaded PDFs, works from the full code text, and handles any Chapter 40 application.

The point is to show a **repeatable way to interpret code**. The assistant works from the
bundled code text, follows a set order of steps, and cites the exact section for every
requirement instead of answering from memory.

## How the AI version works

1. **Understand the proposal** and confirm the zoning district. Sign and design standards differ
   sharply by zone, so it asks for the zone if it isn't given.
2. **Classify the application.** It matches the proposal to a Chapter 40 application and reads
   that section's threshold, procedure type, approval criteria and submission requirements. If the
   procedure turns out to be Type 2, 3 or 4, it says so and recommends routing the application
   elsewhere.
3. **Resolve terms through a fixed hierarchy.** It checks the Chapter 90 definitions first, then
   falls back to *Webster's Third New International Dictionary* for ordinary meaning, and says
   which source it used.
4. **Build a zone-specific checklist** from the city's own application form, the general
   completeness rules (BDC 50.25.1), and the standards the approval criteria point to in
   Chapters 20, 60 and 70.
5. **Ask what was submitted**, then separate missing items from deficient ones. Under
   BDC 50.25.3, an item counts only if it is genuinely required information.
6. **Draft two outputs:** an internal checklist and an incompleteness letter. Every code section
   and defined term is linked to the city's online code (encodePlus).

The skill also lists known misinterpretations to avoid (for example, the real
Design Review Compliance Letter threshold), so the model doesn't make them.

## Files

- `index.html`: the web tool. One self-contained file; the rules live in the `TYPES` object.
- `SKILL.md`: the assistant's instructions.
- `references/`: the Beaverton Development Code text (Chapters 10–70), transcribed application
  checklists, key definitions, and section-to-link lookup tables.
- `assets/incompleteness-letter-template.md`: the letter format.

The code text is the City of Beaverton's public Development Code. Check the
[official code](https://online.encodeplus.com/regs/beaverton-or/doc-viewer.aspx) for current
language.

*Personal prototype, not an official City of Beaverton tool, and not a substitute for staff
review.*
