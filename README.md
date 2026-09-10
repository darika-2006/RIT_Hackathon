# Bank Database Simulation — PostgreSQL

A complete relational schema simulating a multi-service retail bank: core banking, loans, deposits, insurance, pension, government schemes, and support/security — built for a hackathon.

## Files

| File | Purpose |
|---|---|
| `01_schema.sql` | All 20 tables, constraints, foreign keys, and indexes |
| `02_seed_data.sql` | Linked sample data (3 customers) across every table, for demos |
| `README.md` | This file |

## Setup

```bash
createdb bank_sim
psql -d bank_sim -f 01_schema.sql
psql -d bank_sim -f 02_seed_data.sql
```

Requires PostgreSQL 13+. The schema uses the `pgcrypto` extension for `gen_random_uuid()`, which the script enables automatically. All primary keys are UUIDs rather than integers — this avoids ID-collision issues if multiple team members seed data independently during the hackathon, and it mirrors how real banking systems key their records.

## Module map

The 20 tables are grouped into 8 functional domains:

**1. Auth / User**
`customers`, `device_sessions` — the customer identity and their login sessions.

**2. Banking (core)**
`accounts`, `beneficiaries`, `transactions` — every other module ultimately posts money movement through `transactions`, and most services are tied to an `account_id`.

**3. Credit**
`loan_products` → `loan_applications` → `loans` → `loan_repayments`. A product is a template banks offer; an application is a request against a product; an approved application becomes a loan; each EMI paid is a repayment row, optionally linked back to a `transactions` row for the actual money movement.

**4. Savings**
`deposit_products` → `deposits`. A deposit is opened against a specific `account_id`, so the account it matures into is always known.

**5. Insurance**
`insurance_products` → `insurance_policies`.

**6. Pension**
`pension_products` → `pension_accounts`.

**7. Government schemes**
`government_schemes` → `government_benefits`. Each benefit credit also references an `account_id`, since the payout lands in a real account.

**8. Support / Security**
`complaints` (optionally tied to a disputed transaction), `audit_logs` (tied to a customer and session — useful if you're building an AI agent layer on top and want to log every tool call), `notifications`.

## Relationship diagram

```
customers ──┬── device_sessions
            ├── accounts ──┬── transactions
            │              ├── deposits ── deposit_products
            │              └── government_benefits ── government_schemes
            ├── beneficiaries
            ├── loan_applications ── loan_products
            │        └── loans ── loan_repayments ── transactions
            ├── insurance_policies ── insurance_products
            ├── pension_accounts ── pension_products
            ├── complaints ── transactions (optional)
            ├── audit_logs ── device_sessions
            └── notifications
```

Every "X_products" table is a catalog/template table with no customer_id — it defines what the bank offers. Every corresponding "customer-facing" table (applications, policies, accounts, deposits, benefits) has a `customer_id` FK plus a FK back to its product table. This product/instance split means you can add a brand-new loan or insurance product at any time without touching table structure.

## Design choices worth knowing

- **UUID primary keys** everywhere, generated via `gen_random_uuid()`. The seed file instead uses fixed, readable UUIDs (e.g. `00000000-0000-0000-0001-000000000001`) so you can trace exactly which row links to which across tables while demoing.
- **CHECK constraints** are used in place of Postgres ENUM types for all status/type fields (e.g. `account_type`, `status`, `channel`). This keeps the schema easy to alter — adding a new allowed value is a one-line `ALTER TABLE ... DROP CONSTRAINT / ADD CONSTRAINT`, whereas alterating a Postgres ENUM type is more involved.
- **`ON DELETE CASCADE`** is used from `customers` down to their owned rows (accounts, loans, policies, etc.), so deleting a demo customer cleans up after itself. `ON DELETE SET NULL` is used for `audit_logs`, since audit history should usually survive even if the customer or session record is later purged.
- **`loan_repayments.transaction_id`** and **`complaints.transaction_id`** are nullable FKs to `transactions` — a repayment or complaint doesn't strictly need a linked transaction row, but when the money actually moved, you can trace it.
- Indexes are added on every foreign key column plus `transactions.created_at`, since account statements and transaction history are the most common high-volume queries in a system like this.

## Extending this for a hackathon demo

- If you're wiring up an AI agent (the `audit_logs` table is built for this), have every tool call insert a row with `agent_name`, `intent`, `tool_called`, and `result` — that gives you a free activity trail to show judges.
- Sample useful queries to build a demo around:
  - Customer 360 view: join `customers` to `accounts`, `loans`, `deposits`, `insurance_policies`, `pension_accounts` on `customer_id`.
  - Account statement: `SELECT * FROM transactions WHERE account_id = ? ORDER BY created_at DESC`.
  - Loan eligibility check: compare `loan_applications.monthly_income_at_application` and `existing_emi` against `loan_products.min_monthly_income` and `max_existing_emi_ratio`.
- Add more seed rows by following the ID pattern in `02_seed_data.sql` — each table's UUIDs share a group prefix (e.g. all accounts use `...-0001-...`) purely to make the sample data easy to read; it has no meaning to Postgres itself.
