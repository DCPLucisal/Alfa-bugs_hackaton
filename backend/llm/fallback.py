"""Резервные ответы, если LLM недоступна или вернула некорректный текст."""

from typing import Any


FALLBACK_TEXTS = {
    "approve": (
        "По результатам предварительной оценки заявка получила положительную "
        "рекомендацию. Итоговые условия необходимо уточнить у менеджера."
    ),
    "approve_with_conditions": (
        "По результатам предварительной оценки заявка может рассматриваться "
        "при выполнении дополнительных условий. Уточните детали у менеджера."
    ),
    "request_info": (
        "Для продолжения рассмотрения заявки может потребоваться дополнительная "
        "информация. Уточните у менеджера, какие сведения необходимо предоставить."
    ),
    "rejected_with_alternative": (
        "По результатам оценки текущая заявка не получила положительной "
        "рекомендации. Обсудите с менеджером возможные дальнейшие действия."
    ),
}


def fallback_client_text(decision: Any) -> str:
    """Возвращает безопасный шаблон по рекомендации скоринговой системы."""
    if isinstance(decision, dict):
        decision = decision.get("recommendation", decision.get("decision", ""))

    if not isinstance(decision, str):
        decision = ""

    return FALLBACK_TEXTS.get(
        decision.strip().lower(),
        "Заявка находится на рассмотрении. Уточните актуальный статус у менеджера.",
    )


def fallback_manager_summary(
    scoring_result: dict | None = None,
    company_data: dict | None = None,
) -> str:
    """Резервная сводка менеджеру без выдуманных фактов."""
    scoring_result = scoring_result or {}
    company_data = company_data or {}

    recommendation = scoring_result.get(
        "recommendation",
        scoring_result.get("decision", "не указана"),
    )
    score = scoring_result.get("final_score", "не указан")
    risk = scoring_result.get("risk_category", "не указана")
    factors = scoring_result.get("factors", [])

    if not isinstance(factors, list):
        factors = []

    factor_lines = []
    for factor in factors[:10]:
        if isinstance(factor, dict):
            name = factor.get("name") or factor.get("title") or "Фактор"
            description = factor.get("description") or factor.get("value") or ""
            factor_lines.append(f"- {name}: {description}".rstrip(": "))
        elif isinstance(factor, str):
            factor_lines.append(f"- {factor}")

    result = [
        "Сводка по кредитной заявке",
        f"Рекомендация скоринга: {recommendation}",
        f"Итоговый балл: {score}",
        f"Категория риска: {risk}",
    ]

    if factor_lines:
        result.append("Факторы оценки:\n" + "\n".join(factor_lines))
    else:
        result.append("Факторы оценки: не предоставлены.")

    result.append(
        "Перед принятием решения проверьте исходные данные и действующие правила."
    )
    return "\n".join(result)
