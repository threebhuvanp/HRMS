from flask import (
    Flask,
    jsonify,
    request,
    session,
    send_from_directory,
    redirect
)

import sqlite3
import os
from functools import wraps

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# Google authentication
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "workforceai-development-secret-key"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False
)


# =========================================================
# GOOGLE CONFIGURATION
# =========================================================

GOOGLE_CLIENT_ID = (
    "188759653861-r7u2q8g5nt0v6g2ge2lgttjscm1t11as"
    ".apps.googleusercontent.com"
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(__file__)

DATABASE = os.path.join(
    BASE_DIR,
    "database.db"
)

FRONTEND_FOLDER = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "../frontend"
    )
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    connection = sqlite3.connect(
        DATABASE,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA journal_mode=WAL"
    )

    connection.execute(
        "PRAGMA busy_timeout = 10000"
    )

    return connection


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_database():

    connection = get_connection()

    # USERS
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT,
            google_sub TEXT UNIQUE,
            auth_provider TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)

    # EMPLOYEES
    connection.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            employee_code TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            joining_date TEXT,
            manager_id INTEGER,
            status TEXT NOT NULL DEFAULT 'active',

            FOREIGN KEY (user_id)
            REFERENCES users(id)
        )
    """)

    # PERFORMANCE
    connection.execute("""
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            rating REAL DEFAULT 0,
            goal_score REAL DEFAULT 0,
            quality_score REAL DEFAULT 0,
            teamwork_score REAL DEFAULT 0,
            manager_score REAL DEFAULT 0,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (employee_id)
            REFERENCES employees(id)
        )
    """)

    # GOALS
    connection.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            target REAL DEFAULT 100,
            progress REAL DEFAULT 0,
            deadline TEXT,
            status TEXT DEFAULT 'in_progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (employee_id)
            REFERENCES employees(id)
        )
    """)

    # ATTENDANCE
    connection.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            working_days INTEGER DEFAULT 0,
            present_days INTEGER DEFAULT 0,
            absent_days INTEGER DEFAULT 0,
            late_days INTEGER DEFAULT 0,

            FOREIGN KEY (employee_id)
            REFERENCES employees(id)
        )
    """)

    # FEEDBACK
    connection.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            reviewer_id INTEGER,
            period TEXT NOT NULL,
            feedback_text TEXT,
            sentiment TEXT DEFAULT 'neutral',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (employee_id)
            REFERENCES employees(id)
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# AUTH HELPERS
# =========================================================

def hr_required():

    if "user_id" not in session:
        return jsonify({
            "error": "Login required"
        }), 401

    if session.get("role") != "hr":
        return jsonify({
            "error": "HR access required"
        }), 403

    return None


# =========================================================
# FRONTEND
# =========================================================

@app.route("/app")
def frontend():

    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


@app.route("/dashboard")
def dashboard_page():

    if "user_id" not in session:
        return redirect("/app")

    if session.get("role") != "hr":
        return jsonify({
            "error": "HR access required"
        }), 403

    return send_from_directory(
        FRONTEND_FOLDER,
        "dashboard.html"
    )


@app.route("/")
def home():

    return jsonify({
        "message": "WorkforceAI backend is running"
    })


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not name or not email or not password or not role:
        return jsonify({
            "error": "Name, email, password and role are required"
        }), 400

    allowed_roles = [
        "hr",
        "admin",
        "manager",
        "employee"
    ]

    if role not in allowed_roles:
        return jsonify({
            "error": "Invalid role"
        }), 400

    email = email.strip().lower()

    password_hash = generate_password_hash(
        password
    )

    connection = get_connection()

    try:

        connection.execute("""
            INSERT INTO users (
                name,
                email,
                password_hash,
                auth_provider,
                role
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            password_hash,
            "local",
            role
        ))

        connection.commit()

    except sqlite3.IntegrityError:

        connection.close()

        return jsonify({
            "error": "Email already exists"
        }), 409

    connection.close()

    return jsonify({
        "message": "User registered successfully"
    }), 201


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    email = email.strip().lower()

    connection = get_connection()

    user = connection.execute("""
        SELECT
            id,
            name,
            email,
            password_hash,
            role,
            status
        FROM users
        WHERE email = ?
    """, (email,)).fetchone()

    if user is None:

        connection.close()

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if user["status"] != "active":

        connection.close()

        return jsonify({
            "error": "Account is not active"
        }), 403

    if not user["password_hash"]:

        connection.close()

        return jsonify({
            "error": "This account does not use password login"
        }), 401

    if not check_password_hash(
        user["password_hash"],
        password
    ):

        connection.close()

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    session.clear()

    session["user_id"] = user["id"]
    session["email"] = user["email"]
    session["role"] = user["role"]

    connection.execute("""
        UPDATE users
        SET last_login = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (user["id"],))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }), 200


# =========================================================
# GOOGLE LOGIN
# =========================================================

@app.route("/google-login", methods=["POST"])
def google_login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    credential = data.get("credential")

    if not credential:
        return jsonify({
            "error": "Google credential is required"
        }), 400

    try:

        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

    except ValueError:

        return jsonify({
            "error": "Invalid Google credential"
        }), 401

    except Exception as error:

        print(
            "Google verification error:",
            error
        )

        return jsonify({
            "error": "Google authentication failed"
        }), 401

    google_sub = idinfo.get("sub")
    email = idinfo.get("email")
    name = idinfo.get("name")

    email_verified = idinfo.get(
        "email_verified",
        False
    )

    if not google_sub or not email:

        return jsonify({
            "error": "Google account information is incomplete"
        }), 401

    if not email_verified:

        return jsonify({
            "error": "Google email is not verified"
        }), 401

    email = email.strip().lower()

    if not name:
        name = email.split("@")[0]

    connection = get_connection()

    # Find by Google ID first
    user = connection.execute("""
        SELECT
            id,
            name,
            email,
            google_sub,
            role,
            status,
            password_hash
        FROM users
        WHERE google_sub = ?
    """, (google_sub,)).fetchone()

    # Otherwise find approved account by email
    if user is None:

        user = connection.execute("""
            SELECT
                id,
                name,
                email,
                google_sub,
                role,
                status,
                password_hash
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

    if user is None:

        connection.close()

        return jsonify({
            "error": (
                "Google account is not provisioned "
                "for WorkforceAI. Ask an administrator "
                "to create your WorkforceAI account first."
            )
        }), 403

    if user["status"] != "active":

        connection.close()

        return jsonify({
            "error": "WorkforceAI account is not active"
        }), 403

    if (
        user["google_sub"] is not None
        and user["google_sub"] != google_sub
    ):

        connection.close()

        return jsonify({
            "error": (
                "This WorkforceAI account is "
                "linked to another Google account."
            )
        }), 409

    if user["google_sub"] is None:

        connection.execute("""
            UPDATE users
            SET
                google_sub = ?,
                auth_provider = ?,
                last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            google_sub,
            "local+google"
            if user["password_hash"]
            else "google",
            user["id"]
        ))

    else:

        connection.execute("""
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (user["id"],))

    connection.commit()
    connection.close()

    session.clear()

    session["user_id"] = user["id"]
    session["email"] = user["email"]
    session["role"] = user["role"]
    session["google_sub"] = google_sub

    return jsonify({
        "message": "Google login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }), 200


# =========================================================
# CURRENT USER
# =========================================================

@app.route("/me")
def current_user():

    if "user_id" not in session:

        return jsonify({
            "error": "Not logged in"
        }), 401

    connection = get_connection()

    user = connection.execute("""
        SELECT
            id,
            name,
            email,
            role,
            status
        FROM users
        WHERE id = ?
    """, (session["user_id"],)).fetchone()

    connection.close()

    if user is None:

        session.clear()

        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "logged_in": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "status": user["status"]
        }
    }), 200


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "message": "Logout successful"
    }), 200


