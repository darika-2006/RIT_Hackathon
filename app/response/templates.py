"""Strict Templated Responses for Money/Balances (Zero-Hallucination)"""

TEMPLATES = {
    "balance_inquiry": {
        "ta": "உங்கள் கணக்கில் ({account_number}) இருப்பு ₹{balance:,.2f} உள்ளது.",
        "en": "Your savings account ({account_number}) balance is ₹{balance:,.2f}."
    },
    "transaction_history": {
        "ta": "உங்கள் கடைசி {count} பரிவர்த்தனைகள்:\n{tx_summary}",
        "en": "Your recent {count} transactions:\n{tx_summary}"
    },
    "jewel_loan_confirm": {
        "ta": "நீங்கள் {weight} கிராம் {jewel_type} நகை அடமான கடனாக ₹{amount:,.2f} பெற கோரியுள்ளீர்கள் (கால அளவு: {tenure} மாதங்கள்). உறுதிப்படுத்த 'சரி' அல்லது 'ஆமாம்' என கூறவும்.",
        "en": "You requested ₹{amount:,.2f} against {weight}g of {jewel_type} for {tenure} months. Reply 'yes' or 'confirm' to submit."
    },
    "jewel_loan_success": {
        "ta": "உங்கள் நகை கடன் விண்ணப்பம் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது! விண்ணப்ப எண்: {application_id}. அனுமதிக்கப்பட்ட தொகை: ₹{approved_amount:,.2f}.",
        "en": "Your jewel loan application has been submitted successfully! Reference ID: {application_id}. Approved amount: ₹{approved_amount:,.2f}."
    },
    "mudra_loan_confirm": {
        "ta": "உங்கள் {business_type} தொழிலுக்கான ₹{amount:,.2f} முத்ரா கடன் விண்ணப்பத்தை உறுதிப்படுத்த 'சரி' என கூறவும்.",
        "en": "Please confirm your Mudra loan application of ₹{amount:,.2f} for {business_type}. Reply 'yes' to proceed."
    },
    "mudra_loan_success": {
        "ta": "உங்கள் முத்ரா கடன் விண்ணப்பம் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது! விண்ணப்ப எண்: {application_id}.",
        "en": "Your Mudra loan application has been submitted successfully! Reference ID: {application_id}."
    },
    "shg_savings": {
        "ta": "உங்கள் மதி ({shg_name}) சுய உதவிக் குழு கணக்கில் மொத்த சேமிப்பு ₹{balance:,.2f} உள்ளது.",
        "en": "Your Mathi ({shg_name}) Self Help Group savings balance is ₹{balance:,.2f}."
    },
    "kcc_status": {
        "ta": "உங்கள் பயிர் கடன் (KCC) நிலை: {status}. स्वीकृत வரம்பு: ₹{limit:,.2f}. பயிர் பருவம்: {season}.",
        "en": "Your Kisan Credit Card (KCC) crop loan status is {status}. Approved limit: ₹{limit:,.2f}. Crop season: {season}."
    },
    "scheme_inquiry": {
        "ta": "அரசு திட்டம்: {scheme_name}. நிலை: {status}. பயனடைந்த தொகை: ₹{amount:,.2f}.",
        "en": "Government Scheme: {scheme_name}. Status: {status}. Benefit amount: ₹{amount:,.2f}."
    },
    "help": {
        "ta": "வணக்கம்! நான் உங்கள் தமிழ் வங்கி குரல் உதவியாளர். உங்கள் கணக்கு இருப்பு, மினி ஸ்டேட்மென்ட், நகை கடன், முத்ரா கடன், சுய உதவி குழு சேமிப்பு மற்றும் அரசு திட்டங்கள் பற்றி கேட்கலாம்.",
        "en": "Welcome! I am your Tamil banking voice assistant. You can check balance, recent transactions, apply for jewel/mudra loans, or inquire about Govt schemes."
    },
    "unclear": {
        "ta": "மன்னிக்கவும், உங்கள் கோரிக்கை தெளிவாக புரியவில்லை. கணக்கு இருப்பு, நகை கடன் அல்லது மினி ஸ்டேட்மென்ட் பற்றி கேளுங்கள்.",
        "en": "Sorry, I could not understand your request clearly. Please ask for account balance, jewel loan, or mini statement."
    }
}
