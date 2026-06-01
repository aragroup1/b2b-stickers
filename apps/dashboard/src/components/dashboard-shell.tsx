"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "~/lib/auth";
import {
  LayoutDashboard,
  Tag,
  ShoppingCart,
  Package,
  Users,
  Settings,
  LogOut,
  Layers,
  Factory,
  Sparkles,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/generate", label: "Generate Hub", icon: Sparkles },
  { href: "/industries", label: "Industries", icon: Factory },
  { href: "/listings", label: "Listings", icon: Tag },
  { href: "/orders", label: "Orders", icon: ShoppingCart },
  { href: "/subscriptions", label: "Subscriptions", icon: Package },
  { href: "/customers", label: "Customers", icon: Users },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r bg-gray-50 flex flex-col">
        <div className="p-4 border-b">
          <h1 className="text-lg font-bold text-gray-900">B2B Stickers</h1>
          <p className="text-xs text-gray-500">Admin Dashboard</p>
        </div>

        <nav className="flex-1 p-3 space-y-0.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-gray-900 text-white"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-3 border-t">
          <button
            onClick={logout}
            className="flex items-center gap-3 px-3 py-2 w-full rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      <main className="flex-1 p-6 bg-white">{children}</main>
    </div>
  );
}