# =========================================================
# HR DASHBOARD
# =========================================================

@app.route("/hr/dashboard")
def hr_dashboard():

    error = hr_required()

    if error:
        return error

    connection = get_connection()

    employee_count = connection.execute("""
        SELECT COUNT(*) AS count
        FROM employees
        WHERE status = 'active'
    """).fetchone()["count"]

    performance_count = connection.execute("""
        SELECT COUNT(*) AS count
        FROM performance
    """).fetchone()["count"]

    goal_count = connection.execute("""
        SELECT COUNT(*) AS count
        FROM goals
    """).fetchone()["count"]

    connection.close()

    return jsonify({
        "message": "Welcome to the HR Dashboard",
        "access": "granted",
        "role": "hr",
        "statistics": {
            "employees": employee_count,
            "performance_records": performance_count,
            "goals": goal_count
        }
    }), 200


# =========================================================
# CREATE EMPLOYEE
# =========================================================

@app.route("/employees", methods=["POST"])
def create_employee():

    error = hr_required()

    if error:
        return error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    employee_code = data.get("employee_code")
    department = data.get("department")
    designation = data.get("designation")
    joining_date = data.get("joining_date")
    manager_id = data.get("manager_id")

    if not employee_code or not department or not designation:

        return jsonify({
            "error": (
                "Employee code, department and "
                "designation are required"
            )
        }), 400

    connection = get_connection()

    try:

        cursor = connection.execute("""
            INSERT INTO employees (
                employee_code,
                department,
                designation,
                joining_date,
                manager_id,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            employee_code,
            department,
            designation,
            joining_date,
            manager_id,
            "active"
        ))

        connection.commit()

        employee_id = cursor.lastrowid

    except sqlite3.IntegrityError:

        connection.close()

        return jsonify({
            "error": "Employee code already exists"
        }), 409

    connection.close()

    return jsonify({
        "message": "Employee created successfully",
        "employee_id": employee_id
    }), 201


# =========================================================
# GET EMPLOYEES
# =========================================================

@app.route("/employees", methods=["GET"])
def get_employees():

    error = hr_required()

    if error:
        return error

    connection = get_connection()

    employees = connection.execute("""
        SELECT
            id,
            employee_code,
            department,
            designation,
            joining_date,
            manager_id,
            status
        FROM employees
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return jsonify({
        "employees": [
            dict(employee)
            for employee in employees
        ],
        "count": len(employees)
    }), 200


# =========================================================
# GET ONE EMPLOYEE
# =========================================================

@app.route("/employees/<int:employee_id>")
def get_employee(employee_id):

    error = hr_required()

    if error:
        return error

    connection = get_connection()

    employee = connection.execute("""
        SELECT
            id,
            employee_code,
            department,
            designation,
            joining_date,
            manager_id,
            status
        FROM employees
        WHERE id = ?
    """, (employee_id,)).fetchone()

    connection.close()

    if employee is None:

        return jsonify({
            "error": "Employee not found"
        }), 404

    return jsonify({
        "employee": dict(employee)
    }), 200


# =========================================================
# UPDATE EMPLOYEE
# =========================================================

@app.route("/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):

    error = hr_required()

    if error:
        return error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    connection = get_connection()

    existing = connection.execute("""
        SELECT
            department,
            designation,
            joining_date,
            manager_id,
            status
        FROM employees
        WHERE id = ?
    """, (employee_id,)).fetchone()

    if existing is None:

        connection.close()

        return jsonify({
            "error": "Employee not found"
        }), 404

    department = data.get(
        "department",
        existing["department"]
    )

    designation = data.get(
        "designation",
        existing["designation"]
    )

    joining_date = data.get(
        "joining_date",
        existing["joining_date"]
    )

    manager_id = data.get(
        "manager_id",
        existing["manager_id"]
    )

    status = data.get(
        "status",
        existing["status"]
    )

    if status is None:
        status = existing["status"]

    if not department or not designation:

        connection.close()

        return jsonify({
            "error": "Department and designation are required"
        }), 400

    try:

        connection.execute("""
            UPDATE employees
            SET
                department = ?,
                designation = ?,
                joining_date = ?,
                manager_id = ?,
                status = ?
            WHERE id = ?
        """, (
            department,
            designation,
            joining_date,
            manager_id,
            status,
            employee_id
        ))

        connection.commit()

    except sqlite3.Error as error_db:

        connection.rollback()
        connection.close()

        return jsonify({
            "error": "Database update failed",
            "details": str(error_db)
        }), 500

    connection.close()

    return jsonify({
        "message": "Employee updated successfully"
    }), 200


# =========================================================
# DELETE EMPLOYEE
# =========================================================

@app.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):

    error = hr_required()

    if error:
        return error

    connection = get_connection()

    cursor = connection.execute("""
        DELETE FROM employees
        WHERE id = ?
    """, (employee_id,))

    connection.commit()

    if cursor.rowcount == 0:

        connection.close()

        return jsonify({
            "error": "Employee not found"
        }), 404

    connection.close()

    return jsonify({
        "message": "Employee deleted successfully"
    }), 200


# =========================================================
# PERFORMANCE - CREATE
# =========================================================

@app.route("/performance", methods=["POST"])
def create_performance():

    error = hr_required()

    if error:
        return error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    employee_id = data.get("employee_id")
    period = data.get("period")

    if not employee_id or not period:

        return jsonify({
            "error": "employee_id and period are required"
        }), 400

    rating = float(data.get("rating", 0))
    goal_score = float(data.get("goal_score", 0))
    quality_score = float(data.get("quality_score", 0))
    teamwork_score = float(data.get("teamwork_score", 0))
    manager_score = float(data.get("manager_score", 0))
    comments = data.get("comments", "")

    connection = get_connection()

    employee = connection.execute("""
        SELECT id FROM employees
        WHERE id = ?
    """, (employee_id,)).fetchone()

    if employee is None:

        connection.close()

        return jsonify({
            "error": "Employee not found"
        }), 404

    cursor = connection.execute("""
        INSERT INTO performance (
            employee_id,
            period,
            rating,
            goal_score,
            quality_score,
            teamwork_score,
            manager_score,
            comments
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_id,
        period,
        rating,
        goal_score,
        quality_score,
        teamwork_score,
        manager_score,
        comments
    ))

    connection.commit()

    performance_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "message": "Performance record created",
        "performance_id": performance_id
    }), 201


# =========================================================
# PERFORMANCE - LIST
# =========================================================

@app.route("/performance", methods=["GET"])
def get_performance():

    error = hr_required()

    if error:
        return error

    connection = get_connection()

    rows = connection.execute("""
        SELECT
            p.*,
            e.employee_code,
            e.department,
            e.designation
        FROM performance p
        JOIN employees e
            ON e.id = p.employee_id
        ORDER BY p.id DESC
    """).fetchall()

    connection.close()

    return jsonify({
        "performance": [
            dict(row)
            for row in rows
        ],
        "count": len(rows)
    }), 200


# =========================================================
# GOALS - CREATE
# =========================================================

@app.route("/goals", methods=["POST"])
def create_goal():

    error = hr_required()

    if error:
        return error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    employee_id = data.get("employee_id")
    title = data.get("title")

    if not employee_id or not title:

        return jsonify({
            "error": "employee_id and title are required"
        }), 400

    connection = get_connection()

    cursor = connection.execute("""
        INSERT INTO goals (
            employee_id,
            title,
            description,
            target,
            progress,
            deadline,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_id,
        title,
        data.get("description", ""),
        float(data.get("target", 100)),
        float(data.get("progress", 0)),
        data.get("deadline"),
        data.get("status", "in_progress")
    ))

    connection.commit()

    goal_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "message": "Goal created successfully",
        "goal_id": goal_id
    }), 201


