#!/usr/bin/env python3
"""Turns a patient's coverage into CARIN Digital Insurance Card records.

Reads patients/<slug>/insurance-cards.json and rewrites that patient's
bundle.json so each card's Coverage, payer Organization and the Patient follow
the CARIN Digital Insurance Card guide (C4DIC 2.0.0-ballot): member ID,
group, plan, network, pharmacy (RxBIN, RxPCN, RxGroup, RxID), copays and
deductibles, payer contacts, card colors, logo, barcode, QR code, card front
and back images and the card's notices. Card images are drawn here and saved
next to the bundle (insurance-cards/*.png) as well as embedded in it.

Works for commercial, Marketplace, Medicare, Medicare Part D and Medicaid
cards. Everything is synthetic: plan names, phone numbers (NANP 555-01xx,
reserved for fiction), RxBINs (999xxx) and payer IDs are made up, and every
card image carries a SAMPLE watermark. Medicare's own public phone numbers
are used on Medicare cards because they are the real numbers for Medicare.

  python tools/insurance_cards.py maximus-decimus-meridius
  python tools/insurance_cards.py --all

Needs Pillow and segno (pip install pillow segno).
"""
import argparse
import base64
import io
import json
import sys
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import segno
except ImportError:  # pragma: no cover
    sys.exit("insurance_cards.py needs segno: pip install segno")

ROOT = Path(__file__).resolve().parent.parent
C4DIC = "http://hl7.org/fhir/us/insurance-card/StructureDefinition"
EXT = {k: f"{C4DIC}/C4DIC-{k}-extension" for k in [
    "PlanBeneficiaries", "AdditionalCardInformation", "ColorPalette", "ForegroundColor", "BackgroundColor",
    "HighlightColor", "Logo", "QRCode", "Barcode", "SupportingImage", "CardIssueDate", "BeneficiaryCostString"]}
CLASS_CS = "http://terminology.hl7.org/CodeSystem/coverage-class"
CLASS_EXT_CS = "http://terminology.hl7.org/CodeSystem/C4DICExtendedCoverageClassCS"
COPAY_CS = "http://terminology.hl7.org/CodeSystem/coverage-copay-type"
COPAY_EXT_CS = "http://terminology.hl7.org/CodeSystem/C4DICExtendedCopayTypeCS"
CONTACT_CS = "http://terminology.hl7.org/CodeSystem/contactentity-type"
CONTACT_EXT_CS = "http://terminology.hl7.org/CodeSystem/C4DICExtendedContactTypeCS"
COLOR_CS = "http://terminology.hl7.org/CodeSystem/IECColourManagement"
UUID_NS = uuid.UUID("6d8f3c1e-3a52-4f0c-9b8a-2f4f6c1d7e90")
LAST_UPDATED = "2026-11-03T12:00:00Z"
SAMPLE = "SAMPLE - SYNTHETIC TEST DATA - NOT A REAL CARD"

CONTACTS = {
    "member": (CONTACT_CS, "PATINF", "Patient"),
    "payer": (CONTACT_CS, "PAYOR", "Payor"),
    "pharmacist": (CONTACT_EXT_CS, "pharma", "Pharmacists"),
    "mail_order": (CONTACT_EXT_CS, "rxmailorder", "Mail Order Pharmacy"),
    "provider": (CONTACT_EXT_CS, "provider", "Provider Service"),
    "virtual": (CONTACT_EXT_CS, "virtual", "Virtual Care Services"),
}
COPAY_DISPLAY = {
    "gpvisit": "GP Office Visit", "spvisit": "Specialist Office Visit", "emergency": "Emergency",
    "urgentcare": "Urgent Care", "televisit": "Tele-visit", "copaypct": "Copay Percentage", "copay": "Copay Amount",
    "deductible": "Deductible", "maxoutofpocket": "Maximum out of pocket", "inpthosp": "Inpatient Hospital",
    # IndOutDed is left without a display: the code system's own display has a typo ("Invidual").
    "IndInDed": "Individual In Network Deductible", "IndOutDed": None,
    "IndInMax": "Individual In Network Out of Pocket Maximum", "IndOutMax": "Individual Out of Network Out of Pocket Maximum",
    "FamInDed": "Family In Network Deductible", "FamInMax": "Family In Network Out of Pocket Maximum",
    "rx": "Prescription",
}
EXTENDED_COPAYS = {"IndInDed", "IndOutDed", "IndInMax", "IndOutMax", "FamInDed", "FamInMax", "rx"}

FONTS = "/usr/share/fonts/truetype/dejavu/"


