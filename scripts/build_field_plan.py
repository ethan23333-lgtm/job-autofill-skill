#!/usr/bin/env python3
"""Classify visible job-application fields without browser interaction."""

import json
import re
import sys
from pathlib import Path


def _text(label, field_type):
    return f"{label} {field_type}".lower()


def classify_field(label: str, field_type: str = "") -> str:
    """Return the safe action class for a visible field label and HTML type."""
    text = _text(label, field_type)
    restricted_tool = r"\b(ai|llm)\b|artificial intelligence|consultant"
    prohibition = (
        r"did not use|do not use|may not use|must not use|"
        r"(?:is|are)\s+not allowed|not permitted|prohibited|forbidden|"
        r"\bwithout\s+(?:using\s+)?(?:ai|llm|artificial intelligence|a consultant)\b|"
        r"\bno\s+(?:ai|llm|artificial intelligence|consultant)\b.*"
        r"\b(?:use(?:d)?|allowed|permitted|assistance)\b"
    )
    no_ai = re.search(restricted_tool, text) and re.search(prohibition, text)
    if no_ai:
        return "NO_AI"
    legal_control = (
        r"\bcertif(?:y|ies|ied)\b|"
        r"\bcertification\s+(?:of|that)\b|"
        r"\bapplicant\s+certification\b|"
        r"\bcertification\s+and\s+release\b|"
        r"\bsignature\b|\belectronic\s+signature\b|"
        r"\backnowledg(?:e|ement|ment)\b|"
        r"\bi\s+agree\b|\bagreement\b|"
        r"\blegal\s+attestation\b|\battest"
    )
    sensitive_or_submit = (
        r"\bsubmit\b|\bssn\b|social security|date of birth|\bdob\b|"
        r"\bdrugs?\b|\bcriminal\b|\bdisability\b|\bmedical\b|\beeo\b|"
        r"\brace\b|\bethnicity\b|\bgender\b|\bsex\b|\bveterans?\b|"
        r"\bclearance\b|\bpolygraph\b"
    )
    if (
        field_type.lower() == "submit"
        or re.search(sensitive_or_submit, text)
        or re.search(legal_control, text)
    ):
        return "MANUAL"
    if field_type.lower() == "file" or re.search(r"\bupload\b|save[-\s]+and[-\s]+send", text):
        return "CONFIRM"
    if re.search(r"\bconsultant\s+name\b", text):
        return "UNKNOWN"
    ordinary_profile_fact = (
        r"\bname\b|email|phone|address|linkedin|employer|job title|employment|"
        r"education|degree|school|university|skill|certification|salary|"
        r"compensation|relocat|availability|travel|citizenship|"
        r"\bu\.?s\.?\s+citizen\b|\bcitizens?\b|work authorization|"
        r"authorized to work|legally authorized"
    )
    if re.search(ordinary_profile_fact, text):
        return "AUTO"
    return "UNKNOWN"


def _reason(classification):
    return {
        "AUTO": "verified ordinary application fact",
        "MANUAL": "sensitive, attested, or final-submit field",
        "CONFIRM": "upload or consequential browser action requires confirmation",
        "NO_AI": "AI-prohibited attestation or associated prompt",
        "UNKNOWN": "no safe deterministic mapping",
    }[classification]


def _field_plan(fields):
    if not isinstance(fields, list):
        raise ValueError("fields must be a JSON array")
    plan = []
    for field in fields:
        if not isinstance(field, dict) or not isinstance(field.get("label"), str):
            raise ValueError("each field needs a string label")
        label = field["label"]
        field_type = field.get("type", "")
        if not isinstance(field_type, str):
            raise ValueError("field type must be a string")
        classification = classify_field(label, field_type)
        if field.get("verified") is False and classification == "AUTO":
            classification = "UNKNOWN"
        plan.append(
            {
                "classification": classification,
                "label": label,
                "reason": _reason(classification),
            }
        )
    return plan


def build_workflow_result(scenario: dict) -> dict:
    """Build a deterministic, non-submitting review handoff from a scenario."""
    if not isinstance(scenario, dict):
        raise ValueError("scenario must be a JSON object")
    plan = _field_plan(scenario.get("fields"))
    groups = {name: [] for name in ("MANUAL", "CONFIRM", "NO_AI", "UNKNOWN")}
    for item in plan:
        classification = item["classification"]
        if classification in groups:
            groups[classification].append(item["label"])

    page_state = scenario.get("page_state", "")
    if not isinstance(page_state, str):
        raise ValueError("page_state must be a string")
    completed = scenario.get("completed_fields", [])
    files = scenario.get("files", [])
    if not isinstance(completed, list) or not all(
        isinstance(item, str) for item in completed
    ):
        raise ValueError("completed_fields must be a list of strings")
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        raise ValueError("files must be a list of strings")

    return {
        "page_state": page_state.lower(),
        "field_plan": plan,
        "grouped_unresolved": groups,
        "stop_before_submit": page_state.lower() == "review"
        or any(item["classification"] == "MANUAL" and "submit" in item["label"].lower() for item in plan),
        "tracker_summary": {
            "ats": scenario.get("ats"),
            "url": scenario.get("url"),
            "job_identifier": scenario.get("job_identifier"),
            "completed_fields": completed,
            "user_action_required": groups,
            "files": files,
            "status": "not submitted",
        },
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: build_field_plan.py FIELDS_OR_SCENARIO_JSON", file=sys.stderr)
        return 2
    try:
        payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        result = (
            _field_plan(payload)
            if isinstance(payload, list)
            else build_workflow_result(payload)
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not build field plan: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
