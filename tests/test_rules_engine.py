"""
Tests for the core rules evaluation engine (no DB needed).
Run: pytest tests/ -v
"""
import uuid
from types import SimpleNamespace

from app.services.rules_engine import evaluate_rules


def make_rule(**kwargs) -> SimpleNamespace:
    defaults = {
        "id": uuid.uuid4(),
        "name": "test_rule",
        "description": None,
        "expression": None,
        "field": "amount",
        "operator": "gt",
        "value": 1000,
        "action": "REJECT",
        "priority": 1.0,
        "weight": 10,
        "hard_stop": False,
        "is_active": True,
        "category": "fraud",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


class TestOperators:
    def test_gt_triggers(self):
        rules = [make_rule(operator="gt", value=1000, action="REJECT")]
        outcome, triggered, _, risk_score, normalized_score = evaluate_rules({"amount": 5000}, rules)
        assert outcome == "APPROVE"
        assert len(triggered) == 1
        assert risk_score == 10
        assert normalized_score == 100

    def test_gt_does_not_trigger(self):
        rules = [make_rule(operator="gt", value=1000, action="REJECT")]
        outcome, triggered, _, _, _ = evaluate_rules({"amount": 500}, rules)
        assert outcome == "APPROVE"
        assert triggered == []

    def test_lt_triggers(self):
        rules = [make_rule(field="user_age", operator="lt", value=18, action="REJECT", weight=80)]
        outcome, _, _, _, _ = evaluate_rules({"user_age": 16}, rules)
        assert outcome == "REJECT"

    def test_eq_triggers(self):
        rules = [make_rule(field="country", operator="eq", value="NG", action="REVIEW", weight=55)]
        outcome, _, _, _, _ = evaluate_rules({"country": "NG"}, rules)
        assert outcome == "REVIEW"

    def test_in_triggers(self):
        rules = [make_rule(field="country", operator="in", value=["RU", "NG", "KP"], action="REJECT", weight=90)]
        outcome, _, _, _, _ = evaluate_rules({"country": "RU"}, rules)
        assert outcome == "REJECT"

    def test_not_in_triggers(self):
        rules = [make_rule(field="country", operator="not_in", value=["US", "DE"], action="REVIEW", weight=60)]
        outcome, _, _, _, _ = evaluate_rules({"country": "HR"}, rules)
        assert outcome == "REVIEW"

    def test_contains_triggers(self):
        rules = [make_rule(field="email", operator="contains", value="tempmail", action="REVIEW", weight=60)]
        outcome, _, _, _, _ = evaluate_rules({"email": "user@tempmail.com"}, rules)
        assert outcome == "REVIEW"

    def test_missing_field_does_not_trigger(self):
        rules = [make_rule(field="nonexistent", operator="gt", value=0, action="REJECT")]
        outcome, triggered, _, _, _ = evaluate_rules({"amount": 100}, rules)
        assert outcome == "APPROVE"
        assert triggered == []


class TestOutcomePriority:
    def test_score_thresholds_drive_outcome(self):
        rules = [
            make_rule(name="r1", field="amount", operator="gt", value=100, action="REVIEW", priority=1.0, weight=30),
            make_rule(name="r2", field="amount", operator="gt", value=50, action="REJECT", priority=2.0, weight=55),
        ]
        outcome, triggered, _, risk_score, normalized_score = evaluate_rules({"amount": 200}, rules)
        assert outcome == "REJECT"
        assert len(triggered) == 2
        assert risk_score == 85
        assert normalized_score == 100

    def test_hard_stop_short_circuits(self):
        rules = [
            make_rule(name="stop_rule", field="country", operator="eq", value="KP", hard_stop=True, weight=100, priority=100),
            make_rule(name="later_rule", field="amount", operator="gt", value=100, weight=80, priority=1),
        ]
        outcome, triggered, reasons, risk_score, _ = evaluate_rules({"country": "KP", "amount": 9999}, rules)
        assert outcome == "REJECT"
        assert len(triggered) == 1
        assert triggered[0]["rule_name"] == "stop_rule"
        assert triggered[0]["hard_stop"] is True
        assert reasons[0].startswith("[HARD STOP]")
        assert risk_score == 100


class TestDotNotation:
    def test_nested_field_access(self):
        rules = [make_rule(field="user.age", operator="lt", value=18, action="REJECT", weight=80)]
        outcome, _, _, _, _ = evaluate_rules({"user": {"age": 15}}, rules)
        assert outcome == "REJECT"

    def test_nested_field_missing(self):
        rules = [make_rule(field="user.score", operator="gt", value=100, action="REJECT")]
        outcome, _, _, _, _ = evaluate_rules({"user": {}}, rules)
        assert outcome == "APPROVE"
