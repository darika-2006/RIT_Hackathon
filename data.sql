-- ============================================================
-- BANK DATABASE SIMULATION — SEED DATA
-- Run AFTER 01_schema.sql
-- Uses fixed UUIDs so rows link cleanly across tables for demos.
-- ============================================================

-- ---------------- CUSTOMERS ----------------
INSERT INTO customers (customer_id, full_name, phone_number, email, date_of_birth, gender, address, city, state, occupation, monthly_income, preferred_language, kyc_status)
VALUES
('00000000-0000-0000-0000-000000000001','Aarav Sharma','9876543210','aarav.sharma@example.com','1990-05-14','Male','12 MG Road','Chennai','Tamil Nadu','Software Engineer',85000,'English','Verified'),
('00000000-0000-0000-0000-000000000002','Priya Natarajan','9876543211','priya.n@example.com','1985-11-02','Female','45 Anna Nagar','Chennai','Tamil Nadu','Business Owner',150000,'Tamil','Verified'),
('00000000-0000-0000-0000-000000000003','Ravi Kumar','9876543212','ravi.kumar@example.com','1962-03-20','Male','7 Gandhi Street','Madurai','Tamil Nadu','Retired',25000,'Tamil','Verified');

-- ---------------- DEVICE SESSIONS ----------------
INSERT INTO device_sessions (session_id, customer_id, device_id, device_type, ip_address, otp_verified)
VALUES
('00000000-0000-0000-0011-000000000001','00000000-0000-0000-0000-000000000001','DEVICE-A1','Mobile','103.21.55.10',TRUE);

-- ---------------- ACCOUNTS ----------------
INSERT INTO accounts (account_id, customer_id, account_number, account_type, ifsc_code, branch_name, balance, available_balance, status)
VALUES
('00000000-0000-0000-0001-000000000001','00000000-0000-0000-0000-000000000001','5011000100010001','Savings','HACK0001234','Chennai Main Branch',125000.00,125000.00,'Active'),
('00000000-0000-0000-0001-000000000002','00000000-0000-0000-0000-000000000002','5011000100010002','Current','HACK0001234','Chennai Main Branch',540000.00,540000.00,'Active'),
('00000000-0000-0000-0001-000000000003','00000000-0000-0000-0000-000000000003','5011000100010003','Savings','HACK0005678','Madurai Branch',32000.00,32000.00,'Active');

-- ---------------- BENEFICIARIES ----------------
INSERT INTO beneficiaries (beneficiary_id, customer_id, name, account_number, ifsc_code, bank_name, nickname, status)
VALUES
('00000000-0000-0000-0003-000000000001','00000000-0000-0000-0000-000000000001','Meena Sharma','6022110022001100','HACK0009988','Hack Bank','Wife','Active');

-- ---------------- TRANSACTIONS ----------------
INSERT INTO transactions (transaction_id, account_id, transaction_type, direction, amount, counterparty_name, counterparty_account, channel, description, reference_number, status)
VALUES
('00000000-0000-0000-0002-000000000001','00000000-0000-0000-0001-000000000001','Deposit','Credit',50000.00,NULL,NULL,'Branch','Salary credit','REF1000001','Success'),
('00000000-0000-0000-0002-000000000002','00000000-0000-0000-0001-000000000001','Transfer','Debit',5000.00,'Meena Sharma','6022110022001100','UPI','Sent to wife','REF1000002','Success'),
('00000000-0000-0000-0002-000000000003','00000000-0000-0000-0001-000000000002','Payment','Debit',18500.00,'HackBank Loans','SELF','ATM','EMI payment','REF1000003','Success');

-- ---------------- LOAN PRODUCTS ----------------
INSERT INTO loan_products (loan_product_id, product_name, loan_type, description, min_amount, max_amount, interest_rate, min_tenure_months, max_tenure_months, min_monthly_income, min_age, max_age, min_credit_score, max_existing_emi_ratio, processing_fee, collateral_required, active)
VALUES
('00000000-0000-0000-0004-000000000001','HackBank Personal Loan','Personal','Unsecured personal loan for salaried individuals',50000,1500000,12.50,12,60,20000,21,60,650,0.50,2500,FALSE,TRUE),
('00000000-0000-0000-0004-000000000002','HackBank Home Loan','Home','Home purchase and construction loan',500000,10000000,8.75,60,360,30000,21,65,700,0.50,10000,TRUE,TRUE);

-- ---------------- LOAN APPLICATIONS ----------------
INSERT INTO loan_applications (application_id, customer_id, loan_product_id, requested_amount, requested_tenure, purpose, monthly_income_at_application, existing_emi, eligibility_status, eligibility_reason, status)
VALUES
('00000000-0000-0000-0005-000000000001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0004-000000000001',300000,24,'Home renovation',85000,0,'Eligible','Meets income and credit criteria','Disbursed');

-- ---------------- LOANS ----------------
INSERT INTO loans (loan_id, application_id, customer_id, loan_product_id, principal_amount, interest_rate, tenure_months, emi_amount, outstanding_amount, start_date, next_due_date, status)
VALUES
('00000000-0000-0000-0006-000000000001','00000000-0000-0000-0005-000000000001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0004-000000000001',300000,12.50,24,14135.00,281865.00,'2026-01-15','2026-10-15','Active');

