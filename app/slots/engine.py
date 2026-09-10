import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Required slots per intent
REQUIRED_SLOTS = {
    "jewel_loan_apply": ["jewel_weight_grams", "jewel_type", "requested_amount"],
    "mudra_loan_apply": ["business_type", "requested_amount", "annual_turnover"]
}

# Default values for optional slots
DEFAULT_SLOTS = {
    "jewel_loan_apply": {"tenure_months": 12},
    "mudra_loan_apply": {"tenure_months": 36, "category": "Kishore"}
}

# Multilingual prompts for missing slots
SLOT_PROMPTS = {
    "jewel_weight_grams": {
        "ta": "எத்தனை கிராம் நகை அடமானம் வைக்க விரும்புகிறீர்கள்?",
        "en": "How many grams of gold jewelry do you wish to pledge?"
    },
    "jewel_type": {
        "ta": "நீங்கள் என்ன வகையான நகை அடமானம் வைக்கிறீர்கள்? (உதாரணம்: சங்கிலி, வளையல், மோதிரம், ஆரம்)",
        "en": "What type of jewelry are you pledging? (e.g. chain, bangles, ring, necklace)"
    },
    "requested_amount": {
        "ta": "உங்களுக்கு எவ்வளவு கடன் தொகை தேவைப்படுகிறது?",
        "en": "How much loan amount do you require?"
    },
    "business_type": {
        "ta": "உங்கள் தொழில் அல்லது கடையின் பெயர் என்ன? (உதாரணம்: மளிகை கடை, தையல், பால் பண்ணை)",
        "en": "What is the nature of your business or shop? (e.g. grocery shop, tailoring, dairy)"
    },
    "annual_turnover": {
        "ta": "உங்கள் தொழிலின் ஆண்டு வருமானம் அல்லது டர்ன்ஓவர் எவ்வளவு?",
        "en": "What is your business's annual turnover?"
    }
}


class SlotEngine:
    def process_slots(
        self,
        intent: str,
        current_slots: Dict[str, Any],
        newly_extracted_slots: Dict[str, Any],
        user_text: str,
        customer_profile: Optional[Any] = None
    ) -> Tuple[Dict[str, Any], List[str], Optional[Dict[str, str]]]:
        """
        Slot resolution cascade.
        Merges existing slots, vault profile pre-fills, and newly extracted slots.
        Identifies missing slots and generates targeted prompt for the next missing slot.
        Returns: (merged_slots, missing_slots, next_prompt_dict)
        """
        # Start with current slots
        merged = dict(current_slots or {})

        # Apply defaults if applicable
        if intent in DEFAULT_SLOTS:
            for k, v in DEFAULT_SLOTS[intent].items():
                if k not in merged:
                    merged[k] = v

        # Pre-fill vault fields if customer profile exists
        if customer_profile:
            if hasattr(customer_profile, "account_number") and customer_profile.account_number:
                merged["account_number"] = customer_profile.account_number
            if hasattr(customer_profile, "full_name") and customer_profile.full_name:
                merged["customer_name"] = customer_profile.full_name

        # Merge newly extracted slots from LLM / Rules
        for k, v in newly_extracted_slots.items():
            if v is not None:
                merged[k] = v

        # Heuristic slot extraction directly from raw text if missing
        merged = self._extract_slots_heuristically(intent, merged, user_text)

        # Check required slots for this intent
        required = REQUIRED_SLOTS.get(intent, [])
        missing = [s for s in required if s not in merged or merged[s] is None]

        # Determine prompt for next missing slot
        next_prompt = None
        if missing:
            next_slot = missing[0]
            next_prompt = SLOT_PROMPTS.get(next_slot, {
                "ta": f"தயவுசெய்து {next_slot} விவரத்தை வழங்கவும்.",
                "en": f"Please provide details for {next_slot}."
            })

        return merged, missing, next_prompt

    def _extract_slots_heuristically(self, intent: str, slots: Dict[str, Any], text: str) -> Dict[str, Any]:
        cleaned = text.lower().strip()

        # If we are waiting for jewel_weight_grams
        if "jewel_weight_grams" not in slots or slots["jewel_weight_grams"] is None:
            # Match numbers
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:கிராம்|கிரா|grams|gram|g\b)?", cleaned)
            if m:
                try:
                    val = float(m.group(1))
                    if 0.5 <= val <= 1000: # Reasonable gold weight range
                        slots["jewel_weight_grams"] = val
                except ValueError:
                    pass

        # Jewel type matching
        if "jewel_type" not in slots or slots["jewel_type"] is None:
            jewel_types = {
                "chain": ["சங்கிலி", "செயின்", "chain"],
                "bangles": ["வளையல்", "காப்பு", "bangles", "bangle"],
                "ring": ["மோதிரம்", "ring"],
                "necklace": ["ஆரம்", "ஹாரம்", "நெக்லஸ்", "necklace", "haram"],
                "coin": ["நாணயம்", "காசு", "coin"]
            }
            for j_key, j_words in jewel_types.items():
                for w in j_words:
                    if w in cleaned:
                        slots["jewel_type"] = j_key
                        break

        # Amount matching: e.g. "75000", "75 ஆயிரம்", "75,000", "1 லட்சம்"
        if "requested_amount" not in slots or slots["requested_amount"] is None:
            lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:லட்சம்|lakh|lakhs)", cleaned)
            if lakh_match:
                slots["requested_amount"] = float(lakh_match.group(1)) * 100000.0
            else:
                thousand_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:ஆயிரம்|k|thousand)", cleaned)
                if thousand_match:
                    slots["requested_amount"] = float(thousand_match.group(1)) * 1000.0
                else:
                    amt_match = re.search(r"(\d[\d,]{3,})", cleaned)
                    if amt_match:
                        try:
                            slots["requested_amount"] = float(amt_match.group(1).replace(",", ""))
                        except ValueError:
                            pass

        # Business type matching for Mudra
        if intent == "mudra_loan_apply" and ("business_type" not in slots or slots["business_type"] is None):
            biz_map = {
                "grocery shop": ["மளிகை", "மளிகைகடை", "grocery", "shop", "கடை"],
                "tailoring": ["தையல்", "டெய்லரிங்", "tailor", "tailoring"],
                "dairy": ["பால் பண்ணை", "பால்", "dairy", "milk"],
                "textile": ["ஜவுளி", "துணி", "textile", "clothes"]
            }
            for b_key, b_words in biz_map.items():
                for w in b_words:
                    if w in cleaned:
                        slots["business_type"] = b_key
                        break

        return slots


slot_engine = SlotEngine()
