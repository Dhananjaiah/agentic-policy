import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load env vars (DB settings)
load_dotenv(".env.local")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "insurance_core")
DB_USER = os.getenv("DB_USER", "insurance_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "insurance_pass")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def get_policy_by_id(policy_id: str) -> dict | None:
    """Fetch policy + customer info by policy_id."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT p.*, c.full_name, c.email, c.phone
                FROM policies p
                JOIN customers c ON p.customer_id = c.customer_id
                WHERE p.policy_id = %s
                """,
                (policy_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_claim_by_id(claim_id: str) -> dict | None:
    """Fetch claim + policy info by claim_id."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT cl.*, p.product_name, p.status AS policy_status
                FROM claims cl
                JOIN policies p ON cl.policy_id = p.policy_id
                WHERE cl.claim_id = %s
                """,
                (claim_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_docs_for_policy_or_claim(policy_id: str | None, claim_id: str | None) -> list[dict]:
    """Fetch doc metadata for a given policy or claim."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if claim_id:
                cur.execute(
                    """
                    SELECT * FROM documents
                    WHERE claim_id = %s
                    ORDER BY uploaded_at DESC
                    """,
                    (claim_id,),
                )
            elif policy_id:
                cur.execute(
                    """
                    SELECT * FROM documents
                    WHERE policy_id = %s
                    ORDER BY uploaded_at DESC
                    """,
                    (policy_id,),
                )
            else:
                return []

            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()

