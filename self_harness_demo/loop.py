from __future__ import annotations

from pathlib import Path

from .admission import AdmissionController
from .agent import LLMAgent
from .env import WorkspaceManager
from .logger import JsonlLogger
from .models import HarnessState, QuarantineBranch, RoundRecord
from .patches import CandidateApplier
from .pytest_runner import run_pytest_validation
from .synth import ValidatorSynthesizer
from .validator_materializer import ValidatorMaterializer


class SelfHarnessLoop:
    def __init__(self, runtime_root: Path, max_rounds: int = 4):
        self.runtime_root = runtime_root
        self.max_rounds = max_rounds
        self.workspace_manager = WorkspaceManager(runtime_root)
        self.agent = LLMAgent()
        self.applier = CandidateApplier()
        self.admission = AdmissionController()
        self.synthesizer = ValidatorSynthesizer()
        self.logger = JsonlLogger(runtime_root / "logs" / "rounds.jsonl")

    def _materialize_validators(self, workspace: Path, state: HarnessState) -> None:
        materializer = ValidatorMaterializer(state.generated_validators)
        materializer.materialize_into(workspace)

    def run(self) -> Path:
        state = HarnessState()
        mainline = self.workspace_manager.create_initial_workspace()
        self._materialize_validators(mainline, state)

        # Baseline validation of the initial buggy system.
        baseline = run_pytest_validation(mainline)
        self.synthesizer.update_state_from_failures(baseline.all_failures, state)
        self.logger.log(
            RoundRecord(
                round_id=0,
                source_workspace=str(mainline),
                candidate_workspace=None,
                candidate_name=None,
                action="baseline",
                reason="Initial validation of the buggy workspace.",
                hard_failures=[f.to_dict() for f in baseline.hard_failures],
                soft_failures=[f.to_dict() for f in baseline.soft_failures],
                generated_validators=sorted(state.generated_validators),
            )
        )

        current_failures = baseline.all_failures
        active_workspace = mainline

        for round_id in range(1, self.max_rounds + 1):
            if state.quarantine is not None:
                active_workspace = state.quarantine.workspace
                current_failures = state.quarantine.failure_signatures
            else:
                active_workspace = mainline

            candidate = self.agent.propose(current_failures, state)

            candidate_workspace = self.workspace_manager.clone_workspace(
                active_workspace,
                f"candidate_round_{round_id}_{candidate.name}",
            )
            self._materialize_validators(candidate_workspace, state)
            self.applier.apply(candidate_workspace, candidate)

            outcome = run_pytest_validation(candidate_workspace)
            decision = self.admission.decide(outcome, state)
            self.synthesizer.update_state_from_failures(outcome.all_failures, state)

            if decision.action == "accept":
                new_mainline = self.workspace_manager.clone_workspace(
                    candidate_workspace,
                    f"mainline_round_{round_id}",
                )
                mainline = new_mainline
                state.quarantine = None
                state.regression_memory.append(candidate.name)
                current_failures = []
            elif decision.action == "quarantine":
                quarantine_workspace = self.workspace_manager.clone_workspace(
                    candidate_workspace,
                    f"quarantine_round_{round_id}",
                )
                state.quarantine = QuarantineBranch(
                    workspace=quarantine_workspace,
                    reason=decision.reason,
                    merge_predicate="All current validators pass on a future round.",
                    failure_signatures=outcome.all_failures,
                )
                current_failures = outcome.all_failures
            else:  # reject
                current_failures = outcome.all_failures or current_failures

            self.logger.log(
                RoundRecord(
                    round_id=round_id,
                    source_workspace=str(active_workspace),
                    candidate_workspace=str(candidate_workspace),
                    candidate_name=candidate.name,
                    action=decision.action,
                    reason=decision.reason,
                    hard_failures=[f.to_dict() for f in outcome.hard_failures],
                    soft_failures=[f.to_dict() for f in outcome.soft_failures],
                    generated_validators=sorted(state.generated_validators),
                )
            )

            if decision.action == "accept" and outcome.is_clean:
                return mainline

        return mainline