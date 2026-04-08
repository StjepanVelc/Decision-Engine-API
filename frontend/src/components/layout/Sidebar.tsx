import { NavLink } from "react-router-dom";
import { LayoutDashboard, ShieldCheck, ListChecks, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
    { to: "/", label: "Dashboard", icon: LayoutDashboard },
    { to: "/rules", label: "Rules", icon: ShieldCheck },
    { to: "/decisions", label: "Decisions", icon: ListChecks },
    { to: "/evaluate", label: "Evaluate", icon: Zap },
];

export default function Sidebar() {
    return (
        <aside className="flex flex-col w-60 shrink-0 border-r bg-card h-screen sticky top-0">
            <div className="px-6 py-5 border-b">
                <span className="font-semibold text-lg tracking-tight">
                    Decision Engine
                </span>
            </div>
            <nav className="flex-1 py-4 px-3 space-y-1">
                {links.map(({ to, label, icon: Icon }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={to === "/"}
                        className={({ isActive }) =>
                            cn(
                                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-primary text-primary-foreground"
                                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                            )
                        }
                    >
                        <Icon className="h-4 w-4" />
                        {label}
                    </NavLink>
                ))}
            </nav>
            <div className="px-6 py-4 border-t text-xs text-muted-foreground">
                v1.0 · Portfolio Project
            </div>
        </aside>
    );
}
