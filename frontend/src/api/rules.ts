import client from "./client";
import type { Rule, RuleCreate, RuleUpdate, PaginationParams } from "@/types/api";

export const rulesApi = {
    list: (params?: PaginationParams) =>
        client.get<Rule[]>("/rules/", { params }).then((r) => r.data),

    get: (id: number) =>
        client.get<Rule>(`/rules/${id}`).then((r) => r.data),

    create: (body: RuleCreate) =>
        client.post<Rule>("/rules/", body).then((r) => r.data),

    update: (id: number, body: RuleUpdate) =>
        client.patch<Rule>(`/rules/${id}`, body).then((r) => r.data),

    remove: (id: number) =>
        client.delete(`/rules/${id}`).then((r) => r.data),
};
