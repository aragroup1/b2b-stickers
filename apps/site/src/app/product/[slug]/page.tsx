"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { JsonLd } from "~/components/JsonLd";
import { ProductSchema, BreadcrumbSchema } from "~/lib/schema";

interface Variant {
  id: number;
  size_inches: number;
  pack_quantity: number;
  retail_price: number;
  retail_price_vat: number;
  recurring_price: number;
  recurring_price_vat: number;
  sku: string;
}

interface Product {
  id: number;
  slug: string;
  title: string;
  description: string | null;
  image_url: string;
  industry_name: string | null;
  tags: string[];
  prompt: string | null;
  model_used: string | null;
  style: string | null;
  quality_score: number | null;
  variants: Variant[];
}

interface ShippingAddress {
  name: string;
  line1: string;
  line2?: string;
  city: string;
  state?: string;
  postal_code: string;
  country: string;
}

export default function ProductDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [product, setProduct] = useState<Product | null>(null);
  const [selectedVariant, setSelectedVariant] = useState<Variant | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCheckout, setShowCheckout] = useState(false);
  const [checkoutMode, setCheckoutMode] = useState<"subscribe" | "onetime">("subscribe");
  const [email, setEmail] = useState("");
  const [shipping, setShipping] = useState<ShippingAddress>({
    name: "",
    line1: "",
    city: "",
    postal_code: "",
    country: "GB",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`/api/catalog/products/${slug}`)
      .then((r) => r.json())
      .then((d) => {
        setProduct(d);
        if (d.variants?.length) setSelectedVariant(d.variants[0]);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [slug]);

  const handleCheckout = async () => {
    if (!selectedVariant) return;
    if (!email.includes("@")) {
      setError("Please enter a valid email address");
      return;
    }
    if (!shipping.line1 || !shipping.city || !shipping.postal_code) {
      setError("Please fill in your shipping address");
      return;
    }

    setError("");
    setSubmitting(true);

    const endpoint =
      checkoutMode === "subscribe"
        ? "/api/subscriptions/checkout"
        : "/api/onetime/checkout";
    const body =
      checkoutMode === "subscribe"
        ? {
            variant_id: selectedVariant.id,
            email,
            shipping_address: shipping,
          }
        : {
            variant_id: selectedVariant.id,
            email,
            quantity: 1,
            shipping_address: shipping,
          };

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        setError("Checkout failed. Please try again.");
        setSubmitting(false);
      }
    } catch {
      setError("Checkout failed. Please try again.");
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="py-16 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="mt-4 text-muted-foreground">Loading product...</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 text-center">
        <h1 className="text-2xl font-bold mb-4">Product Not Found</h1>
        <p className="text-muted-foreground mb-6">
          The product you are looking for does not exist or has been removed.
        </p>
        <Link
          href="/shop"
          className="inline-flex h-11 items-center justify-center rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          Browse All Products
        </Link>
      </div>
    );
  }

  const sizes = Array.from(new Set(product.variants.map((v) => v.size_inches))).sort((a, b) => a - b);
  const packs = Array.from(new Set(product.variants.map((v) => v.pack_quantity))).sort((a, b) => a - b);

  const schemaData = ProductSchema({
    title: product.title,
    description: product.description || `${product.title} - Premium custom stickers for UK small businesses`,
    image: product.image_url,
    slug: product.slug,
    price: selectedVariant ? selectedVariant.recurring_price_vat : product.variants[0]?.recurring_price_vat || 0,
    currency: "GBP",
    availability: "https://schema.org/InStock",
    sku: selectedVariant?.sku || product.variants[0]?.sku || "",
    category: product.industry_name || "Stickers & Labels",
  });

  return (
    <>
      <JsonLd data={schemaData} />
      <JsonLd
        data={BreadcrumbSchema([
          { name: "Home", url: "https://b2b-stickers.co.uk/" },
          { name: "Shop", url: "https://b2b-stickers.co.uk/shop" },
          { name: product.title, url: `https://b2b-stickers.co.uk/product/${product.slug}` },
        ])}
      />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex items-center gap-2 text-sm text-muted-foreground flex-wrap">
            <li>
              <Link href="/" className="hover:text-foreground transition-colors">
                Home
              </Link>
            </li>
            <li aria-hidden="true">/</li>
            <li>
              <Link href="/shop" className="hover:text-foreground transition-colors">
                Shop
              </Link>
            </li>
            <li aria-hidden="true">/</li>
            <li aria-current="page" className="text-foreground font-medium truncate max-w-[200px]">
              {product.title}
            </li>
          </ol>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
          {/* Product Image */}
          <div className="space-y-4">
            <div className="aspect-square rounded-xl border bg-muted overflow-hidden">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={`${product.title} - custom sticker design preview`}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground">
                  <svg className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1}
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>
              )}
            </div>
            {product.tags && product.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {product.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Product Details */}
          <div>
            {product.industry_name && (
              <p className="text-sm font-medium text-primary uppercase tracking-wide">
                {product.industry_name}
              </p>
            )}
            <h1 className="text-3xl font-bold tracking-tight mt-2">{product.title}</h1>
            {product.description ? (
              <p className="mt-4 text-muted-foreground leading-relaxed">{product.description}</p>
            ) : (
              <p className="mt-4 text-muted-foreground leading-relaxed">
                Premium custom stickers printed on high-quality vinyl. Weatherproof, UV-resistant,
                and perfect for product packaging and branding. Designed specifically for UK small businesses.
              </p>
            )}

            {/* Features */}
            <div className="mt-6 rounded-lg border bg-muted/30 p-4">
              <h2 className="text-sm font-semibold mb-3">Product Features</h2>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <svg className="h-5 w-5 text-green-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Premium vinyl with weatherproof coating
                </li>
                <li className="flex items-start gap-2">
                  <svg className="h-5 w-5 text-green-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  UV-resistant for indoor and outdoor use
                </li>
                <li className="flex items-start gap-2">
                  <svg className="h-5 w-5 text-green-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Easy peel-and-stick application
                </li>
                <li className="flex items-start gap-2">
                  <svg className="h-5 w-5 text-green-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  UK printed and shipped
                </li>
              </ul>
            </div>

            {/* Variant Selection */}
            <div className="mt-6 space-y-4">
              <div>
                <label className="text-sm font-semibold">Size</label>
                <div className="mt-2 flex flex-wrap gap-2" role="radiogroup" aria-label="Select size">
                  {sizes.map((s) => {
                    const isSelected = selectedVariant?.size_inches === s;
                    return (
                      <button
                        key={s}
                        role="radio"
                        aria-checked={isSelected}
                        className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                          isSelected
                            ? "bg-primary text-primary-foreground border-primary"
                            : "hover:bg-accent"
                        }`}
                        onClick={() => {
                          const v = product.variants.find((x) => x.size_inches === s);
                          if (v) setSelectedVariant(v);
                        }}
                      >
                        {s}&quot;
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold">Pack Size</label>
                <div className="mt-2 flex flex-wrap gap-2" role="radiogroup" aria-label="Select pack size">
                  {packs.map((p) => {
                    const isSelected = selectedVariant?.pack_quantity === p;
                    const hasVariant = product.variants.some(
                      (v) => v.pack_quantity === p && v.size_inches === selectedVariant?.size_inches
                    );
                    return (
                      <button
                        key={p}
                        role="radio"
                        aria-checked={isSelected}
                        disabled={!hasVariant}
                        className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all ${
                          isSelected
                            ? "bg-primary text-primary-foreground border-primary"
                            : hasVariant
                            ? "hover:bg-accent"
                            : "opacity-40 cursor-not-allowed"
                        }`}
                        onClick={() => {
                          const v = product.variants.find(
                            (x) => x.pack_quantity === p && x.size_inches === selectedVariant?.size_inches
                          );
                          if (v) setSelectedVariant(v);
                        }}
                      >
                        {p} stickers
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Pricing & CTA */}
            {selectedVariant && (
              <div className="mt-8 rounded-xl border bg-card p-6">
                <div className="flex items-baseline gap-3">
                  <span className="text-3xl font-bold">
                    £{selectedVariant.recurring_price_vat.toFixed(2)}
                  </span>
                  <span className="text-lg text-muted-foreground line-through">
                    £{selectedVariant.retail_price_vat.toFixed(2)}
                  </span>
                  <span className="ml-auto text-sm font-medium text-green-700 bg-green-100 rounded-full px-3 py-1">
                    Save 10%
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  per month inc. VAT — ships monthly, cancel anytime
                </p>
                <p className="text-xs text-muted-foreground mt-1">SKU: {selectedVariant.sku}</p>

                {!showCheckout ? (
                  <div className="mt-4 space-y-3">
                    <button
                      onClick={() => {
                        setCheckoutMode("subscribe");
                        setShowCheckout(true);
                      }}
                      className="w-full h-12 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors shadow-sm"
                    >
                      Subscribe & Save 10%
                    </button>
                    <button
                      onClick={() => {
                        setCheckoutMode("onetime");
                        setShowCheckout(true);
                      }}
                      className="w-full h-12 rounded-lg border font-semibold hover:bg-accent transition-colors"
                    >
                      Buy Once — £{selectedVariant.retail_price_vat.toFixed(2)}
                    </button>
                  </div>
                ) : (
                  <div className="mt-4 space-y-3">
                    <h3 className="font-semibold">
                      {checkoutMode === "subscribe" ? "Subscribe" : "Buy Once"} —{" "}
                      {selectedVariant.size_inches}" Pack of {selectedVariant.pack_quantity}
                    </h3>

                    {error && (
                      <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                        {error}
                      </div>
                    )}

                    <input
                      type="email"
                      placeholder="Email address"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full rounded-lg border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      required
                    />

                    <input
                      type="text"
                      placeholder="Full name"
                      value={shipping.name}
                      onChange={(e) => setShipping({ ...shipping, name: e.target.value })}
                      className="w-full rounded-lg border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />

                    <input
                      type="text"
                      placeholder="Address line 1"
                      value={shipping.line1}
                      onChange={(e) => setShipping({ ...shipping, line1: e.target.value })}
                      className="w-full rounded-lg border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      required
                    />

                    <input
                      type="text"
                      placeholder="Address line 2 (optional)"
                      value={shipping.line2 || ""}
                      onChange={(e) => setShipping({ ...shipping, line2: e.target.value })}
                      className="w-full rounded-lg border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />

                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="text"
                        placeholder="City"
                        value={shipping.city}
                        onChange={(e) => setShipping({ ...shipping, city: e.target.value })}
                        className="w-full rounded-lg border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                        required
                      />
                      <input
                        type="text"
                        placeholder="Postcode"
                        value={shipping.postal_code}
                        onChange={(e) => setShipping({ ...shipping, postal_code: e.target.value })}
                        className="w-full rounded-lg border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                        required
                      />
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={handleCheckout}
                        disabled={submitting}
                        className="flex-1 h-11 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 disabled:opacity-50 transition-colors"
                      >
                        {submitting ? "Processing..." : "Continue to Payment"}
                      </button>
                      <button
                        onClick={() => {
                          setShowCheckout(false);
                          setError("");
                        }}
                        className="h-11 rounded-lg border px-4 font-medium hover:bg-accent transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    UK made
                  </span>
                  <span className="flex items-center gap-1">
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Fast dispatch
                  </span>
                  <span className="flex items-center gap-1">
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Cancel anytime
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
