"""Strict Tamil & Bilingual Response Templates for Tamil Nadu Micro-Banking"""

TEMPLATES = {
    "balance": {
        "ta": "வணக்கம் {name}! உங்கள் கணக்கில் ({account_number}) இருப்பு ₹{balance:,.2f} உள்ளது.",
        "en": "Welcome {name}! Your savings account ({account_number}) balance is ₹{balance:,.2f}."
    },
    "transactions": {
        "ta": "உங்கள் கடைசி பரிவர்த்தனை: {narration} மதிப்பில் ₹{amount:,.2f} ({date}).",
        "en": "Your recent transaction: {narration} for amount ₹{amount:,.2f} ({date})."
    },
    "jewel_loan_prompt_weight": {
        "ta": "உங்கள் விவரங்கள் சரிபார்க்கப்பட்டன. எத்தனை கிராம் நகை அடமானம் வைக்க விரும்புகிறீர்கள்?",
        "en": "Your profile details have been verified. How many grams of gold jewelry do you wish to pledge?"
    },
    "jewel_loan_prompt_type": {
        "ta": "என்ன வகையான நகை அடமானம் வைக்கிறீர்கள்? (உதாரணம்: சங்கிலி, வளையல், மோதிரம், ஆரம்)",
        "en": "What type of jewelry are you pledging? (e.g. chain, bangles, ring, necklace)"
    },
    "jewel_loan_prompt_amount": {
        "ta": "உங்களுக்கு எவ்வளவு கடன் தொகை தேவைப்படுகிறது?",
        "en": "How much loan amount do you require?"
    },
    "jewel_loan_prompt_tenure": {
        "ta": "கடன் கால அளவு எத்தனை மாதங்கள்? (இயல்புநிலை: 12 மாதங்கள்)",
        "en": "What is the desired loan tenure in months?"
    },
    "jewel_loan_confirm": {
        "ta": "நீங்கள் {weight} கிராம் {jewel_type} நகை அடமான கடனாக ₹{amount:,.2f} பெற விண்ணப்பிக்கிறீர்கள் (கால அளவு: {tenure} மாதங்கள்). உறுதிப்படுத்த 'சரி' என கூறவும்.",
        "en": "You requested ₹{amount:,.2f} against {weight}g of {jewel_type} for {tenure} months. Reply 'yes' to confirm."
    },
    "jewel_loan_success": {
        "ta": "உங்கள் நகை கடன் விண்ணப்பம் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது! விண்ணப்ப எண்: {application_id}. அனுமதிக்கப்பட்ட தொகை: ₹{approved_amount:,.2f}.",
        "en": "Your jewel loan application has been submitted successfully! Reference ID: {application_id}. Approved amount: ₹{approved_amount:,.2f}."
    },
    "mudra_loan_confirm": {
        "ta": "உங்கள் {business_type} தொழிலுக்கான ₹{amount:,.2f} முத்ரா கடன் விண்ணப்பத்தை உறுதிப்படுத்த 'சரி' என கூறவும்.",
        "en": "Please confirm your Mudra loan application of ₹{amount:,.2f} for {business_type}. Reply 'yes' to submit."
    },
    "mudra_loan_success": {
        "ta": "உங்கள் முத்ரா கடன் விண்ணப்பம் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது! விண்ணப்ப எண்: {application_id}.",
        "en": "Your Mudra loan application has been submitted successfully! Reference ID: {application_id}."
    },
    "shg_savings": {
        "ta": "உங்கள் மதி (Mathi) சுய உதவிக் குழு ({shg_name}) சேமிப்பு ₹{balance:,.2f}.",
        "en": "Your Mathi Self Help Group ({shg_name}) savings balance is ₹{balance:,.2f}."
    },
    "kcc_status": {
        "ta": "உங்கள் பயிர் கடன் நிலை: {status}. வரம்பு: ₹{limit:,.2f}. பருவம்: {season}.",
        "en": "Your Kisan Credit Card crop loan status is {status}. Approved limit: ₹{limit:,.2f}. Season: {season}."
    },
    "scheme_inquiry": {
        "ta": "அரசு திட்டம்: {scheme_name}. நிலை: {status}. பயனடைந்த தொகை: ₹{amount:,.2f}.",
        "en": "Government Scheme: {scheme_name}. Status: {status}. Benefit amount: ₹{amount:,.2f}."
    },
    "conflict_alert": {
        "ta": "ஒரு முக்கிய செய்தி: {conflict_msg} இதை சரிசெய்ய விரும்புகிறீர்களா?",
        "en": "Important alert: {conflict_msg} Would you like to resolve this?"
    },
    "help": {
        "ta": "வணக்கம்! நான் உங்கள் தமிழ் வங்கி குரல் உதவியாளர். கணக்கு இருப்பு, மினி ஸ்டேட்மென்ட், நகை கடன், முத்ரா கடன், சுய உதவி குழு சேமிப்பு மற்றும் அரசு திட்டங்களை பற்றி விசாரிக்கலாம்.",
        "en": "Welcome! I am your Tamil banking voice assistant. Ask about balance, transactions, jewel/mudra loans, SHG savings or Govt schemes."
    },
    "error": {
        "ta": "மன்னிக்கவும், வங்கி தகவல்களை பெற முடியவில்லை. பிறகு முயற்சிக்கவும்.",
        "en": "Sorry, unable to fetch banking details right now. Please try again."
    },
    "unclear": {
        "ta": "மன்னிக்கவும், எனக்கு புரியவில்லை. மீண்டும் கூற முடியுமா?",
        "en": "Sorry, I could not understand. Could you please repeat?"
    }
}
