"use client";

import { AuthProvider } from "~/lib/auth";
import { AuthGuard } from "~/components/auth-guard";
import { DashboardShell } from "~/components/dashboard-shell";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider>
      <AuthGuard>
        <DashboardShell>{children}</DashboardShell>
      </AuthGuard>
    </AuthProvider>
  );
}
