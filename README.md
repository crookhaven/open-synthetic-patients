# open-synthetic-patients

Open, fully synthetic FHIR R4 test patients for interoperability testing. **No real PHI.**

Every patient here is made up. Each one is documented with what it's good for, where it came
from and its license, so you can pick the right test patient without opening a 1 MB bundle.
See **[CATALOG.md](CATALOG.md)** for the full list.

## Why this exists

Real patient data is the best test data, but it can't be shared without de-identification
that holds up legally. These patients are built to behave like real records instead:
realistic histories, US coding (US Core, LOINC, RxNorm, SNOMED CT, CVX, ICD-10-CM), claims
and coverage, clinical notes and imaging reports. Planned variants add the problems real
records have, such as duplicates from several sources, conflicting entries and missing
values, described as patterns rather than copied from anyone's chart.

## Layout

```
patients/<slug>/
  bundle.json     FHIR R4 Bundle (the "clean" variant)
  patient.json    the patient card: summary, conditions, use cases, source, license
  build.ps1       script that rebuilds the bundle (where one exists)
  NOTICE          attribution, for patients derived from another project
  piqi/           PIQI messages (clinical, IPS, claims) built from bundle.json, ready to score
marketplace/      real 2026 Marketplace plans for one ZIP code, for plan comparison testing
tools/
  check_safety.py     checks that every patient is tagged, documented and synthetic
  build_catalog.py    builds catalog.json and CATALOG.md from the patient cards
  powershell/         shared builders and publishing scripts (HAPI, SMART Health Links)
catalog.json      machine-readable index of every patient (generated)
CATALOG.md        human-readable index (generated)
sources.json      other data sources, with section, type and license
SOURCES.md        human-readable list of other sources (generated)
```

Each patient card lists **variants**. Today every patient has a `clean` variant; `messy`
(real-world data-quality problems) and `deidentified` variants will sit beside it.

## Using a patient

- **Download a bundle:** open the patient's folder and download `bundle.json`, or use the raw
  URL, for example
  `https://raw.githubusercontent.com/crookhaven/open-synthetic-patients/main/patients/mavis-dracula/bundle.json`.
- **Find patients by use case:** `catalog.json` lists every patient's `use_cases`, such as
  `carin-bb-claims`, `ips`, `piqi-data-quality` or `cpap-coverage`.
- **Load into a FHIR server:** `tools/powershell/publish_to_hapi.ps1` uploads a bundle to the
  public HAPI test server in dependency order.

## Safety rules

- Every resource carries the `HTEST` ("test health data") meta tag.
- Contact details use reserved test ranges: `example.org` emails, 555-01xx phone numbers.
  SSNs, if any, use the never-issued 999 range.
- No patient may be built from, or copied from, a real person's record, even with details
  changed.
- `tools/check_safety.py` enforces these rules on every pull request.

## Licensing

- **Patient data and documentation:** [CC BY 4.0](LICENSE). Reuse it freely, including
  commercially, as long as you give credit (see [CITATION.cff](CITATION.cff)).
- **Scripts and tools** (`*.ps1`, `*.py`, `tools/`, `.github/`): [Apache 2.0](LICENSE-CODE).
- **Marketplace plans** (`marketplace/`) are US government public data from CMS.
- **Exceptions are stated per patient.** A patient derived from another project keeps that
  project's license; for example, Kimberly Gonzalez is Apache 2.0 because she is built on
  [APEX Atlas](https://github.com/ParkerApex/apex-atlas). Each `patient.json` has a
  `license` field, and a `NOTICE` file where attribution is required.

## Other sources

Looking for something this collection doesn't have yet? [SOURCES.md](SOURCES.md) lists other
open synthetic and test data sources, from Synthea, ONC's Inferno data and MIMIC-IV to
international sets from Australia, Europe, Canada, India and Africa. It's grouped by region
and by what you're testing, with each source's type (FHIR download, generator, API sandbox
and so on) so you can see at a glance how you'd get the data.

## Contributing

New patients and variants are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Origin

These patients were first built for testing
[M5 Whole Health](https://github.com/crookhaven/M5-WholeHealth), an open-source,
patient-controlled health data app, at HL7 and CMS Health Tech Ecosystem connectathons.
