# Other synthetic and test data sources

Other open sources of FHIR test patients, and the kind of testing each one is best for.
This repository links to them rather than copying them, so each keeps its own license and
updates. A patient from one of these is only copied here when it has been reworked (like
Kimberly Gonzalez, built on APEX Atlas) and its license allows it.

| Source | What it is | Best for | Region and coding | Depth per patient | License |
|---|---|---|---|---|---|
| [APEX Atlas](https://github.com/ParkerApex/apex-atlas) | Generated US population: 20,000 patients as bulk files and 25 readable bundles, plus a provider directory and scheduling data | Bulk data and performance testing at scale, US Core conformance, provider directory (Plan-Net) and scheduling scenarios, and a starting point for enriched patients | US: US Core 6.1, RxNorm, LOINC, SNOMED CT, Coverage, InsurancePlan | Focused: a few conditions, observations and medications per patient, with clean, fully resolving references | Apache 2.0 |
| [Synthea](https://github.com/synthetichealth/synthea) | Simulator that generates lifetime US patient histories on demand, for any state, city or age range | Long longitudinal histories, many patients with varied demographics, claims and encounters over decades | US: US Core 6.1, LOINC, RxNorm, CVX, SNOMED CT; claims and EOBs (not CARIN-profiled by default) | Deep: hundreds of resources per patient, with clinical notes. Some simulated care follows older guidance, so check vaccines and medicines for recent scenarios | Apache 2.0 |
| [HL7 AU FHIR Test Data](https://github.com/hl7au/au-fhir-test-data) | About 1,500 hand-written files: 89 patients plus practitioners, organizations and locations | Testing against the Australian guides (AU Base, AU Core, AU eRequesting, AU Patient Summary), and missing or suppressed data handling: 53 cases built for exactly that | Australia: IHI and Medicare identifiers, SNOMED CT-AU and Australian medicine and vaccine codes, Australian addresses | Varies: several rich patients, many focused on a single scenario | CC0 |
| [HL7 DARTS](https://github.com/HL7/fhir-darts) and [DAPL](https://github.com/HL7/fhir-dapl) examples | The same 10 patients as original US Core, pseudonymized and de-identified (HHS Safe Harbor), plus de-identified examples of most resource types | De-identification testing: a before-and-after answer key, and importing data in DAPL profiles | US: US Core in, DAPL profiles out | Focused: one condition per patient, built to show each transformation | CC0 |

## Choosing a source

- **US clinical and claims testing with realistic depth:** the patients in this repository,
  or Synthea for more variety.
- **Scale and bulk data:** APEX Atlas.
- **Australian implementations, or how an app handles missing and suppressed data:** HL7 AU
  FHIR Test Data.
- **De-identification:** the DARTS and DAPL examples.

When adding a source, include its license and what it's best for.
