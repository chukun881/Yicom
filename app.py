"""Local payslip helper: Flask API + CSV employee store."""

import csv
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "employees.csv"
FIELDNAMES = ["Name", "IC", "Daily Rate"]


def _ensure_csv() -> None:
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()


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


if __name__ == "__main__":
    _ensure_csv()
    # Avoid port 5000 on macOS: AirPlay Receiver often uses it and returns HTTP 403 in browsers.
    port = int(os.environ.get("PORT", "5001"))
    print(f"\n  Payslip app - open in your browser:\n  http://127.0.0.1:{port}/\n")
    app.run(host="127.0.0.1", port=port, debug=True)
