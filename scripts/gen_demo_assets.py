"""Regenerate demo assets (PDFs, images, voice notes) from the fixture CSVs.

Outputs to data/raw/{manuals,images,voice}/. Run after cloning or after updating fixtures.
Usage: python scripts/gen_demo_assets.py
"""
from __future__ import annotations

import csv
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "data" / "fixtures"
RAW = ROOT / "data" / "raw"
MANUALS = RAW / "manuals"
IMAGES = RAW / "images"
VOICE = RAW / "voice"


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ensure_dirs() -> None:
    for d in (MANUALS, IMAGES, VOICE):
        d.mkdir(parents=True, exist_ok=True)


def copy_csvs_to_raw() -> None:
    for name in ("incidents.csv", "parts.csv", "error_codes.csv"):
        shutil.copyfile(FIXTURES / name, RAW / name)


# ----------------------------- PDF manuals -----------------------------


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontSize=22, spaceAfter=18
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontSize=15, spaceBefore=14, spaceAfter=8
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=6
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontSize=10, leading=14, spaceAfter=6
        ),
        "mono": ParagraphStyle(
            "mono",
            parent=base["Code"],
            fontName="Courier",
            fontSize=9,
            leading=12,
            spaceAfter=6,
        ),
    }


def _table(rows: list[list[str]], col_widths: list[float]) -> Table:
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


SAFETY_NOTES = {
    "Conveyor": (
        "Lock out and tag out the main disconnect before working on drive components. "
        "Belt tension exceeds 2 kN under operating load — release tension from the take-up "
        "assembly before removing guards. Never bypass photo eyes or pull-cord safeties; "
        "the system is designed to stop on loss of either signal."
    ),
    "Compressor": (
        "Always depressurize the receiver tank to 0 bar and verify with the drain valve "
        "before opening any pressurized line. Oil reservoir reaches 90 C during normal "
        "operation — allow 30 minutes of cool-down before draining. Use only ISO VG 46 oil "
        "or equivalent synthetic rated for rotary-screw service."
    ),
    "Pump": (
        "Verify suction and discharge valves are closed and the casing is drained before "
        "removing the stuffing box or seal flush lines. Product contamination risk if the "
        "mechanical seal fails — always wear chemical-resistant gloves and eye protection "
        "during seal service. Re-prime the pump before returning to service."
    ),
}


MAINTENANCE_SCHEDULES = {
    "Conveyor": [
        ["Interval", "Task", "Reference"],
        ["Daily", "Visual belt check and debris clear at tail pulley", "sec. 2.1"],
        ["Weekly", "Drive motor amp draw log and thermography spot check", "sec. 2.2"],
        ["Monthly", "Belt tension measurement and drive coupling alignment", "sec. 3.1"],
        ["Quarterly", "Gearbox oil sample, breather cap inspection, bearing grease", "sec. 3.2"],
        ["Annually", "Full gearbox oil change (ISO VG 220), motor insulation test", "sec. 4.0"],
    ],
    "Compressor": [
        ["Interval", "Task", "Reference"],
        ["Daily", "Check oil level, drain condensate, record discharge pressure", "sec. 2.1"],
        ["Weekly", "Inspect intake filter differential pressure, belt tension", "sec. 2.2"],
        ["500 hr", "Change oil filter, verify pressure switch differential", "sec. 3.1"],
        ["2000 hr", "Full oil change, air-end inspection, valve function test", "sec. 3.2"],
        ["8000 hr", "Overhaul unloader assembly, replace intake filter element", "sec. 4.0"],
    ],
    "Pump": [
        ["Interval", "Task", "Reference"],
        ["Daily", "Check seal flush flow, discharge pressure, vibration level", "sec. 2.1"],
        ["Weekly", "Verify alignment, bearing temperature log, leak inspection", "sec. 2.2"],
        ["Monthly", "Vibration signature capture, NPSH margin verification", "sec. 3.1"],
        ["Annually", "Mechanical seal inspection, wear ring clearance check", "sec. 3.2"],
        ["3 years", "Full casing open-up, impeller balance, bearing replacement", "sec. 4.0"],
    ],
}


