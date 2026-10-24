def calculate_score(fns_data: dict, bki_data: dict, amount: int, term_value: int, term_unit: str = "months") -> dict:
    score = 100
    factors = []

    if fns_data is None:
        fns_data = {}
    if bki_data is None:
        bki_data = {}

    if term_unit == "days":
        term_months = term_value / 30
    elif term_unit == "years":
        term_months = term_value * 12
    else:
        term_months = term_value

    okved = str(fns_data.get("okved", ""))
    okved_prefix = okved[:2] 

    if okved_prefix in ("45", "46", "47"):
        score -= 20
        factors.append({"factor": "industry", "impact": -20, "reason": "Торговля - высокий риск"})
    elif okved_prefix.isdigit() and 10 <= int(okved_prefix) <= 33:
        score -= 5
        factors.append({"factor": "industry", "impact": -5, "reason": "Производство - низкий риск"})
    elif okved_prefix in ("41", "42", "43"):
        score -= 15
        factors.append({"factor": "industry", "impact": -15, "reason": "Строительство - средний риск"})
    elif okved_prefix.isdigit() and 58 <= int(okved_prefix) <= 63:
        score -= 5
        factors.append({"factor": "industry", "impact": -5, "reason": "IT - низкий риск"})


    if fns_data.get("form") == "IP":
        score -= 10
        factors.append({"factor": "form", "impact": -10, "reason": "ИП - упрощенная отчетность"})

    if amount > 5_000_000:
        score -= 15
        factors.append({"factor": "amount", "impact": -15, "reason": "Сумма > 5 млн"})
    elif amount > 3_000_000:
        score -= 5
        factors.append({"factor": "amount", "impact": -5, "reason": "Сумма > 3 млн"})

    if term_months > 36:
        score -= 15
        factors.append({"factor": "term", "impact": -15, "reason": f"Срок > 3 лет ({round(term_months)} мес.)"})
    elif term_months > 24:
        score -= 5
        factors.append({"factor": "term", "impact": -5, "reason": f"Срок > 2 лет ({round(term_months)} мес.)"})

    if not bki_data.get("found_in_bki", False):
        score -= 10
        factors.append({"factor": "bki", "impact": -10, "reason": "Нет кредитной истории"})
    elif bki_data.get("overdue_count_12m", 0) > 0:
        score -= 30
        factors.append({"factor": "bki", "impact": -30, "reason": f"Просрочки: {bki_data['overdue_count_12m']}"})

    if fns_data.get("status") != "active":
        score = 0
        factors.append({"factor": "status", "impact": -100, "reason": "Компания не действующая"})

    if score >= 70:
        risk = "low"
        recommendation = "approve"
    elif score >= 50:
        risk = "middle"
        recommendation = "approve_with_conditions"
    elif score >= 30:
        risk = "middle"
        recommendation = "request_info"
    else:
        risk = "high"
        recommendation = "rejected_with_alternative"

    return {
        "final_score": max(0, score),
        "risk_category": risk,
        "recommendation": recommendation,
        "factors": factors,
    }