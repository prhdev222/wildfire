#!/usr/bin/env python3
"""Clean wildfire project data with only the Python standard library."""

from __future__ import annotations

import csv
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

MENTAL_FIELDS = [
    "dementia",
    "alcoholism",
    "amphetamine",
    "addict_substance",
    "schizophrenia",
    "other_phy",
    "bipolar",
    "depression",
    "anxiety",
    "low_iq",
    "learning_disorder",
    "autistics",
    "adhd",
    "suicide",
    "game_adult",
    "game_child",
    "other_disease",
    "seizure",
]


def col_index(cell_ref: str) -> int:
    n = 0
    for ch in re.match(r"([A-Z]+)", cell_ref).group(1):
        n = n * 26 + ord(ch) - 64
    return n - 1


def xlsx_sheets(path: Path) -> dict[str, list[list[str]]]:
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", NS):
                shared.append("".join(t.text or "" for t in si.findall(".//a:t", NS)))

        workbook = ET.fromstring(z.read("xl/workbook.xml"))
        rel_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rels = {
            r.attrib["Id"]: r.attrib["Target"]
            for r in rel_root.findall("rel:Relationship", NS)
        }

        sheets = {}
        for sheet in workbook.findall(".//a:sheet", NS):
            rid = sheet.attrib[f"{{{NS['r']}}}id"]
            target = rels[rid]
            if not target.startswith("xl/"):
                target = "xl/" + target
            rows = []
            root = ET.fromstring(z.read(target))
            for row in root.findall(".//a:sheetData/a:row", NS):
                values = []
                for cell in row.findall("a:c", NS):
                    idx = col_index(cell.attrib["r"])
                    while len(values) <= idx:
                        values.append("")
                    cell_type = cell.attrib.get("t")
                    value_node = cell.find("a:v", NS)
                    if cell_type == "s" and value_node is not None:
                        value = shared[int(value_node.text)]
                    elif cell_type == "inlineStr":
                        value = "".join(t.text or "" for t in cell.findall(".//a:t", NS))
                    elif value_node is not None:
                        value = value_node.text or ""
                    else:
                        value = ""
                    values[idx] = value.strip() if isinstance(value, str) else value
                rows.append(values)
            sheets[sheet.attrib["name"]] = rows
        return sheets


def table(rows: list[list[str]]) -> list[dict[str, str]]:
    header = [h.strip() for h in rows[0]]
    out = []
    for row in rows[1:]:
        row = row + [""] * (len(header) - len(row))
        out.append(dict(zip(header, row[: len(header)])))
    return out


def number(value: object) -> float | None:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def year(value: object) -> int | None:
    n = number(value)
    if n is None:
        return None
    y = int(n)
    return y - 543 if y > 2400 else y