def build_manual(
    out: Path,
    machine_type: str,
    model_no: str,
    error_codes: list[dict],
    parts: list[dict],
    incidents: list[dict],
) -> None:
    styles = _styles()
    doc = SimpleDocTemplate(
        str(out),
        pagesize=LETTER,
        leftMargin=0.8 * inch,
        rightMargin=0.8 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        title=f"{machine_type} {model_no} Service Manual",
    )
    story: list = []

    story.append(Paragraph(f"{machine_type} Service Manual", styles["title"]))
    story.append(Paragraph(f"Model {model_no}", styles["h1"]))
    story.append(
        Paragraph(
            f"Document revision 4.2 — issued for plant maintenance crews servicing "
            f"{machine_type.lower()} equipment in the {model_no} product family. This "
            f"manual supersedes revision 4.1 and incorporates field-reported issues "
            f"through the most recent service bulletin cycle.",
            styles["body"],
        )
    )
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("Section 1 — Safety", styles["h1"]))
    story.append(Paragraph(SAFETY_NOTES[machine_type], styles["body"]))

    story.append(PageBreak())
    story.append(Paragraph("Section 2 — Routine Maintenance", styles["h1"]))
    story.append(
        Paragraph(
            "Follow the schedule below to keep the unit within warranty and to minimize "
            "unplanned downtime. Log each completed task in the CMMS with the technician "
            "ID and the measured values listed under the referenced section.",
            styles["body"],
        )
    )
    story.append(Spacer(1, 0.15 * inch))
    story.append(_table(MAINTENANCE_SCHEDULES[machine_type], [80, 280, 80]))

    story.append(PageBreak())
    story.append(Paragraph("Section 3 — Fault Codes and Response", styles["h1"]))
    story.append(
        Paragraph(
            "Each fault code below raises an alarm on the HMI and writes a time-stamped "
            "entry to the event log. Acknowledge the alarm, isolate power where required, "
            "and follow the response procedure. Record the resolution in the incident "
            "tracker so the retrieval model can surface it for future events.",
            styles["body"],
        )
    )

    for ec in error_codes:
        story.append(Spacer(1, 0.15 * inch))
        story.append(
            Paragraph(
                f"{ec['fault_code']} — {ec['description'].split(' - ')[0]}",
                styles["h2"],
            )
        )
        detail = ec["description"].split(" - ", 1)
        if len(detail) == 2:
            story.append(Paragraph(f"<b>Detail:</b> {detail[1]}", styles["body"]))
        related_incidents = [i for i in incidents if i["fault_code"] == ec["fault_code"]]
        if related_incidents:
            sample = related_incidents[0]
            story.append(
                Paragraph(
                    f"<b>Typical symptom:</b> {sample['symptom']}", styles["body"]
                )
            )
            story.append(
                Paragraph(
                    f"<b>Response:</b> {sample['fix_applied']}", styles["body"]
                )
            )
            if sample.get("parts_used"):
                story.append(
                    Paragraph(
                        f"<b>Parts typically consumed:</b> {sample['parts_used']}",
                        styles["body"],
                    )
                )
            dt = sample.get("downtime_min")
            if dt:
                story.append(
                    Paragraph(
                        f"<b>Typical downtime:</b> approximately {dt} minutes when "
                        f"parts are on hand.",
                        styles["body"],
                    )
                )

    story.append(PageBreak())
    story.append(Paragraph("Section 4 — Spare Parts Catalog", styles["h1"]))
    story.append(
        Paragraph(
            "Parts listed below are stocked for this model at the central warehouse. "
            "Lead time for non-stocked items is 10 to 14 business days. Verify the model "
            "number on the equipment nameplate before ordering.",
            styles["body"],
        )
    )
    story.append(Spacer(1, 0.15 * inch))
    parts_rows: list[list[str]] = [["Part Number", "Description"]]
    for p in parts:
        parts_rows.append([p["part_no"], p["name"]])
    story.append(_table(parts_rows, [140, 300]))

    story.append(PageBreak())
    story.append(Paragraph("Section 5 — Torque and Clearance Reference", styles["h1"]))
    ref_rows = [
        ["Fastener", "Torque (Nm)", "Thread"],
        ["Motor mount bolt M12", "85", "lubricated"],
        ["Coupling hub grub screw M8", "22", "dry"],
        ["Gearbox drain plug M16", "45", "with sealant"],
        ["Bearing housing cap M10", "40", "lubricated"],
        ["Pressure switch mount M6", "9", "dry"],
    ]
    story.append(_table(ref_rows, [220, 100, 100]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "Clearances: impeller to wear ring 0.3 to 0.5 mm radial; belt deflection at "
            "midspan 8 to 12 mm under 5 kgf load; gearbox backlash 0.08 to 0.12 mm at "
            "output shaft. Values outside these ranges require disassembly and component "
            "renewal per Section 3.",
            styles["body"],
        )
    )

    doc.build(story)


