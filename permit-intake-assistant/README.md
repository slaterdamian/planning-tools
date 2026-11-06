# Development code intake assistant (Beaverton Type 1)

An AI assistant, packaged as a Claude skill, that helps a planner check whether a City of
Beaverton Type 1 land use application is complete. It covers sign permits, Design Review
Compliance Letters, Single-Detached & Middle Housing Design Review One, Legal Lot Determinations,
landscape tree removals and other Chapter 40 applications.

The point is to show a **repeatable way to interpret code**. The assistant works from the
bundled code text, follows a set order of steps, and cites the exact section for every
requirement instead of answering from memory.

## How it works

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

- `SKILL.md`: the assistant's instructions.
- `references/`: the Beaverton Development Code text (Chapters 10–70), transcribed application
  checklists, key definitions, and section-to-link lookup tables.
- `assets/incompleteness-letter-template.md`: the letter format.

The code text is the City of Beaverton's public Development Code. Check the
[official code](https://online.encodeplus.com/regs/beaverton-or/doc-viewer.aspx) for current
language.

*Personal prototype, not an official City of Beaverton tool, and not a substitute for staff
review.*
