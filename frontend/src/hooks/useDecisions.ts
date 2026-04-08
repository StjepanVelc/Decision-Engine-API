import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { decisionsApi } from "@/api/decisions";
import type { DecisionRequest } from "@/types/api";

export const DECISIONS_KEY = ["decisions"] as const;

export function useDecisions() {
    return useQuery({
        queryKey: DECISIONS_KEY,
        queryFn: () => decisionsApi.list({ limit: 50 }),
    });
}

export function useDecision(id: number) {
    return useQuery({
        queryKey: [...DECISIONS_KEY, id],
        queryFn: () => decisionsApi.get(id),
        enabled: !!id,
    });
}

export function useEvaluate() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (body: DecisionRequest) => decisionsApi.evaluate(body),
        onSuccess: () => qc.invalidateQueries({ queryKey: DECISIONS_KEY }),
    });
}
