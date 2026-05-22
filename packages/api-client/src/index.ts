import type { Product, StickerVariant, Subscription, Customer, Trend } from "@b2b-stickers/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  catalog: {
    list: (params?: Record<string, string>) =>
      fetchJson<{ products: Product[] }>(`/catalog/products?${new URLSearchParams(params)}`),
    detail: (slug: string) => fetchJson<Product>(`/catalog/products/${slug}`),
  },
  subscriptions: {
    checkout: (body: { variant_id: number; email: string; shipping_address: unknown }) =>
      fetchJson<{ checkout_url: string }>("/subscriptions/checkout", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    portal: () => fetchJson<{ portal_url: string }>("/subscriptions/portal"),
  },
  customers: {
    me: () => fetchJson<Customer>("/customers/me"),
    mySubscriptions: () => fetchJson<{ subscriptions: Subscription[] }>("/customers/me/subscriptions"),
    myShipments: () => fetchJson<{ shipments: unknown[] }>("/customers/me/shipments"),
  },
  trends: {
    list: () => fetchJson<{ trends: Trend[] }>("/trends"),
  },
};
