#!/usr/bin/env python3

from __future__ import annotations

import csv
import html
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "semesters" / "FA25" / "raw"
OUT = ROOT / "data" / "semesters" / "FA25"
LEGACY = ROOT.parent / "253 - Fall 2025" / "FA25"


PROJECTS_CSV = RAW / "projects.csv"
JUDGES_CSV = RAW / "judges.csv"
JUDGE_ASSIGNMENTS_XLSX = RAW / "Projects-Assigned-to-Judges-2.xlsx"
CAP1_ASSIGNMENTS_XLSX = RAW / "Projects-Assigned-to-CapstoneI.xlsx"
CAP1_TEAMS_XLSX = RAW / "Fall 2025 - Cap 1.xlsx"


FINAL_TITLE_KEY = (
    "Final Project Title (Carefully type the final project name here; in case your project "
    "name has been refined, use the final name that you guys have agreed upon; in case your "
    "project name has not changed from what mentioned above, retype the name the way you want "
    "it to be shown at the showcase)"
)


def slugify(text: str) -> str:
    text = html.unescape(text).strip().lower()
    text = text.replace("&", " and ")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def clean_text(text: str) -> str:
    text = html.unescape(text or "")
    text = text.replace("\u200b", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_display_name(text: str) -> str:
    text = clean_text(text)
    if not text:
        return text

    parts = [part.strip() for part in text.split(",")]
    parts = [part for part in parts if part]

    def fix_case(value: str) -> str:
        if value == value.lower() or value == value.upper():
            return " ".join(segment.capitalize() for segment in value.split())
        return value

    parts = [fix_case(part) for part in parts]
    return ", ".join(parts)


def split_people(text: str) -> list[str]:
    text = clean_text(text)
    if not text:
      return []
    parts = re.split(r"\s*[;,]\s*", text)
    return [p.strip() for p in parts if p.strip()]


def extract_youtube_url(value: str) -> str | None:
    value = (value or "").strip()
    if not value:
        return None
    match = re.search(r'src="([^"]+)"', value)
    if match:
        return match.group(1)
    match = re.search(r"(https?://[^\s<>\"']+)", value)
    return match.group(1) if match else None


def read_projects() -> list[dict]:
    with PROJECTS_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    projects_by_slug: OrderedDict[str, dict] = OrderedDict()

    for row in rows:
        original_title = clean_text(row.get("Project Title", ""))
        final_title = clean_text(row.get(FINAL_TITLE_KEY, "")) or original_title
        degree_program = original_title.split(":", 1)[0].strip() if ":" in original_title else "Capstone"
        slug = slugify(final_title)
        project = {
            "id": slug,
            "title": final_title,
            "slug": slug,
            "legacyTitle": original_title,
            "degreeProgram": degree_program,
            "shortDescription": clean_text(row.get("Project Short Description", "")),
            "teamMembers": split_people(row.get("Capstone II Team Members (Only include those students who actually contributed to the project; those note listed will receive an incomplete)", "")),
            "productOwners": split_people(row.get("Product Owners and Mentors", "")),
            "posterUrl": clean_text(row.get("Poster (link to a publicly available pdf file that include the latest version of the poster)", "")),
            "documentationUrl": clean_text(row.get("Project Documentation (link to a publicly available pdf file that include your latest version of your project documentation)", "")),
            "slidesUrl": clean_text(row.get("Project Presentation Slides (link to a publicly available pdf file that include your latest version of your project presentation slides)", "")),
            "introVideoUrl": extract_youtube_url(row.get("Introduction Video\n\nYou publish your vide on YouTube, make it publicly available, and then you must click on Share, and then choose Embedded. You will get a sting like this: \n\n<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/6-7mG95eNvs\" title=\"YouTube video player\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>", "")),
            "demoVideoUrl": extract_youtube_url(row.get("Demo Video \n\nUse the same instructions as indicated for the Introduction video above.", "")),
        }
        projects_by_slug[slug] = project

    return list(projects_by_slug.values())


def read_judges() -> list[dict]:
    with JUDGES_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    judges: OrderedDict[str, dict] = OrderedDict()
    for row in rows:
        name = normalize_display_name(
            f"{clean_text(row.get('Last Name', ''))}, {clean_text(row.get('First Name', ''))}"
        ).strip(", ")
        key = name.lower()
        if key in judges:
            continue
        judges[key] = {
            "name": name,
            "email": clean_text(row.get("Email Address", "")),
            "jobTitle": clean_text(row.get("Job Title", "")),
            "highestDegree": clean_text(row.get("Highest Academic Degree", "")),
            "company": clean_text(row.get("Company Name (FIU or the name of your company)", "")),
            "slots": [],
        }
    return list(judges.values())


XML_NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def xlsx_col_to_index(col: str) -> int:
    value = 0
    for ch in col:
        if ch.isalpha():
            value = value * 26 + (ord(ch.upper()) - 64)
    return value - 1


def read_xlsx_rows(path: Path, sheet_name: str = "Form Responses 1") -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as zf:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            shared = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in shared.findall("a:si", XML_NS):
                shared_strings.append("".join(node.text or "" for node in si.iterfind(".//a:t", XML_NS)))

        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}

        target = None
        for sheet in workbook.find("a:sheets", XML_NS):
            if sheet.attrib.get("name") == sheet_name:
                target = rel_map[sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]]
                break
        if not target:
            raise RuntimeError(f"Missing sheet {sheet_name} in {path}")

        root = ET.fromstring(zf.read("xl/" + target))
        rows = []
        headers: list[str] | None = None

        for row in root.findall(".//a:sheetData/a:row", XML_NS):
            values: dict[int, str] = {}
            for cell in row.findall("a:c", XML_NS):
                ref = cell.attrib.get("r", "")
                idx = xlsx_col_to_index("".join(ch for ch in ref if ch.isalpha()))
                cell_type = cell.attrib.get("t")
                val_node = cell.find("a:v", XML_NS)
                value = "" if val_node is None or val_node.text is None else val_node.text
                if cell_type == "s" and value != "":
                    value = shared_strings[int(value)]
                elif cell_type == "inlineStr":
                    value = "".join(node.text or "" for node in cell.iterfind(".//a:t", XML_NS))
                values[idx] = clean_text(value)

            row_values = [values.get(i, "") for i in range(max(values.keys(), default=-1) + 1)]
            if headers is None:
                headers = row_values
                continue
            padded = row_values + [""] * (len(headers) - len(row_values))
            rows.append(dict(zip(headers, padded)))

        return rows


