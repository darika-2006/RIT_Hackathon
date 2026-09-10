import logging
from typing import Dict, Any, Tuple
from app.integrations.llm_client import llm_client
from app.intent.rules import classify_intent_by_rules

logger = logging.getLogger(__name__)

VALID_INTENTS = {
    "balance_inquiry",
    "transaction_history",
    "jewel_loan_apply",
    "mudra_loan_apply",
    "shg_savings",
    "kcc_status",
    "scheme_inquiry",
    "help",
    "unclear"
}


async def classify_intent(text: str) -> Tuple[str, float, Dict[str, Any]]:
    """
    Resilient Intent Classifier following Fallback Hierarchy:
    1. Primary: Remote Friend's GPU Ollama
    2. Secondary: Groq Cloud API
    3. Tertiary: Local CPU Ollama
    4. Fallback: Regex Rules Matcher (Tamil & Tanglish)
    """
    # 1-3: Try LLM Stack
    llm_res = await llm_client.classify_intent(text)
    if llm_res:
        intent, conf, slots = llm_res
        if intent in VALID_INTENTS and conf >= 0.5:
            # Also run rules to enrich slot extraction if rules caught specific numbers
            rule_intent, rule_conf, rule_slots = classify_intent_by_rules(text)
            merged_slots = {**rule_slots, **slots}
            return intent, conf, merged_slots

    # 4: Rule-based fallback
    logger.info("Falling back to rule-based Tamil/Tanglish intent classification")
    return classify_intent_by_rules(text)
