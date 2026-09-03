---
name: api-contracts
description: >-
  Use this skill when designing, reviewing, or modifying APIs to enforce contract governance, strict backward compatibility, schema validation, and standardized RFC 7807 error responses.
---

# API Contract Governance Protocol

<CRITICAL_DIRECTIVE>
APIs are permanent public contracts. Never break downstream mobile apps, web clients, or microservices with unexpected field deletions, type mutations, or ad-hoc error formats.
</CRITICAL_DIRECTIVE>

<CORE_STANDARDS>
1. **Strict Backward Compatibility (Non-Breaking Invariants)**:
   - Field Deletion / Renaming: BANNED without a version bump (`/v1` -> `/v2`).
   - Fields can only be deprecated, never removed prematurely.
   - Enums: Append-only. Clients MUST handle unknown enum values gracefully via fallback defaults.
   - Adding required fields to request payloads is considered a breaking change. New request fields MUST be optional with sensible defaults.

2. **Schema-First Runtime Validation**:
   - Every input payload, query parameter, and route parameter MUST be parsed and validated through a schema engine (Zod, Pydantic, Joi, or Protocol Buffers).
   - Strip unknown fields or reject unexpected inputs explicitly to prevent parameter tampering.

3. **Standardized RFC 7807 Problem Details**:
   - ALL HTTP error responses MUST conform to RFC 7807 JSON structure:
     ```json
     {
       "type": "https://api.example.com/errors/invalid-payment",
       "title": "Invalid Payment Details",
       "status": 422,
       "detail": "The card expiration month must be between 1 and 12.",
       "instance": "/orders/ord_123/checkout",
       "code": "CARD_EXPIRY_INVALID"
     }
     ```
   - Never return raw database stack traces or generic strings (`{"error": "something went wrong"}`).

4. **Idempotent Pagination & Filtering**:
   - Use cursor-based pagination (`cursor`, `limit`) for high-volume datasets over offset-based (`page`, `offset`) to prevent skipped/duplicate items on fast-mutating tables.

5. **Versioning & Deprecation Lifecycle**:
   - Emit `Deprecation` and `Sunset` HTTP headers (RFC 8594) when client requests deprecated endpoints or fields.
</CORE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Review Diff Against Contract**: Check if any response field was mutated, removed, or made required.
2. **Enforce Schema Guard**: Validate inputs with strict DTOs.
3. **Format Error Responses**: Standardize all failures under RFC 7807.
</PROCEDURAL_WORKFLOW>
