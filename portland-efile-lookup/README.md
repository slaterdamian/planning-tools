# Portland eFile case lookup

**[Live demo →](https://slaterdamian.github.io/planning-tools/portland-efile-lookup/)**

A small tool that turns a PortlandMaps land use case number into a search on the City of
Portland's public eFiles records site.

PortlandMaps and eFiles write the same case differently. PortlandMaps uses
`2024-073629-000-00-LU`, while eFiles indexes it as `LU 24-073629`. This page converts one format
to the other and opens the matching eFiles search, so you don't have to retype the number.

## How it works

- Checks the input against the PortlandMaps `YYYY-NNNNNN-NNN-NN-LU` pattern and shows the converted
  eFiles reference as you type.
- Opens `efiles.portlandoregon.gov` in a new tab with a search for that reference, newest records
  first.

## Run locally

Open `index.html` in a browser. It's one self-contained file. The only network request is the
eFiles search you open.

*Personal prototype, not an official City of Portland tool.*
