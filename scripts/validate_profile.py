#!/usr/bin/env python3
"""Validate dependency-free job-autofill profile and answer-bank files."""

import json
import re
import sys
from datetime import date
from pathlib import Path


REQUIRED_SECTIONS = ("identity", "contact", "eligibility", "preferences", "education", "employment", "skills", "certifications")
FACT_KEYS = ("value", "verified", "source", "last_updated", "sensitivity")
SENSITIVITIES = {"standard", "personal", "sensitive", "prohibited_store"}
MONTH_PERIOD = re.compile(r"\b\d{4}-\d{2}\b")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ANSWER_KEYS = (
    "id",
    "prompt_pattern",
    "text",
    "applicant_authored",
    "ai_prohibited",
    "verified",
)


def _scalar(text):
    if text == "{}":
        return {}
    if text == "[]":
        return []
    if text in {"null", "~"}:
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if text.startswith(('"', "'")):
        if len(text) < 2 or text[-1] != text[0]:
            raise ValueError("Unclosed or mismatched quoted scalar")
        return text[1:-1]
    if text.endswith(('"', "'")):
        raise ValueError("Unclosed or mismatched quoted scalar")
    try:
        return int(text)
    except ValueError:
        return text


def _yaml_lines(text):
    return [(len(line) - len(line.lstrip()), line.strip()) for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def _parse_yaml(text):
    lines = _yaml_lines(text)

    def node(index, indent):
        return parse_list(index, indent) if lines[index][1].startswith("- ") else parse_map(index, indent)

    def child(index, parent_indent):
        if index < len(lines) and lines[index][0] > parent_indent:
            return node(index, lines[index][0])
        return {}, index

    def parse_map(index, indent):
        result = {}
        while index < len(lines) and lines[index][0] == indent and not lines[index][1].startswith("- "):
            key, _, value = lines[index][1].partition(":")
            if not _:
                raise ValueError(f"Invalid YAML line: {lines[index][1]}")
            index += 1
            if value.strip():
                result[key] = _scalar(value.strip())
            else:
                result[key], index = child(index, indent)
        return result, index

    def parse_list(index, indent):
        result = []
        while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
            body = lines[index][1][2:].strip()
            index += 1
            if ":" not in body:
                result.append(_scalar(body))
                continue
            key, _, value = body.partition(":")
            item = {key: _scalar(value.strip())} if value.strip() else {}
            if not value.strip():
                item[key], index = child(index, indent)
            if index < len(lines) and lines[index][0] == indent + 2 and not lines[index][1].startswith("- "):
                rest, index = parse_map(index, indent + 2)
                item.update(rest)
            result.append(item)
        return result, index

    if not lines:
        return {}
    parsed, index = node(0, lines[0][0])
    if index != len(lines):
        raise ValueError("Unsupported YAML structure")
    return parsed


def _load(path):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text) if Path(path).suffix.lower() == ".json" else _parse_yaml(text)


def _check_fact(fact, path, errors):
    if not isinstance(fact, dict):
        errors.append(f"{path} must use a fact wrapper")
        return
    for key in FACT_KEYS:
        if key not in fact:
            errors.append(f"{path} is missing {key}")
    if "value" in fact and fact["value"] is not None and not isinstance(fact["value"], (str, int, float, bool, list)):
        errors.append(f"{path}.value must be a scalar, list, or null")
    if "verified" in fact and type(fact["verified"]) is not bool:
        errors.append(f"{path}.verified must be a boolean")
    if "source" in fact and fact["source"] is not None and not isinstance(fact["source"], str):
        errors.append(f"{path}.source must be a string or null")
    if "last_updated" in fact and fact["last_updated"] is not None and not _valid_date(fact["last_updated"]):
        errors.append(f"{path}.last_updated must be a valid calendar date (YYYY-MM-DD) or null")
    sensitivity = fact.get("sensitivity")
    if sensitivity not in SENSITIVITIES:
        errors.append(f"{path} has invalid sensitivity")
    if sensitivity == "prohibited_store" and fact.get("value") is not None:
        errors.append(f"{path} is prohibited_store and must have a null value")


def _valid_date(value):
    if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _check_exact_date(fact, path, errors):
    if not isinstance(fact, dict) or fact.get("value") is None:
        return
    if not _valid_date(fact["value"]):
        errors.append(f"{path} must be a valid calendar date (YYYY-MM-DD) or null")
    if fact.get("verified") is not True:
        errors.append(f"{path} must be verified before use")
    if not isinstance(fact.get("source"), str) or not fact["source"].strip():
        errors.append(f"{path} must have a source before use")


