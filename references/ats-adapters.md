# ATS Adapters

Use an adapter only after verifying the current URL and visible page state. Recognition signals and mappings are hints, never permission to guess a locator, field meaning, or value. Inspect one stable section, make a field plan, fill verified `AUTO` facts in a batch, then perform targeted verification. If signals conflict or the page differs materially, use the generic adapter.

## Generic adapter

Use for unrecognized sites or mismatched variants. Read visible labels, group the current section into profile-backed `AUTO` fields and `MANUAL`/`CONFIRM`/`NO_AI`/`UNKNOWN` fields, then work only from that fresh visible state. Do not load unrelated adapters or repeatedly rediscover the same section.

## Workday

| Topic | Guidance |
|---|---|
| Recognition | URLs commonly contain `myworkdayjobs.com`, `/wday/`, or `candidate`; headings often include `My Experience`, `My Information`, or `Job Application`. |
| Segments | Account/sign-in, My Information, Experience, Education, Skills, Voluntary Disclosures, Self-Identify, Review. |
| Stable fields | Name/contact, address, work experience, education, skills, work authorization, preferences. |
| Dynamic behavior | Modal dialogs, repeatable experience cards, searchable comboboxes, client-side validation, and occasionally embedded content. Wait for the active section and inspect it after each add/edit action. |
| Fallback | Use generic when a tenant uses custom sections, labels, or an embedded third-party assessment. |

## Greenhouse

| Topic | Guidance |
|---|---|
| Recognition | URLs commonly contain `greenhouse.io`, `boards.greenhouse.io`, or `job-boards.greenhouse.io`; headings often include `Apply for this job`. |
| Segments | Usually one application page with contact, resume/attachments, demographic/EEO, job-specific questions, and submit controls. |
| Stable fields | Name, email, phone, location, LinkedIn/portfolio, resume/cover-letter upload, and ordinary application questions. |
| Dynamic behavior | Custom questions may appear conditionally; upload inputs may be hidden behind buttons; forms can be embedded in an iframe on an employer site. Verify the active frame and revealed labels. |
| Fallback | Use generic for custom employer embeds, multi-page variants, or labels that do not match visible state. |

## Lever

| Topic | Guidance |
|---|---|
| Recognition | URLs commonly contain `jobs.lever.co` or `jobs.eu.lever.co`; headings often include `Apply for this job`. |
| Segments | Typically one page: contact, resume/attachments, links, work authorization, custom questions, diversity/EEO, review/submit. |
| Stable fields | Name, email, phone, current location, links, resume upload, and verified ordinary questions. |
| Dynamic behavior | Custom questions can be required conditionally; file inputs can be hidden or styled; referral and consent controls vary by employer. |
| Fallback | Use generic when an employer uses a custom hosted application or the page is embedded. |

## USAJOBS

| Topic | Guidance |
|---|---|
| Recognition | URLs commonly contain `usajobs.gov`; visible pages include job announcements, profile/resume pages, `Apply`, or an agency application handoff. |
| Segments | USAJOBS account/profile and documents, eligibility questionnaire, agency handoff, review, and agency submission. |
| Stable fields | Contact, citizenship/work authorization when verified, resume/document selection, experience, education, preferences. |
| Dynamic behavior | The application may transfer to an agency system in a new tab; questionnaires have required eligibility/attestation wording; documents are selected or uploaded through account tools. |
| Fallback | Use generic once redirected to an agency site or when an announcement-specific questionnaire differs from the visible USAJOBS flow. |

## PeopleSoft

| Topic | Guidance |
|---|---|
| Recognition | URLs often contain `/psc/`, `psp/`, `HRS_`, or PeopleSoft component names; headings can include `Careers`, `My Profile`, `Job Application`, `Preferences`, or `Questionnaire`. |
| Segments | Terms, profile/personal information, preferences, education, work experience, questionnaires, attachments, review/submit. |
| Stable fields | Contact, preferences, education, repeatable employment rows, skills, and non-sensitive availability. |
| Dynamic behavior | Stateful multi-step pages, server round trips, add-row controls, lookup dialogs, conditional subpages, and iframe-like dynamic content. Save only when appropriate and Browser confirmation policy permits; re-snapshot after navigation or an add-row action. |
| Fallback | Use generic if organization-specific PeopleSoft customization changes labels, workflow, or component behavior. |

## Shared control rules

- Verify a control from current visible state before every action.
- Use one fresh snapshot per stable section; re-inspect after navigation, a modal, dynamic reveal, validation failure, or add-row action.
- Never guess dropdown options, lookup values, or dates.
- Do not upload files, answer sensitive questions, complete CAPTCHA, certify attestations, or trigger final **Submit** without the handling required in `safety-and-confirmations.md` and the active Browser policy.
