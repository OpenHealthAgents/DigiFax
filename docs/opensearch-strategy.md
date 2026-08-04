# OpenSearch Indexing & Multi-Tenant Filtering Strategy

This document details the multi-tenant indexing architecture, search configurations, k-NN vector filters, and security parameters implemented for the medingest platform.

---

## 1. Multi-Tenant Index Architecture

OpenSearch supports multi-tenancy through two main patterns. We evaluated both for medingest:

| Strategy | Description | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Shared Index with Term Filters** | A single unified index (`medingest-documents`) where every document carries a `tenant_id` field. Queries strictly enforce matching filters. | Cost-effective, easy alias management, fast mapping changes. | Logical isolation requires diligent queries implementation. |
| **Index per Tenant** | Separate indexes dynamically named (e.g., `medingest-documents-{tenant_id}`). | Hard physical isolation at the index layer. | High resource overhead (shard limits), complex mappings management. |

### 1.1 Recommendation & Implementation
We implemented **Shared Index with Term Filters**. To prevent cross-tenant queries, the search port interface mandates `tenant_id` scopes. This is supplemented at the API layer where search controllers derive `tenant_id` directly from authenticated requests.

---

## 2. OpenSearch Schema Mapping

Every indexed document specifies a `tenant_id` mapping of type `keyword` to allow direct filtering:

```json
{
  "mappings": {
    "properties": {
      "tenant_id": { "type": "keyword" },
      "ocr_text": { "type": "text" },
      "entities": { "type": "object" },
      "fhir_resources": { "type": "object" },
      "audit_logs": { "type": "text" },
      "embedding": {
        "type": "knn_vector",
        "dimension": 1536,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib"
        }
      }
    }
  }
}
```

---

## 3. Prevent Cross-Tenant Leakage

### 3.1 Keyword Search query filter:
All keyword searches utilize OpenSearch boolean (`bool`) queries containing a term filter to restrict matches:
```json
{
  "query": {
    "bool": {
      "must": {
        "multi_match": {
          "query": "Glucose",
          "fields": ["ocr_text", "audit_logs"]
        }
      },
      "filter": {
        "term": { "tenant_id": "tenant-abc" }
      }
    }
  }
}
```

### 3.2 Vector Search query filter:
All vector/k-NN searches apply the same filter restriction to prevent cross-tenant scans:
```json
{
  "query": {
    "bool": {
      "must": {
        "knn": {
          "embedding": {
            "vector": [0.1, -0.2, ...],
            "k": 10
          }
        }
      },
      "filter": {
        "term": { "tenant_id": "tenant-abc" }
      }
    }
  }
}
```
