from flask import Flask, jsonify, send_from_directory
from dataloader import load_all_data
from risk_engine import calculate_risk
from intelligence.data_adapter import get_employee_evidence
from intelligence.risk_engine import calculate_risk as calculate_intelligence_risk
from intelligence.qwen_engine import analyze_employee
from pathlib import Path


app = Flask(__name__)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# -----------------------------
# FRONTEND ROUTES
# -----------------------------

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/dashboard")
def dashboard():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.route("/employee/<employee_id>")
def employee_page(employee_id):
    return send_from_directory(FRONTEND_DIR, "employee.html")


# -----------------------------
# EMPLOYEE API
# -----------------------------

@app.route("/api/employees")
def employees():
    data = load_all_data()

    result = []

    for employee in data.values():
        result.append({
            "employee_id": employee["employee_id"],
            "name": employee["name"],
            "role": employee["role"],
            "department": employee["department"],
            "risk": calculate_risk(employee)
        })

    return jsonify(result)


@app.route("/api/employees/<employee_id>")
def employee_details(employee_id):
    data = load_all_data()

    employee = data.get(employee_id)

    if not employee:
        return jsonify({
            "error": "Employee not found"
        }), 404

    return jsonify({
        "profile": employee,
        "risk": calculate_risk(employee)
    })


# -----------------------------
# AI WORKFORCE INTELLIGENCE
# -----------------------------

@app.route("/api/ai/employee/<employee_code>")
def ai_employee(employee_code):

    evidence = get_employee_evidence(employee_code)

    if evidence is None:
        return jsonify({
            "error": "Employee not found"
        }), 404

    risk = calculate_intelligence_risk(evidence)

    analysis = analyze_employee(
        evidence,
        risk
    )

    return jsonify({
        "employee": evidence,
        "risk": risk,
        "ai_analysis": analysis
    })


# -----------------------------
# START SERVER
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)