def gen_manuals(
    incidents: list[dict], parts: list[dict], error_codes: list[dict]
) -> None:
    incidents_by_machine: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for inc in incidents:
        incidents_by_machine[(inc["machine_type"], inc["model_no"])].append(inc)
    parts_by_machine: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for p in parts:
        parts_by_machine[(p["machine_type"], p["model_no"])].append(p)
    ec_by_type: dict[str, list[dict]] = defaultdict(list)
    for ec in error_codes:
        ec_by_type[ec["machine_type"]].append(ec)

    targets = [("Conveyor", "CX-200"), ("Compressor", "AX-75"), ("Pump", "VP-40")]
    for mt, model in targets:
        out = MANUALS / f"{mt.lower()}_{model.replace('-', '_')}_service_manual.pdf"
        build_manual(
            out,
            mt,
            model,
            ec_by_type[mt],
            parts_by_machine[(mt, model)],
            incidents_by_machine[(mt, model)],
        )
        print(f"wrote {out.relative_to(ROOT)}")


# ----------------------------- Schematic images -----------------------------


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _schematic(
    out: Path,
    title: str,
    machine: str,
    fault_code: str,
    severity: str,
    part_no: str,
    part_name: str,
    annotations: list[str],
) -> None:
    W, H = 1024, 768
    img = Image.new("RGB", (W, H), "#0b1220")
    d = ImageDraw.Draw(img)

    d.rectangle((0, 0, W, 64), fill="#1e293b")
    d.text((24, 18), title, fill="#f8fafc", font=_font(22))

    d.text((24, 88), f"Machine: {machine}", fill="#93c5fd", font=_font(18))
    d.text((24, 116), f"Fault code: {fault_code}", fill="#fca5a5", font=_font(18))
    d.text((24, 144), f"Severity: {severity}", fill="#fde68a", font=_font(18))
    d.text((24, 172), f"Part: {part_no} — {part_name}", fill="#a7f3d0", font=_font(18))

    cx, cy = W // 2 + 60, H // 2 + 40
    d.rectangle((cx - 180, cy - 120, cx + 180, cy + 120), outline="#64748b", width=3)
    d.text((cx - 60, cy - 150), "component", fill="#cbd5e1", font=_font(14))
    d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), outline="#38bdf8", width=3)
    d.line((cx - 180, cy, cx - 40, cy), fill="#64748b", width=2)
    d.line((cx + 40, cy, cx + 180, cy), fill="#64748b", width=2)
    d.line((cx, cy - 120, cx, cy - 40), fill="#64748b", width=2)
    d.line((cx, cy + 40, cx, cy + 120), fill="#64748b", width=2)

    d.text((cx - 220, cy - 140), "IN", fill="#f8fafc", font=_font(12))
    d.text((cx + 190, cy - 6), "OUT", fill="#f8fafc", font=_font(12))
    d.text((cx - 10, cy - 138), "SENSE", fill="#f8fafc", font=_font(12))
    d.text((cx - 18, cy + 124), "DRAIN", fill="#f8fafc", font=_font(12))

    y = 220
    d.text((24, y), "Notes:", fill="#f8fafc", font=_font(16))
    y += 28
    for a in annotations:
        d.text((36, y), f"- {a}", fill="#cbd5e1", font=_font(13))
        y += 22

    d.text((24, H - 30), "FixFirst Edge — schematic reference", fill="#475569", font=_font(11))
    img.save(out, "PNG")


