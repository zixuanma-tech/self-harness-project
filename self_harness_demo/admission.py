from __future__ import annotations

from .models import Decision, HarnessState, ValidationOutcome


class AdmissionController:
    def decide(self, outcome: ValidationOutcome, state: HarnessState) -> Decision:
        if outcome.hard_failures:
            return Decision(action="reject", reason="Hard validator failure detected.")
        if outcome.soft_failures:
            return Decision(action="quarantine", reason="Soft validators still fail; keep candidate out of mainline.")
        return Decision(action="accept", reason="All current validators pass.")
