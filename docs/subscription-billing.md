# Subscription Tiers & Billing Abstractions

This document details the multi-tenant SaaS subscription tiers, operational quota allocations, usage tracking, and outbound payment abstractions.

---

## 1. Subscription Tiers & Quota Matrix

The medingest platform partitions services into three standard licensing tiers:

| Tier | Monthly Price | Storage Quota | OCR Quota | API Quota | Document Quota |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Free** | $0.00 | 500 MB | 100 pages | 1,000 requests | 50 documents |
| **Professional** | $149.00 | 10,000 MB | 2,000 pages | 50,000 requests | 1,000 documents |
| **Enterprise** | Custom | 1,000,000 MB | 50,000 pages | 1,000,000 requests | 20,000 documents |

---

## 2. Usage Tracking Model

Consumption parameters are mapped to a `SubscriptionUsage` value object, exposing comparisons against the tenant's `SubscriptionQuotas`:

```
  [Ingest Inbound Document]
              │
              ▼
  ┌───────────────────────┐
  │ Check Storage Quota   │ (storage_used_mb + file_size_mb <= max_storage_mb)
  └───────────┬───────────┘
              │
              ▼
  ┌───────────────────────┐
  │  Check Document Limit │ (documents_used + 1 <= max_documents_monthly)
  └───────────┬───────────┘
              │
              ▼
       [Save Document]
```

---

## 3. Billing Service Port (Payment Abstraction)

To prevent coupling with specific payment vendors (e.g. Stripe, Recurly), billing integrations are decoupled behind the outbound port `IBillingService`:

```
  ┌───────────────┐
  │  Domain Layer │
  └───────┬───────┘
          │ (calls port)
          ▼
  ┌───────────────┐
  │IBillingService│ (Outbound Port)
  └───────┬───────┘
          │
    ┌─────┴─────────────────────┐
    ▼                           ▼
  ┌───────────────────┐       ┌───────────────────┐
  │   StripeAdapter   │       │   MockBilling     │ (Adapters)
  └───────────────────┘       └───────────────────┘
```
