"use client";

import { useEffect, useState } from "react";

interface DashboardData {
  products: { total: number; approved: number; active: number };
  trends: { total: number };
  subscriptions: { active: number; mrr: number };
  orders: { this_month: number; revenue_this_month: number };
}

export default function DashboardHome() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/analytics/dashboard")
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;
  if (!data) return <div className="p-8">Failed to load</div>;

  const cards = [
    { label: "Total Products", value: data.products.total },
    { label: "Approved", value: data.products.approved },
    { label: "Active", value: data.products.active },
    { label: "Trends", value: data.trends.total },
    { label: "Active Subs", value: data.subscriptions.active },
    { label: "MRR", value: `£${data.subscriptions.mrr.toFixed(2)}` },
    { label: "Orders This Month", value: data.orders.this_month },
    { label: "Revenue This Month", value: `£${data.orders.revenue_this_month.toFixed(2)}` },
  ];

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => (
          <div key={card.label} className="rounded-lg border bg-card p-6 shadow-sm">
            <p className="text-sm text-muted-foreground">{card.label}</p>
            <p className="text-2xl font-bold mt-1">{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
