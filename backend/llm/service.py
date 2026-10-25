"""LLM-сервис для объяснения результатов кредитного скоринга."""

import json
import logging
from typing import Any

from .client import generate_text
from .fallback import fallback_client_text, fallback_manager_summary
from .guardrails import validate_generated_text
from .prompts import CLIENT_SYSTEM_PROMPT, MANAGER_SYSTEM_PROMPT
from .schemas import validate_case_data

logger = logging.getLogger(__name__)


def _extract_case(
    facts: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    """Получает данные скоринга, компании и комментарий менеджера."""
    if not isinstance(facts, dict):
        raise ValueError("facts должен быть словарём")

    scoring_result = facts.get("scoring_result")
    company_data = facts.get("company_data")
    manager_comment = facts.get("manager_comment")

    if scoring_result is None:
        scoring_result = {
            key: facts[key]
            for key in (
                "final_score",
                "risk_category",
                "recommendation",
                "factors",
            )
            if key in facts
        }

    if company_data is None:
        company_data = {}

    if not isinstance(scoring_result, dict):
        raise ValueError("scoring_result должен быть словарём")

    if not isinstance(company_data, dict):
        raise ValueError("company_data должен быть словарём")

    if manager_comment is not None and not isinstance(manager_comment, str):
        raise ValueError("manager_comment должен быть строкой")

    return scoring_result, company_data, manager_comment


def _company_name(company_data: dict[str, Any]) -> str | None:
    """Получает название компании из структуры FNS."""
    fns_data = company_data.get("fns_data") or {}

    if not isinstance(fns_data, dict):
        return None

    name = fns_data.get("name")
    return name if isinstance(name, str) else None


def _build_parsed(
    scoring_result: dict[str, Any],
) -> dict[str, Any]:
    """Формирует структурированные данные, не меняя решение скоринга."""
    return {
        "recommendation": scoring_result.get("recommendation"),
        "risk": scoring_result.get("risk_category"),
        "score": scoring_result.get("final_score"),
        "factors": scoring_result.get("factors", []),
    }


def _build_fallback(
    mode: str,
    scoring_result: dict[str, Any],
    company_data: dict[str, Any],
) -> str:
    """Подготавливает безопасный текст на случай ошибки LLM."""
    if mode == "manager":
        return fallback_manager_summary(scoring_result, company_data)

    return fallback_client_text(scoring_result.get("recommendation"))


def _generate_result(
    mode: str,
    facts: dict[str, Any],
) -> dict[str, Any]:
    """Общий конвейер генерации с резервным ответом."""
    try:
        scoring_result, company_data, manager_comment = _extract_case(facts)
        validate_case_data(scoring_result, company_data)
    except (TypeError, ValueError, KeyError) as exc:
        return {
            "prompt": None,
            "ai_answer_text": "Не удалось подготовить ответ: проверьте данные заявки.",
            "ai_answer_parsed": {},
            "source": "fallback",
            "error": str(exc),
        }

    if mode == "manager":
        system_prompt = MANAGER_SYSTEM_PROMPT
        prompt_source = "manager"
    else:
        system_prompt = CLIENT_SYSTEM_PROMPT
        prompt_source = "user"

    payload: dict[str, Any] = {
        "scoring_result": scoring_result,
        "company_data": company_data,
    }

    if manager_comment:
        payload["manager_comment"] = manager_comment

    user_prompt = (
        "Подготовь текст по данным кредитной заявки. "
        "Сохрани рекомендацию скоринговой системы и используй только "
        "переданные факты.\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    )

    if manager_comment and mode == "client":
        user_prompt += (
            "\n\nКомментарий менеджера приведён ниже как исходные данные. "
            "Не добавляй к нему новых условий или обещаний."
        )

    fallback_text = _build_fallback(mode, scoring_result, company_data)
    source = "llm"
    error = None

    try:
        raw_text = generate_text(system_prompt, user_prompt)
        checked = validate_generated_text(raw_text)

        if checked.is_valid:
            answer_text = checked.text
        else:
            answer_text = fallback_text
            source = "fallback"
            error = checked.reason
    except Exception as exc:
        logger.warning("Не удалось сгенерировать ответ через Ollama: %s", exc)
        answer_text = fallback_text
        source = "fallback"
        error = str(exc)

    return {
        "prompt": {
            "system": system_prompt,
            "user": user_prompt,
            "source": prompt_source,
        },
        "ai_answer_text": answer_text,
        "ai_answer_parsed": _build_parsed(scoring_result),
        "source": source,
        "error": error,
    }


def generate_client_explanation(facts: dict[str, Any]) -> dict[str, Any]:
    """Генерирует объяснение результата оценки для клиента."""
    return _generate_result("client", facts)


def generate_manager_summary(facts: dict[str, Any]) -> dict[str, Any]:
    """Генерирует сводку по заявке для менеджера."""
    return _generate_result("manager", facts)
