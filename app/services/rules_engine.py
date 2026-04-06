"""
Core rules evaluation engine.
Evaluates a JSON payload against a list of Rule objects and
returns the triggered rules along with the final outcome.

Supported operators:
  gt, lt, gte, lte, eq, neq, in, not_in, contains, not_contains
"""
from typing import Any, Dict, List, Tuple

from app.models.rule import Rule

# Decision priority (higher index = more severe; determines final outcome)
OUTCOME_PRIORITY = {"APPROVE": 0, "REVIEW": 1, "REJECT": 2}


def _get_field_value(payload: Dict[str, Any], field: str) -> Any:
    """Support dot-notation field access, e.g. 'user.age'."""
    keys = field.split(".")
    value = payload
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _evaluate_operator(operator: str, payload_value: Any, rule_value: Any) -> bool:
    """Return True if the condition expressed by the operator is met."""
    if payload_value is None:
        return False

    try:
        match operator:
            case "gt":
                return float(payload_value) > float(rule_value)
            case "lt":
                return float(payload_value) < float(rule_value)
            case "gte":
                return float(payload_value) >= float(rule_value)
            case "lte":
                return float(payload_value) <= float(rule_value)
            case "eq":
                return str(payload_value).lower() == str(rule_value).lower()
            case "neq":
                return str(payload_value).lower() != str(rule_value).lower()
            case "in":
                return payload_value in rule_value
            case "not_in":
                return payload_value not in rule_value
            case "contains":
                return str(rule_value).lower() in str(payload_value).lower()
            case "not_contains":
                return str(rule_value).lower() not in str(payload_value).lower()
            case _:
                return False
    except (TypeError, ValueError):
        return False


def evaluate_rules(
    payload: Dict[str, Any],
    rules: List[Rule],
) -> Tuple[str, List[dict], List[str]]:
    """
    Evaluate all active rules against the payload.

    Returns:
        outcome        – "APPROVE" | "REVIEW" | "REJECT"
        triggered      – list of dicts describing matched rules
        reasons        – human-readable reasons
    """
    triggered: List[dict] = []
    final_outcome = "APPROVE"

    for rule in rules:
        field_value = _get_field_value(payload, str(rule.field))
        matched = _evaluate_operator(str(rule.operator), field_value, rule.value)

        if matched:
            triggered.append(
                {
                    "rule_id": str(rule.id),
                    "rule_name": str(rule.name),
                    "action": str(rule.action),
                    "field": str(rule.field),
                    "operator": str(rule.operator),
                    "threshold": rule.value,
                    "actual_value": field_value,
                }
            )
            # Escalate outcome only if the new action is more severe
            rule_action = str(rule.action)
            if OUTCOME_PRIORITY.get(rule_action, 0) > OUTCOME_PRIORITY.get(final_outcome, 0):
                final_outcome = rule_action

    reasons = [
        f"Rule '{t['rule_name']}' triggered: {t['field']} {t['operator']} {t['threshold']} "
        f"(actual: {t['actual_value']}) → {t['action']}"
        for t in triggered
    ]

    if not triggered:
        reasons = ["No rules triggered. Default outcome: APPROVE."]

    return final_outcome, triggered, reasons
