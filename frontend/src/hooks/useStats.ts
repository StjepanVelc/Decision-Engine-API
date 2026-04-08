import { useQuery } from "@tanstack/react-query";
import { statsApi } from "@/api/stats";

export const STATS_KEY = ["stats"] as const;

export function useStats() {
    return useQuery({
        queryKey: STATS_KEY,
        queryFn: statsApi.get,
        refetchInterval: 30_000,
    });
}
