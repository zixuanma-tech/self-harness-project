from __future__ import annotations

from .models import FailureSignature, HarnessState


class ValidatorSynthesizer:
    def update_state_from_failures(
        self,
        failures: list[FailureSignature],
        state: HarnessState,
    ) -> None:
        for failure in failures:
            if failure.kind == "inventory_not_restored":
                state.generated_validators.add("soft_inventory_restore_qty_two")
            elif failure.kind == "duplicate_refund":
                state.generated_validators.add("hard_idempotent_cancel_guard")
