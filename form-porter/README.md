# PDF-to-web-form converter ("Planning Forms Porter")

**[Live demo →](https://slaterdamian.github.io/planning-tools/form-porter/)**

A single-page tool that reads a community development application PDF and rebuilds it as a web
form. It's meant to show how a city could move its paper and PDF applications online without
hand-building each form.

## What it does

- **Extracts fields** from fillable (AcroForm) PDFs, and finds field locations on flat PDFs from
  underscores, ruled lines and checkbox glyphs.
- **Infers labels and input types.** It reads the text around each field and uses keyword and
  formatting rules to decide whether a field expects a date, a phone number, an area and so on.
- **Groups structure:** repeating sections (more than one applicant or owner), tables, and related
  checkboxes.
- **Links fields to existing systems.** Fields such as email or site address are tagged to
  placeholder categories: Contacts/CRM, Property/GIS, Licenses, Permit, Payments, E-sign and
  Documents.
- **Flags uncertainty.** Fields it can't classify confidently are marked for human review rather
  than guessed.

There are three views: the generated **web form** (with an applicant/staff toggle and a side panel
showing where on the PDF each field came from), a **field map** for correcting labels, types and
links, and a **schema** view that exports a JSON form definition.

## Test case

The demo loads Beaverton's Wall/Freestanding Sign Application (`sign-application.pdf`, a public
city form). On that form it accounts for all **305** PDF fields:

- They collapse to **88** web fields: 66 one-to-one, 110 into two repeating blocks, and 120 into a
  sign-inventory table with automatic totals, plus grouped checkboxes.
- **43** fields are linked to placeholder systems.
- **14** are flagged for manual review, mostly measurements with no units.

It was also tested on two synthetic PDFs that use different conventions (tooltips, radio groups,
dropdowns, an underscore-based flat layout). It has not yet been run on other real city forms, so
expect some misread labels on new layouts. The field map view is there to correct them.

## Run locally

Open `index.html` in a browser, or serve the folder (`python -m http.server`). PDF parsing uses
pdf.js from cdnjs. You can drop any PDF onto the page.

*Personal prototype, not an official City of Beaverton product.*
