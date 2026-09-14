import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:4b"

def build_evidence(employee, risk):
    return {
        "employee_id": employee["employee_id"],
        "name": employee["name"],
        "role": employee["role"],
        "department": employee["department"],
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "risk_factors": risk["factors"],
        "attendance": employee["attendance"],
        "performance": employee["performance"],
        "engagement": employee["engagement"],
        "feedback": employee["feedback"],
        "skills": employee["skills"],
        "career": employee["career"]
    }

def analyze_employee(evidence):
    prompt = f"""
You are an HR workforce intelligence analyst.

Analyze the employee evidence below.

IMPORTANT RULES:
- The risk score and risk level are calculated by the backend.
- Do NOT change or recalculate the official risk score.
- Do NOT invent employee data.
- Use only the evidence provided.
- Identify meaningful patterns across different HR data sources.
- Explain possible concerns carefully. Do not claim causation.
- Recommend practical HR actions.

Return your response using these sections:

RISK ASSESSMENT
KEY SIGNALS
CROSS-SOURCE INSIGHT
RECOMMENDED ACTIONS
CONFIDENCE
LIMITATIONS

EMPLOYEE EVIDENCE:
{evidence}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"]