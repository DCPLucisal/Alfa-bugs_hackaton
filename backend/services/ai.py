def ai_pre_scoring(scoring_result: dict, company_data: dict) -> dict:
    """
    ИИ для клиента на этапе pre-scoring (до отправки).
    Простой язык, совет: что можно изменить.
    """
    fns = company_data.get("fns_data") or {}
    name = fns.get("name", "Компания")
    score = scoring_result["final_score"]
    risk = scoring_result["risk_category"]
    rec = scoring_result["recommendation"]
    
    if rec == "approve":
        text = (
            f"Компания «{name}» получила оценку {score}/100 (низкий риск). "
            f"Хорошие шансы на одобрение! Можете отправлять заявку."
        )
    elif rec == "approve_with_conditions":
        text = (
            f"Компания «{name}» получила оценку {score}/100 (средний риск). "
            f"Мы можем одобрить кредит с условиями. Рекомендуем снизить сумму "
            f"или увеличить срок, чтобы повысить шансы."
        )
    elif rec == "request_info":
        text = (
            f"Компания «{name}» получила оценку {score}/100. "
            f"Для финального решения потребуются дополнительные документы "
            f"(например, выписка по счету за 3 месяца)."
        )
    else:  # rejected_with_alternative
        text = (
            f"Компания «{name}» получила оценку {score}/100 (высокий риск). "
            f"К сожалению, текущие параметры могут привести к отказу. "
            f"Рекомендуем снизить сумму или рассмотреть другой продукт "
            f"(например, кредитную линию)."
        )
    
    return {
        "prompt": {
            "system": "Ты кредитный аналитик. Объясни клиенту оценку простым языком.",
            "user": f"Компания: {name}, Балл: {score}, Риск: {risk}",
            "source": "user",
        },
        "ai_answer_text": text,
        "ai_answer_parsed": {"recommendation": rec, "risk": risk, "score": score},
    }


def ai_manager_summary(scoring_result: dict, company_data: dict) -> dict:
    """
    ИИ-резюме для менеджера (формальный тон, все детали).
    """
    fns = company_data.get("fns_data") or {}
    bki = company_data.get("bki_data") or {}
    
    name = fns.get("name", "Компания")
    okved = fns.get("okved", "")
    form = fns.get("form", "")
    status = fns.get("status", "")
    overdue = bki.get("overdue_count_12m", 0)
    found_in_bki = bki.get("found_in_bki", False)
    
    score = scoring_result["final_score"]
    risk = scoring_result["risk_category"]
    rec = scoring_result["recommendation"]
    factors = scoring_result["factors"]
    
    text = (
        f"Заявка компании «{name}» (ОКВЭД: {okved}, форма: {form}, статус: {status}). "
        f"Кредитная история: {'есть' if found_in_bki else 'нет'}, "
        f"просрочек за 12 мес.: {overdue}. "
        f"Итоговый балл: {score}/100, риск: {risk}. "
        f"Рекомендация системы: {rec}. "
        f"Ключевые факторы: {', '.join([f['reason'] for f in factors])}."
    )
    
    return {
        "prompt": {
            "system": "Ты кредитный аналитик. Сформируй резюме для менеджера.",
            "user": f"Компания: {name}, Балл: {score}, Факторы: {factors}",
            "source": "manager",
        },
        "ai_answer_text": text,
        "ai_answer_parsed": {
            "recommendation": rec,
            "risk": risk,
            "score": score,
            "factors": factors,
        },
    }


def ai_client_result(scoring_result: dict, company_data: dict, manager_comment: str | None = None) -> dict:
    """
    ИИ-объяснение для клиента после решения менеджера.
    Включает альтернативы и комментарий менеджера.
    """
    fns = company_data.get("fns_data") or {}
    name = fns.get("name", "Компания")
    score = scoring_result["final_score"]
    risk = scoring_result["risk_category"]
    rec = scoring_result["recommendation"]
    
    if rec == "approve":
        text = (
            f"Поздравляем! Компания «{name}» получила одобрение. "
            f"Балл: {score}/100. Деньги будут зачислены на счет после подписания договора."
        )
    elif rec == "approve_with_conditions":
        text = (
            f"Компания «{name}» получила предварительное одобрение с условиями. "
            f"Балл: {score}/100. Для получения полной суммы потребуется залог "
            f"или поручитель. Свяжитесь с менеджером для уточнения."
        )
    elif rec == "request_info":
        text = (
            f"Компания «{name}» получила оценку {score}/100. "
            f"Для финального решения нужны дополнительные документы. "
            f"Загрузите выписку по счету за 3 месяца в личном кабинете."
        )
    else:  # rejected_with_alternative
        text = (
            f"К сожалению, мы не можем одобрить кредит на запрошенную сумму. "
            f"Причина: {risk} риск (балл {score}/100). "
            f"Но мы можем предложить альтернативу — кредитную линию на меньшую сумму "
            f"без залога. Это закроет кассовый разрыв."
        )
    
    # Если менеджер оставил комментарий — добавляем его
    if manager_comment:
        text += f"\n\nКомментарий менеджера: «{manager_comment}»"
    
    return {
        "prompt": {
            "system": "Ты кредитный аналитик. Объясни клиенту финальное решение.",
            "user": f"Компания: {name}, Балл: {score}, Рекомендация: {rec}",
            "source": "user",
        },
        "ai_answer_text": text,
        "ai_answer_parsed": {"recommendation": rec, "risk": risk, "score": score},
    }