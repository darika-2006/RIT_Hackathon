import re
from typing import Dict, Any, Tuple


INTENT_PATTERNS = [
    (
        "jewel_loan_apply",
        r"நகை\s*கடன்|ஜுவல்\s*லோன்|கோல்ட்\s*லோன்|நகை\s*அடமானம்|அடமானம்|தங்கம்|நகை|jewel\s*loan|gold\s*loan|nagai\s*kadan|jewel"
    ),
    (
        "mudra_loan_apply",
        r"முத்ரா\s*கடன்|தொழில்\s*கடன்|வியாபார\s*கடன்|கடை\s*loan|வணிக\s*கடன்|mudra\s*loan|mudra|business\s*loan|thozhil\s*kadan"
    ),
    (
        "shg_savings",
        r"மதி|சுய\s*உதவிக்\s*குழு|சுய\s*உதவி|மகளிர்\s*குழு|shg|mathi\s*group|mathi|group\s*savings|shg\s*savings"
    ),
    (
        "kcc_status",
        r"பயிர்\s*கடன்|kcc|விவசாய\s*கடன்|குறுவை|சம்பா|crop\s*loan|payir\s*kadan|vivasaya\s*kadan|kisaan"
    ),
    (
        "scheme_inquiry",
        r"மகளிர்\s*உரிமை|உரிமைத்\s*தொகை|pmjdy|pmfby|jan\s*dhan|ஜன\s*தன்|பயிர்\s*காப்பீடு|அரசு\s*திட்டம்|scheme|government\s*benefit|magalir\s*urimai"
    ),
    (
        "balance_inquiry",
        r"பாலன்ஸ்|கணக்கு\s*இருப்பு|இருப்பு|எவ்வளவு\s*இருக்கு|எவ்வளவு\s*பணம்|கணக்கில்\s*எவ்வளவு|balance|check\s*balance|how\s*much\s*money|account\s*balance"
    ),
    (
        "transaction_history",
        r"பரிவர்த்தனை|மினி\s*ஸ்டேட்மென்ட்|ஸ்டேட்மென்ட்|வரவு|செலவு|transaction|history|statement|mini\s*statement|recent\s*transaction|last\s*5"
    ),
    (
        "help",
        r"உதவி|help|support|என்ன\s*செய்ய|வழிமுறைகள்"
    )
]


def classify_intent_by_rules(text: str) -> Tuple[str, float, Dict[str, Any]]:
    """
    Regex fallback classifier for Tamil & Tanglish/English inputs.
    Returns (intent, confidence, extracted_slots).
    """
    cleaned_text = text.lower().strip()
    extracted_slots: Dict[str, Any] = {}

    for intent_name, pattern in INTENT_PATTERNS:
        if re.search(pattern, cleaned_text, re.IGNORECASE):
            # Extract possible numeric slots if relevant
            # Grams for jewel loan: e.g. "16 கிராம்", "16g", "16 grams"
            gram_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:கிராம்|கிரா|grams|gram|g\b)", cleaned_text)
            if gram_match:
                try:
                    extracted_slots["jewel_weight_grams"] = float(gram_match.group(1))
                except ValueError:
                    pass

            # Money amounts: e.g. "75000 ரூபாய்", "Rs 75000", "75k", "75,000"
            amount_match = re.search(r"(?:rs\.?|ரூபாய்|₹)?\s*(\d[\d,]*)(?:\s*(?:ரூபாய்|rs|rupees|lakh|லட்சம்))?", cleaned_text)
            if amount_match:
                val_str = amount_match.group(1).replace(",", "")
                if val_str.isdigit() and len(val_str) >= 3:
                    try:
                        extracted_slots["requested_amount"] = float(val_str)
                    except ValueError:
                        pass

            # Jewel type detection
            jewel_types = {
                "chain": ["சங்கிலி", "செயின்", "chain"],
                "bangles": ["வளையல்", "காப்பு", "bangles", "bangle"],
                "ring": ["மோதிரம்", "ring"],
                "necklace": ["ஆரம்", "ஹாரம்", "நெக்லஸ்", "necklace", "haram"],
                "coin": ["நாணயம்", "காசு", "coin"]
            }
            for j_key, j_words in jewel_types.items():
                for word in j_words:
                    if word in cleaned_text:
                        extracted_slots["jewel_type"] = j_key
                        break

            return intent_name, 0.85, extracted_slots

    return "unclear", 0.3, {}
