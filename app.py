from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

# ── Patient & Staff Data ──────────────────────────────────────────────────────

PATIENT = {
    "name": "Arjun Mehta",
    "age": 58,
    "gender": "M",
    "bed": "4B",
    "doctor": "Dr. Priya Sharma",
    "ward": "General Medicine"
}

STAFF = {
    "doc":  {"name": "Dr. Priya Sharma", "role": "Doctor",        "status": "available"},
    "nur":  {"name": "Nurse on Duty",    "role": "Nurse",          "status": "available"},
    "sup":  {"name": "Support Staff",    "role": "Support",        "status": "available"},
    "emer": {"name": "Emergency Team",   "role": "Emergency",      "status": "standby"},
}

SCENARIOS = {
    "normal":   {"hr":[65,80],   "bps":[110,130], "bpd":[70,85],  "spo2":[96,100], "temp":[36.2,37.2], "resp":[13,18]},
    "tachy":    {"hr":[110,140], "bps":[115,135], "bpd":[75,90],  "spo2":[94,98],  "temp":[36.8,37.4], "resp":[18,24]},
    "hyper":    {"hr":[70,90],   "bps":[155,175], "bpd":[95,110], "spo2":[95,99],  "temp":[36.5,37.2], "resp":[14,20]},
    "hypoxia":  {"hr":[90,115],  "bps":[100,130], "bpd":[60,80],  "spo2":[85,92],  "temp":[36.2,37.0], "resp":[22,30]},
    "fever":    {"hr":[88,110],  "bps":[115,135], "bpd":[72,88],  "spo2":[94,98],  "temp":[38.4,39.6], "resp":[18,26]},
    "critical": {"hr":[140,180], "bps":[80,100],  "bpd":[45,60],  "spo2":[80,88],  "temp":[39.5,40.5], "resp":[28,36]},
}

# ── Helper ────────────────────────────────────────────────────────────────────

def rnd(lo, hi, decimals=0):
    v = random.uniform(lo, hi)
    return round(v, decimals) if decimals else round(v)

def get_status(value, vital):
    if vital == "hr":
        if value < 50 or value > 130: return "danger"
        if value < 60 or value > 100: return "warn"
    elif vital == "bps":
        if value > 180 or value < 90: return "danger"
        if value > 140 or value < 100: return "warn"
    elif vital == "spo2":
        if value < 90: return "danger"
        if value < 95: return "warn"
    elif vital == "temp":
        if value > 39 or value < 35.5: return "danger"
        if value > 37.5 or value < 36: return "warn"
    elif vital == "resp":
        if value > 30 or value < 8: return "danger"
        if value > 20 or value < 12: return "warn"
    return "ok"

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", patient=PATIENT)


@app.route("/api/vitals")
def vitals():
    scenario_key = request.args.get("scenario", "normal")
    if scenario_key not in SCENARIOS:
        scenario_key = "normal"

    s = SCENARIOS[scenario_key]
    hr   = rnd(s["hr"][0],   s["hr"][1])
    bps  = rnd(s["bps"][0],  s["bps"][1])
    bpd  = rnd(s["bpd"][0],  s["bpd"][1])
    spo2 = rnd(s["spo2"][0], s["spo2"][1])
    temp = rnd(s["temp"][0], s["temp"][1], decimals=1)
    resp = rnd(s["resp"][0], s["resp"][1])

    return jsonify({
        "hr":   {"value": hr,   "status": get_status(hr,   "hr")},
        "bp":   {"value": f"{bps}/{bpd}", "systolic": bps, "status": get_status(bps, "bps")},
        "spo2": {"value": spo2, "status": get_status(spo2, "spo2")},
        "temp": {"value": temp, "status": get_status(temp, "temp")},
        "resp": {"value": resp, "status": get_status(resp, "resp")},
    })


@app.route("/api/call_staff", methods=["POST"])
def call_staff():
    data = request.get_json(silent=True) or {}
    staff_id = data.get("staff_id", "")

    if staff_id not in STAFF:
        return jsonify({"error": "Unknown staff ID"}), 400

    member = STAFF[staff_id]
    return jsonify({
        "success": True,
        "staff_id": staff_id,
        "name": member["name"],
        "role": member["role"],
        "message": f"{member['name']} has been notified and is on the way."
    })


@app.route("/api/patient")
def patient():
    return jsonify(PATIENT)


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
