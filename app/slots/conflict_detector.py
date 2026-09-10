import logging
from typing import List, Dict, Any
from app.schemas import ConflictAlert, Customer360

logger = logging.getLogger(__name__)

# Try importing fuzzywuzzy or RapidFuzz
try:
    from fuzzywuzzy import fuzz
except ImportError:
    try:
        from rapidfuzz import fuzz
    except ImportError:
        # Basic fallback matching if library unavailable
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


def detect_conflicts(customer: Customer360) -> List[ConflictAlert]:
    """
    Proactive cross-document conflict detection across customer vault.
    Compares PAN Name vs Aadhaar Full Name using fuzzy string matching.
    If similarity < 90%, generates a conflict alert.
    """
    alerts: List[ConflictAlert] = []

    aadhaar_name = customer.full_name.strip() if customer.full_name else ""
    pan_name = customer.pan_name.strip() if customer.pan_name else ""

    if aadhaar_name and pan_name:
        similarity = fuzz.token_sort_ratio(aadhaar_name.upper(), pan_name.upper())
        logger.info(f"Cross-doc name match: '{pan_name}' vs '{aadhaar_name}' -> Similarity: {similarity}%")
        
        if similarity < 90:
            msg_ta = f"PAN பெயர் '{pan_name}' மற்றும் ஆதார் பெயர் '{aadhaar_name}' பொருந்தவில்லை."
            msg_en = f"PAN Name '{pan_name}' and Aadhaar Name '{aadhaar_name}' do not match ({similarity}% match)."
            alerts.append(
                ConflictAlert(
                    type="name_mismatch",
                    message_ta=msg_ta,
                    message_en=msg_en,
                    severity="high"
                )
            )

    return alerts
