# AGENTS.md

## Role

Codex maintains documentation and acts as a deterministic compiler/renderer of the models within the authorized task scope.
Codex is NOT the architecture decision authority.

## Source of Truth

- Architecture SSOT: `model/architecture.yml`, its invariants and applicable Accepted ADRs in `docs/architecture/decisions/`, accounting for subsequent supersession.
- Persistent domain SSOT: `model/domain.yml`, explained by `model/domain_decisions.md`, within ADR-018 boundaries.
- Proposed class-design SSOT: `model/design.yml`, explained by `model/design_decisions.md`. It describes proposed classes, not approved or implemented application code.
- Presentation models: `model/logical_presentation.yml`, `model/physical_presentation.yml` and `model/c4_container_presentation.yml`. They define visual composition and projections of existing architecture facts; they cannot create architectural decisions.
- Generated artifacts: `model/db.dbml`, `build/` and `out/`. DBML, SQL, ER and the data dictionary derive from `model/domain.yml`; DBML is not an independent database SSOT.

Authority is by subject, as recorded in ADR-018 and model governance: Project Charter for scope; architecture/invariants and applicable Accepted ADRs for architecture; tech drift resolutions and applicable technology ADRs for technology. `docs/research/arquitectura-informacion.md` derives functional needs within those limits and must be read against subsequent decisions. Do not impose a new linear precedence.

The Charter v1.3 and tech drift register are available at the repository root and as byte-identical archival copies documented in [docs/sources/README.md](docs/sources/README.md). Root originals preserve existing references. TI and referenced spreadsheets remain absent; domain assumption A-011 is partially outdated, as recorded externally in [the reconciliation](docs/architecture/reconciliation.md). Do not infer additional requirements from absent sources. Consult the [decision index](docs/architecture/decisions/index.md) for documented evolution and approval evidence limits; these descriptive records do not resolve TMD or CF-001. Report conflicts that cannot be resolved from available evidence.

README.md is an entry point; Overview.md is a dated inspection. Neither is an independent architecture authority.

Never edit generated files manually.

## Decision States

- Accepted ADRs record approved decisions within their stated scope. Read historical ADRs together with later decisions that supersede parts of them; Accepted does not make every historical statement current.
- `confirmed` means confirmed in the model, not implemented or deployed. The architecture model's overall `draft` status remains unchanged.
- `proposed` class designs remain proposals even when their diagrams are generated.
- Preserve `assumption`, `inferred` and `ia_only` qualifications; they do not authorize promotion to approved requirements.
- Check `open_questions` in architecture, domain and design. An empty architecture list does not close domain/design questions or unspecified details.
- Generated output preserves the source's status and cannot approve decisions or prove runtime behavior.

## Architecture Rules

- Never invent architecture.
- Never add, remove, rename or reinterpret architectural elements unless explicitly requested.
- Never resolve `open_questions`.
- Never convert candidates or implementation options into confirmed technologies.
- Never change `status`, `source`, `conflicts`, architectural invariants or governance rules unless explicitly requested.
- If required information is absent or ambiguous, fail clearly and report it.
- Architecture changes are model-first and require explicit instruction.
- Never modify the architecture model merely to make a validator or renderer succeed.

## Backend development conventions

For backend development documentation and implementation guidance, consult [common conventions](docs/development/backend-conventions.md) and, for Java services, [Java/Spring conventions](docs/development/java-spring-conventions.md). These session-authorized conventions do not change model ownership, approve integration contracts or add columns implicitly.

## Validation

Use the repository Makefile as the canonical execution interface when execution is relevant to the task.

Before generation run:

`make validate`

If validation fails, fix only files that are explicitly within the scope of the current task, or report the failure.

Do not change architectural facts to satisfy validation.

Documentation-only changes require a coherence, link and diff review, not generation. Audits and read-only tasks require neither generators nor file modifications; run only checks compatible with their restrictions.

If Make or required dependencies are unavailable, report the limitation without installing tools unless authorized. Equivalent direct validator invocations with available dependencies may be used and must be reported; see README.md. Passing validation is not proof of complete architectural compliance or runtime security.

## Views

- Render architecture views declared in `model/architecture.yml`, presentation views declared in the presentation models, and proposed class diagrams declared in `model/design.yml`.
- Each view's declared membership (`views[].elements`, or `class_diagrams[].elements` for classes) is authoritative within its model, subject to that model's existing projection rules. Presentation models do not replace canonical architecture views.
- Maximum architectural nodes per view is defined by `architecture.view_constraints.max_nodes_per_view`.
- Never insert undeclared architectural nodes into a view.
- Graphical stubs and legends are presentation artifacts, not architecture.
- Final views must not contain elements with `status: open_question`.
- Do not introduce implicit collapse. Preserve explicit presentation `collapse` mappings and the existing C4 projections: context aggregation, component-to-parent lifting and PostgreSQL/pgvector grouping representing the single physical instance in ADR-018. The C4 generator currently performs these projections without a per-view `collapse` field; this records existing presentation behavior and authorizes no new grouping or architecture change.
- Respect `include_external` exactly as declared by the view.

## Generated Artifacts

- Never hand-edit `model/db.dbml`, `build/` or `out/`.
- Fix generators, not generated SVG/PDF files.
- Output must be reproducible from the same model and dependency versions.
- Do not treat generated artifacts as architecture source files.

## Icons

- Prefer classes available in the installed `diagrams` package.
- Verify classes programmatically before referencing them.
- Never invent icon class names.
- Never download third-party icons without explicit approval.
- `assets/icons/` is reserved for explicitly approved local icons.
- Use a generic fallback when no approved icon exists and report the fallback.

## Technology Decisions

Do not infer concrete technologies from generic capabilities.

Use the current model and applicable ADRs for the documented technology choices. Historical options are not current alternatives: LogBERT and the standalone anomaly detector are outside the MVP under ADR-010. Keep unspecified models, versions and implementation details unspecified; an approved provider does not authorize selecting them.

## Workflow

Keep changes small and scoped to the requested task.

Before completion, apply the checks appropriate to the authorized scope:

1. For documentation-only work, review coherence with the existing sources, links and the diff. For audits/read-only work, preserve the task's no-write restrictions. Neither requires generation or `make all`.
2. For model or generator changes, run `make validate` and the relevant validation targets (including `make validate_design` for class design), then the affected generator/build target and `make all` when generation is in scope.
3. Run relevant tests for changed executable behavior; `make all` does not run unittest.
4. Report checks actually run, environment limitations, unresolved questions and, when rendering, warnings, fallback icons and visual issues. Do not report historical checks as current results.

When consuming this repository from backend or IaC repositories, identify the consulted revision and relevant model IDs, invariants and ADRs. Preserve proposed/open states and ownership boundaries. Report missing contracts or contradictions instead of inventing architecture to complete implementation.

If `make all` fails, correct only files authorized by the task.

Never modify `model/architecture.yml` merely to make generated output succeed.
