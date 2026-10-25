"""LLM-модуль кредитного кабинета."""

from .service import generate_client_explanation, generate_manager_summary

__all__ = [
    "generate_client_explanation",
    "generate_manager_summary",
]
