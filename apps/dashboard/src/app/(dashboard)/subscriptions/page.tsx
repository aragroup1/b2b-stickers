"use client";

import { useEffect, useState } from "react";

interface Subscription {
  id: number;
  customer_id: number;
  variant_id: number;
  recurring_amount: number;
  discount_percent: number;
  status: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

export default function SubscriptionsPage() {
  const [subs, setSubs] = useState<Subscription[]>([]);

  useEffect(() => {
    fetch("/api/subscriptions")
      .then((r) => r.json())
      .then((d) => setSubs(d.subscriptions || []));
  }, []);

  const activeMrr = subs
    .filter((s) => s.status === "active")
    .reduce((sum, s) => sum + Number(s.recurring_amount), 0);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Subscriptions</h1>
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">Active Subs</p>
          <p className="text-2xl font-bold">{subs.filter((s) => s.status === "active").length}</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">MRR</p>
          <p className="text-2xl font-bold">£{activeMrr.toFixed(2)}</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">Churned</p>
          <p className="text-2xl font-bold">{subs.filter((s) => s.status === "canceled").length}</p>
        </div>
      </div>
      <div className="rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left">ID</th>
              <th className="px-4 py-3 text-left">Variant</th>
              <th className="px-4 py-3 text-left">Amount</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Renews</th>
            </tr>
          </thead>
          <tbody>
            {subs.map((s) => (
              <tr key={s.id} className="border-t">
                <td className="px-4 py-3">{s.id}</td>
                <td className="px-4 py-3">{s.variant_id}</td>
                <td className="px-4 py-3">£{Number(s.recurring_amount).toFixed(2)}</td>
                <td className="px-4 py-3">
                  <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                    s.status === "active" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                  }`}>
                    {s.status}
                  </span>
                </td>
                <td className="px-4 py-3">{new Date(s.current_period_end).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
