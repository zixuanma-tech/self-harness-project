from __future__ import annotations

from .models import CandidateModification, FailureSignature, HarnessState
from .llm_client import ask_llm


ALLOWED_PATCHES = {
    "make_cancel_idempotent": "Fix duplicate refund by making cancel_order idempotent.",
    "restore_inventory_on_cancel": "Restore inventory when an order is canceled.",
    "noop": "Make no change.",
}


class LLMAgent:
    """
    LLM-backed candidate generator for the minimal Self-Harness demo.
    """

    def propose(
        self,
        failure_signatures: list[FailureSignature],
        harness_state: HarnessState,
    ) -> CandidateModification:
        failure_text = "\n".join(
            f"- severity={f.severity}, kind={f.kind}, nodeid={f.nodeid}"
            for f in failure_signatures
        ) or "(none)"

        validator_text = "\n".join(sorted(harness_state.generated_validators)) or "(none)"

        prompt = f"""
You are selecting the next candidate patch for a minimal Self-Harness repair loop.

Current failure signatures:
{failure_text}

Current generated validators:
{validator_text}

You must choose exactly ONE patch name from the following list:
- make_cancel_idempotent
- restore_inventory_on_cancel
- noop

Decision rules:
1. If there is a duplicate_refund hard failure, prefer make_cancel_idempotent.
2. If duplicate_refund is gone but inventory_not_restored remains, prefer restore_inventory_on_cancel.
3. If nothing is clearly actionable, choose noop.

Return ONLY the patch name, with no explanation.
""".strip()

        answer = ask_llm(prompt).strip()

        if answer not in ALLOWED_PATCHES:
            answer = "noop"

        return CandidateModification(
            name=answer,
            description=ALLOWED_PATCHES[answer],
        )