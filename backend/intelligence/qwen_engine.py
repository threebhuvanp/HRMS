import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:4b"


def analyze_employee(evidence, risk):
    prompt = f"""
You are an enterprise HR workforce intelligence analyst.

Analyze the employee evidence below.

IMPORTANT RULES:
- The official risk score and risk level are calculated by the backend.
- Do NOT change, override, or recalculate the official risk score.
- Do NOT invent employee data.
- Use ONLY the evidence provided.
- Identify patterns across multiple HR data sources.
- Do not claim causation.
- Distinguish retention risk from performance concerns and skill gaps.
- Recommend practical, supportive HR actions.
- Recommendations must be based on evidence.

OFFICIAL RISK:
Score: {risk["risk_score"]}
Level: {risk["risk_level"]}

RISK FACTORS:
{risk["factors"]}

EMPLOYEE EVIDENCE:
{evidence}

Return exactly these sections:

RISK ASSESSMENT
KEY SIGNALS
CROSS-SOURCE INSIGHT
RECOMMENDED ACTIONS
CONFIDENCE
LIMITATIONS
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