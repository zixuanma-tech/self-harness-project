from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FailureSignature:
    kind: str
    severity: str  # "hard" or "soft"
    nodeid: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ValidationOutcome:
    hard_failures: list[FailureSignature] = field(default_factory=list)
    soft_failures: list[FailureSignature] = field(default_factory=list)
    passed: list[str] = field(default_factory=list)
    raw_summary: dict[str, int] = field(default_factory=dict)

    @property
    def all_failures(self) -> list[FailureSignature]:
        return [*self.hard_failures, *self.soft_failures]

    @property
    def is_clean(self) -> bool:
        return not self.hard_failures and not self.soft_failures


@dataclass(slots=True)
class CandidateModification:
    name: str
    description: str


@dataclass(slots=True)
class QuarantineBranch:
    workspace: Path
    reason: str
    merge_predicate: str
    failure_signatures: list[FailureSignature] = field(default_factory=list)


@dataclass(slots=True)
class HarnessState:
    generated_validators: set[str] = field(default_factory=set)
    regression_memory: list[str] = field(default_factory=list)
    quarantine: QuarantineBranch | None = None
    used_budget: float = 0.0


@dataclass(slots=True)
class Decision:
    action: str  # accept / reject / quarantine
    reason: str


@dataclass(slots=True)
class RoundRecord:
    round_id: int
    source_workspace: str
    candidate_workspace: str | None
    candidate_name: str | None
    action: str
    reason: str
    hard_failures: list[dict[str, Any]]
    soft_failures: list[dict[str, Any]]
    generated_validators: list[str]
