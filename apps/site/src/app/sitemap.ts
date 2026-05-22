import { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://b2b-stickers.co.uk";

  // Static pages
  const staticPages = [
    { url: `${baseUrl}/`, priority: 1.0, changeFrequency: "daily" as const },
    { url: `${baseUrl}/shop`, priority: 0.9, changeFrequency: "daily" as const },
    { url: `${baseUrl}/industry`, priority: 0.8, changeFrequency: "weekly" as const },
    { url: `${baseUrl}/account`, priority: 0.3, changeFrequency: "monthly" as const },
    { url: `${baseUrl}/legal/terms`, priority: 0.3, changeFrequency: "yearly" as const },
    { url: `${baseUrl}/legal/privacy`, priority: 0.3, changeFrequency: "yearly" as const },
    { url: `${baseUrl}/legal/cookies`, priority: 0.3, changeFrequency: "yearly" as const },
  ];

  // Industry pages
  const industries = [
    "food-beverage",
    "health-beauty",
    "home-garden",
    "fashion-accessories",
    "pets",
    "tech-gadgets",
    "stationery-paper",
    "art-craft",
    "events-weddings",
    "fitness-sports",
    "fba-sellers",
    "subscription-boxes",
  ];

  const industryPages = industries.map((slug) => ({
    url: `${baseUrl}/shop?industry=${slug}`,
    priority: 0.7,
    changeFrequency: "weekly" as const,
  }));

  // Try to fetch dynamic products from API
  let productPages: MetadataRoute.Sitemap = [];
  try {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    const res = await fetch(`${apiBase}/catalog/products?limit=1000`, {
      next: { revalidate: 3600 }, // Revalidate every hour
    });
    if (res.ok) {
      const data = await res.json();
      const products = data.products || [];
      productPages = products.map((product: { slug: string; updated_at?: string }) => ({
        url: `${baseUrl}/product/${product.slug}`,
        priority: 0.8,
        changeFrequency: "weekly" as const,
        lastModified: product.updated_at ? new Date(product.updated_at) : new Date(),
      }));
    }
  } catch {
    // If API is not available, return static pages only
  }

  return [...staticPages, ...industryPages, ...productPages];
}
