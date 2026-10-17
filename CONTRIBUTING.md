# Contributing

Thanks for adding to the collection. Every change goes through a pull request, and the
**Safety and catalog** check must pass before it can merge.

## Adding a patient

1. Create `patients/<slug>/`, where `<slug>` is the patient's name in lowercase with hyphens.
2. Add the FHIR R4 Bundle as `bundle.json`. Tag every resource with
   `{"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "HTEST"}` in
   `meta.tag`.
3. Add a `patient.json` card. Copy one from an existing patient and fill in every field:
   `slug`, `name`, `summary`, `conditions`, `use_cases`, `source`, `license`, `attribution`,
   `variants` and `"synthetic": true`.
4. If the patient is derived from another project, keep that project's license in the card
   and add a `NOTICE` file explaining what you changed.
5. Run the checks and rebuild the catalog:

   ```
   python tools/check_safety.py
   python tools/build_catalog.py
   ```

6. Commit `catalog.json` and `CATALOG.md` along with the patient.

## Adding a variant

Put the file beside the clean bundle (for example `bundle-messy.json`) and list it in the
card's `variants`. In the card's `notes`, describe what the variant changes, such as
"duplicate medications from two sources, three lab results with Unknown units".

## Rules

- **No real people.** Never build a patient from a real record, even with details changed,
  and never include real names, addresses, phone numbers, emails or identifiers.
- **Use reserved test values:** `example.org` emails, 555-01xx phone numbers, and SSNs in the
  999 range.
- **Respect licenses.** Only add data whose license allows redistribution, and state it.

## Use case tags

Reuse existing tags in `use_cases` where they fit, so the catalog stays searchable. Current
tags include `us-core`, `ips`, `piqi-data-quality`, `carin-bb-claims`, `coverage`,
`marketplace-plan-comparison`, `imaging`, `clinical-notes`, `referrals`, `dental`, `vision`,
`hearing`, `dermatology`, `smart-health-links`, `cpap-coverage`, `glp1-prior-auth`,
`cgm-coverage`, `intentional-gaps`, `minimal`, `large-record` and `quick-demo`.
