from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable, Tuple


@dataclass(frozen=True)
class Task:
    task_id: str
    kind: str
    required_mechanisms: FrozenSet[str]  # evaluation-only ground truth
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
        task.task_id, "baseline", mechanisms, task.baseline_tools,
        task.required_context_items, task.required_context_items * task.context_tokens_per_item,
        task.required_verification_steps, 1.0, 0, 0, 0,
    )


def select_mechanisms(task: Task) -> Tuple[str, ...]:
    """Simple feature-based selector; required_mechanisms is never read here."""
    selected = {"framing"}

    if task.kind in {"evidence_verification", "simple_factual"}:
        selected.add("evidence_check")
    if task.baseline_tools > 0 or task.required_context_items >= 4:
        selected.add("retrieval")
    if task.required_verification_steps > 0:
        selected.add("verification")
    if task.kind in {"repository_analysis", "planning"} or task.required_context_items >= 5:
        selected.add("summarization")

    return tuple(sorted(selected & task.available_mechanisms))


def evaluate_selector(task: Task, selected: Tuple[str, ...]) -> tuple[float, int]:
    """Return outcome proxy and correction count from selector mistakes.

    This is a deterministic scoring model for protocol validation, not a reasoning-quality
    evaluator. Missing required mechanisms incur a correction; extra mechanisms incur no
    reward and therefore remain visible as unnecessary activation.
    """
    missing = task.required_mechanisms - set(selected)
    corrections = len(missing)
    outcome = max(0.0, 1.0 - 0.25 * corrections)
    return outcome, corrections


def run_selective(task: Task) -> RunResult:
    mechanisms = select_mechanisms(task)
    outcome, corrections = evaluate_selector(task, mechanisms)
    return RunResult(
        task.task_id, "selective", mechanisms, task.baseline_tools,
        task.required_context_items, task.required_context_items * task.context_tokens_per_item,
        task.required_verification_steps, outcome,
        len(task.required_mechanisms - set(mechanisms)), corrections, 1,
    )


def summarize(runs: Iterable[RunResult]) -> dict:
    runs = list(runs)
    baseline = {r.task_id: r for r in runs if r.procedure == "baseline"}
    selective = {r.task_id: r for r in runs if r.procedure == "selective"}
    task_ids = sorted(set(baseline) & set(selective))
    if not task_ids:
        raise ValueError("summary requires matching baseline and selective runs")

    rows = []
    for task_id in task_ids:
        br, sr = baseline[task_id], selective[task_id]
        rows.append({
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
        })
    return {"tasks": rows}


def fixture_tasks() -> list[Task]:
    common = frozenset({"framing", "evidence_check", "retrieval", "verification", "summarization"})
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
    print("Experiment 001 — heuristic selective activation harness")
    print("NOTE: the selector is deterministic; outcome is a protocol proxy, not model quality.")
    for row in report["tasks"]:
        print(row)
    assert any(row["activation_reduction"] > 0 for row in report["tasks"])
    assert any(row["correction_delta"] > 0 for row in report["tasks"]) is False
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
