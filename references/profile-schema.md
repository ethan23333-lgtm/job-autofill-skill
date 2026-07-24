# Candidate Profile Schema

`candidate-profile.yml` contains reusable, verified application facts. Keep a real profile outside this distributable skill package. Unknown facts remain `null`; do not add passwords, SSNs, dates of birth, medical information, EEO data, criminal history, drug-use answers, or other `prohibited_store` values.

## Root shape

```yaml
schema_version: 1
profile:
  identity: {}
  contact: {}
  eligibility: {}
  preferences: {}
  education: []
  employment: []
  skills: []
  certifications: []
```

## Fact wrapper

Every reusable scalar fact uses this wrapper. `value` may be a scalar, list, or `null`.

```yaml
value: null
verified: false
source: null
last_updated: null
sensitivity: standard
```

| Field | Requirement |
|---|---|
| `value` | The fact to map to a visible form field; use `null` when unknown. |
| `verified` | `true` only after the applicant confirms the value is current and accurate. |
| `source` | Origin such as `applicant-confirmed`, `resume-2026-07`, or `transcript`; never store a secret. |
| `last_updated` | ISO date (`YYYY-MM-DD`) of the last confirmation, or `null`. |
| `sensitivity` | One of the allowed levels below. |

Allowed sensitivity levels:

| Level | Use |
|---|---|
| `standard` | Ordinary facts such as skills, job titles, and locations. |
| `personal` | Contact or ordinary identity information. |
| `sensitive` | A fact that requires current, task-specific user authorization before entry. |
| `prohibited_store` | Never store the value in this profile; its `value` must be `null`. |

## Section conventions

Use stable, human-readable keys. The profile is a source of facts, not a complete record of every ATS-specific question.

- `identity`: name components and other ordinary identity values.
- `contact`: email, phone, address, and professional links.
- `eligibility`: verified reusable values such as citizenship and work authorization. Treat attestations, clearance, legal, and sensitive disclosures according to `safety-and-confirmations.md`; an attestation remains manual even when its underlying fact is verified.
- `preferences`: verified relocation, salary, availability, travel, work arrangement, and location preferences.
- `education`: a list of records. Each record has `institution`, `degree`, `field_of_study`, `graduation_date`, and other facts using the wrapper.
- `employment`: a list of records. Each record has `employer`, `job_title`, `location`, `start_date`, `end_date`, `source_period`, `hours_per_week`, `description`, and similar facts using the wrapper.
- `skills`: a list of fact wrappers, one verified skill per entry.
- `certifications`: a list of fact wrappers, one verified certification per entry. Never use raw strings or unwrapped certification records.

## Dates and incomplete sources

Exact form dates must be verified `YYYY-MM-DD` values. A resume that says `2023-07 to 2023-10` does **not** establish days. Preserve that evidence separately:

```yaml
source_period:
  value: "2023-07 to 2023-10"
  verified: true
  source: resume
  last_updated: "2026-07-23"
  sensitivity: standard
start_date:
  value: null
  verified: false
  source: null
  last_updated: null
  sensitivity: standard
end_date:
  value: null
  verified: false
  source: null
  last_updated: null
  sensitivity: standard
```

Never infer the first or last day of a month. Leave exact date fields untouched and classify them as `UNKNOWN` until the applicant supplies and verifies them.
