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

const ruleSchema = z.object({
    name: z.string().min(1, "Name is required"),
    field: z.string().min(1, "Field is required"),
    operator: z.enum(OPERATORS as [RuleOperator, ...RuleOperator[]]),
    value: z.string().min(1, "Value is required"),
    action: z.enum(ACTIONS as [RuleAction, ...RuleAction[]]),
    priority: z.number().int().min(0),
    description: z.string().optional(),
    category: z.string().optional(),
});

type RuleForm = z.infer<typeof ruleSchema>;

function actionBadge(action: RuleAction) {
    const variants: Record<RuleAction, "default" | "secondary" | "destructive"> =
        { APPROVE: "default", REVIEW: "secondary", REJECT: "destructive" };
    return <Badge variant={variants[action]}>{action}</Badge>;
}

function parseValue(raw: string, op: RuleOperator) {
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
            operator: "eq",
            action: "REVIEW",
        },
    });

    function openCreate() {
        setEditing(null);
        form.reset({ priority: 0, operator: "eq", action: "REVIEW" });
        setOpen(true);
    }

    function openEdit(rule: Rule) {
        setEditing(rule);
        form.reset({
            name: rule.name,
            field: rule.field,
            operator: rule.operator,
            value: Array.isArray(rule.value)
                ? rule.value.join(", ")
                : String(rule.value),
            action: rule.action,
            priority: rule.priority,
            description: rule.description ?? "",
            category: rule.category ?? "",
        });
        setOpen(true);
    }

    async function onSubmit(data: RuleForm) {
        const payload = {
            ...data,
            value: parseValue(data.value, data.operator),
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
                <p className="text-muted-foreground">Loading…</p>
            ) : (
                <div className="rounded-md border">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Name</TableHead>
                                <TableHead>Field</TableHead>
                                <TableHead>Operator</TableHead>
                                <TableHead>Value</TableHead>
                                <TableHead>Action</TableHead>
                                <TableHead>Priority</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="w-20" />
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {rules.length === 0 ? (
                                <TableRow>
                                    <TableCell
                                        colSpan={8}
                                        className="text-center text-muted-foreground py-10"
                                    >
                                        No rules yet. Create one to get started.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                rules.map((rule) => (
                                    <TableRow key={rule.id}>
                                        <TableCell className="font-medium">{rule.name}</TableCell>
                                        <TableCell className="font-mono text-xs">
                                            {rule.field}
                                        </TableCell>
                                        <TableCell>
                                            <code className="text-xs bg-muted px-1 py-0.5 rounded">
                                                {rule.operator}
                                            </code>
                                        </TableCell>
                                        <TableCell className="max-w-[120px] truncate text-sm">
                                            {Array.isArray(rule.value)
                                                ? rule.value.join(", ")
                                                : String(rule.value)}
                                        </TableCell>
                                        <TableCell>{actionBadge(rule.action)}</TableCell>
                                        <TableCell>{rule.priority}</TableCell>
                                        <TableCell>
                                            <Badge
                                                variant={rule.is_active ? "default" : "secondary"}
                                            >
                                                {rule.is_active ? "Active" : "Inactive"}
                                            </Badge>
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
