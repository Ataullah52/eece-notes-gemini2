#!/usr/bin/env python3
"""
build_index.py — Rebuilds AI_INDEX.md from src/data/chapters/ and src/data/curriculumData.ts.
Usage: python3 build_index.py
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "src" / "data" / "curriculumData.ts"
CHAPTERS_DIR = ROOT / "src" / "data" / "chapters"
INDEX_FILE = ROOT / "AI_INDEX.md"


def parse_chapter_file(file_path: Path, default_prefix: str, idx: int) -> dict:
    text = file_path.read_text(encoding="utf-8")
    ch_id_match = re.search(r'["\']?id["\']?\s*:\s*["\']([^"\']+)["\']', text)
    unit_match = re.search(r'["\']?unitNumber["\']?\s*:\s*["\']([^"\']+)["\']', text)
    title_match = re.search(r'["\']?title["\']?\s*:\s*["\']([^"\']+)["\']', text)

    blocks_match = re.search(r'["\']?blocks["\']?\s*:\s*\[', text)
    blocks_text = text[blocks_match.start() :] if blocks_match else text
    block_ids = re.findall(r'["\']?id["\']?\s*:\s*["\']([^"\']+)["\']', blocks_text)

    return {
        "file": f"src/data/chapters/{file_path.parent.name}/{file_path.name}",
        "id": ch_id_match.group(1) if ch_id_match else file_path.stem,
        "unit": unit_match.group(1) if unit_match else f"{default_prefix} {idx:02d}",
        "title": title_match.group(1) if title_match else file_path.stem,
        "block_count": len(block_ids),
    }


def collect_course_chapters(course_folder: str, default_prefix: str) -> list[dict]:
    folder = CHAPTERS_DIR / course_folder
    if not folder.exists():
        return []
    chapters = []
    ts_files = sorted(folder.glob("*.ts"))
    for idx, ts_file in enumerate(ts_files, start=1):
        chapters.append(parse_chapter_file(ts_file, default_prefix, idx))
    return chapters


def main() -> None:
    if not DATA_FILE.exists():
        print(f"Curriculum file not found: {DATA_FILE}")
        return

    eece_chapters = collect_course_chapters("eece1111", "Module")
    phy_chapters = collect_course_chapters("phy1101", "Module")
    ce_chapters = collect_course_chapters("ce1101", "Experiment")
    math_chapters = collect_course_chapters("math1101", "Module")
    chem_chapters = collect_course_chapters("chem1101", "Module")

    eece_total = sum(c["block_count"] for c in eece_chapters)
    phy_total = sum(c["block_count"] for c in phy_chapters)
    ce_total = sum(c["block_count"] for c in ce_chapters)
    math_total = sum(c["block_count"] for c in math_chapters)
    chem_total = sum(c["block_count"] for c in chem_chapters)

    lines = [
        "# EECE Notes Curriculum Index (`AI_INDEX.md`)",
        "",
        "> **Navigation Map for Authoring**",
        "> Generated automatically by `python3 build_index.py` from `src/data/chapters/` and `src/data/curriculumData.ts`.",
        "",
        "---",
        "",
        "## `EECE11` · 1st Year · 1st Semester (18.75 Total Credits)",
        "",
        "| Sl. | Course Code | Course Title | Type | Contact Hrs/Wk | Credits | Populated Chapter Units | Total Blocks |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        f"| 1 | **`EECE1111`** | Electrical Circuits I | Theory | 3.00 | 3.00 | `Module 01` – `Module 06` ({len(eece_chapters)} modules) | {eece_total} blocks |",
        "| 2 | **`EECE1112`** | Electrical Circuits I Sessional | Sessional | 3.00 | 1.50 | `Module 01` (1 module) | 0 blocks |",
        f"| 3 | **`PHY1101`** | Physics | Theory | 3.00 | 3.00 | `Module 01` – `Module 07` ({len(phy_chapters)} modules) | {phy_total} blocks |",
        f"| 4 | **`CE1101`** | Engineering Graphics | Sessional | 3.00 | 1.50 | `Experiment 01` – `Practical Exam Guide` ({len(ce_chapters)} units) | {ce_total} blocks |",
        "| 5 | **`HUM1101`** | English | Theory | 3.00 | 3.00 | `Module 01` – `Module 08` (8 modules) | 0 blocks |",
        f"| 6 | **`MATH1101`** | Differential Calculus and Analytical Geometry | Theory | 3.00 | 3.00 | `Module 01` – `Module 08` ({len(math_chapters)} modules) | {math_total} blocks |",
        f"| 7 | **`CHEM1101`** | Physical and Inorganic Chemistry | Theory | 3.00 | 3.00 | `Module 01` – `Module 09` ({len(chem_chapters)} modules) | {chem_total} blocks |",
        "| 8 | **`EECE1100`** | Viva-voce | Sessional | — | 0.75 | `Module 01` (1 module) | 0 blocks |",
    ]

    course_sections = [
        ("EECE1111", "Electrical Circuits I", eece_chapters, eece_total),
        ("PHY1101", "Physics", phy_chapters, phy_total),
        ("CE1101", "Engineering Graphics", ce_chapters, ce_total),
        ("MATH1101", "Differential Calculus and Analytical Geometry", math_chapters, math_total),
        ("CHEM1101", "Physical and Inorganic Chemistry", chem_chapters, chem_total),
    ]

    for code, title, chapters, total in course_sections:
        lines.extend(
            [
                "",
                "---",
                "",
                f"## `{code}` · {title} ({len(chapters)} Units — {total} Blocks)",
                "",
                "| Unit | Chapter ID | Title | Source File | Block Count |",
                "| :--- | :--- | :--- | :--- | :--- |",
            ]
        )
        for ch in chapters:
            lines.append(
                f"| `{ch['unit']}` | `{ch['id']}` | {ch['title']} | `{ch['file']}` | {ch['block_count']} |"
            )

    lines.extend(
        [
            "",
            "---",
            "",
            "## `EECE12` – `EECE42` · Remaining Semesters",
            "",
            "- **`EECE12`** (1st Year · 2nd Semester): *Empty (No courses added yet)*",
            "- **`EECE21`** (2nd Year · 1st Semester): *Empty (No courses added yet)*",
            "- **`EECE22`** (2nd Year · 2nd Semester): *Empty (No courses added yet)*",
            "- **`EECE31`** (3rd Year · 1st Semester): *Empty (No courses added yet)*",
            "- **`EECE32`** (3rd Year · 2nd Semester): *Empty (No courses added yet)*",
            "- **`EECE41`** (4th Year · 1st Semester): *Empty (No courses added yet)*",
            "- **`EECE42`** (4th Year · 2nd Semester): *Empty (No courses added yet)*",
            "",
        ]
    )

    INDEX_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"Generated {INDEX_FILE.name}: "
        f"EECE1111 ({len(eece_chapters)} units, {eece_total} blocks), "
        f"PHY1101 ({len(phy_chapters)} units, {phy_total} blocks), "
        f"CE1101 ({len(ce_chapters)} units, {ce_total} blocks), "
        f"MATH1101 ({len(math_chapters)} units, {math_total} blocks), "
        f"CHEM1101 ({len(chem_chapters)} units, {chem_total} blocks)."
    )


if __name__ == "__main__":
    main()
