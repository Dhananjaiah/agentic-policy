-- Drop existing tables (for local dev convenience)
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS claims CASCADE;
DROP TABLE IF EXISTS policies CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- 1) Customers
CREATE TABLE customers (
    customer_id      BIGSERIAL PRIMARY KEY,
    full_name        VARCHAR(150) NOT NULL,
    email            VARCHAR(150) NOT NULL,
    phone            VARCHAR(30)  NOT NULL,
    date_of_birth    DATE         NOT NULL,
    city             VARCHAR(100),
    state            VARCHAR(100),
    country          VARCHAR(100) DEFAULT 'India',
    created_at       TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2) Policies
CREATE TABLE policies (
    policy_id        VARCHAR(32) PRIMARY KEY,
    customer_id      BIGINT NOT NULL REFERENCES customers(customer_id),
    product_code     VARCHAR(50) NOT NULL,        -- HLTH_SILVER, MOTOR_GOLD, etc.
    product_name     VARCHAR(100) NOT NULL,       -- "Health Shield Silver"
    start_date       DATE NOT NULL,
    end_date         DATE NOT NULL,
    status           VARCHAR(20) NOT NULL,        -- ACTIVE / LAPSED / EXPIRED / CANCELLED
    sum_insured      NUMERIC(14,2) NOT NULL,
    annual_premium   NUMERIC(14,2) NOT NULL,
    created_at       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_policies_customer_id ON policies(customer_id);
CREATE INDEX idx_policies_status ON policies(status);

-- 3) Claims
CREATE TABLE claims (
    claim_id            VARCHAR(32) PRIMARY KEY,
    policy_id           VARCHAR(32) NOT NULL REFERENCES policies(policy_id),
    claim_type          VARCHAR(20) NOT NULL,     -- HEALTH / MOTOR / PROPERTY / LIFE
    status              VARCHAR(20) NOT NULL,     -- OPEN / UNDER_REVIEW / APPROVED / REJECTED / CLOSED
    reported_date       DATE NOT NULL,
    loss_date           DATE NOT NULL,
    requested_amount    NUMERIC(14,2) NOT NULL,
    approved_amount     NUMERIC(14,2),
    currency            VARCHAR(3) NOT NULL DEFAULT 'INR',
    last_updated        TIMESTAMP NOT NULL DEFAULT NOW(),
    reason_if_rejected  TEXT
);

CREATE INDEX idx_claims_policy_id ON claims(policy_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_reported_date ON claims(reported_date);

-- 4) Documents metadata (for S3 / SharePoint)
CREATE TABLE documents (
    document_id     BIGSERIAL PRIMARY KEY,
    policy_id       VARCHAR(32) REFERENCES policies(policy_id),
    claim_id        VARCHAR(32) REFERENCES claims(claim_id),
    doc_type        VARCHAR(50) NOT NULL,       -- KYC, HOSPITAL_BILL, DISCHARGE_SUMMARY, FIR, etc.
    storage_system  VARCHAR(20) NOT NULL,       -- S3, SHAREPOINT
    storage_path    TEXT NOT NULL,              -- s3 key or sharepoint URL
    uploaded_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_claim_id ON documents(claim_id);
CREATE INDEX idx_documents_policy_id ON documents(policy_id);
CREATE INDEX idx_documents_doc_type ON documents(doc_type);

