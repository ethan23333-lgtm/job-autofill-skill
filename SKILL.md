---
name: job-autofill
description: Use when Codex needs to quickly fill a job application from a verified candidate profile, continue an existing Workday, Greenhouse, Lever, USAJOBS, or PeopleSoft application, reduce repetitive browser form entry, or stop an application at review before final Submit. Coordinates with career-ops for job search, tailoring, and tracking; handles only application-field planning and safe autofill.
---

# Job Autofill

## Scope

Use this skill for application-field planning and safe autofill only. Keep job discovery, ranking, JD analysis, resume tailoring, cover-letter generation, and application tracking in career-ops. Consume a user request, a job URL or current browser tab, an optional career-ops handoff, and a candidate-profile path. Produce a browser field plan, one unresolved-question handoff, and a tracker-ready completion summary.

Never invent qualifications, dates, metrics, eligibility, or answers. Never click final **Submit**.

## Required workflow

Follow this sequence for every application:

1. **Locate and validate inputs.** Use the explicitly supplied profile path or ask for it. Read `references/profile-schema.md`, then run `python3 scripts/validate_profile.py PROFILE`. If the applicant supplies an optional answer bank, also read `references/answer-bank-schema.md` and run `python3 scripts/validate_profile.py PROFILE --answer-bank ANSWER_BANK`. Stop on validation errors. Reuse answer-bank text only when it is non-null, applicant-authored, verified, and not AI-prohibited; never generate or rewrite it.
2. **Accept the application target.** Use the current browser tab or explicit job URL. Reuse an authenticated in-progress tab; do not reload without a concrete reason.
3. **Identify the ATS family from visible state.** Use the URL, visible headings, page structure, and controls to distinguish Workday, Greenhouse, Lever, USAJOBS, PeopleSoft, or an unknown/generic form.
4. **Read only the matching ATS reference plus safety reference.** Read `references/ats-adapters.md` for the identified family and `references/safety-and-confirmations.md`; do not load unrelated adapter sections.
5. **Inspect one stable application section and construct a field plan.** Take one page/section snapshot, map visible labels to verified profile facts, write the visible labels/types as a JSON array, and run `python3 scripts/build_field_plan.py SECTION_FIELDS.json`. Treat the utility as a conservative planning aid; visible state and browser policy remain authoritative.
6. **Fill all verified safe fields consecutively.** Build locators from the same fresh visible snapshot and batch independent fields. Use adapter mappings as hints, never as permission to guess locators or values.
7. **Verify the section with targeted checks.** Confirm the values that were entered and read any validation messages without repeating a full-page extraction.
8. **Group unresolved independent questions into one handoff.** Ask the user for all independent missing facts together; do not interrupt after each field.
9. **Pause for sensitive data, uploads, attestations, CAPTCHA, AI-prohibited prompts, or unverified facts.** Leave these fields untouched unless the user supplies the current fact or action-time confirmation required by the active browser policy.
10. **Stop at review before final Submit.** The final submission remains user-controlled even if every other field is complete.
11. **Return tracker-ready status.** Summarize the ATS, URL/job identifier, sections completed, fields left for the user, files uploaded or pending, validation issues, and explicit status: not submitted. For a deterministic handoff, `scripts/build_field_plan.py` also accepts a scenario JSON object containing `fields`, `page_state`, and tracker metadata; its result groups unresolved fields and always reports `not submitted`.

### Field action classifications

| Classification | Use for | Action |
|---|---|---|
| AUTO | Verified identity/contact, education, employment, skills/certifications, citizenship/work authorization, ordinary preferences, relocation, availability, and travel | Fill consecutively from the verified profile; verify afterward. |
| MANUAL | Sensitive or legally consequential questions: criminal history, drug use, medical/disability, EEO/demographic data, veteran status, clearance disclosures, SSN, DOB, signatures, acknowledgments, agreements, and attestations | Stop and let the user answer. Current user authorization does not override browser policy. |
| CONFIRM | File uploads and externally consequential save/send actions requiring action-time confirmation | Pause for the browser's required confirmation, then act only after confirmation. |
| NO_AI | A prompt or certification that prohibits AI/consultant assistance, and associated prose | Do not draft, rewrite, or fill. The applicant must author and certify it personally. |
| UNKNOWN | Any unmatched label, unverified value, or ambiguous control | Leave untouched and include it in the handoff. Never guess. |

## Browser and safety rules

The active browser-control skill is authoritative for browser setup, visible-state inspection, locator construction, interaction order, confirmation prompts, uploads, and handoff. Follow it before any browser action. Action-time confirmation requirements remain authoritative even when a field is classified AUTO or CONFIRM.

- Inspect visible or interactive state before acting; use one fresh snapshot per stable section.
- Do not inspect cookies, local storage, passwords, profiles, or session stores.
- Do not enter credentials or sensitive personal data from the distributable skill.
- Do not infer exact employment dates from month-only data.
- Do not fabricate or transform a user fact to satisfy browser validation.
- Stop for CAPTCHA, legal attestations, sensitive questions, unverified values, and upload confirmation.
- Never click, press, or otherwise trigger final **Submit**.

## Handoff format

At the end of the run, report:

- **Application:** ATS, job title/identifier, and URL
- **Completed:** sections and safe fields verified
- **User action required:** grouped unresolved, sensitive, NO_AI, confirmation, and CAPTCHA items
- **Files:** uploaded, pending, or not requested
- **Status:** not submitted
- **Career-ops handoff:** tracker-ready facts, including timestamp if available and any validation error
