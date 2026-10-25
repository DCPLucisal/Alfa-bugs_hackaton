from dataclasses import dataclass


MAX_RESPONSE_LENGTH = 3000

ERROR_MARKERS = (
    "traceback (most recent call last)",
    "connection refused",
    "internal server error",
    "thinking process",
)


@dataclass
class GuardrailResult:
    is_valid: bool
    text: str
    reason: str | None = None


def validate_generated_text(text: str) -> GuardrailResult:
    if not isinstance(text, str):
        return GuardrailResult(
            False, "", "Ответ модели не является текстом."
        )

    cleaned = text.strip()

    if not cleaned:
        return GuardrailResult(
            False, "", "Модель вернула пустой ответ."
        )

    if len(cleaned) > MAX_RESPONSE_LENGTH:
        return GuardrailResult(
            False,
            "",
            f"Ответ превышает лимит {MAX_RESPONSE_LENGTH} символов.",
        )

    lower_text = cleaned.lower()

    if any(marker in lower_text for marker in ERROR_MARKERS):
        return GuardrailResult(
            False,
            "",
            "Ответ содержит признаки технической ошибки или внутреннего вывода.",
        )

    return GuardrailResult(True, cleaned)


def check_response(text: str) -> str:
    result = validate_generated_text(text)

    if not result.is_valid:
        raise ValueError(
            result.reason or "Ответ модели не прошёл проверку."
        )

    return result.text