def norm_en(value: str) -> str:
    value = value.upper().replace("CHANGWAT ", "").replace("PROVINCE", "")
    value = re.sub(r"[^A-Z]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def load_description() -> list[dict[str, str]]:
    rows = table(xlsx_sheets(ROOT / "Dataset_description.xlsx")["Sheet1"])
    current_file = ""
    current_table = ""
    out = []
    for row in rows:
        current_file = row["File"] or current_file
        current_table = row["Table_name"] or current_table
        if not row["Features"]:
            continue
        out.append(
            {
                "file": current_file,
                "table_name": current_table,
                "field": row["Features"],
                "description": row["Description"],
            }
        )
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    health_rows = table(xlsx_sheets(ROOT / "health_region.xlsx")["Sheet1"])
    health_by_key = {}
    en_to_th = {}
    for row in health_rows:
        y = year(row["year_c"])
        province = row["province"]
        health_by_key[(province, y)] = {
            "province": province,
            "province_en": row["province_en"].title(),
            "health_region": str(int(number(row["health_region"]) or 0)),
            "population": number(row["pop"]),
        }
        en_to_th[norm_en(row["province_en"])] = province

    records = {}
    for key, value in health_by_key.items():
        province, y = key
        records[key] = {"province": province, "year": y, **value}

    psych_rows = table(xlsx_sheets(ROOT / "Psychi_cases.xlsx")["Final"])
    for row in psych_rows:
        key = (row["province"], year(row["year_c"]))
        rec = records.setdefault(key, {"province": row["province"], "year": key[1]})
        rec.update(
            {
                "province_en": row["province_en"].title(),
                "health_region": str(int(number(row["health_region"]) or 0)),
                "population": number(row["pop"]),
            }
        )
        for field in MENTAL_FIELDS:
            rec[field] = number(row.get(field))

    fire_rows = table(xlsx_sheets(ROOT / "Fire_area_prep_province.xlsx")["Sheet1"])
    for row in fire_rows:
        key = (row["province"], year(row["year"]))
        rec = records.setdefault(key, {"province": row["province"], "year": key[1]})
        rec["number_of_wildfire"] = number(row["number_of_wildfire"])
        rec["wildfire_area_rai"] = number(row["total_area"])
        rec["wildfire_area_sqkm"] = (
            rec["wildfire_area_rai"] * 0.0016
            if rec.get("wildfire_area_rai") is not None
            else None
        )

    area_rows = table(
        xlsx_sheets(ROOT / "province_area.xlsx")["071da6e1-50f8-4816-979f-9e20bbf"]
    )
    for row in area_rows:
        key = (row["province"], year(row["year"]))
        rec = records.setdefault(key, {"province": row["province"], "year": key[1]})
        rec["province_area_sqkm"] = number(row["area"])

    with (ROOT / "PM25_YEARLY.csv").open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            province = en_to_th[norm_en(row["province"])]
            key = (province, year(row["year"]))
            rec = records.setdefault(key, {"province": province, "year": key[1]})
            rec["pm25_total_count"] = number(row["total_count"])
            rec["pm25_avg"] = number(row["PM25_dcount"])

    fields = [
        "province",
        "province_en",
        "year",
        "health_region",
        "population",
        "province_area_sqkm",
        "number_of_wildfire",
        "wildfire_area_rai",
        "wildfire_area_sqkm",
        "wildfire_area_percent",
        "pm25_avg",
        "pm25_total_count",
        *MENTAL_FIELDS,
        "total_mental_cases",
    ]

    cleaned = []
    for rec in records.values():
        area = rec.get("province_area_sqkm")
        fire_area = rec.get("wildfire_area_sqkm")
        rec["wildfire_area_percent"] = (
            fire_area / area * 100 if fire_area is not None and area else None
        )
        rec["total_mental_cases"] = sum(rec.get(f) or 0 for f in MENTAL_FIELDS)
        cleaned.append({field: rec.get(field) for field in fields})
    cleaned.sort(key=lambda r: (r["year"] or 0, r["province"] or ""))

    cause_rows = xlsx_sheets(ROOT / "wildfire_causes.xlsx")["Sheet2"]
    cause_header = cause_rows[0]
    causes = []
    for row in cause_rows[1:]:
        if len(row) < 2 or not row[1]:
            continue
        cause = row[1].strip()
        for idx, heading in enumerate(cause_header):
            y = year(heading)
            if y is None or idx >= len(row):
                continue
            value = number(row[idx])
            if value is None:
                continue
            causes.append({"year": y, "cause": cause, "area_rai": value})

    dictionary = load_description()

    write_csv(OUT / "clean_province_year.csv", cleaned, fields)
    write_csv(OUT / "clean_wildfire_causes_long.csv", causes, ["year", "cause", "area_rai"])
    write_csv(
        OUT / "data_dictionary_cleaned.csv",
        dictionary,
        ["file", "table_name", "field", "description"],
    )

    years = sorted({r["year"] for r in cleaned if r["year"]})
    provinces = sorted({r["province"] for r in cleaned if r["province"]})
    coverage = defaultdict(int)
    for row in cleaned:
        for field in fields:
            if row.get(field) not in (None, ""):
                coverage[field] += 1

    payload = {
        "generated_from": [
            "Dataset_description.xlsx",
            "Fire_area_prep_province.xlsx",
            "PM25_YEARLY.csv",
            "Psychi_cases.xlsx",
            "health_region.xlsx",
            "province_area.xlsx",
            "wildfire_causes.xlsx",
            "description.jpg",
        ],
        "rows": cleaned,
        "causes": causes,
        "dictionary": dictionary,
        "fields": fields,
        "mental_fields": MENTAL_FIELDS,
        "summary": {
            "province_year_rows": len(cleaned),
            "cause_rows": len(causes),
            "province_count": len(provinces),
            "year_min": min(years),
            "year_max": max(years),
            "best_overlap": "2016-2022 for wildfire + PM2.5 + health; 2018-2022 when province area is required.",
            "coverage": dict(coverage),
        },
    }

    with (ROOT / "site" / "data.js").open("w", encoding="utf-8") as f:
        f.write("window.WILDFIRE_DATA = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    print(f"Wrote {OUT / 'clean_province_year.csv'}")
    print(f"Wrote {OUT / 'clean_wildfire_causes_long.csv'}")
    print(f"Wrote {OUT / 'data_dictionary_cleaned.csv'}")
    print(f"Wrote {ROOT / 'site' / 'data.js'}")


if __name__ == "__main__":
    main()
