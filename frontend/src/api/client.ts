import axios from "axios";
import type { ApiError } from "@/types/api";

const client = axios.create({
    baseURL: "/api/v1",
    headers: { "Content-Type": "application/json" },
});

// Normalise error shape so callers always get { code, message, details }
client.interceptors.response.use(
    (res) => res,
    (err) => {
        const data: ApiError = err.response?.data ?? {
            code: "NETWORK_ERROR",
            message: "Unable to reach the server.",
            details: null,
        };
        return Promise.reject(data);
    }
);

export default client;
