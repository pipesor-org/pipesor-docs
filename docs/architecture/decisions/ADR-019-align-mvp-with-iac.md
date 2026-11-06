Title: Align the controlled MVP with accepted IaC decisions
Status: Accepted
Date: 2026-11-06
Authority: explicit user confirmation in the local pipesor-docs reconciliation session

## Context

IaC records decisions that the previous canonical model had not incorporated.
The user instructed us to retain the Terraform direction and explicitly confirmed
alignment of ACA native ingress, exclusion of workload Blob, the Foundry foundation
and temporary dev-only preparation. This approval concerns architecture and local
preparation; it does not authorize Azure writes, deployment or contract approval.

Sources inspected at `pipesor-iac@4b42c0c8e66578dfb890ae1cca8c9c31c774026e`:

- [IaC ADR 003: native ingress](https://github.com/pipesor-org/pipesor-iac/blob/4b42c0c8e66578dfb890ae1cca8c9c31c774026e/docs/adr-003-mvp-native-ingress.md).
- [MVP baseline: workload Blob and Foundry](https://github.com/pipesor-org/pipesor-iac/blob/4b42c0c8e66578dfb890ae1cca8c9c31c774026e/docs/mvp-resource-baseline.md).
- [IaC ADR 004: preparation and deployment scope](https://github.com/pipesor-org/pipesor-iac/blob/4b42c0c8e66578dfb890ae1cca8c9c31c774026e/docs/adr-004-mvp-state-and-deployment.md).

## Decision

### API exposure

Use Azure Container Apps native ingress for the controlled MVP. Remove the active
APIM node and its routing hops. The dashboard queries Pipeline, Log/Event and
Diagnostic directly through their authorized ACA endpoints; GitHub Actions queries
Diagnostic and publishes the artifact in its own workflow. These are the previous
consumer/producer paths with the dedicated routing hop removed, not new services.
The component view projects dashboard/workflow calls onto Diagnostic API.

Keep Microsoft Entra ID for applicable authentication. Authorization, scopes,
resource checks and audit/trace propagation belong to the responsible services.
Only authorized external-consumer endpoints may be exposed; internal services are
not made public by this decision. Exact exposure, URIs, credentials, audiences and
caller contracts remain pending. No replacement gateway, proxy or WAF is selected.
Native ingress is not APIM/WAF-equivalent centralized governance; mandatory policy
conflicts require review. GitHub App remains read-only.

### Workload evidence

Exclude workload Azure Blob Storage and remove its active datastore/relationship.
GitHub Actions remains the original workflow-log source. PostgreSQL retains
sanitized operational evidence, metadata, excerpts and RAG knowledge. Do not store
raw sensitive payloads or duplicate complete workflow logs by inference.

Remove the Blob-specific optional `evidence_items.storage_container` and
`blob_object_key` columns and their paired-nullability CHECK from the generated
schema. Preserve generic evidence identity, provenance, size/hash, references and
ownership. This is a model/schema change, not a migration executed against a live
database. Any existing consumer/database requires an explicit migration assessment.
Do not infer a replacement locator format or evidence-retrieval mechanism.

The 365-day policy of ADR-013 remains. Independent original-log preservation,
GitHub deletion/access changes and retrieval/retention guarantees remain unresolved
under PD-017/030/031; GitHub retention is not proof of meeting that policy. Blob for
Terraform state remains in scope and is distinct from workload evidence.

### AI foundation

Use the accepted Microsoft Foundry AIServices account and project foundation,
public HTTPS with Entra-only authentication, instead of a standalone OpenAI account
candidate. It is managed infrastructure, not a new Pipesor microservice.
Preserve the logical external inference capability, its ID, sanitized contract,
ACA orchestration and PostgreSQL/pgvector ownership. The existing GPT-4 family/API
strategy is not expanded into a concrete model/deployment selection.

Account/project creation does not establish a compatible application endpoint/SDK,
model availability, processing geography, embeddings/dimension, grants or eligible
corpus. These remain explicit prerequisites; no Search, agents, model hosting on
ACA or credentials are introduced.

### Terraform and preparation scope

Terraform implements infrastructure. Preserve the four isolated environment roots
and states, but only dev is selected for the current academic MVP, temporarily in
Ramiro's Students subscription/UPC tenant. Keep account identifiers as explicit IaC
inputs; do not duplicate personal contact or account metadata in models.

IaC ADR 004 governs the accepted preparation, state custody and dev procedures
within its scope. No environment is provisioned by this decision. Services must be
implemented, integrated locally and validated, with complete cost/access/readiness
review and explicit target/action authorization before Azure writes, bootstrap or
state operations. Do not extend procedural dev exceptions to future environments
or copy state/identities into a future project-controlled target implicitly.

## Evolution and limits

- Partially supersedes ADR-003/006/008/016 only for APIM/perimeter routing.
  Identity selection, protected consumption, review, publication and ownership stay.
- Partially supersedes DD-006's workload Blob representation. ADR-018's instance,
  ownership, logical references and CQRS remain unchanged.
- Complements ADR-004/007/015 with infrastructure foundation information; it does
  not resolve concrete models, embeddings or application API compatibility.
- Supplements the deployment baseline for preparation; historical decisions and
  the two earlier reconciliations retain their original dates and evidence.

Update canonical/presentation models, guards, regression tests and generated
artifacts together. Consumers must consult this ADR and a reviewed docs revision;
their old APIM/Blob readiness records require their own authorized updates. This
repository does not modify neighboring repositories or prove deployed security.
