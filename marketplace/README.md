# Marketplace plans

Real 2026 ACA Marketplace plans saved from the CMS Marketplace API, for testing plan comparison
and Real-Time Benefits screens without an API key.

| File | What it is |
|---|---|
| `marketplace_plans_48201.json` | All 60 plans offered in ZIP 48201 (Wayne County, Michigan) for a made-up household: one 41-year-old non-smoker. Includes each plan's drug coverage for a few common medicines (`_drug_coverage`) and a link to its Summary of Benefits and Coverage (`_sbc`). |

The plans and prices are real public data from CMS; the household is made up. The file has the
shape of the Marketplace API's plan search response, plus the `_household`, `_drug_coverage`
and `_sbc` fields added by M5 Whole Health's fetch script. Load it in M5 Whole Health's
**Compare plans** screen.

Prices are for plan year 2026 and will not match later years. This data is US government
public data, not covered by this repository's CC BY 4.0 license.
