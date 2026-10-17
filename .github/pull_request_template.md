## What this adds or changes

<!-- New patient, new variant, fix, tooling? One or two sentences. -->

## Checklist

- [ ] Every patient is fully synthetic, and none is based on a real person's record
- [ ] Every resource has the `HTEST` meta tag
- [ ] Contact details use test values (`example.org`, 555-01xx, SSN in the 999 range)
- [ ] `patient.json` is filled in, including `source`, `license` and `attribution`
- [ ] Data from another project keeps its license, with a `NOTICE` where required
- [ ] I ran `python tools/build_catalog.py` and committed `catalog.json` and `CATALOG.md`
