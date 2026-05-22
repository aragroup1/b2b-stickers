"use client";

import { useEffect, useState } from "react";

interface Listing {
  id: number;
  product_title: string;
  platform: string;
  status: string;
  platform_url: string | null;
  error_message: string | null;
}

export default function ListingsPage() {
  const [listings, setListings] = useState<Listing[]>([]);

  useEffect(() => {
    fetch("/api/listings")
      .then((r) => r.json())
      .then((d) => setListings(d.listings || []));
  }, []);

  const statusColor = (status: string) => {
    switch (status) {
      case "live": return "bg-green-100 text-green-800";
      case "queued": return "bg-yellow-100 text-yellow-800";
      case "failed": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Listings</h1>
      <div className="rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left">Product</th>
              <th className="px-4 py-3 text-left">Platform</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Error</th>
            </tr>
          </thead>
          <tbody>
            {listings.map((l) => (
              <tr key={l.id} className="border-t">
                <td className="px-4 py-3">{l.product_title}</td>
                <td className="px-4 py-3 capitalize">{l.platform.replace("_", " ")}</td>
                <td className="px-4 py-3">
                  <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${statusColor(l.status)}`}>
                    {l.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-red-600 text-xs">{l.error_message ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
