Title: Dashboard served from Azure Container Apps
Status: Accepted
Date: 2026-11-24
Amends: ADR-008 (hosting only; React SPA and TypeScript are kept)

## Context

[ADR-008](ADR-008-react-azure-static-web-apps.md) hosts the React SPA on Azure Static Web Apps.
[ADR-019](ADR-019-align-mvp-with-iac.md) already removed its API Management hop and
[ADR-022](ADR-022-platform-identity-without-entra-app-registrations.md) removed its Entra sign-in,
so the dashboard needs only static hosting plus a public HTTPS origin.

The academic MVP runs on an Azure for Students subscription whose policy allows five regions:
`brazilsouth`, `northcentralus`, `westus3`, `southcentralus` and `mexicocentral`. Azure Static Web
Apps is not offered in any of them. The first dev rollout on 22/11/2026 found this and moved the
dashboard to a Container App:

- [pipesor-iac#29](https://github.com/pipesor-org/pipesor-iac/commit/8e5c39baf17fba7acf6dc78d737334892811836c) (`8e5c39b`, "fix(dev):
  apply findings from the first dev rollout");
- [pipesor-frontend#38](https://github.com/pipesor-org/pipesor-frontend/commit/0c25791aaf0962c3d6e6fd57171e63ed2967cb09) (`0c25791`),
  which publishes the dashboard image.

The [decision index](index.md) and the [runtime manifest](../../development/runtime-manifest.md)
recorded the change as a divergence with no ADR. On 24/11/2026 the project owner confirmed it:
Static Web Apps was dropped because of that subscription limitation.

## Decision

- **The dashboard runs as an external Azure Container App**, `dashboard`, in the same Container
  Apps environment as the services. Its public origin is `https://dashboard.<env-domain>`, which is
  also the CORS origin the services accept.
- **The image** is built from pipesor-frontend. It holds the static build served by unprivileged
  nginx on port 8080. At start-up the container writes `/config.js` and the Content Security Policy
  from its environment (Ingestion, Pipeline and Recommendation URLs, optional GitHub App install
  URL). No runtime secret reaches the browser.
- **Identity:** the app has its own user-assigned managed identity. Its only role is to read the
  registry pull secret through a Key Vault reference. It calls no Azure resource and no Pipesor API
  on its own behalf; the browser calls the services with the user's session token (ADR-022).
- ADR-008's other decisions are kept: React SPA, TypeScript (ADR-018) and access to the services
  through Container Apps native ingress (ADR-019).

## Consequences

- `web_dashboard` in [the architecture model](../../../model/architecture.yml) is hosted on Azure
  Container Apps; the physical and C4 views show it that way.
- **What is lost:** Static Web Apps' global edge distribution and preview environments.
  The app runs one replica in the environment's region. A dashboard outage no longer depends on
  another Azure product, but it does share the environment with the services.
- **Cost:** the Container App is billed like the other workloads, instead of the free Static Web
  Apps tier.
- **Reversibility:** the pipesor-iac Static Web Apps module is still in the environment roots and is
  off in dev. Moving back is possible in a subscription or region that offers the service, and it
  would need a new ADR. Without one, Container Apps remains the decision.
- **Limits:** this ADR records an implemented, confirmed change. It does not prove that any
  environment is currently deployed. qa, preprod and prod are not deployed.
