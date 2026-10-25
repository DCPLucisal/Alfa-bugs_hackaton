
import unittest
from unittest.mock import patch

from llm.service import (
    generate_client_explanation,
    generate_manager_summary,
)


SAMPLE_FACTS = {
    "scoring_result": {
        "final_score": 75,
        "risk_category": "умеренный",
        "recommendation": "approve",
        "factors": [
            {"reason": "Достаточный срок деятельности компании"}
        ],
    },
    "company_data": {
        "fns_data": {
            "name": "Тестовая компания",
        },
        "bki_data": {
            "found_in_bki": True,
            "overdue_count_12m": 0,
        },
    },
}


class TestLLMService(unittest.TestCase):

    @patch("llm.service.validate_case_data")
    @patch("llm.service.generate_text")
    def test_client_explanation_uses_llm(
        self, mock_generate_text, mock_validate
    ):
        mock_generate_text.return_value = (
            "Компания получила положительную рекомендацию."
        )

        result = generate_client_explanation(SAMPLE_FACTS)

        self.assertEqual(result["source"], "llm")
        self.assertEqual(
            result["ai_answer_text"],
            "Компания получила положительную рекомендацию.",
        )
        self.assertIsNone(result["error"])
        self.assertEqual(
            result["ai_answer_parsed"]["recommendation"],
            "approve",
        )
        self.assertIn("system", result["prompt"])

    @patch("llm.service.validate_case_data")
    @patch("llm.service.generate_text")
    def test_client_explanation_uses_fallback_on_error(
        self, mock_generate_text, mock_validate
    ):
        mock_generate_text.side_effect = RuntimeError("Ollama недоступна")

        result = generate_client_explanation(SAMPLE_FACTS)

        self.assertEqual(result["source"], "fallback")
        self.assertTrue(result["ai_answer_text"])
        self.assertEqual(result["error"], "Ollama недоступна")
        self.assertEqual(
            result["ai_answer_parsed"]["recommendation"],
            "approve",
        )

    @patch("llm.service.validate_case_data")
    @patch("llm.service.generate_text")
    def test_manager_summary_uses_llm(
        self, mock_generate_text, mock_validate
    ):
        mock_generate_text.return_value = "Сводка по заявке готова."

        result = generate_manager_summary(SAMPLE_FACTS)

        self.assertEqual(result["source"], "llm")
        self.assertEqual(
            result["ai_answer_text"],
            "Сводка по заявке готова.",
        )
        self.assertIsNone(result["error"])
        self.assertEqual(
            result["ai_answer_parsed"]["recommendation"],
            "approve",
        )

    @patch("llm.service.validate_case_data")
    @patch("llm.service.generate_text")
    def test_manager_summary_uses_fallback_on_error(
        self, mock_generate_text, mock_validate
    ):
        mock_generate_text.side_effect = RuntimeError("Тайм-аут")

        result = generate_manager_summary(SAMPLE_FACTS)

        self.assertEqual(result["source"], "fallback")
        self.assertIn("Сводка", result["ai_answer_text"])
        self.assertEqual(result["error"], "Тайм-аут")


if __name__ == "__main__":
    unittest.main()
