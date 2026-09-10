from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import pool
from tts_service import synthesize_speech


app = FastAPI(
    title="Micro Banking API",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Micro Banking API"
    }


@app.get("/health")
def health():
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


# --------------------------------------------------
# CUSTOMERS
# --------------------------------------------------

@app.get("/api/customers")
def get_customers():

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    customer_id,
                    full_name,
                    phone_number,
                    occupation,
                    monthly_income,
                    preferred_language,
                    kyc_status
                FROM customers
                ORDER BY customer_id
            """)

            rows = cur.fetchall()

            return [
                {
                    "customer_id": row[0],
                    "full_name": row[1],
                    "phone_number": row[2],
                    "occupation": row[3],
                    "monthly_income": row[4],
                    "preferred_language": row[5],
                    "kyc_status": row[6]
                }
                for row in rows
            ]


# --------------------------------------------------
# SINGLE CUSTOMER
# --------------------------------------------------

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str):

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    customer_id,
                    full_name,
                    phone_number,
                    email,
                    date_of_birth,
                    gender,
                    address,
                    city,
                    state,
                    occupation,
                    monthly_income,
                    preferred_language,
                    kyc_status
                FROM customers
                WHERE customer_id = %s
            """, (customer_id,))

            row = cur.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Customer not found"
                )

            return {
                "customer_id": row[0],
                "full_name": row[1],
                "phone_number": row[2],
                "email": row[3],
                "date_of_birth": row[4],
                "gender": row[5],
                "address": row[6],
                "city": row[7],
                "state": row[8],
                "occupation": row[9],
                "monthly_income": row[10],
                "preferred_language": row[11],
                "kyc_status": row[12]
            }


# --------------------------------------------------
# ACCOUNTS
# --------------------------------------------------

@app.get("/api/customers/{customer_id}/accounts")
def get_accounts(customer_id: str):

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    account_id,
                    account_number,
                    account_type,
                    ifsc_code,
                    branch_name,
                    balance,
                    available_balance,
                    status,
                    opened_at
                FROM accounts
                WHERE customer_id = %s
                ORDER BY account_id
            """, (customer_id,))

            rows = cur.fetchall()

            return [
                {
                    "account_id": row[0],
                    "account_number": row[1],
                    "account_type": row[2],
                    "ifsc_code": row[3],
                    "branch_name": row[4],
                    "balance": row[5],
                    "available_balance": row[6],
                    "status": row[7],
                    "opened_at": row[8]
                }
                for row in rows
            ]


# --------------------------------------------------
# BALANCE
# --------------------------------------------------

@app.get("/api/customers/{customer_id}/balance")
def get_balance(customer_id: str):

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    account_id,
                    account_number,
                    balance,
                    available_balance
                FROM accounts
                WHERE customer_id = %s
                  AND status = 'ACTIVE'
            """, (customer_id,))

            rows = cur.fetchall()

            return [
                {
                    "account_id": row[0],
                    "account_number": row[1],
                    "balance": row[2],
                    "available_balance": row[3]
                }
                for row in rows
            ]


# --------------------------------------------------
# TRANSACTIONS
# --------------------------------------------------

@app.get("/api/customers/{customer_id}/transactions")
def get_transactions(customer_id: str):

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    t.transaction_id,
                    t.account_id,
                    t.transaction_type,
                    t.direction,
                    t.amount,
                    t.counterparty_name,
                    t.channel,
                    t.description,
                    t.reference_number,
                    t.status,
                    t.created_at
                FROM transactions t
                JOIN accounts a
                    ON t.account_id = a.account_id
                WHERE a.customer_id = %s
                ORDER BY t.created_at DESC
            """, (customer_id,))

            rows = cur.fetchall()

            return [
                {
                    "transaction_id": row[0],
                    "account_id": row[1],
                    "transaction_type": row[2],
                    "direction": row[3],
                    "amount": row[4],
                    "counterparty_name": row[5],
                    "channel": row[6],
                    "description": row[7],
                    "reference_number": row[8],
                    "status": row[9],
                    "created_at": row[10]
                }
                for row in rows
            ]


# --------------------------------------------------
# BENEFICIARIES
# --------------------------------------------------

@app.get("/api/customers/{customer_id}/beneficiaries")
def get_beneficiaries(customer_id: str):

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    beneficiary_id,
                    name,
                    account_number,
                    ifsc_code,
                    bank_name,
                    nickname,
                    status
                FROM beneficiaries
                WHERE customer_id = %s
                ORDER BY name
            """, (customer_id,))

            rows = cur.fetchall()

            return [
                {
                    "beneficiary_id": row[0],
                    "name": row[1],
                    "account_number": row[2],
                    "ifsc_code": row[3],
                    "bank_name": row[4],
                    "nickname": row[5],
                    "status": row[6]
                }
                for row in rows
            ]


# --------------------------------------------------
# LOAN PRODUCTS
# --------------------------------------------------

