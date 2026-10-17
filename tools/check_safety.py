#!/usr/bin/env python3
"""Checks that every patient in this repository is clearly synthetic and documented.

Usage: python tools/check_safety.py

Fails (exit 1) on:
  - a patient folder without a valid patient.json card (required fields, license)
  - a card variant whose bundle file is missing or is not a FHIR Bundle
  - any resource without the HTEST ("test health data") meta tag
  - anything that looks like a real Social Security number: a bare ###-##-#### in an
    issuable range, or any value of an identifier whose system is the US SSN system

Warns (does not fail) on contact details outside the reserved test ranges: phone
numbers that are not 555-01xx and emails outside example.com/.org/.net or *.test.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATIENTS = ROOT / "patients"

REQUIRED_CARD_FIELDS = ["schema", "slug", "name", "summary", "use_cases", "source", "license", "attribution", "variants"]
KNOWN_LICENSES = {"CC-BY-4.0", "Apache-2.0", "CC0-1.0"}
HTEST_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ActReason"
SSN_SYSTEM = "http://hl7.org/fhir/sid/us-ssn"

# A bare SSN pattern, not part of a longer token (so member IDs like "AHP-778-48-1978" pass).
BARE_SSN = re.compile(r"(?<![\w-])(\d{3})-(\d{2})-(\d{4})(?![\w-])")
# A phone number standing on its own, so pieces of UUIDs and other IDs don't match.
PHONE = re.compile(r"(?<![\w-])\(?(\d{3})\)?[-. ](\d{3})[-. ](\d{4})(?![\w-])")
EMAIL = re.compile(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")
SAFE_EMAIL_DOMAINS = ("example.com", "example.org", "example.net")


def issuable_ssn(area, group, serial):
    """True if this could be a real, issued SSN (area not 000/666/9xx, group/serial not zero)."""
    a = int(area)
    return a != 0 and a != 666 and a < 900 and int(group) != 0 and int(serial) != 0


def check_strings(value, where, errors, warnings):
    if isinstance(value, dict):
        for k, v in value.items():
            check_strings(v, where, errors, warnings)
    elif isinstance(value, list):
        for v in value:
            check_strings(v, where, errors, warnings)
    elif isinstance(value, str):
        for m in BARE_SSN.finditer(value):
            if issuable_ssn(*m.groups()):
                errors.append(f"{where}: looks like a real SSN: {m.group(0)} (use the 999 range)")
        for m in PHONE.finditer(value):
            if not (m.group(2) == "555" and m.group(3).startswith("01")):
                warnings.append(f"{where}: phone number outside the 555-01xx test range: {m.group(0)}")
        for m in EMAIL.finditer(value):
            domain = m.group(1).lower()
            if not (domain.endswith(SAFE_EMAIL_DOMAINS) or domain.endswith(".test")):
                warnings.append(f"{where}: email outside reserved test domains: {m.group(0)}")


def check_bundle(path, label, errors, warnings):
    try:
        bundle = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}: cannot read as JSON ({exc})")
        return
    if bundle.get("resourceType") != "Bundle":
        errors.append(f"{label}: not a FHIR Bundle")
        return
    for i, entry in enumerate(bundle.get("entry", [])):
        resource = entry.get("resource", {})
        rtype = resource.get("resourceType", "?")
        where = f"{label} entry {i} ({rtype})"
        tags = resource.get("meta", {}).get("tag", [])
        if not any(t.get("code") == "HTEST" and t.get("system") == HTEST_SYSTEM for t in tags):
            errors.append(f"{where}: missing the HTEST meta tag")
        for ident in resource.get("identifier", []):
            if ident.get("system") == SSN_SYSTEM and not str(ident.get("value", "")).startswith("999"):
                errors.append(f"{where}: SSN identifier outside the never-issued 999 range")
        check_strings(resource, where, errors, warnings)


def main():
    errors, warnings = [], []
    folders = sorted(p for p in PATIENTS.iterdir() if p.is_dir())
    for folder in folders:
        card_path = folder / "patient.json"
        if not card_path.exists():
            errors.append(f"{folder.name}: missing patient.json")
            continue
        card = json.loads(card_path.read_text(encoding="utf-8"))
        missing = [f for f in REQUIRED_CARD_FIELDS if not card.get(f)]
        if missing:
            errors.append(f"{folder.name}/patient.json: missing {', '.join(missing)}")
        if card.get("slug") != folder.name:
            errors.append(f"{folder.name}/patient.json: slug must match the folder name")
        if card.get("license") not in KNOWN_LICENSES:
            errors.append(f"{folder.name}/patient.json: license must be one of {sorted(KNOWN_LICENSES)}")
        if card.get("synthetic") is not True:
            errors.append(f"{folder.name}/patient.json: must state \"synthetic\": true")
        for variant, file_name in card.get("variants", {}).items():
            path = folder / file_name
            if not path.exists():
                errors.append(f"{folder.name}: variant '{variant}' file {file_name} not found")
                continue
            check_bundle(path, f"{folder.name}/{file_name}", errors, warnings)
    for w in sorted(set(warnings)):
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"Checked {len(folders)} patients: {len(errors)} errors, {len(set(warnings))} warnings.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
