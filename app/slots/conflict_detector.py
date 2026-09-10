import logging
from typing import List, Dict, Any
from app.schemas import Customer360

logger = logging.getLogger(__name__)

# Import fuzzy matching library
try:
    from fuzzywuzzy import fuzz
except ImportError:
    try:
        from rapidfuzz import fuzz
    except ImportError:
        class SimpleFuzz:
            @staticmethod
            def token_sort_ratio(s1: str, s2: str) -> int:
                s1_set = set(s1.upper().split())
                s2_set = set(s2.upper().split())
                if not s1_set or not s2_set:
                    return 0
                intersection = s1_set.intersection(s2_set)
                return int((2.0 * len(intersection) / (len(s1_set) + len(s2_set))) * 100)
        fuzz = SimpleFuzz()


def detect_conflicts(customer_360: Customer360) -> List[Dict[str, Any]]:
    """
    Proactive cross-document conflict detection.
    Compares PAN Name vs Aadhaar Name using fuzzy string matching.
    If similarity < 90%, returns conflict dictionary alerts.
    """
    conflicts: List[Dict[str, Any]] = []

    aadhaar_name = customer_360.full_name.strip() if customer_360.full_name else ""
    pan_name = customer_360.pan_name.strip() if customer_360.pan_name else ""

    if aadhaar_name and pan_name:
        similarity = fuzz.token_sort_ratio(aadhaar_name.upper(), pan_name.upper())
        logger.info(f"Fuzzy Name Match: PAN '{pan_name}' vs Aadhaar '{aadhaar_name}' -> Ratio: {similarity}%")
        
        if similarity < 90:
            conflicts.append({
                "type": "name_mismatch",
                "severity": "high",
                "message_ta": f"PAN பெயர் '{pan_name}' மற்றும் ஆதார் பெயர் '{aadhaar_name}' பொருந்தவில்லை. வங்கி நிராகரிக்கலாம்.",
                "message_en": f"PAN Name '{pan_name}' and Aadhaar Name '{aadhaar_name}' do not match ({similarity}% match).",
                "similarity_score": similarity
            })

    return conflicts
