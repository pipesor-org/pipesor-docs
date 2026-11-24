# Protected workflow evidence 2.2

Status: approved MVP contract. It extends [2.1](protected-evidence-v2.1.md) without
reinterpreting 2.0 or 2.1. Broker property `schemaMajor` remains `2`.

## Motivation

The 2.1 locator restricts the archive member to `[0-9]{1,9}_verify.txt`, the file of a
single pilot workflow, and to a single line. Real failures (Maven, npm, Docker, test
reports, set-up steps) live in other members and often span several lines. The
Charter requires at least ten failure scenarios, which 2.1 cannot represent.

## Compatibility

- Consumers accept `schema_version` `2.0`, `2.1` and `2.2`.
- A 2.1 message keeps its exact 2.1 rules. Every valid 2.1 locator is also a valid
  2.2 locator; producers emit `2.2` from this version on.
- 2.0 messages must not contain `evidence.source_locator`; 2.1 and 2.2 messages must.
- Persisted 2.1 locators are not rewritten.

## Aggregate source locator

```text
v2:job:<job-id>:member:<member>:lines:<first>-<last>:sha256:<digest>
```

| Part | Rule |
|---|---|
| `job-id` | canonical positive decimal, ≤ 20 digits, equal to the authenticated GitHub job id |
| `member` | the exact ZIP member name of the attempt log archive, percent-encoded (RFC 3986): bytes outside `A-Z a-z 0-9 - . _ ~` are encoded as `%XX` with uppercase hex. Encoded length 1–765. Decoded value: valid UTF-8, 1–255 bytes, no leading `/`, no `\`, no `..` segment, no control characters, at most one `/` (root member or one directory level) |
| `first`, `last` | positive decimal line numbers (1-based) within the member, `first ≤ last`, `last - first ≤ 199` |
| `digest` | lowercase SHA-256 over the exact original UTF-8 bytes of lines `first..last`, including their terminators and an initial BOM if present, before masking |

Validation regular expression for the encoded form (the decoded rules above still apply):

```text
^v2:job:[1-9][0-9]{0,19}:member:(?:[A-Za-z0-9._~-]|%[0-9A-F]{2}){1,765}:lines:[1-9][0-9]{0,8}-[1-9][0-9]{0,8}:sha256:[0-9a-f]{64}$
```

Implementations must decode the member to apply the decoded rules, and must compare
locators byte-for-byte in encoded form for replay and conflict detection.

Known divergence (audit 2026-11-24): the services' member validators disagree on cases
this grammar leaves open. A `.` segment is rejected by Ingestion and Correlation but
accepted by Log/Event, NLP and Recommendation. An empty segment (`dir/`) is rejected by
the Java services but accepted by NLP. C1 controls (U+0080–U+009F) are rejected only by
Log/Event and Recommendation. A non-canonical `%XX` for an unreserved byte (e.g. `%41`)
is rejected only by Log/Event. Pending owner decision: this document should fix the
canonical `%XX` form, empty and `.` segments, and what counts as a control character.

## Ownership of the grammar

This document is the single source of the locator grammar. Services must not
encode a workflow-specific file name in validators, database CHECK constraints or UI
schemas. Database constraints may check shape (prefix, length, digest format) but
not member names.

## Unchanged

Masking, minimization of `evidence.excerpt`, preservation and replay rules, conflict
on changed locator, and the statement that the locator is provenance and not
authorization remain exactly as in 2.1.
