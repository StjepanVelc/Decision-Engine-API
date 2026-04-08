"""
Safe DSL expression evaluator using Python's stdlib ast module.

Supported syntax:
  - Comparisons:   amount > 1000, score <= 0.5, status == "blocked"
  - Membership:    country in ["NG", "KP"],  action not in [1, 2]
  - Logic:         risk > 50 and verified == False
  - Attribute path: user.age > 18  (dot-notation resolved against payload)
  - Not:           not is_verified

Payload values are available as top-level names AND via dot-notation:
  payload = {"user": {"age": 25}, "amount": 5000}
  → "amount > 1000"       = True
  → "user.age >= 18"      = True  (resolved via _dot_lookup)

Only a strict whitelist of AST node types is permitted; anything else
raises ExpressionError to prevent code injection.
"""

import ast
import operator
from typing import Any

__all__ = ["evaluate_expression", "ExpressionError"]


class ExpressionError(ValueError):
    """Raised for invalid or unsafe expressions."""


# ---------------------------------------------------------------------------
# Whitelisted AST node types
# ---------------------------------------------------------------------------
_SAFE_NODES = frozenset(
    {
        ast.Expression,
        ast.BoolOp,
        ast.And,
        ast.Or,
        ast.UnaryOp,
        ast.Not,
        ast.Compare,
        ast.BinOp,  # arithmetic allowed for value computation
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.In,
        ast.NotIn,
        ast.Name,
        ast.Attribute,  # dot-notation: user.age, transaction.metadata.score
        ast.Constant,
        ast.List,
        ast.Tuple,
        ast.Set,
        ast.Load,
    }
)

# ---------------------------------------------------------------------------
# Comparison operator dispatch
# ---------------------------------------------------------------------------
_CMP_OPS: dict[type, Any] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
}

_BIN_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _dot_lookup(name: str, context: dict[str, Any]) -> Any:
    """Resolve 'user.age' style names against payload using dot-notation."""
    parts = name.split(".")
    value: Any = context
    for part in parts:
        if isinstance(value, dict):
            if part not in value:
                raise ExpressionError(f"Field '{name}' not found in payload")
            value = value[part]
        else:
            raise ExpressionError(f"Cannot traverse '{part}' in non-dict value")
    return value


def _check_nodes(tree: ast.AST) -> None:
    """Walk the AST and raise if any node type is not whitelisted."""
    for node in ast.walk(tree):
        if type(node) not in _SAFE_NODES:
            raise ExpressionError(
                f"Unsafe expression: node type '{type(node).__name__}' is not allowed"
            )


# ---------------------------------------------------------------------------
# Recursive evaluator
# ---------------------------------------------------------------------------
def _attr_to_dotted(node: ast.AST) -> str:
    """Recursively convert an ast.Attribute chain to a dotted string.
    e.g. user.address.city -> 'user.address.city'
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_attr_to_dotted(node.value)}.{node.attr}"
    raise ExpressionError("Unsupported attribute access pattern")


def _eval_node(node: ast.AST, ctx: dict[str, Any]) -> Any:  # noqa: PLR0911
    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.Name):
        name = node.id
        if name in ctx:
            return ctx[name]
        raise ExpressionError(f"Field '{name}' not found in payload")

    if isinstance(node, ast.Attribute):
        dotted = _attr_to_dotted(node)
        if dotted in ctx:
            return ctx[dotted]
        raise ExpressionError(f"Field '{dotted}' not found in payload")

    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return [_eval_node(elt, ctx) for elt in node.elts]

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.Not):
            return not _eval_node(node.operand, ctx)
        raise ExpressionError("Unsupported unary operator")

    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            return all(_eval_node(v, ctx) for v in node.values)
        if isinstance(node.op, ast.Or):
            return any(_eval_node(v, ctx) for v in node.values)
        raise ExpressionError("Unsupported boolean operator")

    if isinstance(node, ast.BinOp):
        op_fn = _BIN_OPS.get(type(node.op))
        if op_fn is None:
            raise ExpressionError(f"Unsupported binary operator: {type(node.op).__name__}")
        try:
            return op_fn(_eval_node(node.left, ctx), _eval_node(node.right, ctx))
        except (TypeError, ZeroDivisionError) as exc:
            raise ExpressionError(f"Arithmetic error in expression: {exc}") from exc

    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, ctx)
        for op, comparator in zip(node.ops, node.comparators):
            op_fn = _CMP_OPS.get(type(op))
            if op_fn is None:
                raise ExpressionError(f"Unsupported comparator: {type(op).__name__}")
            right = _eval_node(comparator, ctx)
            try:
                result = op_fn(left, right)
            except TypeError as exc:
                raise ExpressionError(f"Type mismatch in comparison: {exc}") from exc
            if not result:
                return False
            left = right  # Python allows chained comparisons: 1 < x < 10
        return True

    raise ExpressionError(f"Unsupported AST node: {type(node).__name__}")


# ---------------------------------------------------------------------------
# Build flat context — dot-notation names like "user.age" pre-resolved
# ---------------------------------------------------------------------------
def _build_context(payload: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten nested dict into dotted keys so 'user.age' resolves correctly."""
    ctx: dict[str, Any] = {}
    for key, value in payload.items():
        full_key = f"{prefix}.{key}" if prefix else key
        ctx[full_key] = value
        if isinstance(value, dict):
            ctx.update(_build_context(value, full_key))
    return ctx


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def evaluate_expression(expression: str, payload: dict[str, Any]) -> bool:
    """
    Evaluate a DSL *expression* against a *payload* dict.

    Returns True if the expression is satisfied, False otherwise.
    Raises ExpressionError on syntax errors or unsafe constructs.

    Examples
    --------
    >>> evaluate_expression("amount > 1000", {"amount": 5000})
    True
    >>> evaluate_expression("country in ['NG', 'KP']", {"country": "NG"})
    True
    >>> evaluate_expression("score >= 0.8 and verified == False", {"score": 0.9, "verified": False})
    True
    """
    if not expression or not expression.strip():
        raise ExpressionError("Expression must not be empty")

    # Parse
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"Syntax error in expression: {exc}") from exc

    # Safety check — walk before eval
    _check_nodes(tree)

    # Build flat context (handles dot-notation)
    ctx = _build_context(payload)

    # Evaluate
    try:
        result = _eval_node(tree.body, ctx)
    except ExpressionError:
        raise
    except Exception as exc:
        raise ExpressionError(f"Evaluation error: {exc}") from exc

    if not isinstance(result, bool):
        raise ExpressionError(
            f"Expression must evaluate to a boolean, got {type(result).__name__}"
        )
    return result
