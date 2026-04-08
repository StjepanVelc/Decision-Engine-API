import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Layout from "@/components/layout/Layout";
import DashboardPage from "@/pages/DashboardPage";
import RulesPage from "@/pages/RulesPage";
import DecisionsPage from "@/pages/DecisionsPage";
import EvaluatePage from "@/pages/EvaluatePage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 10_000,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="rules" element={<RulesPage />} />
            <Route path="decisions" element={<DecisionsPage />} />
            <Route path="evaluate" element={<EvaluatePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
