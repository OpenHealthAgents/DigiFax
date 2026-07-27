# API Specifications & Multi-Tenant Endpoint Guards

This document specifies the validation requirements, error responses, and OpenAPI contracts enforced across all FastAPI routes in the DigiFax platform.

---

## 1. Unified Validation Guard Pipeline

Every HTTP request entering our controllers passes through the following validation sequence before dispatching to application use cases:

```
  [Inbound Request]
          │
          ▼
  ┌──────────────┐
  │ Tenant & Org │ (Mandate X-Tenant-ID header presence)
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  RBAC Check  │ (Evaluate role-permissions with inheritance)
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Subscription │ (Assert tenant subscription tier bounds)
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Feature Flag │ (Confirm optional target flags are active)
  └──────┬───────┘
         │
         ▼
  [Execute Use Case]
```

---

## 2. API Endpoint Schemas

### 2.1 Ingest Document Upload (`POST /api/intake/upload`)
* **Purpose**: Manually ingest faxes or PDFs.
* **Headers**:
  * `X-Tenant-ID`: `tenant-123` (Required)
  * `X-Organization-ID`: `org-main` (Optional)
* **Body (Multipart Form)**:
  * `file`: Binary payload (Required)
  * `source`: `API_UPLOAD` (Optional)
* **Required Permission**: `document:write`
* **Optional Feature Flag**: `auto_ocr`

#### Success Response (`200 OK`)
```json
{
  "status": "success",
  "document_id": "doc-uuid-12345"
}
```

#### Error Responses
* **`400 Bad Request`**: Missing headers or invalid upload format.
  ```json
  {
    "detail": {
      "message": "X-Tenant-ID header is required",
      "code": "MISSING_TENANT"
    }
  }
  ```
* **`403 Forbidden`**: Insufficient permissions.
  ```json
  {
    "detail": {
      "message": "Forbidden: Insufficient permissions",
      "code": "FORBIDDEN_PERMISSIONS"
    }
  }
  ```
* **`403 Forbidden`**: Feature flag not enabled.
  ```json
  {
    "detail": {
      "message": "Forbidden: Feature auto_ocr is not enabled for this tenant",
      "code": "FEATURE_DISABLED"
    }
  }
  ```

---

### 2.2 Telephony Fax Webhook (`POST /api/intake/fax`)
* **Purpose**: Telephony FoIP ingestion mapping source to `FAX_UPLOAD`.
* **Headers**:
  * `X-Tenant-ID`: `tenant-123` (Required)
* **Body (Multipart Form)**:
  * `file`: TIFF / PDF binary payload (Required)
* **Required Permission**: `document:write`

---

### 2.3 Email Parser Webhook (`POST /api/intake/email`)
* **Purpose**: Ingest email attachments mapping source to `EMAIL_ATTACHMENT`.
* **Headers**:
  * `X-Tenant-ID`: `tenant-123` (Required)
* **Body (Multipart Form)**:
  * `file`: PDF attachment binary payload (Required)
* **Required Permission**: `document:write`
