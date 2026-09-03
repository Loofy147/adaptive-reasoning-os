from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import FrozenSet, Iterable, Tuple


@dataclass(frozen=True)
class Task:
    task_id: str
    kind: str
    required_mechanisms: FrozenSet[str]
    available_mechanisms: FrozenSet[str]
    required_context_items: int
    context_tokens_per_item: int
    required_verification_steps: int
    baseline_tools: int


@dataclass(frozen=True)
class RunResult:
    task_id: str
    procedure: str
    active_mechanisms: Tuple[str, ...]
    tools_invoked: int
    context_items_loaded: int
    context_tokens_estimate: int
    verification_steps: int
    outcome_score: float
    unsupported_claims: int
    correction_count: int
    control_overhead_units: int

    @property
    def activation_count(self) -> int:
        return len(self.active_mechanisms)


def run_baseline(task: Task) -> RunResult:
    mechanisms = tuple(sorted(task.available_mechanisms))
    return RunResult(
        task_id=task.task_id,
        procedure="baseline",
        active_mechanisms=mechanisms,
        tools_invoked=task.baseline_tools,
        context_items_loaded=task.required_context_items,
        context_tokens_estimate=task.required_context_items * task.context_tokens_per_item,
        verification_steps=task.required_verification_steps,
        outcome_score=1.0,
        unsupported_claims=0,
        correction_count=0,
        control_overhead_units=0,
    )


def run_selective(task: Task) -> RunResult:
    # Deterministic oracle for the protocol harness only.
    # A future model-backed experiment must replace this with an actual selector.
    mechanisms = tuple(sorted(task.required_mechanisms))
    return RunResult(
        task_id=task.task_id,
        procedure="selective",
        active_mechanisms=mechanisms,
        tools_invoked=task.baseline_tools,
        context_items_loaded=task.required_context_items,
        context_tokens_estimate=task.required_context_items * task.context_tokens_per_item,
        verification_steps=task.required_verification_steps,
        outcome_score=1.0,
        unsupported_claims=0,
        correction_count=0,
        control_overhead_units=1,
    )


def summarize(runs: Iterable[RunResult]) -> dict:
    runs = list(runs)
    baseline = [r for r in runs if r.procedure == "baseline"]
    selective = [r for r in runs if r.procedure == "selective"]
    if not baseline or not selective:
        raise ValueError("summary requires both baseline and selective runs")

    b = {r.task_id: r for r in baseline}
    s = {r.task_id: r for r in selective}
    task_ids = sorted(set(b) & set(s))

    rows = []
    for task_id in task_ids:
        br, sr = b[task_id], s[task_id]
        rows.append(
            {
                "task_id": task_id,
                "baseline_activation": br.activation_count,
                "selective_activation": sr.activation_count,
                "activation_reduction": br.activation_count - sr.activation_count,
                "baseline_context_tokens": br.context_tokens_estimate,
                "selective_context_tokens": sr.context_tokens_estimate,
                "context_token_reduction": br.context_tokens_estimate - sr.context_tokens_estimate,
                "outcome_delta": sr.outcome_score - br.outcome_score,
                "unsupported_claim_delta": sr.unsupported_claims - br.unsupported_claims,
                "correction_delta": sr.correction_count - br.correction_count,
                "control_overhead": sr.control_overhead_units,
            }
        )

    return {"tasks": rows}


def fixture_tasks() -> list[Task]:
    common = frozenset({
        "framing",
        "evidence_check",
        "retrieval",
        "verification",
        "summarization",
    })
    return [
        Task("T1", "simple_factual", frozenset({"framing", "evidence_check"}), common, 1, 120, 1, 0),
        Task("T2", "architecture", frozenset({"framing", "retrieval", "verification"}), common, 4, 180, 2, 1),
        Task("T3", "debugging", frozenset({"framing", "retrieval", "verification"}), common, 5, 200, 2, 2),
        Task("T4", "repository_analysis", frozenset({"framing", "retrieval", "summarization", "verification"}), common, 8, 220, 3, 2),
        Task("T5", "planning", frozenset({"framing", "summarization", "verification"}), common, 5, 180, 2, 1),
        Task("T6", "evidence_verification", frozenset({"framing", "evidence_check", "retrieval", "verification"}), common, 6, 200, 3, 2),
    ]


def main() -> int:
    tasks = fixture_tasks()
    runs = [r for task in tasks for r in (run_baseline(task), run_selective(task))]
    report = summarize(runs)

    print("Experiment 001 — deterministic protocol harness")
    print("NOTE: this validates accounting/protocol, not real model efficacy.")
    for row in report["tasks"]:
        print(row)

    assert all(row["outcome_delta"] == 0.0 for row in report["tasks"])
    assert any(row["activation_reduction"] > 0 for row in report["tasks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
