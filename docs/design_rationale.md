# MoMo SMS Database — Design Rationale & Data Dictionary



The schema centers on **Transactions** as the fact table, since every business question in this project ("how much moved through the system," "who transacted with whom," "which categories dominate") is answered by aggregating transaction rows. **Users** is separated out rather than embedding sender/receiver names directly on Transactions, because the same phone number appears repeatedly as both sender and receiver across many transactions — storing names inline would duplicate data and make updates (e.g. correcting a misspelled name) require touching every affected row. Two foreign keys on Transactions (`sender_id`, `receiver_id`) both reference Users, modeling the two distinct roles a single user can play without needing two separate tables.

**Transaction_Categories** is a lookup table rather than a hardcoded ENUM on Transactions because categories carry their own metadata (a code used by the ETL rules engine, a description) and the set of categories is expected to grow as new SMS patterns are identified. Because a real transaction can reasonably belong to more than one category (a merchant payment that is also a utility bill), and a category obviously applies to many transactions, we resolved this many-to-many relationship with the **Transaction_Category_Map** junction table rather than forcing a single category per transaction, which would lose information the ETL categorizer already produces.

**System_Logs** exists as a separate audit table, one-to-many from Transactions, so that pipeline errors, warnings, and processing notes (from `parse_xml.py`, `clean_normalize.py`, `categorize.py`, `load_db.py`) can be traced back to the transaction that caused them, without polluting the Transactions table itself with operational metadata. The foreign key is nullable because some log entries are pipeline-level (e.g. "export completed") rather than transaction-specific.

CHECK constraints (positive amounts, non-negative fees and balances, sender ≠ receiver) and FOREIGN KEY constraints enforce integrity at the database layer rather than relying solely on the Python ETL code to catch bad data.

## Data Dictionary

### Users
| Column | Type | Constraints | Description |
|---|---|---|---|
| user_id | INT | PK, AUTO_INCREMENT | Surrogate key |
| phone_number | VARCHAR(15) | NOT NULL, UNIQUE | MSISDN, international format |
| first_name | VARCHAR(50) | NOT NULL | Given name |
| last_name | VARCHAR(50) | NOT NULL | Surname / business name |
| national_id | VARCHAR(20) | UNIQUE, NULLABLE | National ID, absent for merchant/system accounts |
| account_status | ENUM | NOT NULL, DEFAULT 'ACTIVE' | ACTIVE / SUSPENDED / CLOSED |
| account_balance | DECIMAL(14,2) | NOT NULL, CHECK ≥ 0 | Last known balance |
| registration_date | DATETIME | NOT NULL | First-seen timestamp (business meaning) |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Row creation timestamp (audit) |
| updated_at | DATETIME | NOT NULL, auto-updates | Row last-modified timestamp (audit) |

### Transaction_Categories
| Column | Type | Constraints | Description |
|---|---|---|---|
| category_id | INT | PK, AUTO_INCREMENT | Surrogate key |
| category_name | VARCHAR(50) | NOT NULL, UNIQUE | Display name |
| category_code | VARCHAR(20) | NOT NULL, UNIQUE | Code used by categorize.py |
| transaction_type | ENUM | NOT NULL | TRANSFER / PAYMENT / WITHDRAWAL / DEPOSIT / AIRTIME / BILL_PAYMENT |
| description | VARCHAR(255) | NULLABLE | When this category applies |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Row creation timestamp (audit) |
| updated_at | DATETIME | NOT NULL, auto-updates | Row last-modified timestamp (audit) |

### Transactions
| Column | Type | Constraints | Description |
|---|---|---|---|
| transaction_id | BIGINT | PK, AUTO_INCREMENT | Surrogate key |
| reference_number | VARCHAR(30) | NOT NULL, UNIQUE | MoMo reference from SMS |
| sender_id | INT | FK → Users, NOT NULL | Who paid |
| receiver_id | INT | FK → Users, NOT NULL | Who received funds |
| amount | DECIMAL(14,2) | NOT NULL, CHECK > 0 | Transaction amount |
| transaction_fee | DECIMAL(10,2) | NOT NULL, DEFAULT 0, CHECK ≥ 0 | Provider fee |
| currency | CHAR(3) | NOT NULL, DEFAULT 'RWF' | ISO currency code |
| balance_after | DECIMAL(14,2) | NULLABLE | Sender balance post-transaction |
| status | ENUM | NOT NULL, DEFAULT 'COMPLETED' | PENDING / COMPLETED / FAILED / REVERSED |
| transaction_date | DATETIME | NOT NULL | Parsed transaction timestamp |
| raw_sms_body | TEXT | NULLABLE | Original SMS for audit |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Row creation timestamp — when the ETL inserted this record |
| updated_at | DATETIME | NOT NULL, auto-updates | Row last-modified timestamp — e.g. when status changes PENDING → COMPLETED |

### Transaction_Category_Map (junction table)
| Column | Type | Constraints | Description |
|---|---|---|---|
| map_id | INT | PK, AUTO_INCREMENT | Surrogate key |
| transaction_id | BIGINT | FK → Transactions, NOT NULL | |
| category_id | INT | FK → Transaction_Categories, NOT NULL | |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | When the ETL applied this tag |
| updated_at | DATETIME | NOT NULL, auto-updates | Row last-modified timestamp (audit) |
| — | — | UNIQUE(transaction_id, category_id) | Prevents duplicate tagging |

### System_Logs
| Column | Type | Constraints | Description |
|---|---|---|---|
| log_id | INT | PK, AUTO_INCREMENT | Surrogate key |
| transaction_id | BIGINT | FK → Transactions, NULLABLE | NULL for pipeline-level logs |
| process_type | ENUM | NOT NULL | PARSING / VALIDATION / CATEGORIZATION / INSERTION / EXPORT |
| log_level | ENUM | NOT NULL, DEFAULT 'INFO' | INFO / WARNING / ERROR |
| message | TEXT | NOT NULL | Log message |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Log timestamp |
| updated_at | DATETIME | NOT NULL, auto-updates | Row last-modified timestamp (audit) — kept for schema consistency; logs are normally immutable |

## Security & Data-Quality Rules Implemented
1. **Referential integrity** — every FK is enforced (`ON DELETE RESTRICT` for Users↔Transactions, so a user with transaction history cannot be silently deleted; `ON DELETE CASCADE` for the junction table, so removing a transaction cleans up its tags; `ON DELETE SET NULL` for logs, so deleting a transaction doesn't destroy its audit trail).
2. **CHECK constraints** prevent negative amounts, negative fees, negative balances, and a transaction where sender and receiver are the same account.
3. **UNIQUE constraints** on `phone_number`, `national_id`, `reference_number`, and the category-map pair prevent duplicate accounts and duplicate transaction ingestion (idempotent re-runs of the ETL).
4. **Indexes** on all foreign keys and on frequently filtered/sorted columns (`transaction_date`, `status`, `account_status`) support the query patterns used by the dashboard and analytics.
