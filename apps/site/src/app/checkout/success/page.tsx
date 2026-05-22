"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

function CheckoutSuccessContent() {
  const searchParams = useSearchParams();
  const [verifying, setVerifying] = useState(true);
  const [type, setType] = useState<"subscription" | "onetime" | "sample">("subscription");

  useEffect(() => {
    const sessionId = searchParams.get("session_id");
    const purchaseType = searchParams.get("type");
    if (purchaseType) {
      setType(purchaseType as "subscription" | "onetime" | "sample");
    }
    if (sessionId) {
      setTimeout(() => setVerifying(false), 1500);
    } else {
      setVerifying(false);
    }
  }, [searchParams]);

  const titles = {
    subscription: "Welcome aboard!",
    onetime: "Order confirmed!",
    sample: "Sample order confirmed!",
  };

  const messages = {
    subscription:
      "Your subscription is now active. You'll receive your first shipment soon. Manage your subscription anytime from your account.",
    onetime:
      "Your order has been confirmed. We'll dispatch your stickers within 1-2 business days. You'll receive a tracking email once shipped.",
    sample:
      "Your sample pack order is confirmed. We'll send your samples within 1-2 business days so you can see the quality before subscribing.",
  };

  if (verifying) {
    return (
      <div className="flex flex-col items-center py-24">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="mt-4 text-muted-foreground">Confirming your order...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md px-4 py-16 text-center">
      <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
        <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 className="text-3xl font-bold mb-4">{titles[type]}</h1>
      <p className="text-muted-foreground mb-8">{messages[type]}</p>
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          href="/account"
          className="inline-flex h-11 items-center justify-center rounded-lg bg-primary px-8 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Go to Account
        </Link>
        <Link
          href="/shop"
          className="inline-flex h-11 items-center justify-center rounded-lg border px-8 text-sm font-semibold hover:bg-accent transition-colors"
        >
          Continue Shopping
        </Link>
      </div>
    </div>
  );
}

export default function CheckoutSuccessPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col items-center py-24">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="mt-4 text-muted-foreground">Confirming your order...</p>
      </div>
    }>
      <CheckoutSuccessContent />
    </Suspense>
  );
}