-- ---------------- LOAN REPAYMENTS ----------------
INSERT INTO loan_repayments (repayment_id, loan_id, amount, principal_component, interest_component, payment_date, payment_method, transaction_id, status)
VALUES
('00000000-0000-0000-0007-000000000001','00000000-0000-0000-0006-000000000001',14135.00,11010.00,3125.00,'2026-09-15','Auto-debit','00000000-0000-0000-0002-000000000003','Success');

-- ---------------- DEPOSIT PRODUCTS ----------------
INSERT INTO deposit_products (deposit_product_id, product_name, deposit_type, min_amount, max_amount, interest_rate, min_tenure_months, max_tenure_months, premature_withdrawal_allowed, premature_penalty, active)
VALUES
('00000000-0000-0000-0008-000000000001','HackBank Fixed Deposit','Fixed',10000,5000000,7.25,6,120,TRUE,1.00,TRUE);

-- ---------------- DEPOSITS ----------------
INSERT INTO deposits (deposit_id, customer_id, account_id, deposit_product_id, principal_amount, interest_rate, tenure_months, start_date, maturity_date, maturity_amount, status)
VALUES
('00000000-0000-0000-0009-000000000001','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0001-000000000002','00000000-0000-0000-0008-000000000001',200000,7.25,12,'2026-02-01','2027-02-01',214500.00,'Active');

-- ---------------- INSURANCE PRODUCTS ----------------
INSERT INTO insurance_products (insurance_product_id, product_name, insurance_type, description, min_age, max_age, premium_amount, premium_frequency, coverage_amount, tenure_years, eligibility_criteria, active)
VALUES
('00000000-0000-0000-000a-000000000001','HackBank Term Life Cover','Life','Simple term life insurance plan',18,65,1200.00,'Yearly',5000000,20,'Indian resident, age 18-65',TRUE);

-- ---------------- INSURANCE POLICIES ----------------
INSERT INTO insurance_policies (policy_id, customer_id, insurance_product_id, policy_number, start_date, end_date, premium_amount, next_premium_date, coverage_amount, nominee_name, status)
VALUES
('00000000-0000-0000-000b-000000000001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-000a-000000000001','POL-2026-0001','2026-03-01','2046-03-01',1200.00,'2027-03-01',5000000,'Meena Sharma','Active');

-- ---------------- PENSION PRODUCTS ----------------
INSERT INTO pension_products (pension_product_id, product_name, description, min_age, max_joining_age, contribution_frequency, minimum_contribution, maximum_contribution, pension_options, eligibility_criteria, active)
VALUES
('00000000-0000-0000-000c-000000000001','HackBank National Pension Scheme','Retirement savings plan with government backing',18,60,'Monthly',500,50000,'Conservative, Balanced, Aggressive','Indian citizen aged 18-60',TRUE);

-- ---------------- PENSION ACCOUNTS ----------------
INSERT INTO pension_accounts (pension_account_id, customer_id, pension_product_id, account_number, monthly_contribution, chosen_pension, next_contribution_date, total_contributed, status, nominee_name)
VALUES
('00000000-0000-0000-000d-000000000001','00000000-0000-0000-0000-000000000003','00000000-0000-0000-000c-000000000001','PEN-0001-2026',2000,'Conservative','2026-10-05',24000.00,'Active','Lakshmi Kumar');

-- ---------------- GOVERNMENT SCHEMES ----------------
INSERT INTO government_schemes (scheme_id, scheme_name, scheme_type, description, min_age, max_age, income_limit, occupation_requirement, benefit_amount, frequency, eligibility_criteria, active)
VALUES
('00000000-0000-0000-000e-000000000001','Senior Citizen Pension Scheme','Welfare','Monthly pension support for senior citizens',60,120,60000,NULL,2000,'Monthly','Age 60+, annual income below limit',TRUE);

-- ---------------- GOVERNMENT BENEFITS ----------------
INSERT INTO government_benefits (benefit_id, customer_id, scheme_id, account_id, amount, credit_date, reference_number, status, description)
VALUES
('00000000-0000-0000-000f-000000000001','00000000-0000-0000-0000-000000000003','00000000-0000-0000-000e-000000000001','00000000-0000-0000-0001-000000000003',2000,'2026-09-01','GOV-REF-0001','Credited','Monthly senior citizen pension credit');

-- ---------------- COMPLAINTS ----------------
INSERT INTO complaints (complaint_id, customer_id, transaction_id, category, description, priority, status, resolved_at, resolution)
VALUES
('00000000-0000-0000-0010-000000000001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0002-000000000002','Transaction Dispute','UPI transfer amount deducted twice','High','Resolved','2026-09-05 10:00:00','Duplicate debit reversed to account');

-- ---------------- AUDIT LOGS ----------------
INSERT INTO audit_logs (log_id, customer_id, session_id, agent_name, intent, action, tool_called, request_summary, result)
VALUES
('00000000-0000-0000-0012-000000000001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0011-000000000001','BankingAgent','check_balance','fetch_account_balance','get_balance_tool','User asked for savings account balance','Returned balance 125000.00');

-- ---------------- NOTIFICATIONS ----------------
INSERT INTO notifications (notification_id, customer_id, channel, title, message, is_read)
VALUES
('00000000-0000-0000-0013-000000000001','00000000-0000-0000-0000-000000000001','SMS','EMI Debited','Your EMI of Rs.14135 has been debited towards your Personal Loan.',FALSE);