def font(size, bold=False):
    for name in (["DejaVuSans-Bold.ttf"] if bold else ["DejaVuSans.ttf"]):
        try:
            return ImageFont.truetype(FONTS + name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ barcodes
# Code 128 (set B): bar and space widths for symbols 0..106.
CODE128 = [
    "212222", "222122", "222221", "121223", "121322", "131222", "122213", "122312", "132212", "221213",
    "221312", "231212", "112232", "122132", "122231", "113222", "123122", "123221", "223211", "221132",
    "221231", "213212", "223112", "312131", "311222", "321122", "321221", "312212", "322112", "322211",
    "212123", "212321", "232121", "111323", "131123", "131321", "112313", "132113", "132311", "211313",
    "231113", "231311", "112133", "112331", "132131", "113123", "113321", "133121", "313121", "211331",
    "231131", "213113", "213311", "213131", "311123", "311321", "331121", "312113", "312311", "332111",
    "314111", "221411", "431111", "111224", "111422", "121124", "121421", "141122", "141221", "112214",
    "112412", "122114", "122411", "142112", "142211", "241211", "221114", "413111", "241112", "134111",
    "111242", "121142", "121241", "114212", "124112", "124211", "411212", "421112", "421211", "212141",
    "214121", "412121", "111143", "111341", "131141", "114113", "114311", "411113", "411311", "113141",
    "114131", "311141", "411131", "211412", "211214", "211232", "2331112"]


def code128(text, module=2, height=60):
    codes = [104] + [ord(c) - 32 for c in text]
    check = (codes[0] + sum(i * c for i, c in enumerate(codes[1:], 1))) % 103
    widths = "".join(CODE128[c] for c in codes + [check]) + CODE128[106]
    total = sum(int(w) for w in widths) + 20
    img = Image.new("1", (total * module, height), 1)
    d = ImageDraw.Draw(img)
    x, bar = 10 * module, True
    for w in widths:
        w = int(w) * module
        if bar:
            d.rectangle((x, 0, x + w - 1, height), fill=0)
        x += w
        bar = not bar
    return img.convert("RGB")


def qr(text, scale=4):
    buf = io.BytesIO()
    segno.make(text, error="m").save(buf, kind="png", scale=scale, border=2)
    return Image.open(io.BytesIO(buf.getvalue())).convert("RGB")


# ------------------------------------------------------------------ drawing
def logo_image(brand, width=360, height=96):
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    c = rgb(brand["color"])
    acc = rgb(brand["accent"])
    d.ellipse((8, 12, 80, 84), fill=c)
    d.text((44, 48), brand["mark"], font=font(34, True), fill=acc, anchor="mm")
    d.text((96, 20), brand["name"], font=font(30, True), fill=c)
    d.text((97, 60), brand["tagline"], font=font(16), fill=(90, 90, 90))
    return img


def watermark(img):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((img.width / 2, img.height / 2), "SAMPLE", font=font(110, True), fill=(255, 255, 255, 60), anchor="mm")
    out = Image.alpha_composite(img.convert("RGBA"), layer.rotate(18, center=(img.width / 2, img.height / 2)))
    return out.convert("RGB")


def card_front(card, patient_name):
    W, H = 640, 404
    b = card["brand"]
    img = Image.new("RGB", (W, H), rgb(b["color"]))
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 40, W, H), fill=rgb(b["accent"]))
    d.ellipse((24, 22, 74, 72), fill=rgb(b["accent"]))
    d.text((49, 47), b["mark"], font=font(26, True), fill=rgb(b["color"]), anchor="mm")
    d.text((88, 24), b["name"], font=font(26, True), fill="white")
    d.text((89, 56), card["card_title"], font=font(15), fill=(230, 235, 240))
    y = 100
    rows = [("Member", patient_name)]
    if not card.get("hide_member_id_row"):
        rows.append(("Member ID", card["member_id"]))
    rows += [tuple(r) for r in card["front_rows"]]
    right = (420 if card.get("copay_box") else W) - 12
    for label, value in rows:
        d.text((28, y), label.upper(), font=font(12, True), fill=(200, 210, 220))
        size = 18
        while size > 11 and d.textlength(value, font=font(size, True)) > right - 180:
            size -= 1
        d.text((180, y - 3 + (18 - size) // 2), value, font=font(size, True), fill="white")
        y += 30
    if card.get("copay_box"):
        x0 = 420
        d.rounded_rectangle((x0, 96, W - 24, 96 + 26 * len(card["copay_box"]) + 14), 8, fill=(255, 255, 255))
        for i, (label, value) in enumerate(card["copay_box"]):
            d.text((x0 + 12, 106 + 26 * i), label, font=font(13), fill=(40, 40, 40))
            d.text((W - 36, 106 + 26 * i), value, font=font(13, True), fill=(20, 20, 20), anchor="ra")
    d.text((28, H - 30), card["footer"], font=font(13, True), fill=rgb(b["color"]))
    d.text((W - 24, H - 30), "SAMPLE", font=font(13, True), fill=rgb(b["color"]), anchor="ra")
    return watermark(img)


def card_back(card, barcode_img, qr_img):
    W, H = 640, 404
    b = card["brand"]
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 34), fill=rgb(b["color"]))
    d.text((20, 8), f"{b['name']}  ·  {card['card_title']}", font=font(15, True), fill="white")
    y = 46
    for label, value in card["back_rows"]:
        d.text((20, y), label, font=font(13), fill=(70, 70, 70))
        d.text((300, y), value, font=font(13, True), fill=(20, 20, 20))
        y += 21
    y += 6
    for line in card["back_notes"]:
        d.text((20, y), line, font=font(11), fill=(70, 70, 70))
        y += 15
    q = qr_img.resize((104, 104), Image.NEAREST)
    img.paste(q, (W - 124, 44))
    bc = barcode_img.resize((min(360, barcode_img.width), 46))
    img.paste(bc, (20, H - 92))
    d.text((20, H - 42), card["member_id"], font=font(11), fill=(40, 40, 40))
    d.text((20, H - 24), SAMPLE, font=font(11, True), fill=(180, 30, 30))
    return watermark(img)


