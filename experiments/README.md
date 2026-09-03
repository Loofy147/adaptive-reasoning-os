# Experiments

The experiments directory is intentionally small. It evaluates mechanisms before turning them into architecture.

## Experiment 001 — Minimal Selective Activation

Question: can a selective procedure reduce activation footprint without reducing task outcome?

The first version is a deterministic harness. It does not call an LLM and does not claim to measure reasoning quality by itself. Its purpose is to make the measurement protocol executable and expose the fields needed for a later model-backed run.

### Compared procedures

- `baseline`: activates the full task-declared mechanism set.
- `selective`: activates the smallest set required by the task specification.

### Recorded variables

- task id and class
- required mechanisms
- active mechanisms
- tools invoked
- context items loaded
- context token estimate
- verification steps
- outcome score
- unsupported-claim count
- correction count
- control overhead

### Primary comparisons

1. Outcome preservation: selective outcome must not materially underperform baseline.
2. Activation reduction: selective should reduce active mechanisms/context where the task permits it.
3. Control overhead: selection cost must remain visible rather than being hidden inside the result.

A passing deterministic harness is not evidence that selective activation improves real model performance. It only proves that the measurement protocol and accounting are internally consistent.