def validate_profile(path: str) -> list[str]:
    """Return human-readable validation errors for a JSON or simple YAML profile."""
    try:
        data = _load(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"Could not read profile: {exc}"]

    errors = []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    profile = data.get("profile") if isinstance(data, dict) else None
    if not isinstance(profile, dict):
        return errors + ["profile must be a mapping"]
    for section in REQUIRED_SECTIONS:
        if section not in profile:
            errors.append(f"profile is missing {section}")

    for section in ("identity", "contact", "eligibility", "preferences"):
        values = profile.get(section, {})
        if not isinstance(values, dict):
            errors.append(f"profile.{section} must be a mapping")
        else:
            for name, fact in values.items():
                _check_fact(fact, f"profile.{section}.{name}", errors)
                if name.endswith("_date"):
                    _check_exact_date(fact, f"profile.{section}.{name}", errors)

    for section in ("education", "employment"):
        records = profile.get(section, [])
        if not isinstance(records, list):
            errors.append(f"profile.{section} must be a list")
            continue
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"profile.{section}[{index}] must be a mapping")
                continue
            for name, fact in record.items():
                _check_fact(fact, f"profile.{section}[{index}].{name}", errors)
                if name.endswith("_date"):
                    _check_exact_date(fact, f"profile.{section}[{index}].{name}", errors)
            if section == "employment":
                period_fact = record.get("source_period")
                period = period_fact.get("value") if isinstance(period_fact, dict) else None
                if isinstance(period, str) and MONTH_PERIOD.search(period):
                    for name in ("start_date", "end_date"):
                        fact = record.get(name, {})
                        if isinstance(fact, dict) and fact.get("value") is not None:
                            if fact.get("verified") is not True or not fact.get("source") or not _valid_date(fact["value"]):
                                errors.append(f"profile.employment[{index}].{name}: exact dates from a month-only source_period require independent verification")
                            elif not period_fact.get("source") or fact.get("source") == period_fact.get("source"):
                                errors.append(f"profile.employment[{index}].{name}: exact dates from a month-only source_period require an independent source")

    for section in ("skills", "certifications"):
        facts = profile.get(section, [])
        if not isinstance(facts, list):
            errors.append(f"profile.{section} must be a list")
        else:
            for index, fact in enumerate(facts):
                _check_fact(fact, f"profile.{section}[{index}]", errors)
    return errors


def validate_answer_bank(path: str) -> list[str]:
    """Return human-readable validation errors for an optional answer bank."""
    try:
        data = _load(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"Could not read answer bank: {exc}"]

    errors = []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    answers = data.get("answers") if isinstance(data, dict) else None
    if not isinstance(answers, list):
        return errors + ["answers must be a list"]

    seen_ids = set()
    for index, answer in enumerate(answers):
        path_prefix = f"answers[{index}]"
        if not isinstance(answer, dict):
            errors.append(f"{path_prefix} must be a mapping")
            continue
        for key in ANSWER_KEYS:
            if key not in answer:
                errors.append(f"{path_prefix} is missing {key}")

        answer_id = answer.get("id")
        if not isinstance(answer_id, str) or not answer_id.strip():
            errors.append(f"{path_prefix}.id must be a non-empty string")
        elif answer_id in seen_ids:
            errors.append(f"{path_prefix}: duplicate answer id {answer_id}")
        else:
            seen_ids.add(answer_id)

        pattern = answer.get("prompt_pattern")
        if not isinstance(pattern, str) or not pattern.strip():
            errors.append(f"{path_prefix}.prompt_pattern must be a non-empty string")
        else:
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as exc:
                errors.append(f"{path_prefix}.prompt_pattern is invalid: {exc}")

        text = answer.get("text")
        if text is not None and not isinstance(text, str):
            errors.append(f"{path_prefix}.text must be a string or null")
        for flag in ("applicant_authored", "ai_prohibited", "verified"):
            if flag in answer and type(answer[flag]) is not bool:
                errors.append(f"{path_prefix}.{flag} must be a boolean")

        if answer.get("ai_prohibited") is True and text is not None:
            errors.append(f"{path_prefix}.text must be null when ai_prohibited is true")
        if text is not None and answer.get("applicant_authored") is not True:
            errors.append(f"{path_prefix}.text requires applicant_authored true")
    return errors


def main():
    if len(sys.argv) not in {2, 4} or (
        len(sys.argv) == 4 and sys.argv[2] != "--answer-bank"
    ):
        print(
            "Usage: validate_profile.py PROFILE [--answer-bank ANSWER_BANK]",
            file=sys.stderr,
        )
        return 2
    errors = validate_profile(sys.argv[1])
    if errors:
        print("\n".join(errors))
        return 1
    print("Profile valid")
    if len(sys.argv) == 4:
        answer_errors = validate_answer_bank(sys.argv[3])
        if answer_errors:
            print("\n".join(answer_errors))
            return 1
        print("Answer bank valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
