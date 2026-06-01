"use client";

import { useEffect, useState } from "react";
import { getAuthHeaders } from "~/lib/auth";

interface Industry {
  id: number;
  slug: string;
  name: string;
  parent_id: number | null;
}

export default function IndustriesPage() {
  const [industries, setIndustries] = useState<Industry[]>([]);

  useEffect(() => {
    fetch("/api/industries", { headers: getAuthHeaders() })
      .then((r) => r.json())
      .then((d) => setIndustries(d.industries || []));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Industries</h1>
      <div className="rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Slug</th>
              <th className="px-4 py-3 text-left">Parent ID</th>
            </tr>
          </thead>
          <tbody>
            {industries.map((ind) => (
              <tr key={ind.id} className="border-t">
                <td className="px-4 py-3">{ind.name}</td>
                <td className="px-4 py-3 text-muted-foreground">{ind.slug}</td>
                <td className="px-4 py-3 text-muted-foreground">{ind.parent_id ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