def gen_images(incidents: list[dict], parts: list[dict]) -> None:
    parts_by_no = {p["part_no"]: p for p in parts}
    picks = [
        ("inc-001", "Drive motor overload trip"),
        ("inc-003", "Mechanical seal leak path"),
        ("inc-008", "Unloader valve solenoid"),
        ("inc-007", "Gearbox output seal"),
        ("inc-013", "Drive motor winding failure"),
        ("inc-025", "Impeller wear ring clearance"),
    ]
    inc_by_id = {i["id"]: i for i in incidents}
    annotations_lib = {
        "inc-001": [
            "Thermal relay trips when sustained current exceeds 115 percent of nameplate.",
            "Check motor mount torque; vibration can accelerate insulation fatigue.",
            "Re-torque to 85 Nm after 4 hour run-in.",
        ],
        "inc-003": [
            "Seal faces lapped to 0.5 He light band flatness.",
            "Flush port pressure must be 0.5 bar above stuffing box.",
            "Replace both primary and secondary elastomers as a set.",
        ],
        "inc-008": [
            "Solenoid coil resistance 24 to 28 ohms cold.",
            "Cycle time must be under 400 ms at rated pressure.",
            "Verify cutoff at 8.5 bar and restart at 7.2 bar.",
        ],
        "inc-007": [
            "Output seal lip direction must face oil side (outward garter spring).",
            "Refill with ISO VG 220 to sight glass mid-mark.",
            "Replace breather cap simultaneously to relieve internal pressure.",
        ],
        "inc-013": [
            "Full motor swap preferred; original scheduled for rewind.",
            "Insulation resistance must read over 5 M-ohm phase to ground before return.",
            "Log serial number and hours on spare unit for tracking.",
        ],
        "inc-025": [
            "Wear ring radial clearance 0.30 to 0.50 mm when new.",
            "Field-balance impeller to below 2.5 mm/s RMS at bearing housing.",
            "Inspect casing hydraulic-shock contact surface before reinstall.",
        ],
    }
    for idx, (inc_id, title) in enumerate(picks, start=1):
        inc = inc_by_id.get(inc_id)
        if not inc:
            continue
        part_no = inc.get("parts_used", "") or ""
        part_no = part_no.split(",")[0].strip() if part_no else ""
        part = parts_by_no.get(part_no, {})
        out = (
            IMAGES
            / f"schematic_{idx:02d}_{inc['machine_type'].lower()}_{inc['fault_code']}.png"
        )
        _schematic(
            out,
            title,
            f"{inc['machine_type']} {inc['model_no']}",
            inc["fault_code"],
            inc["severity"],
            part_no or "-",
            part.get("name", "-"),
            annotations_lib.get(inc_id, ["See service manual for detail."]),
        )
        print(f"wrote {out.relative_to(ROOT)}")


# ----------------------------- Voice notes -----------------------------


def gen_voice() -> None:
    notes = [
        (
            "voice_01_conveyor_e04.wav",
            "This is maintenance tech on conveyor CX 200. We have an E 04 fault — "
            "motor overload alarm. Drive motor tripped after three hours continuous "
            "running. Checking thermal overload relay and motor mounts now.",
        ),
        (
            "voice_02_pump_seal_leak.wav",
            "Pump VP 40 has a seal leak. Fluid pooling under the housing. Looks like "
            "the mechanical seal assembly failed. Marking severity critical and "
            "isolating the pump.",
        ),
        (
            "voice_03_compressor_pressure.wav",
            "Compressor AX 75 is showing P 21 — pressure regulation fault. Downstream "
            "pressure is dropping below six bar with an audible knock. Going to check "
            "the intake filter and pressure regulator.",
        ),
        (
            "voice_04_gearbox_leak.wav",
            "Conveyor CX 300 — gearbox output seal is leaking. E 08 alarm is active. "
            "Drive response is sluggish. Need gearbox output seal GS 300 O from stores.",
        ),
        (
            "voice_05_vibration.wav",
            "Pump VP 40 vibration alarm. V 07 fault code. Bearing housing is reading "
            "over seven millimeters per second RMS. Need to rebalance the impeller "
            "and swap the bearing set.",
        ),
    ]

    if shutil.which("espeak-ng"):
        for name, text in notes:
            out = VOICE / name
            subprocess.run(["espeak-ng", "-w", str(out), text], check=True)
            print(f"wrote data/raw/voice/{name}")
        return

    try:
        import pyttsx3
    except ImportError:
        print("espeak-ng and pyttsx3 missing — skipping voice generation")
        return

    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    engine.setProperty("volume", 1.0)
    voices = engine.getProperty("voices")
    if voices:
        engine.setProperty("voice", voices[0].id)
    for name, text in notes:
        out = VOICE / name
        engine.save_to_file(text, str(out))
    engine.runAndWait()
    for name, _ in notes:
        print(f"wrote data/raw/voice/{name}")


# ----------------------------- Entry point -----------------------------


def main() -> None:
    ensure_dirs()
    copy_csvs_to_raw()
    incidents = load_csv(FIXTURES / "incidents.csv")
    parts = load_csv(FIXTURES / "parts.csv")
    error_codes = load_csv(FIXTURES / "error_codes.csv")
    gen_manuals(incidents, parts, error_codes)
    gen_images(incidents, parts)
    gen_voice()
    print("done")


if __name__ == "__main__":
    main()
