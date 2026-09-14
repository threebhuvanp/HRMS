from dataloader import load_all_data


def calculate_risk(employee):
    score = 0
    factors = []

    attendance = employee["attendance"]
    performance = employee["performance"]
    engagement = employee["engagement"]
    career = employee["career"]

    # Attendance signal
    attendance_drop = (
        attendance["previous_attendance_rate"]
        - attendance["attendance_rate"]
    )

    if attendance_drop >= 7:
        score += 20
        factors.append({
            "factor": "Attendance decline",
            "impact": 20,
            "evidence": f"Attendance dropped by {attendance_drop} percentage points."
        })
    elif attendance_drop >= 3:
        score += 10
        factors.append({
            "factor": "Attendance decline",
            "impact": 10,
            "evidence": f"Attendance dropped by {attendance_drop} percentage points."
        })

    # Performance signal
    performance_drop = (
        performance["previous_performance_score"]
        - performance["performance_score"]
    )

    if performance_drop >= 1:
        score += 20
        factors.append({
            "factor": "Performance decline",
            "impact": 20,
            "evidence": f"Performance score dropped by {performance_drop:.1f}."
        })
    elif performance_drop >= 0.5:
        score += 10
        factors.append({
            "factor": "Performance decline",
            "impact": 10,
            "evidence": f"Performance score dropped by {performance_drop:.1f}."
        })

    # Engagement signal
    engagement_drop = (
        engagement["previous_engagement_score"]
        - engagement["engagement_score"]
    )

    if engagement_drop >= 10:
        score += 20
        factors.append({
            "factor": "Engagement decline",
            "impact": 20,
            "evidence": f"Engagement score dropped by {engagement_drop} points."
        })
    elif engagement_drop >= 5:
        score += 10
        factors.append({
            "factor": "Engagement decline",
            "impact": 10,
            "evidence": f"Engagement score dropped by {engagement_drop} points."
        })

    # Career progression signal
    years_since_promotion = career["years_since_promotion"]

    if years_since_promotion >= 2:
        score += 15
        factors.append({
            "factor": "Promotion gap",
            "impact": 15,
            "evidence": f"{years_since_promotion} years since last promotion."
        })
    elif years_since_promotion >= 1.5:
        score += 8
        factors.append({
            "factor": "Promotion gap",
            "impact": 8,
            "evidence": f"{years_since_promotion} years since last promotion."
        })

    # Overall risk level
    if score >= 60:
        risk_level = "HIGH"
    elif score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "employee_id": employee["employee_id"],
        "risk_score": score,
        "risk_level": risk_level,
        "factors": factors
    }


if __name__ == "__main__":
    data = load_all_data()

    for employee_id, employee in data.items():
        result = calculate_risk(employee)

        print("\n" + "=" * 50)
        print(f"Employee: {employee_id}")
        print(f"Risk Score: {result['risk_score']}")
        print(f"Risk Level: {result['risk_level']}")
        print("Factors:")

        for factor in result["factors"]:
            print(
                f"- {factor['factor']} "
                f"(+{factor['impact']}): {factor['evidence']}"
            )