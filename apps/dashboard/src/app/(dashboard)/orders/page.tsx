"use client";

import { useEffect, useState } from "react";

interface Order {
  id: number;
  source: string;
  external_order_id: string | null;
  customer_email: string | null;
  product_title: string | null;
  order_value: number | null;
  fulfillment_status: string;
  created_at: string;
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);

  useEffect(() => {
    fetch("/api/orders")
      .then((r) => r.json())
      .then((d) => setOrders(d.orders || []));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Orders</h1>
      <div className="rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left">ID</th>
              <th className="px-4 py-3 text-left">Source</th>
              <th className="px-4 py-3 text-left">Customer</th>
              <th className="px-4 py-3 text-left">Product</th>
              <th className="px-4 py-3 text-left">Value</th>
              <th className="px-4 py-3 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id} className="border-t">
                <td className="px-4 py-3">{o.id}</td>
                <td className="px-4 py-3 capitalize">{o.source.replace("_", " ")}</td>
                <td className="px-4 py-3">{o.customer_email ?? "—"}</td>
                <td className="px-4 py-3">{o.product_title ?? "—"}</td>
                <td className="px-4 py-3">{o.order_value ? `£${o.order_value}` : "—"}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex rounded-full bg-muted px-2 py-0.5 text-xs font-medium">
                    {o.fulfillment_status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
