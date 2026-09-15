-- =====================================================================
-- MoMo SMS Data Processing System — Database Setup Script
-- Project: momo-sms-analytics
-- Week 2: Database Design and Implementation
-- Engine: MySQL 8.0+
-- =====================================================================

DROP DATABASE IF EXISTS momo_sms_db;
CREATE DATABASE momo_sms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE momo_sms_db;

-- =====================================================================
-- 1. USERS  (Customers — senders and receivers of MoMo transactions)
-- =====================================================================
CREATE TABLE Users (
    user_id             INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Surrogate key for a MoMo account holder',
    phone_number         VARCHAR(15)  NOT NULL UNIQUE COMMENT 'MSISDN in international format, e.g. 250788123456',
    first_name           VARCHAR(50)  NOT NULL COMMENT 'Customer first name as extracted/matched from SMS body',
    last_name            VARCHAR(50)  NOT NULL COMMENT 'Customer last name',
    national_id          VARCHAR(20)  UNIQUE COMMENT 'National ID number, optional (not always present in SMS)',
    account_status       ENUM('ACTIVE', 'SUSPENDED', 'CLOSED') NOT NULL DEFAULT 'ACTIVE' COMMENT 'Current state of the MoMo account',
    account_balance      DECIMAL(14,2) NOT NULL DEFAULT 0.00 COMMENT 'Last known balance in RWF, updated after each transaction',
    registration_date    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When the user was first seen/registered in the system',
    created_at            DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Row creation timestamp (audit)',
    updated_at            DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Row last-modified timestamp (audit)',
    CONSTRAINT chk_balance_non_negative CHECK (account_balance >= 0)
) COMMENT = 'MoMo account holders who appear as sender or receiver in transactions';

CREATE INDEX idx_users_phone ON Users(phone_number);
CREATE INDEX idx_users_status ON Users(account_status);

-- =====================================================================
-- 2. TRANSACTION_CATEGORIES  (Lookup table for transaction types)
-- =====================================================================
CREATE TABLE Transaction_Categories (
    category_id          INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Surrogate key for a transaction category',
    category_name         VARCHAR(50) NOT NULL UNIQUE COMMENT 'Human-readable category, e.g. Airtime Purchase',
    category_code          VARCHAR(20) NOT NULL UNIQUE COMMENT 'Short machine code used by the categorize.py ETL rules engine',
    transaction_type       ENUM('TRANSFER', 'PAYMENT', 'WITHDRAWAL', 'DEPOSIT', 'AIRTIME', 'BILL_PAYMENT') NOT NULL COMMENT 'Broad class of transaction',
    description            VARCHAR(255) COMMENT 'Longer description of when this category applies',
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Row creation timestamp (audit)',
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Row last-modified timestamp (audit)'
) COMMENT = 'Lookup table of transaction categories used by the ETL categorization step';

CREATE INDEX idx_category_type ON Transaction_Categories(transaction_type);

-- --- Users (7 records) ---
INSERT INTO Users (phone_number, first_name, last_name, national_id, account_status, account_balance, registration_date) VALUES
('250788123456', 'Eunice', 'Sangwa',    '1198000000001', 'ACTIVE', 125000.00, '2025-01-10 09:00:00'),
('250788234567', 'Albertine', 'Umuhoza','1198000000002', 'ACTIVE', 48000.00,  '2025-01-11 10:15:00'),
('250788345678', 'Karen', 'Musangwa',   '1198000000003', 'ACTIVE', 302500.00, '2025-01-12 08:30:00'),
('250788456789', 'Kevine', 'Niyonkuru', '1198000000004', 'ACTIVE', 15250.75,  '2025-01-13 14:45:00'),
('250788567890', 'Jean',  'Mugisha',    '1198000000005', 'SUSPENDED', 0.00,   '2025-01-14 16:20:00'),
('250788678901', 'Alpha Store', 'Ltd',  NULL,            'ACTIVE', 890000.00, '2025-01-15 11:00:00'),
('250788789012', 'MTN',   'Airtime',    NULL,             'ACTIVE', 0.00,     '2025-01-01 00:00:00');

