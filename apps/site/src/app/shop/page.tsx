"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Metadata } from "next";

interface Product {
  id: number;
  slug: string;
  title: string;
  description: string | null;
  image_url: string;
  industry_name: string | null;
  tags: string[];
  variants: Array<{
    id: number;
    material: string;
    shape: string;
    pack_quantity: number;
    retail_price: number;
    retail_price_vat: number;
    recurring_price_vat: number;
  }>;
}

const industries = [
  { slug: "", label: "All Industries" },
  { slug: "food-beverage", label: "Food & Beverage" },
  { slug: "health-beauty", label: "Health & Beauty" },
  { slug: "home-garden", label: "Home & Garden" },
  { slug: "fashion-accessories", label: "Fashion & Accessories" },
  { slug: "pets", label: "Pets" },
  { slug: "fba-sellers", label: "Etsy & Handmade" },
];

function ShopContent() {
  const searchParams = useSearchParams();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const industry = searchParams.get("industry") || "";

  useEffect(() => {
    const params = new URLSearchParams();
    if (industry) params.set("industry", industry);

    fetch(`/api/catalog/products?${params.toString()}`)
      .then((r) => r.json())
      .then((d) => {
        setProducts(d.products || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [industry]);

  const filteredProducts = searchQuery
    ? products.filter(
        (p) =>
          p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.tags?.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : products;

  if (loading) {
    return (
      <div className="py-16 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="mt-4 text-muted-foreground">Loading products...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="mb-6">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground">
          <li>
            <Link href="/" className="hover:text-foreground transition-colors">
              Home
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li aria-current="page" className="text-foreground font-medium">
            Shop
          </li>
        </ol>
      </nav>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar Filters */}
        <aside className="lg:w-64 shrink-0">
          <div className="sticky top-24">
            <h2 className="text-lg font-semibold mb-4">Filter by Industry</h2>
            <nav aria-label="Industry filters" className="space-y-1">
              {industries.map((ind) => (
                <Link
                  key={ind.slug}
                  href={ind.slug ? `/shop?industry=${ind.slug}` : "/shop"}
                  className={`block rounded-md px-3 py-2 text-sm transition-colors ${
                    (industry === ind.slug) || (!industry && !ind.slug)
                      ? "bg-primary text-primary-foreground font-medium"
                      : "text-foreground/80 hover:bg-accent"
                  }`}
                  aria-current={industry === ind.slug ? "page" : undefined}
                >
                  {ind.label}
                </Link>
              ))}
            </nav>

            <div className="mt-8 rounded-lg border bg-card p-4">
              <h3 className="font-semibold text-sm mb-2">Subscribe & Save</h3>
              <p className="text-xs text-muted-foreground">
                Subscribe to any sticker and save 10% every month. Cancel anytime.
              </p>
            </div>
          </div>
        </aside>

        {/* Product Grid */}
        <div className="flex-1">
          <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold">
                {industry
                  ? industries.find((i) => i.slug === industry)?.label || "Shop"
                  : "All Stickers & Labels"}
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                {filteredProducts.length} product{filteredProducts.length !== 1 ? "s" : ""} available
              </p>
            </div>
            <div className="relative">
              <input
                type="search"
                placeholder="Search stickers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full sm:w-64 rounded-md border bg-background px-3 py-2 pl-9 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                aria-label="Search products"
              />
              <svg
                className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>

          {filteredProducts.length === 0 ? (
            <div className="rounded-lg border bg-card p-12 text-center">
              <svg
                className="mx-auto h-12 w-12 text-muted-foreground mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
              </svg>
              <h3 className="text-lg font-semibold mb-2">No products found</h3>
              <p className="text-muted-foreground text-sm">
                Try adjusting your search or browse a different industry.
              </p>
              <Link
                href="/shop"
                className="mt-4 inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                View All Products
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredProducts.map((p) => {
                const minPrice = Math.min(...p.variants.map((v) => v.retail_price_vat));
                const minSubPrice = Math.min(...p.variants.map((v) => v.recurring_price_vat));
                return (
                  <article
                    key={p.id}
                    className="group flex flex-col rounded-xl border bg-card overflow-hidden shadow-sm hover:shadow-md transition-all"
                  >
                    <Link href={`/product/${p.slug}`} className="relative aspect-square bg-muted overflow-hidden">
                      {p.image_url ? (
                        <img
                          src={p.image_url}
                          alt={`${p.title} - custom sticker design`}
                          className="h-full w-full object-cover transition-transform group-hover:scale-105"
                          loading="lazy"
                        />
                      ) : (
                        <div className="flex h-full items-center justify-center text-muted-foreground">
                          <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={1}
                              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                          </svg>
                        </div>
                      )}
                      {p.industry_name && (
                        <span className="absolute top-3 left-3 rounded-full bg-background/90 backdrop-blur-sm px-3 py-1 text-xs font-medium">
                          {p.industry_name}
                        </span>
                      )}
                    </Link>
                    <div className="flex flex-1 flex-col p-4">
                      <h2 className="text-base font-semibold group-hover:text-primary transition-colors">
                        <Link href={`/product/${p.slug}`}>{p.title}</Link>
                      </h2>
                      {p.description && (
                        <p className="mt-1 text-sm text-muted-foreground line-clamp-2">{p.description}</p>
                      )}
                      <div className="mt-auto pt-3 flex items-baseline gap-2">
                        <span className="text-lg font-bold">£{minSubPrice.toFixed(2)}</span>
                        <span className="text-sm text-muted-foreground line-through">
                          £{minPrice.toFixed(2)}
                        </span>
                        <span className="ml-auto text-xs font-medium text-green-700 bg-green-100 rounded-full px-2 py-0.5">
                          Save 10%
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">per month inc. VAT</p>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ShopPage() {
  return (
    <Suspense
      fallback={
        <div className="py-16 text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      }
    >
      <ShopContent />
    </Suspense>
  );
}
