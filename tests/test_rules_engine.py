"""
Tests for the core rules evaluation engine (no DB needed).
Run: pytest tests/ -v
"""
import pytest

from app.models.rule import Rule
from app.services.rules_engine import evaluate_rules
import uuid
from datetime import datetime, timezone


def make_rule(**kwargs) -> Rule:
    defaults = {
        "id": uuid.uuid4(),
        "name": "test_rule",
        "description": None,
        "field": "amount",
        "operator": "gt",
        "value": 1000,
        "action": "REJECT",
        "priority": 1.0,
        "is_active": True,
        "category": "fraud",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    rule = Rule.__new__(Rule)
    for k, v in defaults.items():
        setattr(rule, k, v)
    return rule


class TestOperators:
    def test_gt_triggers(self):
        rules = [make_rule(operator="gt", value=1000, action="REJECT")]
        outcome, triggered, _ = evaluate_rules({"amount": 5000}, rules)
        assert outcome == "REJECT"
        assert len(triggered) == 1

    def test_gt_does_not_trigger(self):
        rules = [make_rule(operator="gt", value=1000, action="REJECT")]
        outcome, triggered, _ = evaluate_rules({"amount": 500}, rules)
        assert outcome == "APPROVE"
        assert triggered == []

    def test_lt_triggers(self):
        rules = [make_rule(field="user_age", operator="lt", value=18, action="REJECT")]
        outcome, _, _ = evaluate_rules({"user_age": 16}, rules)
        assert outcome == "REJECT"

    def test_eq_triggers(self):
        rules = [make_rule(field="country", operator="eq", value="NG", action="REVIEW")]
        outcome, _, _ = evaluate_rules({"country": "NG"}, rules)
        assert outcome == "REVIEW"

    def test_in_triggers(self):
        rules = [make_rule(field="country", operator="in", value=["RU", "NG", "KP"], action="REJECT")]
        outcome, _, _ = evaluate_rules({"country": "RU"}, rules)
        assert outcome == "REJECT"

    def test_not_in_triggers(self):
        rules = [make_rule(field="country", operator="not_in", value=["US", "DE"], action="REVIEW")]
        outcome, _, _ = evaluate_rules({"country": "HR"}, rules)
        assert outcome == "REVIEW"

    def test_contains_triggers(self):
        rules = [make_rule(field="email", operator="contains", value="tempmail", action="REVIEW")]
        outcome, _, _ = evaluate_rules({"email": "user@tempmail.com"}, rules)
        assert outcome == "REVIEW"

    def test_missing_field_does_not_trigger(self):
        rules = [make_rule(field="nonexistent", operator="gt", value=0, action="REJECT")]
        outcome, triggered, _ = evaluate_rules({"amount": 100}, rules)
        assert outcome == "APPROVE"
        assert triggered == []


class TestOutcomePriority:
    def test_reject_beats_review(self):
        rules = [
            make_rule(name="r1", field="amount", operator="gt", value=100, action="REVIEW", priority=1.0),
            make_rule(name="r2", field="amount", operator="gt", value=50, action="REJECT", priority=2.0),
        ]
        outcome, triggered, _ = evaluate_rules({"amount": 200}, rules)
        assert outcome == "REJECT"
        assert len(triggered) == 2

    def test_review_does_not_downgrade_reject(self):
        rules = [
            make_rule(name="r1", field="amount", operator="gt", value=100, action="REJECT", priority=2.0),
            make_rule(name="r2", field="flag", operator="eq", value="yes", action="REVIEW", priority=1.0),
        ]
        outcome, _, _ = evaluate_rules({"amount": 200, "flag": "yes"}, rules)
        assert outcome == "REJECT"


class TestDotNotation:
    def test_nested_field_access(self):
        rules = [make_rule(field="user.age", operator="lt", value=18, action="REJECT")]
        outcome, _, _ = evaluate_rules({"user": {"age": 15}}, rules)
        assert outcome == "REJECT"

    def test_nested_field_missing(self):
        rules = [make_rule(field="user.score", operator="gt", value=100, action="REJECT")]
        outcome, _, _ = evaluate_rules({"user": {}}, rules)
        assert outcome == "APPROVE"
