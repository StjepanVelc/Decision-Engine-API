"""
Core rules evaluation engine.
Evaluates a JSON payload against a list of Rule objects and returns
the triggered rules, a cumulative risk score, normalized score, and the final outcome.

Rule evaluation order (per rule, sorted by priority descending):
  1. TASK 1 — Hard stop: if rule.hard_stop is True and it matches → immediately REJECT
  2. TASK 2 — DSL expression: if rule.expression is set → safe AST evaluator
  3. Legacy: field / operator / value

Score calculation (TASK 2):
  risk_score      = sum of weights of all triggered rules
  max_possible    = sum of weights of all rules passed in
  normalized_score = round((risk_score / max_possible) * 100)  or 0 if max=0

Outcome thresholds (based on risk_score):
  risk_score >= 80  → REJECT
  risk_score >= 50  → REVIEW
  else              → APPROVE

Safety (TASK 3):
  Every individual rule evaluation is wrapped in try/except.
  A failing rule is skipped and logged — the engine never crashes.

Supported legacy operators:
  gt, lt, gte, lte, eq, neq, in, not_in, contains, not_contains
"""
import logging
from typing import Any, Dict, List, Tuple

from app.models.rule import Rule
from app.services.expression_evaluator import ExpressionError, evaluate_expression

logger = logging.getLogger(__name__)

# ── Risk-score outcome thresholds ────────────────────────────────────────────
REJECT_THRESHOLD = 80
REVIEW_THRESHOLD = 50


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


def _outcome_from_score(risk_score: int) -> str:
    if risk_score >= REJECT_THRESHOLD:
        return "REJECT"
    if risk_score >= REVIEW_THRESHOLD:
        return "REVIEW"
    return "APPROVE"


def _evaluate_single_rule(rule: Rule, payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Attempt to evaluate one rule against the payload.

    Returns (matched: bool, match_detail: str).
    Raises any exception so the caller can decide how to handle it.
    """
    if rule.expression:
        matched = evaluate_expression(rule.expression, payload)
        return matched, f"expression: {rule.expression}"

    if rule.field and rule.operator:
        field_value = _get_field_value(payload, str(rule.field))
        matched = _evaluate_operator(str(rule.operator), field_value, rule.value)
        return matched, f"{rule.field} {rule.operator} {rule.value} (actual: {field_value})"

    return False, ""


def evaluate_rules(
    payload: Dict[str, Any],
    rules: List[Rule],
) -> Tuple[str, List[dict], List[str], int, int]:
    """
    Evaluate all active rules against the payload.

    Returns:
        outcome           – "APPROVE" | "REVIEW" | "REJECT"
        triggered         – list of dicts describing matched rules
        reasons           – human-readable reasons
        risk_score        – cumulative score from all triggered rules
        normalized_score  – risk_score as a 0-100 percentage of max_possible_score
    """
    triggered: List[dict] = []
    risk_score: int = 0

    # TASK 2: pre-compute maximum possible score for normalization
    max_possible_score: int = sum(
        int(r.weight) if r.weight is not None else 10
        for r in rules
    )

    for rule in rules:
        # TASK 3: safe evaluation — never let a single bad rule crash the engine
        try:
            matched, match_detail = _evaluate_single_rule(rule, payload)
        except ExpressionError as exc:
            logger.warning("Rule '%s' expression error — skipping: %s", rule.name, exc)
            continue
        except Exception as exc:
            logger.error("Rule '%s' evaluation failed unexpectedly — skipping: %s", rule.name, exc)
            continue

        if not matched:
            continue

        weight = int(rule.weight) if rule.weight is not None else 10

        # TASK 1: hard stop — immediately REJECT, no further evaluation
        if rule.hard_stop:
            hard_stop_triggered = {
                "rule_id": str(rule.id),
                "rule_name": str(rule.name),
                "action": "REJECT",
                "weight": weight,
                "match_detail": match_detail,
                "hard_stop": True,
            }
            triggered.append(hard_stop_triggered)
            risk_score += weight
            normalized_score = (
                round((risk_score / max_possible_score) * 100) if max_possible_score > 0 else 0
            )
            reasons = [
                f"[HARD STOP] Rule '{rule.name}' triggered ({match_detail}) "
                f"[weight={weight}] → immediate REJECT"
            ]
            return "REJECT", triggered, reasons, risk_score, normalized_score

        # Normal rule: accumulate score
        risk_score += weight
        triggered.append(
            {
                "rule_id": str(rule.id),
                "rule_name": str(rule.name),
                "action": str(rule.action),
                "weight": weight,
                "match_detail": match_detail,
                "hard_stop": False,
            }
        )

    outcome = _outcome_from_score(risk_score)
    normalized_score = (
        round((risk_score / max_possible_score) * 100) if max_possible_score > 0 else 0
    )

    reasons = [
        f"Rule '{t['rule_name']}' triggered ({t['match_detail']}) "
        f"[weight={t['weight']}] → {t['action']}"
        for t in triggered
    ]

    if not triggered:
        reasons = ["No rules triggered. Default outcome: APPROVE."]

    return outcome, triggered, reasons, risk_score, normalized_score
