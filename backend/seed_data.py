import os
import random
from datetime import timedelta

import psycopg2
from psycopg2.extras import RealDictCursor
from faker import Faker
from dotenv import load_dotenv

# Load local env (DB settings)
load_dotenv(".env.local")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "insurance_core")
DB_USER = os.getenv("DB_USER", "insurance_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "insurance_pass")

fake = Faker("en_IN")
random.seed(42)

PRODUCTS = [
    ("HLTH_SILVER", "Health Shield Silver"),
    ("HLTH_GOLD", "Health Shield Gold"),
    ("HLTH_PLATINUM", "Health Shield Platinum"),
    ("MOTOR_BASIC", "Motor Protect Basic"),
    ("MOTOR_COMPRE", "Motor Protect Comprehensive"),
    ("PROP_HOME", "Home Guard Property"),
    ("LIFE_TERM", "Life Term Secure"),
]

CLAIM_TYPES = ["HEALTH", "MOTOR", "PROPERTY", "LIFE"]
CLAIM_STATUSES = ["OPEN", "UNDER_REVIEW", "APPROVED", "REJECTED", "CLOSED"]
DOC_TYPES = ["KYC", "HOSPITAL_BILL", "DISCHARGE_SUMMARY", "FIR", "ID_PROOF"]


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def seed_customers(cur, count=300):
    customers = []
    for _ in range(count):
        full_name = fake.name()
        email = fake.unique.email()
        phone = fake.msisdn()[:10]
        dob = fake.date_between(start_date="-60y", end_date="-20y")
        city = fake.city()
        state = fake.state()
        cur.execute(
            """
            INSERT INTO customers (full_name, email, phone, date_of_birth, city, state)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING customer_id
            """,
            (full_name, email, phone, dob, city, state),
        )
        customer_id = cur.fetchone()[0]
        customers.append(customer_id)
    return customers


def seed_policies(cur, customers, count=500):
    policies = []
    for i in range(count):
        customer_id = random.choice(customers)
        policy_id = f"POL-{100000 + i}"
        product_code, product_name = random.choice(PRODUCTS)

        start_date = fake.date_between(start_date="-3y", end_date="today")
        end_date = start_date + timedelta(days=365)

        status_weights = ["ACTIVE"] * 5 + ["LAPSED"] * 2 + ["EXPIRED"] * 2 + ["CANCELLED"]
        status = random.choice(status_weights)

        sum_insured = random.choice([200000, 300000, 500000, 1000000, 2000000])
        annual_premium = sum_insured * random.uniform(0.02, 0.06)

        cur.execute(
            """
            INSERT INTO policies (
                policy_id, customer_id, product_code, product_name,
                start_date, end_date, status, sum_insured, annual_premium
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                policy_id,
                customer_id,
                product_code,
                product_name,
                start_date,
                end_date,
                status,
                round(sum_insured, 2),
                round(annual_premium, 2),
            ),
        )
        policies.append(policy_id)
    return policies


def seed_claims(cur, policies, count=1000):
    claims = []
    for i in range(count):
        policy_id = random.choice(policies)
        claim_id = f"CLM-{200000 + i}"

        claim_type = random.choice(CLAIM_TYPES)
        reported_date = fake.date_between(start_date="-2y", end_date="today")
        loss_date = reported_date - timedelta(days=random.randint(0, 10))

        requested_amount = random.choice([25000, 50000, 75000, 100000, 150000, 200000])
        status = random.choice(CLAIM_STATUSES)

        approved_amount = None
        reason_if_rejected = None

        if status == "APPROVED":
            approved_amount = requested_amount * random.uniform(0.6, 1.0)
        elif status == "REJECTED":
            reason_if_rejected = random.choice(
                [
                    "Policy not active at the time of loss",
                    "Non-disclosure of pre-existing condition",
                    "Insufficient documentation",
                    "Loss event not covered under policy terms",
                ]
            )
        elif status in ["OPEN", "UNDER_REVIEW"]:
            pass
        else:
            approved_amount = requested_amount * random.uniform(0.3, 1.0)

        cur.execute(
            """
            INSERT INTO claims (
                claim_id, policy_id, claim_type, status,
                reported_date, loss_date, requested_amount,
                approved_amount, currency, reason_if_rejected
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                claim_id,
                policy_id,
                claim_type,
                status,
                reported_date,
                loss_date,
                round(requested_amount, 2),
                round(approved_amount, 2) if approved_amount is not None else None,
                "INR",
                reason_if_rejected,
            ),
        )
        claims.append(claim_id)
    return claims


def seed_documents(cur, policies, claims, count=2000):
    for _ in range(count):
        if random.random() < 0.8:
            claim_id = random.choice(claims)
            policy_id = None
        else:
            claim_id = None
            policy_id = random.choice(policies)

        doc_type = random.choice(DOC_TYPES)
        storage_system = random.choice(["S3", "SHAREPOINT"])

        if storage_system == "S3":
            storage_path = f"s3://insurance-bucket/{doc_type.lower()}/{fake.uuid4()}.pdf"
        else:
            storage_path = f"https://sharepoint.example.com/docs/{doc_type.lower()}/{fake.uuid4()}.pdf"

        cur.execute(
            """
            INSERT INTO documents (policy_id, claim_id, doc_type, storage_system, storage_path)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (policy_id, claim_id, doc_type, storage_system, storage_path),
        )


def main():
    print("Connecting to DB...")
    conn = get_connection()
    conn.autocommit = False
    cur = conn.cursor()


    try:
        print("Seeding customers...")
        customers = seed_customers(cur, count=300)
        print(f"Inserted {len(customers)} customers")

        print("Seeding policies...")
        policies = seed_policies(cur, customers, count=500)
        print(f"Inserted {len(policies)} policies")

        print("Seeding claims...")
        claims = seed_claims(cur, policies, count=1000)
        print(f"Inserted {len(claims)} claims")

        print("Seeding documents...")
        seed_documents(cur, policies, claims, count=2000)
        print("Inserted ~2000 documents")

        conn.commit()
        print("Seeding completed successfully.")
    except Exception as e:
        conn.rollback()
        print("Error during seeding, rolled back:", e)
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()

