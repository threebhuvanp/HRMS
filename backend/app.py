from intelligence.qwen_engine import build_evidence, analyze_employee
from flask import Flask, jsonify, send_from_directory
from dataloader import load_all_data
from risk_engine import calculate_risk
from pathlib import Path


app = Flask(__name__)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


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

@app.route("/employee/<employee_id>")
def employee_page(employee_id):
    return send_from_directory(FRONTEND_DIR, "employee.html")

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


if __name__ == "__main__":
    app.run(debug=True)