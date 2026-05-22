"use client";

import { useEffect, useState } from "react";

interface Customer {
  id: number;
  email: string;
  name: string | null;
  company_name: string | null;
  created_at: string;
}

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);

  useEffect(() => {
    fetch("/api/customers")
      .then((r) => r.json())
      .then((d) => setCustomers(d.customers || []));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Customers</h1>
      <div className="rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left">Email</th>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Company</th>
              <th className="px-4 py-3 text-left">Joined</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((c) => (
              <tr key={c.id} className="border-t">
                <td className="px-4 py-3">{c.email}</td>
                <td className="px-4 py-3">{c.name ?? "—"}</td>
                <td className="px-4 py-3">{c.company_name ?? "—"}</td>
                <td className="px-4 py-3">{new Date(c.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
