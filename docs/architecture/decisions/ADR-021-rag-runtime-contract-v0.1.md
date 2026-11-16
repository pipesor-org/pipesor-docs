Title: Approve the RAG–Recommendation–IaC runtime contract v0.1
Status: Accepted
Date: 2026-11-16

## Context

RAG already owned authorized knowledge retrieval and PostgreSQL/pgvector, but its
embedding model/dimension, direct provider access, service authentication and
runtime permission split were unresolved. The project owners approved the concrete
v0.1 proposal on 2026-11-16 so implementation and IaC preparation can share one
contract without inventing live Azure values.

## Decision

- RAG uses `text-embedding-3-small` with 1536 dimensions for both documents and
  queries, records model/version compatibility and rejects incompatible vectors.
- RAG calls Azure OpenAI API v1 using its Container App system-assigned identity.
  That identity requires `Cognitive Services OpenAI User` on the applicable account.
- The deployment name is configurable; `pipesor-dev-embeddings` is the proposed dev
  name. Endpoint, concrete deployment identifier, region, deployment type and quota
  remain mandatory environment values validated before activation.
- Recommendation calls RAG with a single-tenant Entra app-only token for an exclusive
  RAG audience and the `Rag.Query` app role. RAG validates signature, issuer,
  audience, lifetime, tenant, role, token type and authorized Recommendation actor,
  then applies its existing scope defense.
- Embedding calls have a total 15-second budget and at most two transient retries in
  one retry layer, respecting `Retry-After`. Dependency or quota failure is a
  recoverable `503`; a successful search without evidence is `no_match`.
- PostgreSQL access separates runtime read, administrative import write and migration
  DDL principals. RAG owns migrations only for its `knowledge` schema.
- Only synthetic corpus is enabled for integration. Every real source requires an
  inventory, provenance, version, sanitization, authorized scope and an accountable
  approver; evaluation material remains separate.

## Consequences

RAG has a dimensioned vector schema and may use a compatible cosine index. Existing
vectors from another dimension/model must be re-embedded through an explicit
migration. IaC may prepare required parameters and grants but this ADR does not
authorize Terraform apply, role assignment, resource creation, production corpus or
claim that region/quota availability has been validated.