def parse_assignment_rows(path: Path) -> OrderedDict[str, list[dict]]:
    assignments: OrderedDict[str, list[dict]] = OrderedDict()
    for row in read_xlsx_rows(path):
        name = normalize_display_name(row.get("Name", ""))
        if not name:
            continue
        slots = assignments.setdefault(name, [])
        for label in ["First", "Second", "Third"]:
            session = clean_text(row.get(f"{label} Session", ""))
            project_title = clean_text(row.get(f"{label} Project", ""))
            if not session and not project_title:
                continue
            slot_time = {
                "First": "2:00 to 2:30 pm",
                "Second": "2:30 to 3:00 pm",
                "Third": "3:00 to 3:30 pm",
            }[label]
            degree_program, _, session_project = session.partition(": ")
            slot = {
                "time": slot_time,
                "projectSlug": slugify(project_title or session_project),
                "projectTitle": project_title or clean_text(session_project),
                "degreeProgram": clean_text(degree_program),
            }
            if slot not in slots:
                slots.append(slot)
    return assignments


def read_cap1_team_name_map() -> dict[str, str]:
    name_map = {}
    for row in read_xlsx_rows(CAP1_TEAMS_XLSX, sheet_name="Teams"):
        email = clean_text(row.get("Email", "")).lower()
        name = normalize_display_name(row.get("Name", ""))
        if email and name:
            name_map[email] = name
    return name_map


def read_capstone1_assignments() -> list[dict]:
    assignments = parse_assignment_rows(CAP1_ASSIGNMENTS_XLSX)
    email_map = read_cap1_team_name_map()
    students = []
    for name, slots in assignments.items():
        display_name = email_map.get(name.lower(), name) if "@" in name else name
        students.append({"name": display_name, "slots": slots})
    return students


def merge_judge_assignments(judges: list[dict]) -> list[dict]:
    assignments = parse_assignment_rows(JUDGE_ASSIGNMENTS_XLSX)
    by_key = OrderedDict((judge["name"].lower(), judge) for judge in judges)

    for name, slots in assignments.items():
        key = name.lower()
        if key not in by_key:
            by_key[key] = {
                "name": name,
                "email": "",
                "jobTitle": "",
                "highestDegree": "",
                "company": "",
                "slots": [],
            }
        existing = by_key[key]["slots"]
        for slot in slots:
            if slot not in existing:
                existing.append(slot)

    result = [judge for judge in by_key.values() if judge["name"].lower() != "example, test"]
    result.sort(key=lambda item: item["name"].lower())
    return result


def write_json(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    projects = read_projects()
    judges = merge_judge_assignments(read_judges())
    capstone1 = read_capstone1_assignments()

    semester = {
        "code": "FA25",
        "title": "Fall 2025 Capstone Showcase",
        "season": "Fall",
        "year": 2025,
        "eventMode": "in-person",
        "notes": "Imported from the Fall 2025 Google Sheets submissions, local semester spreadsheets, and the previously published FA25 assignment pages.",
    }

    content_semester = {
        "code": "FA25",
        "season": "Fall",
        "year": 2025,
        "title": "Fall 2025 Capstone Showcase",
        "eventMode": "in-person",
        "assignmentsPublic": True,
        "judgesPublic": True,
        "stats": {
            "projects": len(projects),
            "judges": len(judges),
            "capstone1Students": len(capstone1),
        },
        "notes": semester["notes"],
        "featuredProjects": [project["slug"] for project in projects[:6]],
    }

    write_json("semester.json", semester)
    write_json("projects.json", projects)
    write_json("judges.json", judges)
    write_json("capstone1.json", capstone1)
    (ROOT / "src" / "content" / "semesters" / "FA25.json").write_text(
        json.dumps(content_semester, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Imported FA25: {len(projects)} projects, {len(judges)} judges, {len(capstone1)} Capstone I students")


if __name__ == "__main__":
    main()
