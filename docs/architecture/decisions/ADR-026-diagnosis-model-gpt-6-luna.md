Title: gpt-6-luna as Recommendation's diagnosis model for dev and the OE3-I2 evaluation
Status: Accepted
Date: 2026-11-23
Amends: ADR-004 (the "GPT-4 family" restriction, for this scope); fixes the variant left open by PD-026 for dev and the OE3-I2 evaluation

## Context

[ADR-004](ADR-004-azure-openai.md) selected Azure OpenAI by API with the GPT-4 family and left the
variant open. [PD-026](../pending-decisions.md) recorded the owner's approval of `gpt-4o` 2024-11-20
(`pipesor-dev-diagnostics`) **only for the DEV smoke test**. The selection for formal validation was
left pending.

The OE3-I2 evaluation must run its `test` split with a single model chosen beforehand on the `dev` split
([evaluation protocol](../../research/protocolo-evaluacion-oe3.md), §6.2). Four candidates were
deployed on the existing Foundry account `ai-pipesor-dev-04f339b7` (DataZoneStandard), one per cost
tier plus the baseline:

| Deployment | Model | USD per 1M tokens (in / out) |
|---|---|---|
| `pipesor-dev-diagnostics` | gpt-4o 2024-11-20 (baseline) | 2.75 / 11.00 |
| `pipesor-dev-diagnostics-luna` | gpt-6-luna 2026-09-22 | 0.11 / 0.55 |
| `pipesor-dev-diagnostics-terra` | gpt-6.1-terra 2026-10-26 | 1.10 / 5.50 |
| `pipesor-dev-diagnostics-sol` | gpt-6.2-sol 2026-11-17 | 2.20 / 11.00 |

The comparison replayed exactly the request Recommendation's `AzureOpenAiInference` builds:
- prompt `diagnostic-hypothesis-v2`;
- strict JSON Schema with the supplied IDs as enums;
- `max_completion_tokens` 1024 and no sampling parameters.

It used fixed inputs for the 13 dev cases (10 positives, 3 outside the inventory): with the frozen
retrieval (C1, protocol §6.1) and without knowledge (C0). Each case ran 3 times, for 312 calls in total.
The data, method and limitations are in
[pipesor-validation-scenarios](https://github.com/pipesor-org/pipesor-validation-scenarios/tree/main/results/model-selection/2026-11-23):

| Model | Gate (C1) | Key-term proxy, positives (C1, majority of 3) | USD per diagnosis | p95 latency |
|---|---|---|---|---|
| gpt-4o | 39/39 | 4/10 | 0.0057 | 4.3 s |
| **gpt-6-luna** | 39/39 | **10/10** | **0.0004** | 9.9 s |
| gpt-6.1-terra | 39/39 | 8/10 | 0.0030 | 5.4 s |
| gpt-6.2-sol | 39/39 | 9/10 | 0.0061 | 3.7 s |

All 312 responses passed the gate: `finish_reason = stop`, no refusals, a valid schema and citations
only to supplied IDs.

## Decision

- Recommendation uses **gpt-6-luna 2026-09-22** through the deployment `pipesor-dev-diagnostics-luna`
  in dev and for the OE3-I2 evaluation runs. The model is frozen before the `test` split runs.
- The basis is protocol §6.2's rule, applied to the gate and the key-term proxy: gpt-6-luna is the
  cheapest model that is not two or more positives below the best.
- **Recorded deviation.** The protocol's primary criterion, the human rubric on repetition 1, was not
  applied before deciding. The project owner chose to proceed on the gate and proxy evidence. The proxy
  has known false negatives, so it may under-count other models; it does not over-count luna. The blind
  rating sheets remain available. If a rubric pass before the `test` runs shows gpt-6-luna two or more
  positives below the best, the decision is revisited.
- The prompt, the schema and the retrieval configuration are unchanged by this decision.

## Consequences

- **Switching `chat_deployment`** to `pipesor-dev-diagnostics-luna` is an IaC change applied by the
  infrastructure session through a reviewed plan. Run manifests record the deployment and the reported
  model version.
- **Latency and tokens:** gpt-6-luna is the slowest candidate (p95 about 9.9 s against 3.7–5.4 s) and
  uses up to about half of the completion budget (525 of 1024 tokens, up to 214 of them for reasoning).
  Diagnosis is asynchronous, so the latency is acceptable. `finish_reason = stop` must keep being
  monitored on long excerpts.
- **Cost:** about USD 0.0004 per diagnosis, against 0.0057 with gpt-4o.
- **Limits of the evidence:**
  - 10 positive dev cases, so one case is 10 points;
  - synthetic and partially simulated scenarios;
  - evidence emulated from the ingestion excerpt and its protection.

  Differences of one case are not claimed as superiority.
- **Scope:** PD-026 remains open for other environments (qa, preprod, prod) and for selections after the
  evaluation. Check the model's retirement date and quota before the next academic cycle.
- **ADR-004** keeps Azure OpenAI by API and the absence of self-hosting or training. Only its GPT-4
  family restriction is amended for this scope.
