# Planning tools

Prototypes for turning development codes, application forms and transit data into structured,
usable answers. Each project was built with AI coding tools (Claude). I set the requirements,
interpreted the code and data, and tested and corrected the output.

These are personal prototypes. They are not official City of Beaverton, City of Portland or TriMet products, and
nothing here is legal or permitting advice.

| Project | What it does | Try it |
|---|---|---|
| [Development code intake assistant](permit-intake-assistant/) | Completeness review for Beaverton Type 1 land use applications: a zone-specific checklist, the applicable code standards and a draft incompleteness letter. There's a rule-based web tool and an AI version that works from the full Development Code. | [Live demo](https://slaterdamian.github.io/planning-tools/permit-intake-assistant/) |
| [Planning Forms Porter](form-porter/) | Reads a city application PDF, extracts every field, infers what each one expects, and rebuilds the form as a web form with a JSON schema. | [Live demo](https://slaterdamian.github.io/planning-tools/form-porter/) |
| [Design Review Helper](design-review-helper/) | A questionnaire that finds which Beaverton design standards and guideline alternatives in Table 60.05.60.2 apply to a residential or small commercial project. | [Live demo](https://slaterdamian.github.io/planning-tools/design-review-helper/) |
| [Portland eFile case lookup](portland-efile-lookup/) | Converts a PortlandMaps land use case number to the eFiles format and opens the matching public records search. | [Live demo](https://slaterdamian.github.io/planning-tools/portland-efile-lookup/) |
| [GTFS frequent-transit toolbox](gtfs-frequent-service/) | An ArcGIS Pro toolbox that classifies transit stops by frequency and builds half-mile access areas around frequent stops and rail lines. | [Toolbox](gtfs-frequent-service/GTFS_Frequent_Service.pyt) |
| [Portland Metro & Measure 50](https://github.com/slaterdamian/portland-metro-measure-50) | A fiscal model of every Portland parcel. It compares Measure 50 taxable value with market value and tax revenue with the cost of public services, then finds the density each zone needs so servicing it isn't a net drain, and tests that against Title 33. | [Interactive map](https://slaterdamian.github.io/portland-metro-measure-50/) |

## License

Code: MIT ([LICENSE](LICENSE)). The Beaverton Development Code text and the sample city
application PDF are public records of the City of Beaverton, included for reference. They are not
covered by the MIT license.
