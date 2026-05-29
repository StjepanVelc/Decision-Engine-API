"""
Seed demo rules for local development and quick reviewer onboarding.

Usage:
    python scripts/seed_demo_data.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import select

DEMO_RULES: list[dict[str, Any]] = [
    {
        "name": "fraud_high_amount",
        "description": "Flag high-value transactions for manual review.",
        "field": "amount",
        "operator": "gt",
        "value": 10000,
        "action": "REVIEW",
        "priority": 20,
        "weight": 30,
        "hard_stop": False,
        "is_active": True,
        "category": "fraud",
    },
    {
        "name": "fraud_sanctioned_country_hard_stop",
        "description": "Immediate reject for sanctioned country list.",
        "expression": "country in ['KP', 'IR']",
        "field": None,
        "operator": None,
        "value": None,
        "action": "REJECT",
        "priority": 100,
        "weight": 100,
        "hard_stop": True,
        "is_active": True,
        "category": "fraud",
    },
    {
        "name": "compliance_minor_user",
        "description": "Reject when user age is below legal threshold.",
        "field": "user.age",
        "operator": "lt",
        "value": 18,
        "action": "REJECT",
        "priority": 50,
        "weight": 80,
        "hard_stop": False,
        "is_active": True,
        "category": "compliance",
    },
    {
        "name": "pricing_loyalty_discount",
        "description": "Approve loyalty discounts for eligible users.",
        "expression": "customer.loyalty_tier in ['gold', 'platinum'] and amount < 2000",
        "field": None,
        "operator": None,
        "value": None,
        "action": "APPROVE",
        "priority": 5,
        "weight": 10,
        "hard_stop": False,
        "is_active": True,
        "category": "pricing",
    },
]


async def seed_demo_rules() -> None:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from app.core.database import AsyncSessionLocal
    from app.models.rule import Rule

    async with AsyncSessionLocal() as session:
        existing_names_result = await session.execute(select(Rule.name))
        existing_names = set(existing_names_result.scalars().all())

        created = 0
        skipped = 0

        for payload in DEMO_RULES:
            if payload["name"] in existing_names:
                skipped += 1
                continue
            session.add(Rule(**payload))
            created += 1

        await session.commit()

    print(f"Seed completed: created={created}, skipped={skipped}, total={len(DEMO_RULES)}")


if __name__ == "__main__":
    asyncio.run(seed_demo_rules())
