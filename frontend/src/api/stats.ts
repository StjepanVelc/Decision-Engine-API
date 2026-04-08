import client from "./client";
import type { Stats } from "@/types/api";

export const statsApi = {
    get: () => client.get<Stats>("/stats/").then((r) => r.data),
};
