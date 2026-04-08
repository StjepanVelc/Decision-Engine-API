import client from "./client";
import type { Decision, DecisionRequest, PaginationParams } from "@/types/api";

export const decisionsApi = {
    list: (params?: PaginationParams) =>
        client.get<Decision[]>("/decisions/", { params }).then((r) => r.data),

    get: (id: number) =>
        client.get<Decision>(`/decisions/${id}`).then((r) => r.data),

    getByReference: (ref: string) =>
        client.get<Decision>(`/decisions/reference/${ref}`).then((r) => r.data),

    evaluate: (body: DecisionRequest) =>
        client.post<Decision>("/decisions/evaluate", body).then((r) => r.data),
};
