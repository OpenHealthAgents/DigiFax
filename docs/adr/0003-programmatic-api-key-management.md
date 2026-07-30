# ADR 0003: Programmatic API Key Management & Obfuscation

## Status
Approved

## Context
Third-party ingestion gateways (e.g. Medplum EHR, physical fax providers) require machine-to-machine integration keys to upload records. These keys must be validated securely without exposing raw secrets.

## Decision
We implement a key management scheme:
1. **API Key Generation**: Generate a cryptographically secure random string token at the tenant administration dashboard.
2. **Obfuscated Prefixes**: Console dashboards return prefix-obfuscated keys (`df_live_8a92...`) for auditing purposes.
3. **API Key Expirations**: Keys support optional expiration timestamps and immediate revocation markers to enforce rotated security lifecycles.

## Consequences
* **Pros**: Secure integration endpoints that bypass interactive user login workflows.
* **Cons**: Key validation checks require database calls, which can be optimized with Redis caching.
