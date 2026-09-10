import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.integrations.llm_client import llm_client
from app.intent.rules import classify_intent_by_rules

logger = logging.getLogger(__name__)


class IntentResult(BaseModel):
    intent: str = Field(..., description="Classified intent name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entity slots")


VALID_INTENTS = {
    "balance_inquiry",
    "transaction_history",
    "jewel_loan_apply",
    "mudra_loan_apply",
    "shg_savings",
    "kcc_status",
    "help",
    "unclear"
}


class IntentClassifier:
    async def classify(self, text: str) -> IntentResult:
        """
        Classifies Tamil and Tanglish user input into a structured IntentResult.
        Pipeline: LLM (Friend GPU -> Groq -> Local CPU) -> Rule-based Tamil/Tanglish matcher fallback.
        """
        # 1. Attempt LLM classification
        llm_res = await llm_client.classify_intent(text)
        if llm_res:
            intent, conf, slots = llm_res
            if intent in VALID_INTENTS and conf >= 0.5:
                # Run rules to complement slot extraction
                rule_intent, rule_conf, rule_slots = classify_intent_by_rules(text)
                merged_entities = {**rule_slots, **slots}
                return IntentResult(
                    intent=intent,
                    confidence=conf,
                    entities=merged_entities
                )

        # 2. Fallback to Regex Rules (Tamil & Tanglish)
        logger.info("Using rule-based Tamil/Tanglish intent classifier fallback")
        intent, conf, slots = classify_intent_by_rules(text)
        return IntentResult(
            intent=intent,
            confidence=conf,
            entities=slots
        )


intent_classifier = IntentClassifier()