-- --- Transaction_Categories (6 records) ---
INSERT INTO Transaction_Categories (category_name, category_code, transaction_type, description) VALUES
('Peer Transfer',        'TXN_P2P',    'TRANSFER',     'Direct transfer between two personal MoMo accounts'),
('Merchant Payment',     'TXN_PAY',    'PAYMENT',      'Payment made to a registered merchant or business account'),
('Cash Withdrawal',      'TXN_WD',     'WITHDRAWAL',   'Cash-out at an agent till'),
('Cash Deposit',         'TXN_DEP',    'DEPOSIT',      'Cash-in at an agent till'),
('Airtime Purchase',     'TXN_AIR',    'AIRTIME',      'Purchase of mobile airtime/bundles'),
('Utility Bill Payment', 'TXN_BILL',   'BILL_PAYMENT', 'Payment toward electricity, water, or other utility bills');


-- =====================================================================
-- 3. TRANSACTIONS  (Core fact table — one row per parsed SMS transaction)
-- =====================================================================
CREATE TABLE Transactions (
    transaction_id        BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Surrogate key for a transaction',
    reference_number        VARCHAR(30) NOT NULL UNIQUE COMMENT 'MoMo transaction reference extracted from the SMS body',
    sender_id               INT NOT NULL COMMENT 'FK to Users — who initiated/paid',
    receiver_id              INT NOT NULL COMMENT 'FK to Users — who received the funds',
    amount                   DECIMAL(14,2) NOT NULL COMMENT 'Transaction amount in RWF',
    transaction_fee           DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Fee charged by the provider, if any',
    currency                  CHAR(3) NOT NULL DEFAULT 'RWF' COMMENT 'ISO currency code',
    balance_after              DECIMAL(14,2) COMMENT 'Sender balance immediately after the transaction, if present in SMS',
    status                     ENUM('PENDING', 'COMPLETED', 'FAILED', 'REVERSED') NOT NULL DEFAULT 'COMPLETED' COMMENT 'Outcome of the transaction',
    transaction_date            DATETIME NOT NULL COMMENT 'Timestamp of the transaction as parsed from the SMS',
    raw_sms_body                 TEXT COMMENT 'Original SMS text, retained for auditability/debugging',
    created_at                    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Row creation timestamp (audit)',
    updated_at                    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Row last-modified timestamp (audit)',
    CONSTRAINT fk_txn_sender FOREIGN KEY (sender_id) REFERENCES Users(user_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_txn_receiver FOREIGN KEY (receiver_id) REFERENCES Users(user_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_amount_positive CHECK (amount > 0),
    CONSTRAINT chk_fee_non_negative CHECK (transaction_fee >= 0),
    CONSTRAINT chk_sender_receiver_diff CHECK (sender_id <> receiver_id)
) COMMENT = 'Core fact table: one row per MoMo transaction parsed from SMS';

CREATE INDEX idx_txn_date ON Transactions(transaction_date);
CREATE INDEX idx_txn_status ON Transactions(status);
CREATE INDEX idx_txn_sender ON Transactions(sender_id);
CREATE INDEX idx_txn_receiver ON Transactions(receiver_id);

-- --- Transactions (7 records) ---
INSERT INTO Transactions (reference_number, sender_id, receiver_id, amount, transaction_fee, currency, balance_after, status, transaction_date, raw_sms_body) VALUES
('MP240115.0930.A12345', 1, 2, 15000.00, 100.00, 'RWF', 109900.00, 'COMPLETED', '2025-01-15 09:30:00', 'You have transferred 15000 RWF to Albertine Umuhoza...'),
('MP240115.1102.B23456', 3, 6, 25000.00, 0.00,   'RWF', 277500.00, 'COMPLETED', '2025-01-15 11:02:00', 'Your payment of 25000 RWF to Alpha Store Ltd was successful...'),
('MP240115.1245.C34567', 4, 7, 2000.00,  0.00,   'RWF', 13250.75,  'COMPLETED', '2025-01-15 12:45:00', 'Your airtime purchase of 2000 RWF was successful...'),
('MP240115.1500.D45678', 2, 1, 10000.00, 50.00,  'RWF', 37950.00,  'COMPLETED', '2025-01-15 15:00:00', 'You have transferred 10000 RWF to Eunice Sangwa...'),
('MP240115.1630.E56789', 6, 3, 5000.00,  0.00,   'RWF', 885000.00, 'REVERSED',  '2025-01-15 16:30:00', 'Transaction reversed: refund of 5000 RWF...'),
('MP240116.0800.F67890', 1, 6, 45000.00, 200.00, 'RWF', 64700.00,  'COMPLETED', '2025-01-16 08:00:00', 'Your payment of 45000 RWF to Alpha Store Ltd was successful...'),
('MP240116.0915.G78901', 3, 7, 1500.00,  0.00,   'RWF', 301000.00, 'PENDING',   '2025-01-16 09:15:00', 'Your airtime purchase of 1500 RWF is being processed...');
 
-- =====================================================================
-- 4. TRANSACTION_CATEGORY_MAP  (Junction table — resolves M:N)
-- =====================================================================
-- A single transaction can carry more than one category tag, and a category
-- applies to many transactions. This junction table resolves that M:N
-- relationship between Transactions and Transaction_Categories.
-- =====================================================================
CREATE TABLE Transaction_Category_Map (
    map_id               INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id         BIGINT NOT NULL COMMENT 'FK to Transactions',
    category_id             INT NOT NULL COMMENT 'FK to Transaction_Categories',
    created_at                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When this category tag was applied by the ETL',
    updated_at                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Row last-modified timestamp (audit)',
    CONSTRAINT fk_map_transaction FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_map_category FOREIGN KEY (category_id) REFERENCES Transaction_Categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_txn_category UNIQUE (transaction_id, category_id)
) COMMENT = 'Junction table resolving the M:N relationship between Transactions and Transaction_Categories';

-- =====================================================================
-- 5. SYSTEM_LOGS  (ETL pipeline audit trail)
-- =====================================================================
CREATE TABLE System_Logs (
    log_id                INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id           BIGINT COMMENT 'FK to Transactions — nullable, since some logs are pipeline-level',
    process_type              ENUM('PARSING', 'VALIDATION', 'CATEGORIZATION', 'INSERTION', 'EXPORT') NOT NULL COMMENT 'Which ETL stage produced this log',
    log_level                  ENUM('INFO', 'WARNING', 'ERROR') NOT NULL DEFAULT 'INFO',
    message                     TEXT NOT NULL COMMENT 'Human-readable log message',
    created_at                   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Row creation timestamp (audit)',
    updated_at                   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Row last-modified timestamp (audit)',
    CONSTRAINT fk_log_transaction FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
        ON UPDATE CASCADE ON DELETE SET NULL
) COMMENT = 'Audit trail for the ETL pipeline';

CREATE INDEX idx_log_level ON System_Logs(log_level);
CREATE INDEX idx_log_process ON System_Logs(process_type);
CREATE INDEX idx_log_created ON System_Logs(created_at);

-- --- Transaction_Category_Map (9 records) ---
INSERT INTO Transaction_Category_Map (transaction_id, category_id) VALUES
(1, 1), (2, 2), (2, 6), (3, 5), (4, 1), (5, 2), (6, 2), (6, 6), (7, 5);

-- --- System_Logs (7 records) ---
INSERT INTO System_Logs (transaction_id, process_type, log_level, message, created_at) VALUES
(1, 'PARSING',      'INFO', 'Successfully parsed SMS node into transaction MP240115.0930.A12345', '2025-01-15 09:30:05'),
(1, 'INSERTION',     'INFO', 'Inserted transaction MP240115.0930.A12345 into Transactions table', '2025-01-15 09:30:06'),
(2, 'CATEGORIZATION', 'INFO', 'Assigned categories Merchant Payment, Utility Bill Payment', '2025-01-15 11:02:04'),
(3, 'VALIDATION',    'WARNING', 'Amount field required rounding from raw SMS text', '2025-01-15 12:45:02'),
(5, 'INSERTION',     'INFO', 'Transaction MP240115.1630.E56789 marked REVERSED on insert', '2025-01-15 16:30:07'),
(NULL, 'EXPORT',     'INFO', 'dashboard.json export completed: 7 transactions exported', '2025-01-16 10:00:00'),
(7, 'VALIDATION',    'ERROR', 'Duplicate reference number check flagged, then cleared after review', '2025-01-16 09:15:03');
