import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2 } from "lucide-react";
import {
    useRules,
    useCreateRule,
    useUpdateRule,
    useDeleteRule,
} from "@/hooks/useRules";
import { Button } from "@/components/ui/button";
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
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import type { Rule, RuleAction, RuleOperator } from "@/types/api";

const OPERATORS: RuleOperator[] = [
    "eq", "ne", "gt", "gte", "lt", "lte",
    "contains", "not_contains", "in", "not_in",
];
const ACTIONS: RuleAction[] = ["APPROVE", "REVIEW", "REJECT"];

const ruleSchema = z
    .object({
        name: z.string().min(1, "Name is required"),
        expression: z.string().optional(),
        field: z.string().optional(),
        operator: z.enum(OPERATORS as [RuleOperator, ...RuleOperator[]]).optional(),
        value: z.string().optional(),
        action: z.enum(ACTIONS as [RuleAction, ...RuleAction[]]),
        priority: z.number().min(0),
        weight: z.number().int().min(0).max(1000),
        hard_stop: z.boolean(),
        description: z.string().optional(),
        category: z.string().optional(),
    })
    .refine(
        (d) => {
            const hasExpr = d.expression && d.expression.trim().length > 0;
            const hasLegacy = d.field && d.field.trim().length > 0 && d.operator && d.value && d.value.trim().length > 0;
            return hasExpr || hasLegacy;
        },
        { message: "Provide either an Expression or all three of Field, Operator, Value", path: ["expression"] }
    );

type RuleForm = z.infer<typeof ruleSchema>;

function actionBadge(action: RuleAction) {
    const variants: Record<RuleAction, "default" | "secondary" | "destructive"> =
        { APPROVE: "default", REVIEW: "secondary", REJECT: "destructive" };
    return <Badge variant={variants[action]}>{action}</Badge>;
}

function parseValue(raw: string, op?: RuleOperator) {
    if (!raw) return raw;
    if (op === "in" || op === "not_in") {
        return raw.split(",").map((s) => s.trim());
    }
    const n = Number(raw);
    return isNaN(n) ? raw : n;
}

