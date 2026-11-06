# Design Review Helper (BDC 60.05.60.2)

**[Live demo →](https://slaterdamian.github.io/planning-tools/design-review-helper/)**

A single-page questionnaire that tells an applicant which Beaverton Development Code design
standards and guideline alternatives apply to their project, using Table 60.05.60.2 (Residential
and Small-Scale Commercial).

## What it does

- **Asks project facts once.** The questions are grouped into four steps: zone and location,
  building and exemptions, project scope and uses, and site work and features. Each answer is reused
  by every standard that depends on it, so nobody has to answer the same thing twice.
- **Handles exceptions.** Where a question describes an exemption, checking it removes the related
  standard instead of adding one.
- **Lists the applicable standards** by category, in a printable summary the applicant can bring to
  a pre-application meeting or attach to a submittal.

## Run locally

Open `index.html` in a browser. It's one self-contained file with no build step. Your answers stay in
the browser.

*Personal prototype, not an official City of Beaverton tool. Always confirm the applicable
standards against the current Development Code.*
