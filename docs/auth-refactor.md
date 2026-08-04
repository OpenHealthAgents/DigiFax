# Authentication & SSO Port Refactoring

This document defines the extensible authentication and Single Sign-On (SSO) architecture designed for the medingest multi-tenant SaaS platform.

---

## 1. Hexagonal Authentication Ports Architecture

To keep the application domain independent of concrete authentication packages (e.g. Better Auth, Auth0, Keycloak), all authentication workflows are isolated behind outbound port interfaces.

```
  ┌──────────────────┐
  │   User Interface  │ (FastAPI / Next.js)
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │    Use Cases     │ (Login, Refresh, Switch)
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │   Auth Ports     │ (IAuthenticationService, ISsoProvider, IUserProvisioningService)
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  Auth Adapters   │ (BetterAuthAdapter, SsoAdapter, ScimAdapter)
  └──────────────────┘
```

---

## 2. Core Authentication Sequences

### 2.1 Single Sign-On (SSO) Login Flow
The following sequence diagram details user authentication via OIDC or SAML federated links:

```mermaid
sequenceDiagram
    autonumber
    actor User as Clinical Practitioner
    participant Client as Next.js UI Portal
    participant API as FastAPI Ingestion Backend
    participant Adapter as BetterAuthAdapter
    participant IDP as Identity Provider (Okta/SAML)

    User->>Client: Click "Login with SSO" (Enter Email/Tenant)
    Client->>API: GET /api/auth/sso/redirect?tenant_id=...
    API->>Adapter: get_sso_redirect_url(tenant_id)
    Adapter->>IDP: Exchange SAML/OIDC metadata configurations
    IDP-->>Adapter: Redirection URL
    Adapter-->>API: Redirection URL
    API-->>Client: Redirect to IDP login screen
    Client->>IDP: Prompt user credentials
    User->>IDP: Authenticate credentials
    IDP-->>Client: Redirect to callback with code/assertion
    Client->>API: POST /api/auth/sso/callback
    API->>Adapter: authenticate_sso(code)
    Adapter->>IDP: Validate token assertion
    IDP-->>Adapter: IDP Claims (email, practitioner_npi)
    Adapter->>API: UserSession (JWT token + roles)
    API-->>Client: Cookie / Session Token (tenant-123)
```

### 2.2 Tenant/Organization Switch Flow
Users holding multiple memberships (e.g., a practitioner working across both *Main Campus* and *St. Jude Outpatient Clinic*) can switch their active context without re-authenticating:

```mermaid
sequenceDiagram
    autonumber
    actor User as Practitioner
    participant Client as Next.js UI Portal
    participant API as FastAPI Ingestion Backend
    participant Adapter as BetterAuthAdapter

    User->>Client: Select facility in Organization Switcher
    Client->>API: POST /api/auth/switch (target_org_id)
    API->>Adapter: switch_organization_context(token, target_org_id)
    Note over Adapter: Verify user holds a membership in target org
    Adapter-->>API: New AuthToken (claims scoped to target_org_id)
    API-->>Client: Update Client Cookies/Token
```

### 2.3 Invitation Acceptance Flow
New reviewers sign up through administrative invitation links:

```mermaid
sequenceDiagram
    autonumber
    actor User as New Reviewer
    participant Client as Next.js UI Portal
    participant API as FastAPI Ingestion Backend
    participant Adapter as BetterAuthAdapter

    User->>Client: Click Invitation Link (email, token)
    Client->>API: POST /api/auth/invitation/accept (token)
    API->>Adapter: verify_invitation_token(token)
    Adapter-->>API: Registration Details (email, target_org_id, target_role)
    API->>API: Provision user membership record
    API-->>Client: Onboarding success redirect to dashboard
```
