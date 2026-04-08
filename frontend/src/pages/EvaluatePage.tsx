import { useState } from "react";
import { useEvaluate } from "@/hooks/useDecisions";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import type { Decision, RuleAction } from "@/types/api";

const EXAMPLE = JSON.stringify(
    {
        amount: 15000,
        country: "NG",
        user_age: 17,
        email_domain: "tempmail.com",
    },
    null,
    2
);

function outcomeBadge(outcome: RuleAction) {
    const map: Record<RuleAction, string> = {
        APPROVE: "bg-green-100 text-green-800 border-green-200",
        REVIEW: "bg-yellow-100 text-yellow-800 border-yellow-200",
        REJECT: "bg-red-100 text-red-800 border-red-200",
    };
    return (
        <span
            className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold ${map[outcome]}`}
        >
            {outcome}
        </span>
    );
}

export default function EvaluatePage() {
    const evaluate = useEvaluate();
    const { toast } = useToast();

    const [payload, setPayload] = useState(EXAMPLE);
    const [referenceId, setReferenceId] = useState("");
    const [category, setCategory] = useState("");
    const [result, setResult] = useState<Decision | null>(null);
    const [parseError, setParseError] = useState("");

    async function handleEvaluate() {
        setParseError("");
        let parsed: Record<string, unknown>;
        try {
            parsed = JSON.parse(payload);
        } catch {
            setParseError("Invalid JSON – please fix the payload.");
            return;
        }
        try {
            const res = await evaluate.mutateAsync({
                payload: parsed,
                reference_id: referenceId || null,
                category: category || null,
            });
            setResult(res);
        } catch (err: unknown) {
            const msg =
                (err as { message?: string })?.message ?? "Evaluation failed";
            toast({ title: "Error", description: msg, variant: "destructive" });
        }
    }

    return (
        <div className="space-y-6 max-w-2xl">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Evaluate</h1>
                <p className="text-muted-foreground">
                    Submit a JSON payload to run it through the decision engine.
                </p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Payload</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <Label htmlFor="payload">JSON Payload</Label>
                        <Textarea
                            id="payload"
                            rows={10}
                            className="font-mono text-sm mt-1"
                            value={payload}
                            onChange={(e) => setPayload(e.target.value)}
                        />
                        {parseError && (
                            <p className="text-xs text-destructive mt-1">{parseError}</p>
                        )}
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="ref">Reference ID (optional)</Label>
                            <Input
                                id="ref"
                                placeholder="txn-12345"
                                value={referenceId}
                                onChange={(e) => setReferenceId(e.target.value)}
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <Label htmlFor="cat">Category (optional)</Label>
                            <Input
                                id="cat"
                                placeholder="fraud"
                                value={category}
                                onChange={(e) => setCategory(e.target.value)}
                                className="mt-1"
                            />
                        </div>
                    </div>
                    <Button
                        onClick={handleEvaluate}
                        disabled={evaluate.isPending}
                        className="w-full"
                    >
                        {evaluate.isPending ? "Evaluating…" : "Run Evaluation"}
                    </Button>
                </CardContent>
            </Card>

            {result && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base flex items-center gap-3">
                            Result {outcomeBadge(result.outcome)}
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4 text-sm">
                        <div className="grid grid-cols-2 gap-2 text-muted-foreground text-xs">
                            <span>Decision ID: <strong className="text-foreground">{result.id}</strong></span>
                            <span>Rules evaluated: <strong className="text-foreground">{result.rules_evaluated}</strong></span>
                            <span>Triggered: <strong className="text-foreground">{result.triggered_rules.length}</strong></span>
                            <span>
                                Reference:{" "}
                                <strong className="text-foreground font-mono">
                                    {result.reference_id ?? "—"}
                                </strong>
                            </span>
                        </div>
                        <Separator />
                        {result.triggered_rules.length > 0 && (
                            <div>
                                <p className="font-medium mb-2">Triggered Rules</p>
                                <ul className="space-y-2">
                                    {result.triggered_rules.map((tr, i) => (
                                        <li key={i} className="bg-muted rounded p-3 text-xs">
                                            <div className="font-medium">
                                                {tr.rule_name}{" "}
                                                <Badge variant="outline" className="ml-1 text-[10px]">
                                                    {tr.action}
                                                </Badge>
                                            </div>
                                            <div className="text-muted-foreground mt-0.5">
                                                {tr.field} <code>{tr.operator}</code> {String(tr.value)}{" "}
                                                · got <code>{String(tr.actual_value)}</code>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        {result.reasons.length > 0 && (
                            <div>
                                <p className="font-medium mb-1">Reasons</p>
                                <ul className="list-disc list-inside space-y-0.5 text-xs text-muted-foreground">
                                    {result.reasons.map((r, i) => (
                                        <li key={i}>{r}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
