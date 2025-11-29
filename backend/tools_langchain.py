from typing import Optional, Dict

from .tools_db import (
    get_policy_by_id,
    get_claim_by_id,
    get_docs_for_policy_or_claim,
)


def get_policy(policy_id: str) -> Dict:
    """Get detailed information about a policy."""
    policy = get_policy_by_id(policy_id)
    if policy is None:
        return {"found": False, "policy_id": policy_id}
    return {"found": True, "policy": policy}


def get_claim(claim_id: str) -> Dict:
    """Get detailed information about a claim."""
    claim = get_claim_by_id(claim_id)
    if claim is None:
        return {"found": False, "claim_id": claim_id}
    return {"found": True, "claim": claim}


def get_documents(
    policy_id: Optional[str] = None,
    claim_id: Optional[str] = None,
) -> Dict:
    """Get document metadata for a policy or claim."""
    docs = get_docs_for_policy_or_claim(policy_id, claim_id)
    return {
        "policy_id": policy_id,
        "claim_id": claim_id,
        "documents": docs,
    }

