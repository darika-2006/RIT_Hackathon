import logging
import re
from typing import Dict, Any, Tuple, Optional, List
from app.slots.engine import slot_engine
from app.schemas import Customer360

logger = logging.getLogger(__name__)

CONFIRM_WORDS = ["சரி", "ஆமாம்", "அனுப்பு", "ஓகே", "ஆம்", "உறுதி", "yes", "confirm", "ok", "yep", "sure"]


class StateMachine:
    def process_turn(
        self,
        intent: str,
        extracted_slots: Dict[str, Any],
        current_session_state: Dict[str, Any],
        user_text: str,
        customer_profile: Customer360
    ) -> Tuple[str, Dict[str, Any], Optional[Dict[str, str]]]:
        """
        Dialog State Machine.
        Manages state transitions: GREETING -> SLOT_FILLING -> CONFIRM -> EXECUTE.
        Returns: (new_dialog_state, accumulated_slots, next_prompt_if_slot_filling)
        """
        current_state = current_session_state.get("dialog_state", "GREETING")
        current_slots = current_session_state.get("slots", {})
        cleaned_text = user_text.lower().strip()

        # Slot-driven intents (Jewel loan & Mudra loan)
        if intent in ("jewel_loan_apply", "mudra_loan_apply"):
            # 1. Process slot engine
            merged_slots, missing_slots, next_prompt = slot_engine.process_slots(
                intent=intent,
                current_slots=current_slots,
                newly_extracted_slots=extracted_slots,
                user_text=user_text,
                customer_profile=customer_profile
            )

            # 2. Check if user is confirming while in CONFIRM state
            user_is_confirming = any(word in cleaned_text for word in CONFIRM_WORDS)

            if current_state == "CONFIRM" and user_is_confirming:
                logger.info(f"User confirmed intent {intent}. Transitioning to EXECUTE.")
                return "EXECUTE", merged_slots, None

            # If there are missing slots -> SLOT_FILLING
            if missing_slots:
                logger.info(f"Missing slots for {intent}: {missing_slots}. State: SLOT_FILLING.")
                return "SLOT_FILLING", merged_slots, next_prompt

            # All slots are present, but user has not yet confirmed -> CONFIRM
            logger.info(f"All slots present for {intent}. Transitioning to CONFIRM state.")
            return "CONFIRM", merged_slots, None

        # Direct execution intents
        return "EXECUTE", extracted_slots, None


state_machine = StateMachine()
