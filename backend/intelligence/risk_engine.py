from .data_adapter import get_employee_evidence


def calculate_risk(evidence):
    score = 0
    factors = []

    performance = evidence["performance"]

    if len(performance) >= 2:
        current = performance[-1]
        previous = performance[-2]

        performance_drop = (
            previous["rating"] - current["rating"]
        )

        if performance_drop >= 1:
            score += 20
            factors.append({
                "factor": "Performance decline",
                "impact": 20,
                "evidence": (
                    f"Performance rating dropped by "
                    f"{performance_drop:.1f}."
                )
            })
        elif performance_drop >= 0.5:
            score += 10
            factors.append({
                "factor": "Performance decline",
                "impact": 10,
                "evidence": (
                    f"Performance rating dropped by "
                    f"{performance_drop:.1f}."
                )
            })

    attendance = evidence["attendance"]

    if attendance:
        attendance_rate = (
            attendance["present_days"]
            / attendance["working_days"]
        ) * 100

        if attendance_rate < 90:
            score += 20
            factors.append({
                "factor": "Attendance concern",
                "impact": 20,
                "evidence": (
                    f"Attendance is {attendance_rate:.1f}%."
                )
            })

    engagement = evidence["engagement"]

    if engagement:
        engagement_drop = (
            engagement["previous_score"]
            - engagement["current_score"]
        )

        if engagement_drop >= 10:
            score += 20
            factors.append({
                "factor": "Engagement decline",
                "impact": 20,
                "evidence": (
                    f"Engagement dropped by "
                    f"{engagement_drop:.0f} points."
                )
            })
        elif engagement_drop >= 5:
            score += 10
            factors.append({
                "factor": "Engagement decline",
                "impact": 10,
                "evidence": (
                    f"Engagement dropped by "
                    f"{engagement_drop:.0f} points."
                )
            })

    career = evidence["career"]

    if career:
        promotion_gap = career["years_since_promotion"]

        if promotion_gap >= 2:
            score += 15
            factors.append({
                "factor": "Promotion gap",
                "impact": 15,
                "evidence": (
                    f"{promotion_gap:.1f} years since "
                    f"last promotion."
                )
            })
        elif promotion_gap >= 1.5:
            score += 8
            factors.append({
                "factor": "Promotion gap",
                "impact": 8,
                "evidence": (
                    f"{promotion_gap:.1f} years since "
                    f"last promotion."
                )
            })

    if score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": min(score, 100),
        "risk_level": level,
        "factors": factors
    }


if __name__ == "__main__":
    evidence = get_employee_evidence("EMP-1042")

    import json

    print(
        json.dumps(
            calculate_risk(evidence),
            indent=2
        )
    )