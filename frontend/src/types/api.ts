// ── Rule ──────────────────────────────────────────────────────────────────────
export interface Rule {
    id: number;
    name: string;
    description: string | null;
    field: string;
    operator: RuleOperator;
    value: string | number | boolean | string[] | number[];
    action: RuleAction;
    priority: number;
    is_active: boolean;
    category: string | null;
    created_at: string;
    updated_at: string;
}

export type RuleOperator =
    | "eq"
    | "ne"
    | "gt"
    | "gte"
    | "lt"
    | "lte"
    | "contains"
    | "not_contains"
    | "in"
    | "not_in";

export type RuleAction = "APPROVE" | "REVIEW" | "REJECT";

export interface RuleCreate {
    name: string;
    description?: string | null;
    field: string;
    operator: RuleOperator;
    value: string | number | boolean | string[] | number[];
    action: RuleAction;
    priority: number;
    is_active?: boolean;
    category?: string | null;
}

export type RuleUpdate = Partial<RuleCreate>;

// ── Decision ──────────────────────────────────────────────────────────────────
export interface Decision {
    id: number;
    reference_id: string | null;
    category: string | null;
    payload: Record<string, unknown>;
    outcome: RuleAction;
    triggered_rules: TriggeredRule[];
    reasons: string[];
    rules_evaluated: number;
    created_at: string;
}

export interface TriggeredRule {
    rule_name: string;
    action: RuleAction;
    field: string;
    operator: RuleOperator;
    value: unknown;
    actual_value: unknown;
}

export interface DecisionRequest {
    payload: Record<string, unknown>;
    reference_id?: string | null;
    category?: string | null;
}

// ── Stats ─────────────────────────────────────────────────────────────────────
export interface Stats {
    total_decisions: number;
    approved: number;
    reviewed: number;
    rejected: number;
    approval_rate: number;
    review_rate: number;
    rejection_rate: number;
}

// ── Error ─────────────────────────────────────────────────────────────────────
export interface ErrorDetail {
    field: string;
    message: string;
}

export interface ApiError {
    code: string;
    message: string;
    details: ErrorDetail[] | null;
}

// ── Pagination helpers ────────────────────────────────────────────────────────
export interface PaginationParams {
    skip?: number;
    limit?: number;
}