export default function RulesPage() {
    const { data: rules = [], isLoading } = useRules();
    const createMutation = useCreateRule();
    const updateMutation = useUpdateRule();
    const deleteMutation = useDeleteRule();
    const { toast } = useToast();

    const [open, setOpen] = useState(false);
    const [editing, setEditing] = useState<Rule | null>(null);

    const form = useForm<RuleForm>({
        resolver: zodResolver(ruleSchema),
        defaultValues: {
            priority: 0,
            weight: 10,
            operator: "eq",
            action: "REVIEW",
            hard_stop: false,
        },
    });

    function openCreate() {
        setEditing(null);
        form.reset({ priority: 0, weight: 10, operator: "eq", action: "REVIEW", hard_stop: false });
        setOpen(true);
    }

    function openEdit(rule: Rule) {
        setEditing(rule);
        form.reset({
            name: rule.name,
            expression: rule.expression ?? "",
            field: rule.field ?? "",
            operator: rule.operator ?? "eq",
            value: rule.value != null
                ? Array.isArray(rule.value)
                    ? rule.value.join(", ")
                    : String(rule.value)
                : "",
            action: rule.action,
            priority: rule.priority,
            weight: rule.weight,
            hard_stop: rule.hard_stop,
            description: rule.description ?? "",
            category: rule.category ?? "",
        });
        setOpen(true);
    }

    async function onSubmit(data: RuleForm) {
        const hasExpr = data.expression && data.expression.trim().length > 0;
        const payload = {
            name: data.name,
            description: data.description || undefined,
            category: data.category || undefined,
            action: data.action,
            priority: data.priority,
            weight: data.weight,
            hard_stop: data.hard_stop,
            ...(hasExpr
                ? { expression: data.expression }
                : {
                    field: data.field,
                    operator: data.operator,
                    value: parseValue(data.value ?? "", data.operator),
                }),
        };
        try {
            if (editing) {
                await updateMutation.mutateAsync({ id: editing.id, body: payload });
                toast({ title: "Rule updated" });
            } else {
                await createMutation.mutateAsync(payload);
                toast({ title: "Rule created" });
            }
            setOpen(false);
        } catch (err: unknown) {
            const msg =
                (err as { message?: string })?.message ?? "Something went wrong";
            toast({ title: "Error", description: msg, variant: "destructive" });
        }
    }

    async function handleDelete(id: number) {
        if (!confirm("Delete this rule?")) return;
        try {
            await deleteMutation.mutateAsync(id);
            toast({ title: "Rule deleted" });
        } catch {
            toast({ title: "Error deleting rule", variant: "destructive" });
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Rules</h1>
                    <p className="text-muted-foreground">
                        Manage evaluation rules for the decision engine.
                    </p>
                </div>
                <Button onClick={openCreate}>
                    <Plus className="mr-2 h-4 w-4" /> New Rule
                </Button>
            </div>

            {isLoading ? (
                <p className="text-muted-foreground">Loadingâ€¦</p>
            ) : (
                <div className="rounded-md border">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Name</TableHead>
                                <TableHead>Condition</TableHead>
                                <TableHead>Action</TableHead>
                                <TableHead>Weight</TableHead>
                                <TableHead>Priority</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Hard Stop</TableHead>
                                <TableHead className="w-20" />
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {rules.length === 0 ? (
                                <TableRow>
                                    <TableCell
                                        colSpan={7}
                                        className="text-center text-muted-foreground py-10"
                                    >
                                        No rules yet. Create one to get started.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                rules.map((rule) => (
                                    <TableRow key={rule.id}>
                                        <TableCell className="font-medium">{rule.name}</TableCell>
                                        <TableCell className="font-mono text-xs max-w-[200px] truncate">
                                            {rule.expression
                                                ? <span title={rule.expression} className="italic text-muted-foreground">{rule.expression}</span>
                                                : `${rule.field} ${rule.operator} ${Array.isArray(rule.value) ? rule.value.join(", ") : String(rule.value)}`}
                                        </TableCell>
                                        <TableCell>{actionBadge(rule.action)}</TableCell>
                                        <TableCell>
                                            <span className="font-mono text-xs bg-muted px-1 py-0.5 rounded">
                                                {rule.weight}
                                            </span>
                                        </TableCell>
                                        <TableCell>{rule.priority}</TableCell>
                                        <TableCell>
                                            <Badge
                                                variant={rule.is_active ? "default" : "secondary"}
                                            >
                                                {rule.is_active ? "Active" : "Inactive"}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            {rule.hard_stop && (
                                                <Badge variant="destructive" className="text-[10px]">Hard Stop</Badge>
                                            )}
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex gap-1">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    onClick={() => openEdit(rule)}
                                                >
                                                    <Pencil className="h-4 w-4" />
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    onClick={() => handleDelete(rule.id)}
                                                >
                                                    <Trash2 className="h-4 w-4 text-destructive" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </div>
            )}

            {/* Create / Edit Dialog */}
            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="max-w-lg">
                    <DialogHeader>
                        <DialogTitle>{editing ? "Edit Rule" : "New Rule"}</DialogTitle>
                    </DialogHeader>
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                {/* Name */}
                                <FormField
                                    control={form.control}
                                    name="name"
                                    render={({ field }) => (
                                        <FormItem className="col-span-2">
                                            <FormLabel>Name</FormLabel>
                                            <FormControl>
                                                <Input placeholder="high_amount_check" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* DSL Expression */}
                                <FormField
                                    control={form.control}
                                    name="expression"
                                    render={({ field }) => (
                                        <FormItem className="col-span-2">
                                            <FormLabel>
                                                Expression{" "}
                                                <span className="text-muted-foreground font-normal text-xs">
                                                    (DSL â€” overrides Field/Operator/Value if set)
                                                </span>
                                            </FormLabel>
                                            <FormControl>
                                                <Textarea
                                                    placeholder="amount > 10000 and country in ['NG', 'KP']"
                                                    className="font-mono text-sm resize-none"
                                                    rows={2}
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* Legacy: Field */}
                                <FormField
                                    control={form.control}
                                    name="field"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Field</FormLabel>
                                            <FormControl>
                                                <Input placeholder="amount" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* Legacy: Operator */}
                                <FormField
                                    control={form.control}
                                    name="operator"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Operator</FormLabel>
                                            <Select
                                                onValueChange={field.onChange}
                                                defaultValue={field.value}
                                                value={field.value}
                                            >
                                                <FormControl>
                                                    <SelectTrigger>
                                                        <SelectValue />
                                                    </SelectTrigger>
                                                </FormControl>
                                                <SelectContent>
                                                    {OPERATORS.map((op) => (
                                                        <SelectItem key={op} value={op}>
                                                            {op}
                                                        </SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* Legacy: Value */}
                                <FormField
                                    control={form.control}
                                    name="value"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Value</FormLabel>
                                            <FormControl>
                                                <Input placeholder="1000" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* Action */}
                                <FormField
                                    control={form.control}
                                    name="action"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Action</FormLabel>
                                            <Select
                                                onValueChange={field.onChange}
                                                defaultValue={field.value}
                                                value={field.value}
                                            >
                                                <FormControl>
                                                    <SelectTrigger>
                                                        <SelectValue />
                                                    </SelectTrigger>
                                                </FormControl>
                                                <SelectContent>
                                                    {ACTIONS.map((a) => (
                                                        <SelectItem key={a} value={a}>
                                                            {a}
                                                        </SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* Weight */}
                                <FormField
                                    control={form.control}
                                    name="weight"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>
                                                Weight{" "}
                                                <span className="text-muted-foreground font-normal text-xs">(0â€“1000)</span>
                                            </FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="number"
                                                    min={0}
                                                    max={1000}
                                                    {...field}
                                                    onChange={(e) =>
                                                        field.onChange(
                                                            isNaN(e.target.valueAsNumber) ? 10 : e.target.valueAsNumber
                                                        )
                                                    }
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* Priority */}
                                <FormField
                                    control={form.control}
                                    name="priority"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Priority</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="number"
                                                    min={0}
                                                    {...field}
                                                    onChange={(e) =>
                                                        field.onChange(
                                                            isNaN(e.target.valueAsNumber)
                                                                ? 0
                                                                : e.target.valueAsNumber
                                                        )
                                                    }
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* Category */}
                                <FormField
                                    control={form.control}
                                    name="category"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Category</FormLabel>
                                            <FormControl>
                                                <Input placeholder="fraud" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* Description */}
                                <FormField
                                    control={form.control}
                                    name="description"
                                    render={({ field }) => (
                                        <FormItem className="col-span-2">
                                            <FormLabel>Description</FormLabel>
                                            <FormControl>
                                                <Input placeholder="Optional description" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                {/* Hard Stop */}
                                <FormField
                                    control={form.control}
                                    name="hard_stop"
                                    render={({ field }) => (
                                        <FormItem className="col-span-2 flex flex-row items-center gap-3">
                                            <FormControl>
                                                <input
                                                    type="checkbox"
                                                    title="Hard Stop"
                                                    checked={field.value}
                                                    onChange={(e) => field.onChange(e.target.checked)}
                                                    className="h-4 w-4 cursor-pointer"
                                                />
                                            </FormControl>
                                            <FormLabel className="!mt-0 cursor-pointer font-medium">
                                                Hard Stop{" "}
                                                <span className="text-muted-foreground font-normal text-xs">
                                                    (immediately REJECTs — skips remaining rules)
                                                </span>
                                            </FormLabel>
                                        </FormItem>
                                    )}
                                />
                            </div>
                            <DialogFooter>
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => setOpen(false)}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    type="submit"
                                    disabled={
                                        createMutation.isPending || updateMutation.isPending
                                    }
                                >
                                    {editing ? "Update" : "Create"}
                                </Button>
                            </DialogFooter>
                        </form>
                    </Form>
                </DialogContent>
            </Dialog>
        </div>
    );
}
