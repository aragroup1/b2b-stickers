import Link from "next/link";
import { Metadata } from "next";
import { JsonLd } from "~/components/JsonLd";
import { LocalBusinessSchema, WebSiteSchema, FAQSchema, BreadcrumbSchema } from "~/lib/schema";

export const metadata: Metadata = {
  title: "Custom Stickers & Labels for UK Small Businesses | Subscribe & Save 10%",
  description:
    "Premium custom stickers and labels for UK small businesses. Subscribe monthly & save 10%. Perfect for breweries, candle makers, skincare brands & Etsy sellers. Free UK shipping over £50. VAT included.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "Custom Stickers & Labels for UK Small Businesses | Subscribe & Save 10%",
    description:
      "Premium custom stickers and labels for UK small businesses. Subscribe monthly & save 10%. Free UK shipping over £50.",
    url: "/",
  },
};

const faqs = [
  {
    question: "What sizes and pack quantities do you offer?",
    answer:
      "We offer stickers in 2\", 3\", 4\", and 5\" sizes with pack quantities of 10, 25, 50, 100, and 250. All stickers are printed on premium vinyl with weatherproof coating.",
  },
  {
    question: "How does the Subscribe & Save work?",
    answer:
      "Subscribe to any sticker design and save 10% off the regular price. Your stickers ship automatically every month. You can pause, skip, or cancel anytime through your account or the Stripe Customer Portal.",
  },
  {
    question: "Do you ship outside the UK?",
    answer:
      "Currently we only ship within the United Kingdom. Standard delivery is 3-5 business days. Express delivery (1-2 days) is available at checkout.",
  },
  {
    question: "Are your stickers waterproof and durable?",
    answer:
      "Yes! All our stickers are printed on premium vinyl with a weatherproof, UV-resistant coating. They're suitable for indoor and outdoor use, including on product packaging, bottles, and containers.",
  },
  {
    question: "Can I get a sample before subscribing?",
    answer:
      "Yes, you can order a sample pack for just £2.99 to see the quality before committing to a subscription. Samples include a variety of sizes so you can find the perfect fit for your products.",
  },
  {
    question: "Do you provide VAT invoices?",
    answer:
      "Yes, VAT invoices are automatically generated for every order. All prices shown include UK VAT at 20%. Your VAT invoice is available in your account dashboard immediately after purchase.",
  },
];

const industries = [
  {
    name: "Food & Beverage",
    slug: "food-beverage",
    description: "Brewery labels, coffee roaster stickers, bakery packaging",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
      </svg>
    ),
  },
  {
    name: "Health & Beauty",
    slug: "health-beauty",
    description: "Candle labels, soap stickers, skincare packaging",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
      </svg>
    ),
  },
  {
    name: "Home & Garden",
    slug: "home-garden",
    description: "Plant pot labels, seed packet stickers, home decor",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
      </svg>
    ),
  },
  {
    name: "Fashion & Accessories",
    slug: "fashion-accessories",
    description: "Jewellery box stickers, clothing labels, bag tags",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
      </svg>
    ),
  },
  {
    name: "Pets",
    slug: "pets",
    description: "Pet treat labels, grooming stickers, toy packaging",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z" />
      </svg>
    ),
  },
  {
    name: "Etsy & Handmade",
    slug: "fba-sellers",
    description: "Thank you stickers, packaging seals, branding labels",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
      </svg>
    ),
  },
];

const trustSignals = [
  { label: "UK Made", description: "Printed and shipped from the UK" },
  { label: "Free Shipping", description: "On orders over £50" },
  { label: "10% Off", description: "With Subscribe & Save" },
  { label: "Cancel Anytime", description: "No contracts, no hassle" },
];

