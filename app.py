"""Local payslip helper: Flask API + CSV employee store."""

import csv
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "employees.csv"
SITES_PATH = BASE_DIR / "sites.csv"
FIELDNAMES = ["Name", "IC", "Daily Rate"]


def _ensure_csv() -> None:
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()


def _ensure_sites_csv() -> None:
    if not SITES_PATH.exists():
        with SITES_PATH.open("w", newline="", encoding="utf-8") as f:
            f.write("Site\n")


def _read_all_rows() -> list[dict[str, str]]:
    _ensure_csv()
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_all_rows(rows: list[dict[str, str]]) -> None:
    _ensure_csv()
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "").strip() for k in FIELDNAMES})


def _normalize_name(name: str) -> str:
    return " ".join(name.strip().split()).lower()


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/advance")
def advance():
    return render_template("advance.html")


@app.get("/api/employees/search")
def search_employees():
    q = request.args.get("q", "").strip().lower()
    rows = _read_all_rows()
    if not q:
        return jsonify([])
    matches = []
    for row in rows:
        name = (row.get("Name") or "").strip()
        if not name:
            continue
        if q in name.lower():
            matches.append(
                {
                    "name": name,
                    "ic": (row.get("IC") or "").strip(),
                    "dailyRate": (row.get("Daily Rate") or "").strip(),
                }
            )
    return jsonify(matches[:50])


@app.post("/api/employees")
def upsert_employee():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    ic = (data.get("ic") or "").strip()
    daily_rate = (data.get("dailyRate") or data.get("daily_rate") or "").strip()

    if not name:
        return jsonify({"ok": False, "error": "Name is required"}), 400

    rows = _read_all_rows()
    key = _normalize_name(name)
    for i, row in enumerate(rows):
        if _normalize_name(row.get("Name", "")) == key:
            rows[i] = {"Name": name, "IC": ic, "Daily Rate": daily_rate}
            _write_all_rows(rows)
            return jsonify({"ok": True, "updated": True})

    rows.append({"Name": name, "IC": ic, "Daily Rate": daily_rate})
    _write_all_rows(rows)
    return jsonify({"ok": True, "updated": False})


@app.get("/api/sites")
def get_sites():
    """Get list of all sites from sites.csv, cleaned and deduplicated"""
    _ensure_sites_csv()
    sites = []
    seen = set()
    with SITES_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            site_name = row.get("Site", "").strip()
            # Only add non-empty, non-duplicate sites
            if site_name and site_name not in seen:
                sites.append(site_name)
                seen.add(site_name)
    return jsonify(sites)


@app.post("/api/sites")
def save_site():
    """Save a new site to sites.csv with sanitization"""
    data = request.get_json(silent=True) or {}
    site_raw = data.get("site", "").strip()
    
    if not site_raw:
        return jsonify({"ok": False, "error": "Site name is required"}), 400
    
    # Data sanitization: convert to Title Case
    # e.g., " project alpha " becomes "Project Alpha"
    site_sanitized = site_raw.title()
    
    # Read existing sites to check for duplicates
    _ensure_sites_csv()
    existing_sites = []
    with SITES_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            site_name = row.get("Site", "").strip()
            if site_name:
                existing_sites.append(site_name)
    
    # Check if site already exists (case-insensitive)
    for existing in existing_sites:
        if existing.lower() == site_sanitized.lower():
            return jsonify({"ok": True, "saved": False, "message": "Site already exists"})
    
    # Append new site to the list
    existing_sites.append(site_sanitized)
    
    # Rewrite the entire file with proper newlines
    with SITES_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Site"])
        writer.writeheader()
        for site in existing_sites:
            writer.writerow({"Site": site})
    
    return jsonify({"ok": True, "saved": True, "site": site_sanitized})


if __name__ == "__main__":
    _ensure_csv()
    # Avoid port 5000 on macOS: AirPlay Receiver often uses it and returns HTTP 403 in browsers.
    port = int(os.environ.get("PORT", "5001"))
    print(f"\n  Payslip app - open in your browser:\n  http://127.0.0.1:{port}/\n")
    app.run(host="127.0.0.1", port=port, debug=True)
