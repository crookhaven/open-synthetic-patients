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
| [MIMIC-IV Clinical Database Demo on FHIR](https://www.physionet.org/content/mimic-iv-fhir-demo/) | 100 real, de-identified hospital patients (Beth Israel Deaconess Medical Center ICU and emergency department) converted to FHIR R4, as bulk NDJSON files (v2.1.0, August 2025) | The closest open option to real-world data: actual labs, medication administrations, microbiology and charted observations, with the gaps and variation of real hospital records. Open access, no credentialing | US: profiles based on US Core R4, with MIMIC-specific terminology | Deep inpatient and emergency care; little outpatient or claims data | ODbL 1.0 (share-alike for databases); citation required. Link to it rather than copying patients into this repository |
| [CMS Synthetic Medicare Claims](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files) (Synthetic RIF files, 2023) | 8,671 synthetic Medicare beneficiaries with about 1.9 million fee-for-service claims (carrier, outpatient, inpatient, skilled nursing, hospice, home health, DME) and 515,000 Part D events, 2015 to 2023 | Claims at volume in Medicare's research file format: testing claims-to-FHIR and CARIN Blue Button mapping, and payer analytics | US Medicare: pipe-delimited RIF files, not FHIR. Generated with Synthea | Claims only, many per beneficiary | US government public data, no use restrictions |
| [CMS Blue Button 2.0 sandbox](https://bluebutton.cms.gov/api-documentation/explore-the-api/) | Synthetic Medicare beneficiaries behind the live Blue Button API (Patient, Coverage, ExplanationOfBenefit), plus a downloadable single-beneficiary sample | Testing an app end to end against a real payer API, including OAuth sign-in, with synthetic members | US Medicare claims as FHIR | Claims and coverage history per beneficiary | Free developer sandbox; register an app to get credentials |
| [Synthea prebuilt data sets](https://synthetichealth.github.io/downloads.html) | Ready-made downloads: Synthetic Denver (6,357 children), a Canadian sample, breast cancer (mCODE), COVID-19 sets, 100-record samples, and the [Coherent Data Set](https://registry.opendata.aws/synthea-coherent-data/) (FHIR plus DICOM imaging, genomics, ECGs and notes, 9 GB) | Pediatric patients, imaging and genomics linked to the same patient, and Synthea data without running the simulator | Mostly US (one Canadian set); same coding as Synthea | Deep, as with Synthea | Free to use; citation requested |
| [HL7 DARTS](https://github.com/HL7/fhir-darts) and [DAPL](https://github.com/HL7/fhir-dapl) examples | The same 10 patients as original US Core, pseudonymized and de-identified (HHS Safe Harbor), plus de-identified examples of most resource types | De-identification testing: a before-and-after answer key, and importing data in DAPL profiles | US: US Core in, DAPL profiles out | Focused: one condition per patient, built to show each transformation | CC0 |

## Choosing a source

- **US clinical and claims testing with realistic depth:** the patients in this repository,
  or Synthea for more variety.
- **Real-world data as close to actual records as an open source allows:** MIMIC-IV on FHIR.
- **Children, imaging or genomics:** the Synthea prebuilt sets (Synthetic Denver, the Coherent
  Data Set).
- **Medicare claims:** the CMS synthetic claims files for volume, the Blue Button 2.0 sandbox
  for a live API.
- **Scale and bulk data:** APEX Atlas.
- **Australian implementations, or how an app handles missing and suppressed data:** HL7 AU
  FHIR Test Data.
- **De-identification:** the DARTS and DAPL examples.

When adding a source, include its license and what it's best for.
