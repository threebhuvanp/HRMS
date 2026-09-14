import sqlite3
import os


DATABASE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "database.db"
)


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def get_employee_evidence(employee_code):
    connection = get_connection()

    employee = connection.execute("""
        SELECT
            id,
            employee_code,
            department,
            designation,
            joining_date,
            status
        FROM employees
        WHERE employee_code = ?
    """, (employee_code,)).fetchone()

    if employee is None:
        connection.close()
        return None

    employee_id = employee["id"]

    performance = connection.execute("""
        SELECT *
        FROM performance
        WHERE employee_id = ?
        ORDER BY id DESC
        LIMIT 2
    """, (employee_id,)).fetchall()

    attendance = connection.execute("""
        SELECT *
        FROM attendance
        WHERE employee_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (employee_id,)).fetchone()

    feedback = connection.execute("""
        SELECT *
        FROM feedback
        WHERE employee_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (employee_id,)).fetchone()

    engagement = connection.execute("""
        SELECT *
        FROM engagement
        WHERE employee_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (employee_id,)).fetchone()

    skills = connection.execute("""
        SELECT skill_name, proficiency
        FROM skills
        WHERE employee_id = ?
    """, (employee_id,)).fetchall()

    career = connection.execute("""
        SELECT *
        FROM career
        WHERE employee_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (employee_id,)).fetchone()

    goals = connection.execute("""
        SELECT *
        FROM goals
        WHERE employee_id = ?
        ORDER BY id DESC
    """, (employee_id,)).fetchall()

    connection.close()

    return {
        "employee_id": employee["employee_code"],
        "name": employee["employee_code"],
        "role": employee["designation"],
        "department": employee["department"],

        "performance": [
            dict(row)
            for row in performance
        ],

        "attendance": (
            dict(attendance)
            if attendance
            else {}
        ),

        "feedback": (
            dict(feedback)
            if feedback
            else {}
        ),

        "engagement": (
            dict(engagement)
            if engagement
            else {}
        ),

        "skills": {
            row["skill_name"]: row["proficiency"]
            for row in skills
        },

        "career": (
            dict(career)
            if career
            else {}
        ),

        "goals": [
            dict(row)
            for row in goals
        ]
    }


if __name__ == "__main__":
    evidence = get_employee_evidence("EMP-1042")

    import json

    print(
        json.dumps(
            evidence,
            indent=2
        )
    )