@app.get("/api/loan-products")
def get_loan_products():

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    loan_product_id,
                    product_name,
                    loan_type,
                    description,
                    min_amount,
                    max_amount,
                    interest_rate,
                    min_tenure_months,
                    max_tenure_months,
                    min_monthly_income,
                    min_age,
                    max_age,
                    min_credit_score,
                    processing_fee,
                    collateral_required,
                    active
                FROM loan_products
                WHERE active = TRUE
                ORDER BY product_name
            """)

            rows = cur.fetchall()

            return [
                {
                    "loan_product_id": row[0],
                    "product_name": row[1],
                    "loan_type": row[2],
                    "description": row[3],
                    "min_amount": row[4],
                    "max_amount": row[5],
                    "interest_rate": row[6],
                    "min_tenure_months": row[7],
                    "max_tenure_months": row[8],
                    "min_monthly_income": row[9],
                    "min_age": row[10],
                    "max_age": row[11],
                    "min_credit_score": row[12],
                    "processing_fee": row[13],
                    "collateral_required": row[14],
                    "active": row[15]
                }
                for row in rows
            ]


# --------------------------------------------------
# CUSTOMER LOANS
# --------------------------------------------------

@app.get("/api/customers/{customer_id}/loans")
def get_customer_loans(customer_id: str):

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    l.loan_id,
                    lp.product_name,
                    l.principal_amount,
                    l.interest_rate,
                    l.tenure_months,
                    l.emi_amount,
                    l.outstanding_amount,
                    l.next_due_date,
                    l.status
                FROM loans l
                JOIN loan_products lp
                    ON l.loan_product_id = lp.loan_product_id
                WHERE l.customer_id = %s
                ORDER BY l.loan_id
            """, (customer_id,))

            rows = cur.fetchall()

            return [
                {
                    "loan_id": row[0],
                    "product_name": row[1],
                    "principal_amount": row[2],
                    "interest_rate": row[3],
                    "tenure_months": row[4],
                    "emi_amount": row[5],
                    "outstanding_amount": row[6],
                    "next_due_date": row[7],
                    "status": row[8]
                }
                for row in rows
            ]


# --------------------------------------------------
# DEPOSITS
# --------------------------------------------------

@app.get("/api/customers/{customer_id}/deposits")
def get_deposits(customer_id: str):

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    d.deposit_id,
                    dp.product_name,
                    dp.deposit_type,
                    d.principal_amount,
                    d.interest_rate,
                    d.tenure_months,
                    d.start_date,
                    d.maturity_date,
                    d.maturity_amount,
                    d.status
                FROM deposits d
                JOIN deposit_products dp
                    ON d.deposit_product_id = dp.deposit_product_id
                WHERE d.customer_id = %s
                ORDER BY d.deposit_id
            """, (customer_id,))

            rows = cur.fetchall()

            return [
                {
                    "deposit_id": row[0],
                    "product_name": row[1],
                    "deposit_type": row[2],
                    "principal_amount": row[3],
                    "interest_rate": row[4],
                    "tenure_months": row[5],
                    "start_date": row[6],
                    "maturity_date": row[7],
                    "maturity_amount": row[8],
                    "status": row[9]
                }
                for row in rows
            ]


# --------------------------------------------------
# GOVERNMENT BENEFITS
# --------------------------------------------------

@app.get("/api/customers/{customer_id}/benefits")
def get_benefits(customer_id: str):

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    gb.benefit_id,
                    gs.scheme_name,
                    gs.scheme_type,
                    gb.amount,
                    gb.credit_date,
                    gb.reference_number,
                    gb.status,
                    gb.description
                FROM government_benefits gb
                JOIN government_schemes gs
                    ON gb.scheme_id = gs.scheme_id
                WHERE gb.customer_id = %s
                ORDER BY gb.credit_date DESC
            """, (customer_id,))

            rows = cur.fetchall()

            return [
                {
                    "benefit_id": row[0],
                    "scheme_name": row[1],
                    "scheme_type": row[2],
                    "amount": row[3],
                    "credit_date": row[4],
                    "reference_number": row[5],
                    "status": row[6],
                    "description": row[7]
                }
                for row in rows
            ]


# --------------------------------------------------
# TEXT-TO-SPEECH (TTS) - 14 INDIC LANGUAGES
# --------------------------------------------------

class TTSRequest(BaseModel):
    text: str
    language: str = "hi"


@app.post("/api/tts/synthesize")
@app.post("/api/speak")
async def tts_endpoint(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        audio_bytes, media_type = await synthesize_speech(req.text, req.language)
        return Response(content=audio_bytes, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tts/synthesize")
@app.get("/api/speak")
async def tts_get_endpoint(text: str, language: str = "hi"):
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        audio_bytes, media_type = await synthesize_speech(text, language)
        return Response(content=audio_bytes, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
