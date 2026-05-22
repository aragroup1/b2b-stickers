"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Subscription {
  id: number;
  variant_id: number;
  product_title: string;
  product_slug: string;
  recurring_amount: number;
  status: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  size_inches: number;
  pack_quantity: number;
}

interface Shipment {
  id: number;
  scheduled_for: string;
  status: string;
  tracking_number: string | null;
  product_title: string;
}

interface Customer {
  id: number;
  email: string;
  name: string | null;
  company_name: string | null;
}

export default function AccountPage() {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/customers/me", { credentials: "include" })
      .then((r) => {
        if (!r.ok) throw new Error("Not authenticated");
        return r.json();
      })
      .then((cust) => {
        setCustomer(cust);
        return Promise.all([
          fetch("/api/customers/me/subscriptions", { credentials: "include" }).then((r) =>
            r.json()
          ),
          fetch("/api/customers/me/shipments", { credentials: "include" }).then((r) =>
            r.json()
          ),
        ]);
      })
      .then(([subsData, shipsData]) => {
        setSubscriptions(subsData.subscriptions || []);
        setShipments(shipsData.shipments || []);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  const handleManage = async () => {
    if (!customer) return;
    const res = await fetch(`/api/subscriptions/portal?customer_id=${customer.id}`);
    const data = await res.json();
    if (data.portal_url) {
      window.location.href = data.portal_url;
    }
  };

  const handleLogin = () => {
    const email = prompt("Enter your email to receive a login link:");
    if (!email) return;
    fetch("/api/customers/auth/magic-link", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.link) {
          alert(`Development link: ${data.link}`);
        } else {
          alert("Login link sent to your email!");
        }
      });
  };

  if (loading) {
    return (
      <div className="py-16 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="mt-4 text-muted-foreground">Loading your account...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-md py-16 text-center px-4">
        <div className="rounded-xl border bg-card p-8 shadow-sm">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-muted">
            <svg className="h-6 w-6 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-2">My Account</h1>
          <p className="text-muted-foreground mb-6">Sign in to manage your subscriptions and view your order history.</p>
          <button
            onClick={handleLogin}
            className="w-full h-11 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
          >
            Sign In with Email
          </button>
          <p className="mt-4 text-xs text-muted-foreground">
            We will send you a secure magic link to access your account.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">My Account</h1>
        {customer && (
          <p className="text-muted-foreground mt-1">{customer.email}</p>
        )}
      </div>

      <div className="grid gap-8">
        {/* Subscriptions */}
        <section aria-labelledby="subscriptions-heading">
          <h2 id="subscriptions-heading" className="text-lg font-semibold mb-4">
            Active Subscriptions
          </h2>
          {subscriptions.length === 0 ? (
            <div className="rounded-xl border bg-card p-8 text-center">
              <p className="text-muted-foreground mb-4">No active subscriptions yet.</p>
              <Link
                href="/shop"
                className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-6 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                Browse Stickers
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {subscriptions.map((sub) => (
                <article
                  key={sub.id}
                  className="rounded-xl border bg-card p-5 shadow-sm"
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div>
                      <h3 className="font-semibold">
                        <Link href={`/product/${sub.product_slug}`} className="hover:text-primary transition-colors">
                          {sub.product_title}
                        </Link>
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {sub.size_inches}&quot; — Pack of {sub.pack_quantity}
                      </p>
                    </div>
                    <span
                      className={`inline-flex self-start rounded-full px-3 py-1 text-xs font-medium ${
                        sub.status === "active"
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {sub.status}
                    </span>
                  </div>
                  <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-4 border-t">
                    <p className="text-sm text-muted-foreground">
                      Next renewal: {new Date(sub.current_period_end).toLocaleDateString("en-GB")}
                    </p>
                    <p className="font-semibold">£{Number(sub.recurring_amount).toFixed(2)}/mo</p>
                  </div>
                </article>
              ))}
              <button
                onClick={handleManage}
                className="w-full sm:w-auto h-10 rounded-lg border px-4 text-sm font-medium hover:bg-accent transition-colors"
              >
                Manage payment / cancel subscription
              </button>
            </div>
          )}
        </section>

        {/* Shipments */}
        <section aria-labelledby="shipments-heading">
          <h2 id="shipments-heading" className="text-lg font-semibold mb-4">
            Recent Shipments
          </h2>
          {shipments.length === 0 ? (
            <div className="rounded-xl border bg-card p-8 text-center">
              <p className="text-muted-foreground">No shipments yet.</p>
            </div>
          ) : (
            <div className="rounded-xl border bg-card overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">Product</th>
                    <th className="px-4 py-3 text-left font-medium">Scheduled</th>
                    <th className="px-4 py-3 text-left font-medium">Status</th>
                    <th className="px-4 py-3 text-left font-medium">Tracking</th>
                  </tr>
                </thead>
                <tbody>
                  {shipments.map((s) => (
                    <tr key={s.id} className="border-t">
                      <td className="px-4 py-3">{s.product_title}</td>
                      <td className="px-4 py-3">
                        {new Date(s.scheduled_for).toLocaleDateString("en-GB")}
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex rounded-full bg-muted px-2 py-0.5 text-xs font-medium capitalize">
                          {s.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {s.tracking_number ? (
                          <span className="font-mono text-xs">{s.tracking_number}</span>
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
