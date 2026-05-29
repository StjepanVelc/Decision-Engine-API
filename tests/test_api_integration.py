"""
Integration tests for FastAPI endpoints.

These tests exercise real HTTP routes against the app,
including DB persistence and stats aggregation.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.core.database import AsyncSessionLocal, Base, engine
from app.main import app
from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.rule import Rule


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    """Isolate tests by cleaning mutable tables before and after each test."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:  # pragma: no cover - environment guard
        pytest.skip(f"PostgreSQL not available for integration tests: {exc}")

    async with AsyncSessionLocal() as session:
        await session.execute(delete(AuditLog))
        await session.execute(delete(Decision))
        await session.execute(delete(Rule))
        await session.commit()

    yield

    async with AsyncSessionLocal() as session:
        await session.execute(delete(AuditLog))
        await session.execute(delete(Decision))
        await session.execute(delete(Rule))
        await session.commit()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as api_client:
        yield api_client


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body


@pytest.mark.asyncio
async def test_create_rule_endpoint(client: AsyncClient):
    payload = {
        "name": f"high_amount_{uuid.uuid4().hex[:8]}",
        "field": "amount",
        "operator": "gt",
        "value": 10000,
        "action": "REVIEW",
        "priority": 10,
        "weight": 30,
        "hard_stop": False,
        "category": "fraud",
    }

    response = await client.post("/api/v1/rules/", json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["name"] == payload["name"]
    assert body["field"] == "amount"
    assert body["operator"] == "gt"
    assert body["weight"] == 30
    assert body["hard_stop"] is False


@pytest.mark.asyncio
async def test_evaluate_decision_endpoint(client: AsyncClient):
    rule_payload = {
        "name": f"reject_high_amount_{uuid.uuid4().hex[:8]}",
        "field": "amount",
        "operator": "gt",
        "value": 10000,
        "action": "REJECT",
        "priority": 50,
        "weight": 80,
        "hard_stop": False,
        "category": "fraud",
    }
    create_rule = await client.post("/api/v1/rules/", json=rule_payload)
    assert create_rule.status_code == 201

    evaluate_payload = {
        "payload": {
            "amount": 15000,
            "country": "NG",
        },
        "reference_id": "integration-demo-1",
        "category": "fraud",
    }

    response = await client.post("/api/v1/decisions/evaluate", json=evaluate_payload)
    assert response.status_code == 201

    body = response.json()
    assert body["outcome"] == "REJECT"
    assert body["risk_score"] == 80
    assert body["normalized_score"] == 100
    assert body["rules_evaluated"] >= 1
    assert len(body["triggered_rules"]) == 1


@pytest.mark.asyncio
async def test_stats_endpoint(client: AsyncClient):
    rule_payload = {
        "name": f"review_medium_amount_{uuid.uuid4().hex[:8]}",
        "field": "amount",
        "operator": "gt",
        "value": 5000,
        "action": "REVIEW",
        "priority": 10,
        "weight": 55,
        "hard_stop": False,
        "category": "fraud",
    }
    create_rule = await client.post("/api/v1/rules/", json=rule_payload)
    assert create_rule.status_code == 201

    evaluate_payload = {
        "payload": {"amount": 7000},
        "reference_id": "integration-demo-2",
        "category": "fraud",
    }
    evaluate = await client.post("/api/v1/decisions/evaluate", json=evaluate_payload)
    assert evaluate.status_code == 201

    response = await client.get("/api/v1/stats/")
    assert response.status_code == 200

    body = response.json()
    assert body["total_decisions"] >= 1
    assert "approve_rate" in body
    assert "review_rate" in body
    assert "reject_rate" in body
