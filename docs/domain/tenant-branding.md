# Domain Design: Tenant Branding Bounded Context

This document defines the Tenant Branding bounded context, enabling multi-tenant visual customizability and routing.

---

## 1. Context & Business Logic

Clinical enterprise subscribers require personalized branding to ensure that practitioner operations align with local network guidelines. The Tenant Branding context decouples branding styles and subdomain routing parameters from core system logic.

```mermaid
classDiagram
    class TenantBranding {
        +String tenant_id
        +BrandingTheme theme
        +LogoSettings logo_settings
        +CustomDomain custom_domain
        +Integer version
        +configure_branding(theme, logo_settings)
        +configure_custom_domain(hostname)
        +verify_custom_domain()
    }
    class BrandingTheme {
        +ColorPalette palette
        +String font_family
        +Boolean dark_mode_preferred
    }
    class ColorPalette {
        +String primary
        +String secondary
        +String accent
        +String background
    }
    class LogoSettings {
        +String light_logo_url
        +String dark_logo_url
        +String fav_icon_url
    }
    class CustomDomain {
        +String hostname
        +String status
        +Boolean ssl_configured
    }

    TenantBranding --> BrandingTheme
    TenantBranding --> LogoSettings
    TenantBranding --> CustomDomain
    BrandingTheme --> ColorPalette
```

---

## 2. Tactical DDD Components

### Aggregate Roots & Entities
* **`TenantBranding` [Aggregate Root]**: Isolates branding styles, custom domains, and styling version controls at the tenant level.

### Value Objects (Immutable)
* **`ColorPalette`**: Primary, secondary, accent, and background colors validated as hexadecimal codes.
* **`BrandingTheme`**: Groups the ColorPalette, custom font family, and dark mode configuration properties.
* **`LogoSettings`**: Image asset URLs for light/dark headers and browser favicons.
* **`CustomDomain`**: Handles vanity DNS domain mappings (`fax.hospital.org`) and TLS certificate states (`PENDING`, `ACTIVE`, `FAILED`).

### Domain Events
* **`BrandingUpdatedEvent`**: Dispatched when theme colors or logos are modified.
* **`CustomDomainConfiguredEvent`**: Triggered when a new domain routing key is registered.
* **`CustomDomainVerifiedEvent`**: Triggered when custom domain DNS validation checks pass.

---

## 3. Operations & Sequence Flow

### Custom Domain Registration & Verification

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Tenant Administrator
    participant UC as ManageCustomDomainUseCase
    participant Repo as ITenantBrandingRepository
    participant Bus as IEventBus

    Admin->>UC: register_domain("tenant-1", "fax.hospital.org")
    UC->>Repo: get_by_tenant_id("tenant-1")
    Repo-->>UC: TenantBranding
    UC->>UC: branding.configure_custom_domain("fax.hospital.org")
    UC->>Repo: save(branding)
    UC->>Bus: publish(CustomDomainConfiguredEvent)
    Bus-->>Admin: PENDING Verification Status
    
    Admin->>UC: verify_domain("tenant-1")
    UC->>Repo: get_by_tenant_id("tenant-1")
    Repo-->>UC: TenantBranding
    UC->>UC: branding.verify_custom_domain()
    UC->>Repo: save(branding)
    UC->>Bus: publish(CustomDomainVerifiedEvent)
    Bus-->>Admin: ACTIVE Routing Status
```

---

## 4. Key Design Decisions

1. **Validation Boundaries**: Hexadecimal codes are asserted upon value object creation inside `ColorPalette` to prevent front-end styling injection risks.
2. **Sequential Registration**: Subdomains are locked in `PENDING` states upon registration, preventing live routing bindings until DNS ownership verification events complete.
3. **Optimistic Concurrency**: Any modifications to the `TenantBranding` aggregate check the `version` field in the database (`BaseInMemoryRepository`) to prevent concurrent overwrite conflicts.