def png_b64(img, colors=96):
    buf = io.BytesIO()
    img.convert("P", palette=Image.ADAPTIVE, colors=colors).save(buf, "PNG", optimize=True)
    return buf.getvalue(), base64.b64encode(buf.getvalue()).decode()


# ------------------------------------------------------------------ FHIR
def image_ext(kind, label, description, data):
    return {"url": EXT[kind], "extension": [
        {"url": "description", "valueString": description},
        {"url": "image", "valueAttachment": {"contentType": "image/png", "data": data}},
        {"url": "label", "valueString": label}]}


def color(kind, hex_color):
    return {"url": EXT[kind], "valueCodeableConcept": {"coding": [{"system": COLOR_CS, "code": hex_color.upper()}]}}


def copay(entry):
    code = entry["type"]
    system = COPAY_EXT_CS if code in EXTENDED_COPAYS else COPAY_CS
    coding = {"system": system, "code": code}
    if COPAY_DISPLAY.get(code, code):
        coding["display"] = COPAY_DISPLAY.get(code, code)
    out = {"type": {"coding": [coding]}}
    if "text" in entry:
        out["type"]["text"] = entry["text"]
    if "amount" in entry:
        out["valueMoney"] = {"value": entry["amount"], "currency": "USD"}
    else:
        out["valueMoney"] = {"extension": [{"url": EXT["BeneficiaryCostString"], "valueString": entry["string"]}]}
    return out


def human_name(patient):
    n = patient["name"][0]
    return {"family": n["family"], "given": n.get("given", [])}


def display_name(patient):
    n = patient["name"][0]
    given = n.get("given", [])
    first = given[0] if given else ""
    middle = (" " + given[1][0] + ".") if len(given) > 1 else ""
    return f"{first}{middle} {n['family']}".strip().upper()


def with_profile(resource, profile):
    meta = resource.setdefault("meta", {})
    profiles = meta.setdefault("profile", [])
    if profile not in profiles:
        profiles.insert(0, profile)
    meta["lastUpdated"] = LAST_UPDATED
    # keep meta keys in a stable order
    resource["meta"] = {k: meta[k] for k in ["lastUpdated", "profile", "tag"] if k in meta} | {
        k: v for k, v in meta.items() if k not in ("lastUpdated", "profile", "tag")}


def ordered(resource, first):
    return {k: resource[k] for k in first if k in resource} | {k: v for k, v in resource.items() if k not in first}


