
from pprint import pprint

from llm.service import (
    generate_client_explanation,
    generate_manager_summary,
)


facts = {
    "scoring_result": {
        "final_score": 75,
        "risk_category": "умеренный",
        "recommendation": "approve",
        "factors": [
            {
                "reason": "Компания ведёт деятельность достаточное время"
            },
            {
                "reason": "В предоставленных данных нет просрочек"
            },
        ],
    },
    "company_data": {
        "fns_data": {
            "name": "Тестовая компания",
            "okved": "62.01",
            "form": "ООО",
            "status": "Действующая",
        },
        "bki_data": {
            "found_in_bki": True,
            "overdue_count_12m": 0,
        },
    },
}

print("\n=== ОБЪЯСНЕНИЕ ДЛЯ КЛИЕНТА ===")
client_result = generate_client_explanation(facts)
pprint(client_result, sort_dicts=False)

print("\n=== СВОДКА ДЛЯ МЕНЕДЖЕРА ===")
manager_result = generate_manager_summary(facts)
pprint(manager_result, sort_dicts=False)
