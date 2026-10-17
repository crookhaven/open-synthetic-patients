#!/usr/bin/env python3
"""Runs the HL7 FHIR validator over every patient bundle and fails on new errors.

Usage:
  python tools/check_validation.py --validator validator_cli.jar [--logs DIR]

Each bundle listed in a patient card's `variants` is validated against FHIR R4,
US Core 6.1.0 and CARIN Blue Button 2.1.0. Errors listed in
tools/validation_known_issues.json are allowed; any other error fails the check.
Patients listed under `skip_patients` are not validated.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWN = ROOT / "tools" / "validation_known_issues.json"
IGS = ["hl7.fhir.us.core#6.1.0", "hl7.fhir.us.carin-bb#2.1.0"]
ERROR_LINE = re.compile(r"^\s*Error @ (?P<path>.*?)(?: \(line \d+, col\d+\))?: (?P<msg>.*)$")
SUMMARY_LINE = re.compile(r"^(Success|\*FAILURE\*):.*$", re.M)


def validate(jar, bundle, log):
    args = ["java", "-jar", jar, str(bundle), "-version", "4.0.1"]
    for ig in IGS:
        args += ["-ig", ig]
    # The terminology server is occasionally unreachable; one retry covers that.
    for _ in range(2):
        out = subprocess.run(args, capture_output=True, text=True).stdout
        log.write_text(out, encoding="utf-8")
        if SUMMARY_LINE.search(out):
            return out
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validator", required=True)
    ap.add_argument("--logs", default="validation-logs")
    a = ap.parse_args()
    known = json.loads(KNOWN.read_text(encoding="utf-8"))
    skip = known.get("skip_patients", {})
    logs = Path(a.logs)
    logs.mkdir(exist_ok=True)
    report, failed, seen = [], False, set()

    for card_path in sorted(ROOT.glob("patients/*/patient.json")):
        slug = card_path.parent.name
        if slug in skip:
            report.append(f"- **{slug}**: skipped ({skip[slug]})")
            continue
        card = json.loads(card_path.read_text(encoding="utf-8"))
        for variant, file in card["variants"].items():
            bundle = card_path.parent / file
            out = validate(a.validator, bundle, logs / f"{slug}-{variant}.log")
            summary = SUMMARY_LINE.search(out)
            if not summary:
                failed = True
                report.append(f"- **{slug}/{file}**: the validator did not finish (see the log)")
                continue
            new, allowed = [], 0
            for line in out.splitlines():
                m = ERROR_LINE.match(line)
                if not m:
                    continue
                hit = next((i for i, k in enumerate(known["known_errors"])
                            if k["patient"] == slug and k["contains"] in m["msg"]), None)
                if hit is None:
                    new.append(f"{m['path']}: {m['msg']}")
                else:
                    allowed += 1
                    seen.add(hit)
            status = "new errors" if new else "passes"
            report.append(f"- **{slug}/{file}**: {status} ({len(new)} new, {allowed} known)")
            for e in new[:25]:
                report.append(f"  - {e}")
                print(f"::error file=patients/{slug}/{file},title=FHIR validation::{e}")
            if len(new) > 25:
                report.append(f"  - ...and {len(new) - 25} more (see the log)")
            failed = failed or bool(new)

    gone = [k for i, k in enumerate(known["known_errors"]) if i not in seen]
    if gone:
        report.append("")
        report.append("Known errors that no longer occur (remove them from tools/validation_known_issues.json):")
        report += [f"- {k['patient']}: {k['contains']}" for k in gone]

    text = "## FHIR validation (FHIR R4, US Core 6.1.0, CARIN Blue Button 2.1.0)\n\n" + "\n".join(report) + "\n"
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
