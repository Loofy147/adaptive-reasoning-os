# Experiment 001 — Current Result

Date: 2026-09-03

## Scope

This run evaluates a deterministic feature-based selector against a deliberately simple baseline on six hand-authored task fixtures.

It is a **protocol result**, not evidence that an LLM reasons better with selective activation.

## Selector behavior

The selector uses task features (`kind`, `baseline_tools`, `required_context_items`, `required_verification_steps`) and does **not** read `required_mechanisms` while selecting. The latter is evaluation-only ground truth.

## Fixture result

| Task | Baseline mechanisms | Selected mechanisms | Reduction | Outcome delta | Corrections |
|---|---:|---:|---:|---:|---:|
| T1 simple factual | 5 | 2 | 3 | 0.00 | 0 |
| T2 architecture | 5 | 3 | 2 | 0.00 | 0 |
| T3 debugging | 5 | 3 | 2 | 0.00 | 0 |
| T4 repository analysis | 5 | 4 | 1 | 0.00 | 0 |
| T5 planning | 5 | 3 | 2 | 0.00 | 0 |
| T6 evidence verification | 5 | 4 | 1 | 0.00 | 0 |

Mean activation reduction: **1.83 mechanisms/task** (36.7% of the five available mechanisms in this fixture).

Context-token reduction: **0**. The experiment intentionally keeps context loading constant so it isolates activation selection.

Selector corrections: **0** on this fixture.

## Interpretation

The selector is internally consistent on the fixture and demonstrates that activation can be represented and measured separately from outcome.

The result does **not** establish:

- improved reasoning quality;
- lower real token usage;
- generalization to unseen tasks;
- superiority over a strong baseline;
- correctness of the heuristic feature rules.

## Next test required

Replace the hand-authored six-task fixture with a held-out task set and introduce a real execution cost model or real model/tool traces. Measure task outcome and activation footprint together. Include adversarial cases where the selector is expected to make mistakes so that unnecessary activation and under-activation are both observable.
