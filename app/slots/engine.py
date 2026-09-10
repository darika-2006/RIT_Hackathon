import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.schemas import Customer360

logger = logging.getLogger(__name__)

# Required slots for Jewel Loan
JEWEL_LOAN_REQUIRED_SLOTS = [
    "jewel_weight_grams",
    "jewel_type",
    "requested_amount",
    "tenure_months"
]

TOTAL_APPLICATION_QUESTIONS = 22

# Multilingual prompts for missing slots
SLOT_PROMPTS = {
    "jewel_weight_grams": {
        "ta": "உங்கள் விவரங்கள் சரிபார்க்கப்பட்டன. எத்தனை கிராம் நகை அடமானம் வைக்க விரும்புகிறீர்கள்?",
        "en": "Your profile details have been verified. How many grams of gold jewelry do you wish to pledge?"
    },
    "jewel_type": {
        "ta": "நீங்கள் என்ன வகையான நகை அடமானம் வைக்கிறீர்கள்? (உதாரணம்: சங்கிலி, வளையல், மோதிரம், ஆரம்)",
        "en": "What type of jewelry are you pledging? (e.g. chain, bangles, ring, necklace)"
    },
    "requested_amount": {
        "ta": "உங்களுக்கு எவ்வளவு கடன் தொகை தேவைப்படுகிறது?",
        "en": "How much loan amount do you require?"
    },
    "tenure_months": {
        "ta": "கடன் கால அளவு எத்தனை மாதங்கள்? (இயல்புநிலை: 12 மாதங்கள்)",
        "en": "What is the desired loan tenure in months? (default: 12 months)"
    }
}


class SlotEngine:
    def process_jewel_loan_slots(
        self,
        customer_360: Customer360,
        current_slots: Dict[str, Any],
        newly_extracted_slots: Dict[str, Any],
        user_text: str
    ) -> Tuple[Dict[str, Any], List[str], Optional[Dict[str, str]], int, int]:
        """
        RAG Slot Filling Engine for Jewel Loans.
        Pre-fills known customer vault fields from Customer360 (reducing questions 22 -> 4).
        Returns: (merged_slots, missing_slots, next_prompt_dict, questions_total, questions_remaining)
        """
        merged = dict(current_slots or {})

        # Pre-fill vault fields from Customer360 profile automatically
        if customer_360:
            merged["customer_name"] = customer_360.full_name
            merged["account_number"] = customer_360.account_number
            merged["phone"] = customer_360.phone
            merged["dob"] = customer_360.dob
            merged["address"] = customer_360.address
            merged["credit_score"] = customer_360.credit_score
            merged["is_kcc_holder"] = customer_360.is_kcc_holder
            merged["is_shg_member"] = customer_360.is_shg_member

        # Default tenure_months if not specified
        if "tenure_months" not in merged or merged["tenure_months"] is None:
            merged["tenure_months"] = 12

        # Merge newly extracted slots
        for k, v in newly_extracted_slots.items():
            if v is not None:
                merged[k] = v

        # Heuristic slot extraction directly from text
        merged = self._extract_jewel_slots(merged, user_text)

        # Check missing required slots
        missing = [s for s in JEWEL_LOAN_REQUIRED_SLOTS if s not in merged or merged[s] is None]

        # Calculate 22 -> 5 questions reduction metrics
        questions_total = TOTAL_APPLICATION_QUESTIONS
        # 18 vault fields auto-filled + filled slots
        filled_count = len([s for s in JEWEL_LOAN_REQUIRED_SLOTS if s in merged and merged[s] is not None])
        questions_remaining = len(missing)

        # Generate prompt for next missing slot
        next_prompt = None
        if missing:
            next_slot = missing[0]
            next_prompt = SLOT_PROMPTS.get(next_slot, {
                "ta": f"தயவுசெய்து {next_slot} விவரத்தை வழங்கவும்.",
                "en": f"Please provide details for {next_slot}."
            })

        return merged, missing, next_prompt, questions_total, questions_remaining

    def _extract_jewel_slots(self, slots: Dict[str, Any], text: str) -> Dict[str, Any]:
        cleaned = text.lower().strip()

        # Match jewel weight in grams
        if "jewel_weight_grams" not in slots or slots["jewel_weight_grams"] is None:
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:கிராம்|கிரா|grams|gram|g\b)?", cleaned)
            if m:
                try:
                    val = float(m.group(1))
                    if 0.5 <= val <= 1000:
                        slots["jewel_weight_grams"] = val
                except ValueError:
                    pass

        # Match jewel type
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

        # Match requested amount
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

        return slots


slot_engine = SlotEngine()