# =========================================================
# ATTENDANCE - CREATE
# =========================================================

@app.route("/attendance", methods=["POST"])
def create_attendance():

    error = hr_required()

    if error:
        return error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    employee_id = data.get("employee_id")
    period = data.get("period")

    if not employee_id or not period:

        return jsonify({
            "error": "employee_id and period are required"
        }), 400

    working_days = int(data.get("working_days", 0))
    present_days = int(data.get("present_days", 0))
    absent_days = int(data.get("absent_days", 0))
    late_days = int(data.get("late_days", 0))

    connection = get_connection()

    connection.execute("""
        INSERT INTO attendance (
            employee_id,
            period,
            working_days,
            present_days,
            absent_days,
            late_days
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        employee_id,
        period,
        working_days,
        present_days,
        absent_days,
        late_days
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Attendance record created"
    }), 201


# =========================================================
# FEEDBACK - CREATE
# =========================================================

@app.route("/feedback", methods=["POST"])
def create_feedback():

    error = hr_required()

    if error:
        return error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body is required"
        }), 400

    employee_id = data.get("employee_id")
    period = data.get("period")
    feedback_text = data.get("feedback_text")

    if not employee_id or not period or not feedback_text:

        return jsonify({
            "error": (
                "employee_id, period and "
                "feedback_text are required"
            )
        }), 400

    sentiment = data.get(
        "sentiment",
        "neutral"
    ).lower()

    if sentiment not in [
        "positive",
        "neutral",
        "mixed",
        "negative"
    ]:
        sentiment = "neutral"

    connection = get_connection()

    connection.execute("""
        INSERT INTO feedback (
            employee_id,
            reviewer_id,
            period,
            feedback_text,
            sentiment
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        employee_id,
        session["user_id"],
        period,
        feedback_text,
        sentiment
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Feedback created successfully"
    }), 201


