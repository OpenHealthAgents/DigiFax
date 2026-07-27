# Tenant Feature Flags & Usage Evaluation Strategy

This document specifies the feature toggling models, beta access rules, license constraints, and usage limits enforced in the DigiFax platform.

---

## 1. Feature Flag Evaluation Strategy

To support tiered capabilities and dynamic product toggles, feature access is resolved sequentially through a multi-stage evaluation pipeline:

```
  [Evaluate Feature Request]
              │
              ▼
  ┌───────────────────────┐
  │ Explicit Toggle Gate  │ (Check if feature_flags[name] is True/False)
  └───────────┬───────────┘
              │
              ▼
  ┌───────────────────────┐
  │    Beta Opt-In Gate   │ (Confirm tenant has opted-in to beta tags)
  └───────────┬───────────┘
              │
              ▼
  ┌───────────────────────┐
  │    License Tier Gate  │ (Assert Enterprise or Pro tier limits)
  └───────────┬───────────┘
              │
              ▼
  ┌───────────────────────┐
  │    Usage Limits Gate  │ (Verify usage count is below daily caps)
  └───────────┬───────────┘
              │
              ▼
    [Feature Available]
```

---

## 2. Evaluation Gates Detail

### 2.1 Standard Enable/Disable Toggles
* Directly mapped as booleans in `TenantConfiguration.feature_flags` (e.g. `"auto_ocr": True` or `"auto_ocr": False`).

### 2.2 Beta Opt-In
* Beta-level features (e.g., `ai_summarization`, `clinical_insights`) require the tenant to carry a beta opt-in tag (e.g. adding the feature key to `"beta_opt_in": ["ai_summarization"]`). If the tag is missing, the feature is disabled.

### 2.3 License Restrictions
* Standard tiers might lock out administrative or high-compute actions (e.g., `billing_write` or `advanced_analytics` is restricted to `Enterprise` or `Pro` plans).

### 2.4 Usage Limits
* Ensures faxes do not exceed subscription caps. If a tenant's transaction count exceeds `max_daily_uploads`, the evaluation pipeline flags a limit breach, rejecting the upload.
