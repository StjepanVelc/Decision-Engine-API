import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rulesApi } from "@/api/rules";
import type { RuleCreate, RuleUpdate } from "@/types/api";

export const RULES_KEY = ["rules"] as const;

export function useRules() {
    return useQuery({ queryKey: RULES_KEY, queryFn: () => rulesApi.list() });
}

export function useRule(id: number) {
    return useQuery({
        queryKey: [...RULES_KEY, id],
        queryFn: () => rulesApi.get(id),
        enabled: !!id,
    });
}

export function useCreateRule() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (body: RuleCreate) => rulesApi.create(body),
        onSuccess: () => qc.invalidateQueries({ queryKey: RULES_KEY }),
    });
}

export function useUpdateRule() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: ({ id, body }: { id: number; body: RuleUpdate }) =>
            rulesApi.update(id, body),
        onSuccess: () => qc.invalidateQueries({ queryKey: RULES_KEY }),
    });
}

export function useDeleteRule() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => rulesApi.remove(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: RULES_KEY }),
    });
}
