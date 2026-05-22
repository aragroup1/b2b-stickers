import Link from "next/link";
import { Metadata } from "next";
import { JsonLd } from "~/components/JsonLd";
import { BreadcrumbSchema } from "~/lib/schema";

export const metadata: Metadata = {
  title: "Stickers by Industry | Custom Labels for Every Business Type",
  description:
    "Browse custom stickers and labels by industry. Find the perfect designs for breweries, candle makers, skincare brands, Etsy sellers, and more. UK-made, weatherproof vinyl stickers.",
  alternates: {
    canonical: "/industry",
  },
  openGraph: {
    title: "Stickers by Industry | Custom Labels for Every Business Type",
    description: "Find the perfect sticker designs for your business type. UK-made premium vinyl stickers.",
    url: "/industry",
  },
};

const industries = [
  {
    name: "Food & Beverage",
    slug: "food-beverage",
    description: "Brewery labels, coffee roaster stickers, bakery packaging, hot sauce labels",
    keywords: ["brewery labels", "coffee stickers", "bakery packaging", "food labels UK"],
    count: 150,
  },
  {
    name: "Health & Beauty",
    slug: "health-beauty",
    description: "Candle warning labels, soap stickers, skincare packaging, shampoo bar labels",
    keywords: ["candle labels", "soap stickers", "skincare labels", "beauty packaging"],
    count: 120,
  },
  {
    name: "Home & Garden",
    slug: "home-garden",
    description: "Plant pot labels, seed packet stickers, home decor labels, garden centre tags",
    keywords: ["plant labels", "seed stickers", "garden labels", "home decor stickers"],
    count: 95,
  },
  {
    name: "Fashion & Accessories",
    slug: "fashion-accessories",
    description: "Jewellery box stickers, clothing labels, bag tags, tote bag stickers",
    keywords: ["jewellery stickers", "clothing labels", "fashion stickers", "accessory labels"],
    count: 80,
  },
  {
    name: "Pets",
    slug: "pets",
    description: "Pet treat labels, grooming stickers, toy packaging, organic pet food tags",
    keywords: ["pet labels", "dog treat stickers", "pet grooming labels", "pet food packaging"],
    count: 65,
  },
  {
    name: "Tech & Gadgets",
    slug: "tech-gadgets",
    description: "Laptop decals, phone case labels, charger cable stickers, electronics tags",
    keywords: ["laptop stickers", "tech labels", "gadget stickers", "electronics packaging"],
    count: 70,
  },
  {
    name: "Stationery & Paper",
    slug: "stationery-paper",
    description: "Envelope seals, thank you stickers, planner labels, journal stickers",
    keywords: ["envelope seals", "thank you stickers", "planner labels", "stationery stickers"],
    count: 110,
  },
  {
    name: "Art & Craft",
    slug: "art-craft",
    description: "Paint tube labels, craft kit stickers, Etsy seller packaging, handmade tags",
    keywords: ["craft stickers", "art labels", "Etsy packaging", "handmade stickers"],
    count: 85,
  },
  {
    name: "Events & Weddings",
    slug: "events-weddings",
    description: "Wedding favour labels, save the date stickers, event badge tags, party favours",
    keywords: ["wedding stickers", "event labels", "favour tags", "party stickers"],
    count: 90,
  },
  {
    name: "Fitness & Sports",
    slug: "fitness-sports",
    description: "Protein powder labels, supplement stickers, sports bottle tags, gym branding",
    keywords: ["supplement labels", "protein stickers", "sports labels", "fitness stickers"],
    count: 55,
  },
  {
    name: "Amazon FBA & E-commerce",
    slug: "fba-sellers",
    description: "Fragile stickers, thank you labels, packaging seals, branding stickers",
    keywords: ["FBA stickers", "Amazon labels", "packaging stickers", "ecommerce labels"],
    count: 130,
  },
  {
    name: "Subscription Boxes",
    slug: "subscription-boxes",
    description: "Box branding stickers, insert labels, thank you cards, unboxing experience",
    keywords: ["subscription box stickers", "box labels", "unboxing stickers", "branding labels"],
    count: 45,
  },
];

export default function IndustriesPage() {
  return (
    <>
      <JsonLd
        data={BreadcrumbSchema([
          { name: "Home", url: "https://b2b-stickers.co.uk/" },
          { name: "Industries", url: "https://b2b-stickers.co.uk/industry" },
        ])}
      />

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
              Industries
            </li>
          </ol>
        </nav>

        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Stickers for Every Industry
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Find the perfect sticker designs tailored to your business type. All printed on premium
            vinyl in the UK with weatherproof coating.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {industries.map((industry) => (
            <article
              key={industry.slug}
              className="group flex flex-col rounded-xl border bg-card p-6 shadow-sm hover:shadow-md hover:border-primary/50 transition-all"
            >
              <h2 className="text-xl font-semibold group-hover:text-primary transition-colors">
                <Link href={`/shop?industry=${industry.slug}`}>{industry.name}</Link>
              </h2>
              <p className="mt-2 text-sm text-muted-foreground flex-1">
                {industry.description}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {industry.keywords.slice(0, 3).map((kw) => (
                  <span
                    key={kw}
                    className="rounded-full bg-muted px-2.5 py-0.5 text-xs text-muted-foreground"
                  >
                    {kw}
                  </span>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  {industry.count}+ designs
                </span>
                <Link
                  href={`/shop?industry=${industry.slug}`}
                  className="inline-flex items-center text-sm font-medium text-primary hover:underline"
                >
                  Browse
                  <svg
                    className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </article>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold mb-4">Not sure what you need?</h2>
          <p className="text-muted-foreground mb-6 max-w-xl mx-auto">
            Browse our full collection of stickers and labels. Filter by industry, size, and pack
            quantity to find the perfect match for your business.
          </p>
          <Link
            href="/shop"
            className="inline-flex h-12 items-center justify-center rounded-md bg-primary px-8 text-base font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            View All Products
          </Link>
        </div>
      </div>
    </>
  );
}