def build_payer(org, card):
    p = card["payer"]
    with_profile(org, f"{C4DIC}/C4DIC-Organization")
    ids = [i for i in org.get("identifier", []) if i.get("type", {}).get("coding", [{}])[0].get("code") != "payerid"]
    if p.get("payer_id"):
        ids.insert(0, {"type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/C4DICIdentifierType", "code": "payerid", "display": "Payer ID"}]},
                       "value": p["payer_id"]})
    org["identifier"] = ids
    org["active"] = True
    org["name"] = p["name"]
    org["type"] = [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/organization-type", "code": "pay", "display": "Payer"}], "text": "Payer"}]
    if p.get("website"):
        org["telecom"] = [{"system": "url", "value": p["website"]}]
    contacts = []
    for key, value in p["contacts"].items():
        system, code, disp = CONTACTS[key]
        c = {"purpose": {"coding": [{"system": system, "code": code, "display": disp}]}}
        if key == "payer":
            a = value
            c["name"] = {"text": "Claims"}
            c["address"] = {"type": "postal", "text": f"{', '.join(a['line'])}, {a['city']}, {a['state']} {a['postalCode']}",
                            "line": a["line"], "city": a["city"], "state": a["state"], "postalCode": a["postalCode"], "country": "US"}
        else:
            c["telecom"] = [{"system": "url" if value.startswith("http") else "phone", "value": value}]
        contacts.append(c)
    org["contact"] = contacts
    org.pop("address", None)
    return ordered(org, ["resourceType", "id", "meta", "identifier", "active", "type", "name", "telecom", "contact"])


def build_coverage(cov, card, patient, patient_ref, payer_ref, images):
    with_profile(cov, f"{C4DIC}/C4DIC-Coverage")
    exts = []
    for name in card.get("plan_beneficiaries", [{"member_id": card["member_id"], "name": human_name(patient)}]):
        exts.append({"url": EXT["PlanBeneficiaries"], "extension": [
            {"url": "memberId", "valueString": name["member_id"]},
            {"url": "name", "valueHumanName": name["name"]}]})
    for note in card["notices"]:
        exts.append({"url": EXT["AdditionalCardInformation"], "valueAnnotation": {"text": note}})
    exts.append({"url": EXT["CardIssueDate"], "valueDate": card["card_issue_date"]})
    b = card["brand"]
    exts.append({"url": EXT["ColorPalette"], "extension": [
        color("ForegroundColor", "#FFFFFF"), color("BackgroundColor", b["color"]), color("HighlightColor", b["accent"])]})
    exts.append(image_ext("Logo", b["name"], f"{b['name']} logo: a {b['mark']} monogram in a circle beside the plan name. Synthetic brand.", images["logo"]))
    exts.append(image_ext("QRCode", "Card details", "QR code on the back of the card holding the plan name, member ID, group and pharmacy numbers as text. Synthetic.", images["qr"]))
    exts.append(image_ext("Barcode", "Member ID barcode", f"Code 128 barcode of the member ID {card['member_id']}, for scanning at check-in. Synthetic.", images["barcode"]))
    exts.append(image_ext("SupportingImage", "Front of insurance card", card["front_description"], images["front"]))
    exts.append(image_ext("SupportingImage", "Back of insurance card", card["back_description"], images["back"]))
    cov["extension"] = exts
    cov["identifier"] = [{"type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "MB", "display": "Member Number"}], "text": "Member ID"},
                          "system": card["member_id_system"], "value": card["member_id"], "assigner": {"display": card["payer"]["name"]}}]
    cov["status"] = "active"
    cov["type"] = card["type"]
    cov["subscriber"] = {"reference": patient_ref, "display": display_name(patient).title()}
    cov["subscriberId"] = card.get("subscriber_id", card["member_id"])
    cov["beneficiary"] = {"reference": patient_ref}
    cov["relationship"] = {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship", "code": "self", "display": "Self"}], "text": "Self"}
    cov["period"] = card["period"]
    cov["payor"] = [{"reference": payer_ref, "display": card["payer"]["name"]}]
    if card.get("order"):
        cov["order"] = card["order"]
    else:
        cov.pop("order", None)
    classes = []
    for key, system in [("group", CLASS_CS), ("plan", CLASS_CS), ("division", CLASS_EXT_CS), ("network", CLASS_EXT_CS),
                        ("rxbin", CLASS_CS), ("rxpcn", CLASS_CS), ("rxgroup", CLASS_CS), ("rxid", CLASS_CS)]:
        v = card.get("classes", {}).get(key)
        if v:
            c = {"type": {"coding": [{"system": system, "code": key}]}, "value": v["value"]}
            if v.get("name"):
                c["name"] = v["name"]
            classes.append(c)
    cov["class"] = classes
    if card.get("copays"):
        cov["costToBeneficiary"] = [copay(c) for c in card["copays"]]
    else:
        cov.pop("costToBeneficiary", None)
    cov.pop("dependent", None)
    return ordered(cov, ["resourceType", "id", "meta", "extension", "identifier", "status", "type", "subscriber", "subscriberId",
                         "beneficiary", "relationship", "period", "payor", "order", "class", "costToBeneficiary"])


def rename_references(entries, target, display):
    """Updates the display on every reference to the payer (claims name it as insurer)."""
    def walk(value):
        if isinstance(value, list):
            for v in value:
                walk(v)
        elif isinstance(value, dict):
            if value.get("reference") == target and "display" in value:
                value["display"] = display
            for v in value.values():
                walk(v)
    for e in entries:
        walk(e["resource"])


def qr_text(card, patient):
    lines = [card["payer"]["name"], f"Member: {display_name(patient)}", f"Member ID: {card['member_id']}"]
    cls = card.get("classes", {})
    if cls.get("group"):
        lines.append(f"Group: {cls['group']['value']}")
    if cls.get("plan"):
        lines.append(f"Plan: {cls['plan']['value']}")
    rx = [f"{k}: {cls[key]['value']}" for k, key in [("RxBIN", "rxbin"), ("RxPCN", "rxpcn"), ("RxGrp", "rxgroup")] if cls.get(key)]
    if rx:
        lines.append(" ".join(rx))
    lines.append(SAMPLE)
    return "\n".join(lines)


def apply(slug):
    folder = ROOT / "patients" / slug
    spec = json.loads((folder / "insurance-cards.json").read_text(encoding="utf-8"))
    bundle_path = folder / "bundle.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    entries = bundle["entry"]
    base = entries[0]["fullUrl"].rsplit("/", 2)[0]
    patient_entry = next(e for e in entries if e["resource"]["resourceType"] == "Patient")
    patient = patient_entry["resource"]
    with_profile(patient, f"{C4DIC}/C4DIC-Patient")
    patient_ref = f"Patient/{patient['id']}"
    out_dir = folder / "insurance-cards"
    out_dir.mkdir(exist_ok=True)

    def find(rtype, rid):
        return next((e for e in entries if e["resource"]["resourceType"] == rtype and e["resource"].get("id") == rid), None)

    def add_entry(rtype, rid, after_type):
        resource = {"resourceType": rtype, "id": rid, "meta": {"tag": [
            {"system": "http://terminology.hl7.org/CodeSystem/v3-ActReason", "code": "HTEST", "display": "test health data"}]}}
        entry = {"fullUrl": f"{base}/{rtype}/{rid}", "resource": resource}
        last = max((i for i, e in enumerate(entries) if e["resource"]["resourceType"] == after_type), default=len(entries) - 1)
        entries.insert(last + 1, entry)
        return entry

    for card in spec["cards"]:
        key = card["key"]
        cov_id = card.get("coverage_id") or str(uuid.uuid5(UUID_NS, f"{slug}/Coverage/{key}"))
        org_id = card.get("payer_id_ref") or str(uuid.uuid5(UUID_NS, f"{slug}/Organization/{key}-payer"))
        org_entry = find("Organization", org_id) or add_entry("Organization", org_id, "Organization")
        cov_entry = find("Coverage", cov_id) or add_entry("Coverage", cov_id, "Coverage")
        org_entry["resource"] = build_payer(org_entry["resource"], card)
        rename_references(entries, f"Organization/{org_id}", card["payer"]["name"])

        b = card["brand"]
        logo_bytes, logo = png_b64(logo_image(b))
        qr_img = qr(qr_text(card, patient))
        qr_bytes, qr64 = png_b64(qr_img, colors=2)
        bar_img = code128(card["member_id"].replace("-", ""))
        bar_bytes, bar64 = png_b64(bar_img, colors=2)
        front_bytes, front = png_b64(card_front(card, display_name(patient)))
        back_bytes, back = png_b64(card_back(card, bar_img, qr_img))
        for name, data in [("logo", logo_bytes), ("qr", qr_bytes), ("barcode", bar_bytes), ("front", front_bytes), ("back", back_bytes)]:
            (out_dir / f"{key}-{name}.png").write_bytes(data)
        images = {"logo": logo, "qr": qr64, "barcode": bar64, "front": front, "back": back}
        cov_entry["resource"] = build_coverage(cov_entry["resource"], card, patient, patient_ref, f"Organization/{org_id}", images)

    bundle_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{slug}: {len(spec['cards'])} cards written")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slugs", nargs="*")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    slugs = args.slugs
    if args.all:
        slugs = sorted(p.parent.name for p in (ROOT / "patients").glob("*/insurance-cards.json"))
    if not slugs:
        parser.error("name a patient folder, or use --all")
    for slug in slugs:
        apply(slug)


if __name__ == "__main__":
    main()