export default function LandingPage() {
  return (
    <>
      <JsonLd data={LocalBusinessSchema()} />
      <JsonLd data={WebSiteSchema()} />
      <JsonLd data={FAQSchema(faqs)} />
      <JsonLd
        data={BreadcrumbSchema([
          { name: "Home", url: "https://b2b-stickers.co.uk/" },
        ])}
      />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-background to-muted/30 py-16 sm:py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Custom Stickers & Labels
              <span className="block text-primary mt-2">Built for UK Small Businesses</span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
              Premium vinyl stickers printed in the UK. Perfect for breweries, candle makers,
              skincare brands, and Etsy sellers. Subscribe monthly and save 10% — cancel anytime.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/shop"
                className="inline-flex h-12 items-center justify-center rounded-md bg-primary px-8 text-base font-semibold text-primary-foreground shadow-sm hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary transition-all"
              >
                Browse Stickers
              </Link>
              <Link
                href="/industry"
                className="inline-flex h-12 items-center justify-center rounded-md border bg-background px-8 text-base font-semibold text-foreground shadow-sm hover:bg-accent transition-colors"
              >
                Find by Industry
              </Link>
            </div>

            {/* Trust Signals */}
            <div className="mt-12 grid grid-cols-2 gap-4 sm:grid-cols-4 max-w-3xl mx-auto">
              {trustSignals.map((signal) => (
                <div
                  key={signal.label}
                  className="rounded-lg border bg-background/60 backdrop-blur-sm p-4 text-center"
                >
                  <p className="font-semibold text-foreground">{signal.label}</p>
                  <p className="text-xs text-muted-foreground mt-1">{signal.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Industries Section */}
      <section className="py-16 sm:py-20" aria-labelledby="industries-heading">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 id="industries-heading" className="text-3xl font-bold tracking-tight sm:text-4xl">
              Stickers for Every Industry
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Browse our curated collections designed specifically for your business type
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {industries.map((industry) => (
              <Link
                key={industry.slug}
                href={`/shop?industry=${industry.slug}`}
                className="group relative flex flex-col rounded-xl border bg-card p-6 shadow-sm hover:shadow-md hover:border-primary/50 transition-all"
              >
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                  {industry.icon}
                </div>
                <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
                  {industry.name}
                </h3>
                <p className="mt-2 text-sm text-muted-foreground">{industry.description}</p>
                <div className="mt-4 flex items-center text-sm font-medium text-primary">
                  Browse collection
                  <svg
                    className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 sm:py-20 bg-muted/30" aria-labelledby="how-it-works-heading">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 id="how-it-works-heading" className="text-3xl font-bold tracking-tight sm:text-4xl">
              How Subscribe & Save Works
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Never run out of stickers again. Set it and forget it.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              {
                step: "1",
                title: "Choose Your Design",
                description: "Browse hundreds of designs or filter by your industry. Pick the size and pack quantity that fits your needs.",
              },
              {
                step: "2",
                title: "Subscribe & Save 10%",
                description: "Subscribe to get 10% off every month. Your stickers ship automatically — no need to reorder.",
              },
              {
                step: "3",
                title: "Receive & Use",
                description: "Premium vinyl stickers delivered to your door. Pause, skip, or cancel anytime from your account.",
              },
            ].map((item) => (
              <div key={item.step} className="relative flex flex-col items-center text-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground text-lg font-bold mb-4">
                  {item.step}
                </div>
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-16 sm:py-20" aria-labelledby="reviews-heading">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 id="reviews-heading" className="text-3xl font-bold tracking-tight sm:text-4xl">
              Trusted by UK Small Businesses
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Join hundreds of businesses using B2B Stickers for their packaging and branding
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              {
                quote: "The subscription model is perfect for our brewery. We get fresh labels every month without having to remember to reorder.",
                author: "James T.",
                business: "Craft Brewery, Bristol",
              },
              {
                quote: "Quality is outstanding. The vinyl stickers hold up perfectly on our candle jars, even with the heat. Highly recommend!",
                author: "Sarah M.",
                business: "Soy Candle Co., Manchester",
              },
              {
                quote: "As an Etsy seller, packaging matters. These stickers add a professional touch that customers notice and appreciate.",
                author: "Lisa K.",
                business: "Handmade Jewellery, London",
              },
            ].map((review, i) => (
              <blockquote
                key={i}
                className="rounded-xl border bg-card p-6 shadow-sm"
              >
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, j) => (
                    <svg key={j} className="h-5 w-5 text-yellow-500 fill-current" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-sm text-foreground mb-4">&ldquo;{review.quote}&rdquo;</p>
                <footer>
                  <p className="text-sm font-medium">{review.author}</p>
                  <p className="text-xs text-muted-foreground">{review.business}</p>
                </footer>
              </blockquote>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 sm:py-20 bg-muted/30" aria-labelledby="faq-heading">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 id="faq-heading" className="text-3xl font-bold tracking-tight sm:text-4xl">
              Frequently Asked Questions
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Everything you need to know about our stickers and subscription service
            </p>
          </div>
          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <details
                key={i}
                className="group rounded-lg border bg-card open:shadow-sm transition-all"
              >
                <summary className="flex cursor-pointer items-center justify-between p-4 text-left font-medium hover:bg-accent/50 rounded-lg transition-colors">
                  {faq.question}
                  <svg
                    className="h-5 w-5 shrink-0 text-muted-foreground transition-transform group-open:rotate-180"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                <div className="px-4 pb-4 text-sm text-muted-foreground">
                  {faq.answer}
                </div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 sm:py-20" aria-labelledby="cta-heading">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-2xl bg-primary px-6 py-16 sm:px-16 sm:py-20 text-center">
            <div className="relative">
              <h2 id="cta-heading" className="text-3xl font-bold tracking-tight text-primary-foreground sm:text-4xl">
                Ready to upgrade your packaging?
              </h2>
              <p className="mx-auto mt-6 max-w-xl text-lg text-primary-foreground/90">
                Browse our collection of premium stickers designed for UK small businesses.
                Subscribe today and save 10% on every order.
              </p>
              <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link
                  href="/shop"
                  className="inline-flex h-12 items-center justify-center rounded-md bg-background px-8 text-base font-semibold text-primary shadow-sm hover:bg-background/90 transition-colors"
                >
                  Shop Now
                </Link>
                <Link
                  href="/industry"
                  className="inline-flex h-12 items-center justify-center rounded-md border border-primary-foreground/30 bg-transparent px-8 text-base font-semibold text-primary-foreground hover:bg-primary-foreground/10 transition-colors"
                >
                  Explore Industries
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
