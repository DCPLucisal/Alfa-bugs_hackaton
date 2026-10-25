
from backend.llm import generate_client_explanation, generate_manager_summary

def ai_pre_scoring(scoring_result: dict, company_data: dict) -> dict:
    """
    ИИ для клиента на этапе pre-scoring (до отправки).
    """
    facts = {
        "scoring_result": scoring_result,
        "company_data": company_data
    }
    
    ai_result = generate_client_explanation(facts)
    
    return {
        "prompt": ai_result.get("prompt"),
        "ai_answer_text": ai_result.get("ai_answer_text"),
        "ai_answer_parsed": ai_result.get("ai_answer_parsed")
    }


def ai_manager_summary(scoring_result: dict, company_data: dict) -> dict:
    """
    ИИ-резюме для менеджера (формальный тон, все детали).
    """
    facts = {
        "scoring_result": scoring_result,
        "company_data": company_data
    }
    
    ai_result = generate_manager_summary(facts)
    
    return {
        "prompt": ai_result.get("prompt"),
        "ai_answer_text": ai_result.get("ai_answer_text"),
        "ai_answer_parsed": ai_result.get("ai_answer_parsed")
    }


def ai_client_result(scoring_result: dict, company_data: dict, manager_comment: str | None = None) -> dict:
    """
    ИИ-объяснение для клиента после решения менеджера.
    """
    facts = {
        "scoring_result": scoring_result,
        "company_data": company_data
    }

    if manager_comment:
        facts["manager_comment"] = manager_comment
        
    ai_result = generate_client_explanation(facts)
    
    return {
        "prompt": ai_result.get("prompt"),
        "ai_answer_text": ai_result.get("ai_answer_text"),
        "ai_answer_parsed": ai_result.get("ai_answer_parsed")
    }