import { useState } from "react";
import { useDecisions } from "@/hooks/useDecisions";
import { decisionsApi } from "@/api/decisions";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import type { Decision, RuleAction } from "@/types/api";

function outcomeBadge(outcome: RuleAction) {
    const variants: Record<RuleAction, "default" | "secondary" | "destructive"> =
        { APPROVE: "default", REVIEW: "secondary", REJECT: "destructive" };
    return <Badge variant={variants[outcome]}>{outcome}</Badge>;
}

export default function DecisionsPage() {
    const { data: decisions = [], isLoading } = useDecisions();
    const [selected, setSelected] = useState<Decision | null>(null);

    async function openDetail(id: number) {
        const detail = await decisionsApi.get(id);
        setSelected(detail);
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Decisions</h1>
                <p className="text-muted-foreground">
                    History of all evaluated decisions.
                </p>
            </div>

            {isLoading ? (
                <p className="text-muted-foreground">Loading…</p>
            ) : (
                <div className="rounded-md border">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>ID</TableHead>
                                <TableHead>Reference</TableHead>
                                <TableHead>Category</TableHead>
                                <TableHead>Outcome</TableHead>
                                <TableHead>Rules Evaluated</TableHead>
                                <TableHead>Triggered</TableHead>
                                <TableHead>Created</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {decisions.length === 0 ? (
                                <TableRow>
                                    <TableCell
                                        colSpan={7}
                                        className="text-center text-muted-foreground py-10"
                                    >
                                        No decisions yet. Use Evaluate to create one.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                decisions.map((d) => (
                                    <TableRow
                                        key={d.id}
                                        className="cursor-pointer hover:bg-muted/50"
                                        onClick={() => openDetail(d.id)}
                                    >
                                        <TableCell className="font-mono text-xs">{d.id}</TableCell>
                                        <TableCell className="font-mono text-xs max-w-[120px] truncate">
                                            {d.reference_id ?? "—"}
                                        </TableCell>
                                        <TableCell>{d.category ?? "—"}</TableCell>
                                        <TableCell>{outcomeBadge(d.outcome)}</TableCell>
                                        <TableCell>{d.rules_evaluated}</TableCell>
                                        <TableCell>{d.triggered_rules.length}</TableCell>
                                        <TableCell className="text-xs text-muted-foreground">
                                            {new Date(d.created_at).toLocaleString()}
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </div>
            )}

            {/* Detail Sheet */}
            <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
                <SheetContent className="w-[480px] overflow-y-auto">
                    <SheetHeader>
                        <SheetTitle>Decision #{selected?.id}</SheetTitle>
                    </SheetHeader>
                    {selected && (
                        <div className="mt-4 space-y-4 text-sm">
                            <div className="flex gap-2">
                                {outcomeBadge(selected.outcome)}
                                {selected.category && (
                                    <Badge variant="outline">{selected.category}</Badge>
                                )}
                            </div>
                            <Separator />
                            <div>
                                <p className="font-medium mb-1">Reference</p>
                                <p className="text-muted-foreground font-mono text-xs">
                                    {selected.reference_id ?? "—"}
                                </p>
                            </div>
                            <div>
                                <p className="font-medium mb-1">Payload</p>
                                <pre className="bg-muted rounded p-3 text-xs overflow-auto">
                                    {JSON.stringify(selected.payload, null, 2)}
                                </pre>
                            </div>
                            <div>
                                <p className="font-medium mb-1">
                                    Triggered Rules ({selected.triggered_rules.length})
                                </p>
                                {selected.triggered_rules.length === 0 ? (
                                    <p className="text-muted-foreground text-xs">None</p>
                                ) : (
                                    <ul className="space-y-2">
                                        {selected.triggered_rules.map((tr, i) => (
                                            <li key={i} className="bg-muted rounded p-2 text-xs">
                                                <span className="font-medium">{tr.rule_name}</span>{" "}
                                                → {tr.action}
                                                <br />
                                                <span className="text-muted-foreground">
                                                    {tr.field} {tr.operator} {String(tr.value)} (got:{" "}
                                                    {String(tr.actual_value)})
                                                </span>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                            <div>
                                <p className="font-medium mb-1">Reasons</p>
                                {selected.reasons.length === 0 ? (
                                    <p className="text-muted-foreground text-xs">None</p>
                                ) : (
                                    <ul className="list-disc list-inside space-y-1 text-xs text-muted-foreground">
                                        {selected.reasons.map((r, i) => (
                                            <li key={i}>{r}</li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                            <p className="text-xs text-muted-foreground">
                                Evaluated {selected.rules_evaluated} rule
                                {selected.rules_evaluated !== 1 ? "s" : ""} ·{" "}
                                {new Date(selected.created_at).toLocaleString()}
                            </p>
                        </div>
                    )}
                </SheetContent>
            </Sheet>
        </div>
    );
}
