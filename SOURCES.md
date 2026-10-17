# Other synthetic and test data sources

Other places to find FHIR test patients, and what each is good for. This repository links
to them rather than copying them, so each keeps its own license and updates. A patient
from one of these is only copied here when it has been reworked (like Kimberly Gonzalez,
built on APEX Atlas) and its license allows it.

| Source | What it is | US fit | Depth per patient | Messy like real data? | License |
|---|---|---|---|---|---|
| [APEX Atlas](https://github.com/ParkerApex/apex-atlas) | Generated US population: 20,000 patients as bulk files, 25 readable bundles, plus a provider directory and scheduling data | Strong: US Core 6.1, RxNorm, LOINC, SNOMED CT, Coverage, InsurancePlan | Thin: about 1.4 conditions, 7 observations and 1 medication per patient; no allergies or claims in the sample | No: very clean | Apache 2.0 |
| [Synthea](https://github.com/synthetichealth/synthea) | Simulator that generates lifetime US patient histories on demand | Strong: US Core 6.1, LOINC, RxNorm, CVX, SNOMED CT; claims and EOBs (not CARIN-profiled) | Deep: hundreds of resources per patient, with notes | No: one simulated health system per patient. Some care patterns are dated (for example live zoster vaccine after 2020) | Apache 2.0 |
| [HL7 AU FHIR Test Data](https://github.com/hl7au/au-fhir-test-data) | About 1,500 hand-written files: 89 patients plus providers and organizations | Weak: Australian identifiers and addresses; medicines and vaccines coded in SNOMED CT-AU or Australian codes, not RxNorm or CVX | Uneven: a few rich patients, most minimal | Yes, by design: 53 missing-field and suppressed-data cases, a good checklist of faults to recreate in US patients | CC0 |
| [HL7 DARTS](https://github.com/HL7/fhir-darts) and [DAPL](https://github.com/HL7/fhir-dapl) examples | The same 10 patients as original US Core, pseudonymized and de-identified (Safe Harbor), plus de-identified examples of most resource types | US Core in, DAPL profiles out | Thin: one condition per patient | No | CC0 |

When adding a source, include its license and a one-line note on what it's good for.
