# Protected workflow evidence 2.1

Status: approved local integration contract for the GitHub aggregate-evidence increment. It extends, and does not reinterpret, protected workflow evidence 2.0.

Current producers emit [protected workflow evidence 2.2](protected-evidence-v2.2.md), which extends this version. These 2.1 rules remain in force for decoding 2.1 messages and for 2.1 locators already emitted or persisted.

## Compatibility

- Step-attributed evidence remains schema `2.0` and must not contain `evidence.source_locator`.
- Job-aggregate evidence uses schema `2.1`, while broker application property `schemaMajor` remains `2`.
- Consumers must retain their 2.0 decoder while accepting 2.1 explicitly. A 2.1 message without a valid locator, or a 2.0 message containing one, is invalid.

## Aggregate source locator

The current bounded Verify profile uses:

```text
v2:job:<job-id>:member:<archive-member>:lines:<first>-<last>:sha256:<digest>
```

For this increment, `<archive-member>` is the exact root ZIP member `[0-9]{1,9}_verify.txt`; the canonical positive-decimal job ID must equal the authenticated GitHub API job identity. The inclusive line range is currently a single line (`first == last`) selected inside the authenticated failed-step time interval. No step identity appears in this locator.

The lowercase digest is SHA-256 over the exact selected UTF-8 source bytes represented by that line before masking. It includes the original line terminator when present and includes an original UTF-8 BOM if the selected first line carried one. Implementations decode only strict UTF-8 and re-encode the retained raw substring; therefore a reproducible check must use the same original member bytes and line boundaries.

`evidence.excerpt` is separately protected and minimized. Its bytes are not the digest input, and the raw private log must not be published merely to make the digest reproducible.

## Preservation and replay

Ingestion binds repository, workflow, run, attempt, job, exact member, line range and digest before protection and freezes the publication plan. Log/Event stores the locator together with the authenticated execution binding. NLP sanitizes the protected excerpt defensively and forwards the locator unchanged. Correlation includes it in replay identity and in the protected signal delivered to Recommendation. Recommendation persists it inside its owned immutable signal snapshot.

A changed locator under an existing evidence/message operation conflicts; duplicate delivery of identical bytes remains idempotent. The locator is provenance metadata, not authorization: every service must still apply its current scope and logical-reference checks.

## Evidence limits

Synthetic fixtures verify compatibility, masking, replay and changed-source rejection. They do not prove live GitHub acquisition. A genuine-source verification requires authorized retained GitHub bytes or an observed approved acquisition, plus the authenticated repository/workflow/run/attempt/job metadata needed to reproduce the locator. No current test result should be described as a live GitHub-to-dashboard execution.
