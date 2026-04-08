import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { useStats } from "@/hooks/useStats";
import { useDecisions } from "@/hooks/useDecisions";

function StatCard({
    title,
    value,
    sub,
}: {
    title: string;
    value: string | number;
    sub?: string;
}) {
    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                    {title}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <p className="text-3xl font-bold">{value}</p>
                {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
            </CardContent>
        </Card>
    );
}

export default function DashboardPage() {
    const { data: stats, isLoading: statsLoading } = useStats();
    const { data: decisions } = useDecisions();

    const chartData = stats
        ? [
            { name: "APPROVE", count: stats.approved, fill: "#22c55e" },
            { name: "REVIEW", count: stats.reviewed, fill: "#f59e0b" },
            { name: "REJECT", count: stats.rejected, fill: "#ef4444" },
        ]
        : [];

    // Recent 7 days activity from decisions list
    const recentActivity = (() => {
        if (!decisions) return [];
        const counts: Record<string, number> = {};
        decisions.slice(0, 50).forEach((d) => {
            const day = new Date(d.created_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
            });
            counts[day] = (counts[day] ?? 0) + 1;
        });
        return Object.entries(counts)
            .slice(-7)
            .map(([date, count]) => ({ date, count }));
    })();

    if (statsLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <p className="text-muted-foreground">Loading stats…</p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
                <p className="text-muted-foreground">
                    Real-time overview of your decision engine.
                </p>
            </div>

            {/* Stat cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <StatCard
                    title="Total Decisions"
                    value={stats?.total_decisions ?? 0}
                />
                <StatCard
                    title="Approved"
                    value={stats?.approved ?? 0}
                    sub={`${((stats?.approval_rate ?? 0) * 100).toFixed(1)}% rate`}
                />
                <StatCard
                    title="Under Review"
                    value={stats?.reviewed ?? 0}
                    sub={`${((stats?.review_rate ?? 0) * 100).toFixed(1)}% rate`}
                />
                <StatCard
                    title="Rejected"
                    value={stats?.rejected ?? 0}
                    sub={`${((stats?.rejection_rate ?? 0) * 100).toFixed(1)}% rate`}
                />
            </div>

            {/* Charts row */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Outcome Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={220}>
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                                <Tooltip />
                                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]}>
                                    {chartData.map((entry, i) => (
                                        <rect key={i} fill={entry.fill} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Recent Activity</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {recentActivity.length === 0 ? (
                            <p className="text-sm text-muted-foreground py-10 text-center">
                                No decisions recorded yet.
                            </p>
                        ) : (
                            <ResponsiveContainer width="100%" height={220}>
                                <BarChart data={recentActivity}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                                    <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                                    <Tooltip />
                                    <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
