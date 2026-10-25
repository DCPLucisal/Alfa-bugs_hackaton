from typing import Any


ALLOWED_RECOMMENDATIONS = {
    "approve",
    "approve_with_conditions",
    "request_info",
    "rejected_with_alternative",
}


def validate_case_data(
    scoring_result: dict[str, Any],
    company_data: dict[str, Any],
) -> None:
    """Проверяет входные данные перед обращением к LLM."""

    if not isinstance(scoring_result, dict):
        raise ValueError("scoring_result должен быть словарём")

    if not isinstance(company_data, dict):
        raise ValueError("company_data должен быть словарём")

    recommendation = scoring_result.get("recommendation")

    if recommendation not in ALLOWED_RECOMMENDATIONS:
        raise ValueError(
            f"Неизвестная рекомендация скоринга: {recommendation}"
        )

    if "final_score" not in scoring_result:
        raise ValueError("В scoring_result отсутствует final_score")

    if "risk_category" not in scoring_result:
        raise ValueError("В scoring_result отсутствует risk_category")

    if not isinstance(scoring_result.get("factors", []), list):
        raise ValueError("Поле factors должно быть списком")
