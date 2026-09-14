import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(filename):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def load_all_data():
    employees = load_json("employees.json")
    attendance = load_json("attendance.json")
    performance = load_json("performance.json")
    engagement = load_json("engagement.json")
    feedback = load_json("feedback.json")
    skills = load_json("skills.json")
    career = load_json("career.json")

    attendance_map = {
        item["employee_id"]: item for item in attendance
    }

    performance_map = {
        item["employee_id"]: item for item in performance
    }

    engagement_map = {
        item["employee_id"]: item for item in engagement
    }

    feedback_map = {
        item["employee_id"]: item for item in feedback
    }

    skills_map = {
        item["employee_id"]: item for item in skills
    }

    career_map = {
        item["employee_id"]: item for item in career
    }

    employees_map = {}

    for employee in employees:
        employee_id = employee["employee_id"]

        employees_map[employee_id] = {
            **employee,
            "attendance": attendance_map.get(employee_id, {}),
            "performance": performance_map.get(employee_id, {}),
            "engagement": engagement_map.get(employee_id, {}),
            "feedback": feedback_map.get(employee_id, {}),
            "skills": skills_map.get(employee_id, {}),
            "career": career_map.get(employee_id, {})
        }

    return employees_map


if __name__ == "__main__":
    data = load_all_data()

    print(f"Loaded {len(data)} employees.")

    employee = data.get("EMP-1042")

    print("\nEmployee Profile:")
    print(json.dumps(employee, indent=2))