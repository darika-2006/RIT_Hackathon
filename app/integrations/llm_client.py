import json
import logging
import re
from typing import Dict, Any, Optional, Tuple
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an Intent Classifier and Entity Extractor for a Tamil Nadu Vernacular Voice Banking Assistant.
Target Region: Tamil Nadu (Tamil & Tanglish/English).

STRICT SAFETY RULE: NEVER generate financial numbers, balances, account details, interest rates, or EMIs.
Your job is ONLY to classify intent and extract slots into structured JSON.

Supported Intents:
1. balance_inquiry (Checking balance, money in account)
2. transaction_history (Recent transactions, mini statement)
3. jewel_loan_apply (Gold loan, jewel mortgage, grams pledged)
4. mudra_loan_apply (Business loan, Mudra scheme, shop loan)
5. shg_savings (Self Help Group / Mathi / மகளிர் குழு savings)
6. kcc_status (Kisan Credit Card / Crop loan / Kuruvai / Samba status)
7. scheme_inquiry (Magalir Urimai Thogai, PMJDY, PMFBY crop insurance)
8. help (General help, unclear request)

Return strictly valid JSON with no markdown block or extra text:
{
  "intent": "<one_of_the_above_intents>",
  "confidence": 0.95,
  "extracted_slots": {
    "jewel_weight_grams": 16.0,
    "jewel_type": "chain",
    "requested_amount": 75000.0,
    "business_type": "grocery shop"
  },
  "reasoning": "brief reason"
}"""


class LLMClient:
    def __init__(self):
        self.timeout = 2.5

    async def classify_intent(self, text: str) -> Optional[Tuple[str, float, Dict[str, Any]]]:
        """
        Attempts LLM classification down the fallback chain:
        1. Friend's GPU Ollama
        2. Groq Cloud API
        3. Local CPU Ollama
        Returns (intent, confidence, extracted_slots) or None on failure.
        """
        # Tier 1: Friend GPU Ollama
        result = await self._call_ollama(
            url=settings.FRIEND_GPU_OLLAMA_URL,
            model=settings.FRIEND_GPU_MODEL,
            user_text=text
        )
        if result:
            logger.info("Intent classified via Friend GPU Ollama")
            return result

        # Tier 2: Groq Cloud API
        if settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith("gsk_your"):
            result = await self._call_groq(user_text=text)
            if result:
                logger.info("Intent classified via Groq Cloud API")
                return result

        # Tier 3: Local CPU Ollama
        result = await self._call_ollama(
            url=settings.LOCAL_OLLAMA_URL,
            model=settings.LOCAL_OLLAMA_MODEL,
            user_text=text
        )
        if result:
            logger.info("Intent classified via Local CPU Ollama")
            return result

        logger.warning("All LLM endpoints unavailable or failed. Falling back to rules.")
        return None

    async def _call_ollama(self, url: str, model: str, user_text: str) -> Optional[Tuple[str, float, Dict[str, Any]]]:
        try:
            endpoint = f"{url.rstrip('/')}/chat/completions"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(endpoint, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return self._parse_json_response(content)
        except Exception as e:
            logger.debug(f"Ollama call to {url} failed: {e}")
        return None

    async def _call_groq(self, user_text: str) -> Optional[Tuple[str, float, Dict[str, Any]]]:
        try:
            endpoint = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": settings.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(endpoint, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return self._parse_json_response(content)
        except Exception as e:
            logger.debug(f"Groq call failed: {e}")
        return None

    def _parse_json_response(self, text: str) -> Optional[Tuple[str, float, Dict[str, Any]]]:
        try:
            # Clean markdown code blocks if present
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?", "", cleaned).rstrip("`").strip()
            
            data = json.loads(cleaned)
            intent = data.get("intent", "unclear")
            confidence = float(data.get("confidence", 0.8))
            slots = data.get("extracted_slots", {})
            if isinstance(slots, dict):
                return intent, confidence, slots
        except Exception as e:
            logger.debug(f"Failed to parse LLM response: {e}")
        return None


llm_client = LLMClient()
