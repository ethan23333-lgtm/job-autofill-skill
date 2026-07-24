# Safety and Confirmations

Classify each visible field before entering a value. The active Browser skill, visible-state requirements, and action-time confirmation policy override this reference.

| Classification | Examples | Handling |
|---|---|---|
| `AUTO` | Verified contact, education, employment, skills/certifications, citizenship/work authorization, ordinary work preferences | Batch-fill only from a verified profile value, then verify the result. |
| `MANUAL` | Criminal history, drug use, medical/disability, EEO/demographic data, veteran status, clearance disclosures, SSN, DOB, legal certifications | Leave untouched for the applicant. A current task-specific user authorization is also required, and browser policy must permit the action. |
| `CONFIRM` | File uploads; save-and-send or other externally consequential actions | Obtain the Browser-required action-time confirmation before acting. |
| `NO_AI` | Any no-AI/no-consultant certification and its associated written response | Do not draft, rewrite, paste, or answer. The applicant must author and certify it personally. |
| `UNKNOWN` | Ambiguous labels, unclear controls, missing profile facts, month-only dates requested as exact dates | Do not guess; collect these in one handoff. |

## Always manual

Final **Submit** is always manual. Do not click it, press Enter to trigger it, or otherwise submit an application. CAPTCHA completion is also user-controlled.

## Uploads and consequential actions

Uploading a resume, transcript, cover letter, portfolio, or other document can disclose personal information. Confirm the exact file and destination at action time whenever the Browser policy requires it. Do not upload a file merely because its name appears in a career-ops handoff. Treat save/send actions as `CONFIRM` when they create an external effect; ordinary navigation remains subject to the active Browser rules.

## Attestations and sensitive answers

Do not infer a sensitive answer from a prior application or profile. An applicant must provide a current response for the current task. This includes eligibility or suitability answers that may change with wording or time. When a form requires an attestation, keep the control manual even if a related profile fact is verified.

A plain citizenship or work-authorization field may be `AUTO` only when its exact answer is verified in the profile. If the fact appears inside a signature, certification, acknowledgment, or agreement, the legal control remains `MANUAL`.

If a prompt says the applicant must certify no AI or consultant assistance, classify both the certification and the corresponding prose as `NO_AI`, regardless of whether the prose is optional. Do not help transform content for that prompt.

## Verification and handoff

Visible state is authoritative. Before each action, verify the field and label in the current stable section; adapter mappings only help identify likely controls. After a safe batch, verify targeted field values and collect independent `MANUAL`, `CONFIRM`, `NO_AI`, and `UNKNOWN` items into one concise applicant handoff.