# =========================================================
# PERFORMANCE INTELLIGENCE
# =========================================================

@app.route("/intelligence/performance", methods=["GET"])
def performance_intelligence():

    error = hr_required()

    if error:
        return error

    connection = get_connection()

    employees = connection.execute("""
        SELECT
            id,
            employee_code,
            department,
            designation
        FROM employees
        WHERE status = 'active'
    """).fetchall()

    results = []

    for employee in employees:

        employee_id = employee["id"]

        performance_rows = connection.execute("""
            SELECT *
            FROM performance
            WHERE employee_id = ?
            ORDER BY id DESC
            LIMIT 2
        """, (employee_id,)).fetchall()

        goal_row = connection.execute("""
            SELECT
                AVG(progress) AS goal_completion
            FROM goals
            WHERE employee_id = ?
        """, (employee_id,)).fetchone()

        attendance_row = connection.execute("""
            SELECT
                SUM(working_days) AS working_days,
                SUM(present_days) AS present_days,
                SUM(absent_days) AS absent_days,
                SUM(late_days) AS late_days
            FROM attendance
            WHERE employee_id = ?
        """, (employee_id,)).fetchone()

        feedback_row = connection.execute("""
            SELECT sentiment
            FROM feedback
            WHERE employee_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (employee_id,)).fetchone()

        # ---------------- PERFORMANCE ----------------

        if performance_rows:

            current = performance_rows[0]

            current_score = (
                current["rating"] * 0.30 +
                current["goal_score"] * 0.25 +
                current["quality_score"] * 0.20 +
                current["teamwork_score"] * 0.10 +
                current["manager_score"] * 0.15
            )

            if len(performance_rows) > 1:

                previous = performance_rows[1]

                previous_score = (
                    previous["rating"] * 0.30 +
                    previous["goal_score"] * 0.25 +
                    previous["quality_score"] * 0.20 +
                    previous["teamwork_score"] * 0.10 +
                    previous["manager_score"] * 0.15
                )

            else:
                previous_score = current_score

        else:

            current_score = 0
            previous_score = 0

        # ---------------- TREND ----------------

        if previous_score:

            trend = (
                (current_score - previous_score)
                / previous_score
            ) * 100

        else:
            trend = 0

        # ---------------- GOALS ----------------

        goal_completion = (
            goal_row["goal_completion"]
            if goal_row["goal_completion"] is not None
            else 0
        )

        # ---------------- ATTENDANCE ----------------

        working_days = (
            attendance_row["working_days"]
            or 0
        )

        present_days = (
            attendance_row["present_days"]
            or 0
        )

        late_days = (
            attendance_row["late_days"]
            or 0
        )

        if working_days > 0:

            attendance_rate = (
                present_days / working_days
            ) * 100

        else:

            attendance_rate = 0

        # ---------------- SENTIMENT ----------------

        sentiment = (
            feedback_row["sentiment"]
            if feedback_row
            else "neutral"
        )

        # ---------------- RISK ENGINE ----------------

        risk_score = 0
        risk_reasons = []

        if current_score < 60:

            risk_score += 35

            risk_reasons.append(
                "Low performance score"
            )

        elif current_score < 75:

            risk_score += 15

            risk_reasons.append(
                "Performance needs attention"
            )

        if trend < -10:

            risk_score += 25

            risk_reasons.append(
                "Significant performance decline"
            )

        elif trend < 0:

            risk_score += 10

            risk_reasons.append(
                "Performance trending downward"
            )

        if goal_completion < 60:

            risk_score += 20

            risk_reasons.append(
                "Low goal completion"
            )

        if attendance_rate > 0 and attendance_rate < 85:

            risk_score += 15

            risk_reasons.append(
                "Low attendance"
            )

        if late_days >= 5:

            risk_score += 10

            risk_reasons.append(
                "Frequent late attendance"
            )

        if sentiment == "negative":

            risk_score += 15

            risk_reasons.append(
                "Negative feedback sentiment"
            )

        if risk_score >= 50:

            risk_level = "High"

        elif risk_score >= 25:

            risk_level = "Medium"

        else:

            risk_level = "Low"

        # ---------------- AI-STYLE INSIGHT ----------------

        if risk_level == "High":

            insight = (
                "This employee shows multiple risk signals. "
                "HR should review recent performance, "
                "goals and attendance before the next review."
            )

            recommendation = (
                "Schedule a manager check-in and create "
                "a short-term improvement plan."
            )

        elif trend > 5 and current_score >= 75:

            insight = (
                "Performance is improving with strong "
                "overall results."
            )

            recommendation = (
                "Recognize the improvement and consider "
                "stretch goals or leadership opportunities."
            )

        elif goal_completion >= 80:

            insight = (
                "Goals are progressing well and the employee "
                "is demonstrating consistent delivery."
            )

            recommendation = (
                "Maintain current support and consider "
                "advanced development opportunities."
            )

        else:

            insight = (
                "Performance is relatively stable, but "
                "continued monitoring can help identify "
                "future changes early."
            )

            recommendation = (
                "Review progress during the next regular "
                "manager check-in."
            )

        results.append({

            "employee_id": employee_id,
            "employee_code": employee["employee_code"],
            "department": employee["department"],
            "designation": employee["designation"],

            "current_performance": round(
                current_score,
                1
            ),

            "previous_performance": round(
                previous_score,
                1
            ),

            "performance_trend": round(
                trend,
                1
            ),

            "goal_completion": round(
                goal_completion,
                1
            ),

            "attendance_rate": round(
                attendance_rate,
                1
            ),

            "feedback_sentiment": sentiment,

            "risk_score": min(
                risk_score,
                100
            ),

            "risk_level": risk_level,

            "risk_reasons": risk_reasons,

            "insight": insight,

            "recommendation": recommendation
        })

    connection.close()

    return jsonify({
        "engine": "WorkforceAI Performance Intelligence",
        "employees_analyzed": len(results),
        "results": results
    }), 200


# =========================================================
# WORKFORCE RISK SUMMARY
# =========================================================

@app.route("/intelligence/risk", methods=["GET"])
def workforce_risk():

    error = hr_required()

    if error:
        return error

    # Reuse intelligence engine
    connection = get_connection()

    employees = connection.execute("""
        SELECT COUNT(*) AS count
        FROM employees
        WHERE status = 'active'
    """).fetchone()["count"]

    connection.close()

    # Calculate intelligence directly through internal request
    # using the same logic endpoint.
    response = performance_intelligence()

    if isinstance(response, tuple):
        response_data = response[0]
    else:
        response_data = response

    data = response_data.get_json()

    results = data.get(
        "results",
        []
    )

    high = sum(
        1
        for item in results
        if item["risk_level"] == "High"
    )

    medium = sum(
        1
        for item in results
        if item["risk_level"] == "Medium"
    )

    low = sum(
        1
        for item in results
        if item["risk_level"] == "Low"
    )

    return jsonify({

        "workforce": {
            "total_employees": employees,
            "high_risk": high,
            "medium_risk": medium,
            "low_risk": low
        },

        "top_risks": [
            item
            for item in results
            if item["risk_level"] == "High"
        ][:5]

    }), 200


# =========================================================
# AI INSIGHTS SUMMARY
# =========================================================

@app.route("/intelligence/insights", methods=["GET"])
def workforce_insights():

    error = hr_required()

    if error:
        return error

    response = performance_intelligence()

    if isinstance(response, tuple):
        response_data = response[0]
    else:
        response_data = response

    data = response_data.get_json()

    results = data.get(
        "results",
        []
    )

    insights = []

    for item in results:

        if item["risk_level"] != "Low":

            insights.append({
                "employee_code": item["employee_code"],
                "department": item["department"],
                "risk_level": item["risk_level"],
                "insight": item["insight"],
                "recommendation": item["recommendation"]
            })

    return jsonify({
        "engine": "WorkforceAI Insights Engine",
        "insights": insights
    }), 200


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    init_database()

    print()
    print("========================================")
    print("   WorkforceAI Backend Starting...")
    print("========================================")
    print("Backend:  http://127.0.0.1:5000")
    print("Frontend: http://127.0.0.1:5000/app")
    print("Dashboard: http://127.0.0.1:5000/dashboard")
    print("Google Login: ENABLED")
    print("Performance Intelligence: ENABLED")
    print("Workforce Risk: ENABLED")
    print("AI Insights: ENABLED")
    print("========================================")
    print()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )