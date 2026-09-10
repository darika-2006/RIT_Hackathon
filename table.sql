CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for gen_random_uuid()
CREATE TABLE customers (
    customer_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name           VARCHAR(150) NOT NULL,
    phone_number        VARCHAR(15) UNIQUE NOT NULL,
    email               VARCHAR(150) UNIQUE,
    date_of_birth       DATE,
    gender              VARCHAR(10) CHECK (gender IN ('Male','Female','Other')),
    address             TEXT,
    city                VARCHAR(100),
    state               VARCHAR(100),
    occupation          VARCHAR(100),
    monthly_income      NUMERIC(12,2),
    preferred_language  VARCHAR(50) DEFAULT 'English',
    kyc_status          VARCHAR(20) DEFAULT 'Pending' CHECK (kyc_status IN ('Pending','Verified','Rejected')),
    created_at          TIMESTAMP DEFAULT now()
);

CREATE TABLE device_sessions (
    session_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id     UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    device_id       VARCHAR(150),
    device_type     VARCHAR(50),
    ip_address      VARCHAR(50),
    login_at        TIMESTAMP DEFAULT now(),
    logout_at       TIMESTAMP,
    is_active       BOOLEAN DEFAULT TRUE,
    otp_verified    BOOLEAN DEFAULT FALSE
);

-- ============================================================
-- 2. BANKING (CORE)
-- ============================================================

CREATE TABLE accounts (
    account_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    account_number      VARCHAR(20) UNIQUE NOT NULL,
    account_type        VARCHAR(20) CHECK (account_type IN ('Savings','Current','Salary')),
    ifsc_code           VARCHAR(11),
    branch_name         VARCHAR(100),
    balance             NUMERIC(15,2) DEFAULT 0,
    available_balance   NUMERIC(15,2) DEFAULT 0,
    status              VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active','Inactive','Frozen','Closed')),
    opened_at           TIMESTAMP DEFAULT now()
);

CREATE TABLE beneficiaries (
    beneficiary_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id      UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    name             VARCHAR(150) NOT NULL,
    account_number   VARCHAR(20) NOT NULL,
    ifsc_code        VARCHAR(11),
    bank_name        VARCHAR(100),
    nickname         VARCHAR(50),
    status           VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active','Inactive')),
    created_at       TIMESTAMP DEFAULT now()
);

CREATE TABLE transactions (
    transaction_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id           UUID NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    transaction_type     VARCHAR(30) CHECK (transaction_type IN ('Deposit','Withdrawal','Transfer','Payment','Refund')),
    direction            VARCHAR(10) CHECK (direction IN ('Credit','Debit')),
    amount               NUMERIC(15,2) NOT NULL,
    counterparty_name    VARCHAR(150),
    counterparty_account VARCHAR(20),
    channel              VARCHAR(30) CHECK (channel IN ('UPI','NEFT','RTGS','IMPS','ATM','Branch','Card','Cheque')),
    description          TEXT,
    reference_number     VARCHAR(50) UNIQUE,
    status               VARCHAR(20) DEFAULT 'Success' CHECK (status IN ('Success','Pending','Failed','Reversed')),
    created_at           TIMESTAMP DEFAULT now()
);

-- ============================================================
-- 3. CREDIT (LOANS)
-- ============================================================

CREATE TABLE loan_products (
    loan_product_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name            VARCHAR(150) NOT NULL,
    loan_type               VARCHAR(50) CHECK (loan_type IN ('Personal','Home','Auto','Education','Business','Gold')),
    description             TEXT,
    min_amount              NUMERIC(15,2),
    max_amount              NUMERIC(15,2),
    interest_rate           NUMERIC(5,2),
    min_tenure_months       INT,
    max_tenure_months       INT,
    min_monthly_income      NUMERIC(12,2),
    min_age                 INT,
    max_age                 INT,
    min_credit_score        INT,
    max_existing_emi_ratio  NUMERIC(4,2),
    processing_fee          NUMERIC(10,2),
    collateral_required     BOOLEAN DEFAULT FALSE,
    active                  BOOLEAN DEFAULT TRUE
);

CREATE TABLE loan_applications (
    application_id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id                     UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    loan_product_id                 UUID NOT NULL REFERENCES loan_products(loan_product_id),
    requested_amount                NUMERIC(15,2),
    requested_tenure                INT,
    purpose                         VARCHAR(200),
    monthly_income_at_application   NUMERIC(12,2),
    existing_emi                    NUMERIC(12,2),
    eligibility_status              VARCHAR(20) CHECK (eligibility_status IN ('Eligible','Not Eligible','Under Review')),
    eligibility_reason              TEXT,
    status                          VARCHAR(20) DEFAULT 'Submitted' CHECK (status IN ('Submitted','Approved','Rejected','Disbursed','Cancelled')),
    created_at                      TIMESTAMP DEFAULT now()
);

CREATE TABLE loans (
    loan_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id      UUID NOT NULL REFERENCES loan_applications(application_id),
    customer_id         UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    loan_product_id     UUID NOT NULL REFERENCES loan_products(loan_product_id),
    principal_amount    NUMERIC(15,2) NOT NULL,
    interest_rate       NUMERIC(5,2),
    tenure_months       INT,
    emi_amount          NUMERIC(12,2),
    outstanding_amount  NUMERIC(15,2),
    start_date          DATE,
    next_due_date       DATE,
    status              VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active','Closed','Defaulted','Foreclosed'))
);

CREATE TABLE loan_repayments (
    repayment_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id               UUID NOT NULL REFERENCES loans(loan_id) ON DELETE CASCADE,
    amount                NUMERIC(12,2) NOT NULL,
    principal_component   NUMERIC(12,2),
    interest_component    NUMERIC(12,2),
    payment_date          DATE,
    payment_method        VARCHAR(30),
    transaction_id        UUID REFERENCES transactions(transaction_id),
    status                VARCHAR(20) DEFAULT 'Success' CHECK (status IN ('Success','Failed','Pending'))
);

-- ============================================================
-- 4. SAVINGS (DEPOSITS)
-- ============================================================

CREATE TABLE deposit_products (
    deposit_product_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name                   VARCHAR(150) NOT NULL,
    deposit_type                   VARCHAR(20) CHECK (deposit_type IN ('Fixed','Recurring')),
    min_amount                     NUMERIC(12,2),
    max_amount                     NUMERIC(15,2),
    interest_rate                  NUMERIC(5,2),
    min_tenure_months              INT,
    max_tenure_months              INT,
    premature_withdrawal_allowed   BOOLEAN DEFAULT TRUE,
    premature_penalty              NUMERIC(5,2),
    active                         BOOLEAN DEFAULT TRUE
);

CREATE TABLE deposits (
    deposit_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id         UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    account_id          UUID NOT NULL REFERENCES accounts(account_id),
    deposit_product_id  UUID NOT NULL REFERENCES deposit_products(deposit_product_id),
    principal_amount    NUMERIC(15,2) NOT NULL,
    interest_rate       NUMERIC(5,2),
    tenure_months       INT,
    start_date          DATE,
    maturity_date       DATE,
    maturity_amount     NUMERIC(15,2),
    status              VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active','Matured','Closed','Premature Withdrawal'))
);

-- ============================================================
-- 5. INSURANCE
-- ============================================================

CREATE TABLE insurance_products (
    insurance_product_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name           VARCHAR(150) NOT NULL,
    insurance_type         VARCHAR(30) CHECK (insurance_type IN ('Life','Health','Vehicle','Property','Travel')),
    description            TEXT,
    min_age                INT,
    max_age                INT,
    premium_amount         NUMERIC(12,2),
    premium_frequency      VARCHAR(20) CHECK (premium_frequency IN ('Monthly','Quarterly','Half-Yearly','Yearly')),
    coverage_amount        NUMERIC(15,2),
    tenure_years           INT,
    eligibility_criteria   TEXT,
    active                 BOOLEAN DEFAULT TRUE
);

CREATE TABLE insurance_policies (
    policy_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id             UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    insurance_product_id    UUID NOT NULL REFERENCES insurance_products(insurance_product_id),
    policy_number           VARCHAR(30) UNIQUE NOT NULL,
    start_date              DATE,
    end_date                DATE,
    premium_amount          NUMERIC(12,2),
    next_premium_date       DATE,
    coverage_amount         NUMERIC(15,2),
    nominee_name            VARCHAR(150),
    status                  VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active','Lapsed','Matured','Claimed','Cancelled'))
);

-- ============================================================
-- 6. PENSION
-- ============================================================

CREATE TABLE pension_products (
    pension_product_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name            VARCHAR(150) NOT NULL,
    description             TEXT,
    min_age                 INT,
    max_joining_age         INT,
    contribution_frequency  VARCHAR(20) CHECK (contribution_frequency IN ('Monthly','Quarterly','Yearly')),
    minimum_contribution    NUMERIC(10,2),
    maximum_contribution    NUMERIC(10,2),
    pension_options         TEXT,
    eligibility_criteria    TEXT,
    active                  BOOLEAN DEFAULT TRUE
);

CREATE TABLE pension_accounts (
    pension_account_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id             UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    pension_product_id      UUID NOT NULL REFERENCES pension_products(pension_product_id),
    account_number          VARCHAR(20) UNIQUE NOT NULL,
    monthly_contribution    NUMERIC(10,2),
    chosen_pension          VARCHAR(100),
    next_contribution_date  DATE,
    total_contributed       NUMERIC(15,2) DEFAULT 0,
    status                  VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active','Inactive','Matured','Closed')),
    nominee_name            VARCHAR(150)
);

-- ============================================================
-- 7. GOVERNMENT SCHEMES
-- ============================================================

CREATE TABLE government_schemes (
    scheme_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_name             VARCHAR(150) NOT NULL,
    scheme_type             VARCHAR(50),
    description             TEXT,
    min_age                 INT,
    max_age                 INT,
    income_limit            NUMERIC(12,2),
    occupation_requirement  VARCHAR(100),
    benefit_amount          NUMERIC(12,2),
    frequency               VARCHAR(20) CHECK (frequency IN ('One-time','Monthly','Quarterly','Yearly')),
    eligibility_criteria    TEXT,
    active                  BOOLEAN DEFAULT TRUE
);

CREATE TABLE government_benefits (
    benefit_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id        UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    scheme_id          UUID NOT NULL REFERENCES government_schemes(scheme_id),
    account_id         UUID NOT NULL REFERENCES accounts(account_id),
    amount             NUMERIC(12,2),
    credit_date        DATE,
    reference_number   VARCHAR(50) UNIQUE,
    status             VARCHAR(20) DEFAULT 'Credited' CHECK (status IN ('Credited','Pending','Failed')),
    description        TEXT
);

-- ============================================================
-- 8. SUPPORT / SECURITY
-- ============================================================

CREATE TABLE complaints (
    complaint_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id      UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    transaction_id   UUID REFERENCES transactions(transaction_id),
    category         VARCHAR(50),
    description      TEXT,
    priority         VARCHAR(10) CHECK (priority IN ('Low','Medium','High','Critical')),
    status           VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open','In Progress','Resolved','Closed')),
    created_at       TIMESTAMP DEFAULT now(),
    resolved_at      TIMESTAMP,
    resolution       TEXT
);

CREATE TABLE audit_logs (
    log_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id       UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    session_id        UUID REFERENCES device_sessions(session_id) ON DELETE SET NULL,
    agent_name        VARCHAR(100),
    intent            VARCHAR(150),
    action            VARCHAR(150),
    tool_called       VARCHAR(150),
    request_summary   TEXT,
    result            TEXT,
    timestamp         TIMESTAMP DEFAULT now()
);

CREATE TABLE notifications (
    notification_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id       UUID NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    channel           VARCHAR(20) CHECK (channel IN ('SMS','Email','Push','In-App')),
    title             VARCHAR(150),
    message           TEXT,
    is_read           BOOLEAN DEFAULT FALSE,
    sent_at           TIMESTAMP DEFAULT now()
);

-- ============================================================
-- INDEXES (foreign keys + common lookup fields)
-- ============================================================

CREATE INDEX idx_device_sessions_customer     ON device_sessions(customer_id);
CREATE INDEX idx_accounts_customer            ON accounts(customer_id);
CREATE INDEX idx_beneficiaries_customer       ON beneficiaries(customer_id);
CREATE INDEX idx_transactions_account         ON transactions(account_id);
CREATE INDEX idx_transactions_created_at      ON transactions(created_at);
CREATE INDEX idx_loan_applications_customer   ON loan_applications(customer_id);
CREATE INDEX idx_loan_applications_product    ON loan_applications(loan_product_id);
CREATE INDEX idx_loans_customer               ON loans(customer_id);
CREATE INDEX idx_loans_application            ON loans(application_id);
CREATE INDEX idx_loan_repayments_loan         ON loan_repayments(loan_id);
CREATE INDEX idx_deposits_customer            ON deposits(customer_id);
CREATE INDEX idx_deposits_account             ON deposits(account_id);
CREATE INDEX idx_insurance_policies_customer  ON insurance_policies(customer_id);
CREATE INDEX idx_pension_accounts_customer    ON pension_accounts(customer_id);
CREATE INDEX idx_government_benefits_customer ON government_benefits(customer_id);
CREATE INDEX idx_complaints_customer          ON complaints(customer_id);
CREATE INDEX idx_audit_logs_customer          ON audit_logs(customer_id);
CREATE INDEX idx_notifications_customer       ON notifications(customer_id);