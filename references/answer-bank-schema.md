# Applicant Answer Bank Schema

An optional answer bank contains only reusable text written and verified by the applicant. Keep the real file outside the distributable skill. Never place credentials, sensitive suitability answers, or AI-assisted text for a no-AI prompt in it.

## Root shape

```yaml
schema_version: 1
answers: []
```

Each answer has exactly these reusable fields:

```yaml
- id: relocation
  prompt_pattern: "willing to relocate"
  text: "Open to relocation on a case-by-case basis."
  applicant_authored: true
  ai_prohibited: false
  verified: true
```

| Field | Requirement |
|---|---|
| `id` | Unique, non-empty identifier. |
| `prompt_pattern` | Non-empty regular expression matched case-insensitively against the visible prompt. |
| `text` | Applicant-authored string or `null`. |
| `applicant_authored` | Boolean; must be `true` before non-null text can be reused. |
| `ai_prohibited` | Boolean; when `true`, `text` must remain `null`. |
| `verified` | Boolean; `true` only when the applicant confirms the text is current. |

Reuse an entry only when `text` is non-null, `applicant_authored`, and `verified`, and `ai_prohibited` is false. A visible no-AI/no-consultant instruction always overrides the answer bank: classify the prompt and associated prose as `NO_AI` and leave both untouched.
