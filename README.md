# Job Autofill Skill

An Agent Skill for planning and safely filling job applications on Workday, Greenhouse, Lever, USAJOBS, PeopleSoft, and generic application forms.

The skill uses a verified candidate profile, fills only supported facts, pauses for sensitive or legally consequential questions, and always stops before final submission.

## Install in Codex

Ask Codex to install:

```text
https://github.com/ethan23333-lgtm/job-autofill-skill
```

Then restart Codex so the skill is discovered.

## Contents

- `SKILL.md`: workflow and safety rules
- `agents/openai.yaml`: Codex display metadata
- `assets/`: example candidate profile and answer bank
- `references/`: schemas, ATS adapters, and confirmation rules
- `scripts/`: profile validation and field-plan generation

## Safety

- Never stores passwords, SSNs, dates of birth, medical information, or demographic answers in the reusable profile.
- Never invents qualifications, employment dates, eligibility, or application answers.
- Leaves sensitive questions, attestations, CAPTCHA, and AI-prohibited prompts to the applicant.
- Never clicks final Submit.

The example files contain fictional placeholder data only. Keep real candidate profiles outside the skill directory and out of version control.
