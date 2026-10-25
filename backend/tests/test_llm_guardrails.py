import unittest

from llm.guardrails import validate_generated_text


class TestLLMGuardrails(unittest.TestCase):

    def test_accepts_normal_response(self):
        result = validate_generated_text(
            "Скоринговая система выдала положительную рекомендацию."
        )
        self.assertTrue(result.is_valid)

    def test_rejects_empty_response(self):
        result = validate_generated_text("   ")
        self.assertFalse(result.is_valid)

    def test_rejects_non_text_response(self):
        result = validate_generated_text(None)
        self.assertFalse(result.is_valid)

    def test_rejects_response_that_is_too_long(self):
        result = validate_generated_text("А" * 3001)
        self.assertFalse(result.is_valid)

    def test_rejects_technical_error(self):
        result = validate_generated_text(
            "Traceback (most recent call last)"
        )
        self.assertFalse(result.is_valid)

    def test_rejects_internal_thinking_marker(self):
        result = validate_generated_text(
            "Thinking Process: let me reason about this"
        )
        self.assertFalse(result.is_valid)


if __name__ == "__main__":
    unittest.main()
