import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import CookieBanner from "~/components/CookieBanner";
import { JsonLd } from "~/components/JsonLd";
import { OrganizationSchema } from "~/lib/schema";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0f172a",
};

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://b2b-stickers.co.uk"),
  title: {
    default: "B2B Stickers UK | Custom Labels & Stickers for Small Businesses",
    template: "%s | B2B Stickers UK",
  },
  description:
    "Premium custom stickers and labels for UK small businesses. Subscribe & save 10% on monthly sticker deliveries. Perfect for breweries, candle makers, skincare brands & Etsy sellers. Free UK shipping over £50.",
  keywords: [
    "custom stickers UK",
    "business labels",
    "product stickers",
    "branding stickers",
    "sticker subscription UK",
    "small business stickers",
    "brewery labels",
    "candle labels",
    "skincare labels",
    "Etsy packaging stickers",
    "UK made stickers",
    "vinyl stickers wholesale",
    "custom product labels",
    "packaging stickers",
    "logo stickers UK",
  ],
  authors: [{ name: "B2B Stickers Ltd" }],
  creator: "B2B Stickers Ltd",
  publisher: "B2B Stickers Ltd",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "en_GB",
    url: "/",
    siteName: "B2B Stickers UK",
    title: "B2B Stickers UK | Custom Labels & Stickers for Small Businesses",
    description:
      "Premium custom stickers and labels for UK small businesses. Subscribe & save 10%. Free UK shipping over £50.",
    images: [
      {
        url: "/images/og-default.jpg",
        width: 1200,
        height: 630,
        alt: "B2B Stickers UK - Custom labels and stickers for small businesses",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "B2B Stickers UK | Custom Labels & Stickers for Small Businesses",
    description:
      "Premium custom stickers and labels for UK small businesses. Subscribe & save 10%. Free UK shipping over £50.",
    images: ["/images/og-default.jpg"],
  },
  verification: {
    google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-GB">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={inter.className}>
        <JsonLd data={OrganizationSchema} />
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-primary focus:text-primary-foreground focus:px-4 focus:py-2 focus:rounded-md"
        >
          Skip to main content
        </a>

        <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
            <Link href="/" className="flex items-center gap-2 text-xl font-bold tracking-tight" aria-label="B2B Stickers UK - Home">
              <svg
                className="h-8 w-8 text-primary"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
              <span className="hidden sm:inline">B2B Stickers</span>
            </Link>

            <nav className="flex items-center gap-1 sm:gap-4" aria-label="Main navigation">
              <Link
                href="/shop"
                className="rounded-md px-3 py-2 text-sm font-medium text-foreground/80 hover:text-foreground hover:bg-accent transition-colors"
              >
                Shop
              </Link>
              <Link
                href="/industry"
                className="hidden md:inline-flex rounded-md px-3 py-2 text-sm font-medium text-foreground/80 hover:text-foreground hover:bg-accent transition-colors"
              >
                Industries
              </Link>
              <Link
                href="/account"
                className="rounded-md px-3 py-2 text-sm font-medium text-foreground/80 hover:text-foreground hover:bg-accent transition-colors"
              >
                Account
              </Link>
              <Link
                href="/shop"
                className="ml-2 inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                Get Started
              </Link>
            </nav>
          </div>
        </header>

        <main id="main-content" className="min-h-[calc(100vh-16rem)]">
          {children}
        </main>

        <footer className="border-t bg-muted/30">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              <div>
                <h3 className="font-semibold mb-3">B2B Stickers</h3>
                <p className="text-sm text-muted-foreground">
                  Premium custom stickers and labels for UK small businesses. Subscribe & save on monthly deliveries.
                </p>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Shop</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><Link href="/shop" className="hover:text-foreground transition-colors">All Products</Link></li>
                  <li><Link href="/shop?industry=food-beverage" className="hover:text-foreground transition-colors">Food & Beverage</Link></li>
                  <li><Link href="/shop?industry=health-beauty" className="hover:text-foreground transition-colors">Health & Beauty</Link></li>
                  <li><Link href="/shop?industry=home-garden" className="hover:text-foreground transition-colors">Home & Garden</Link></li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Support</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><Link href="/account" className="hover:text-foreground transition-colors">My Account</Link></li>
                  <li><Link href="/legal/terms" className="hover:text-foreground transition-colors">Terms & Conditions</Link></li>
                  <li><Link href="/legal/privacy" className="hover:text-foreground transition-colors">Privacy Policy</Link></li>
                  <li><Link href="/legal/cookies" className="hover:text-foreground transition-colors">Cookie Policy</Link></li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Contact</h3>
                <address className="not-italic text-sm text-muted-foreground space-y-2">
                  <p>B2B Stickers Ltd</p>
                  <p>United Kingdom</p>
                  <p>
                    <a href="mailto:hello@b2b-stickers.co.uk" className="hover:text-foreground transition-colors">
                      hello@b2b-stickers.co.uk
                    </a>
                  </p>
                </address>
              </div>
            </div>
            <div className="mt-12 pt-8 border-t flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
              <p>© {new Date().getFullYear()} B2B Stickers Ltd. All rights reserved.</p>
              <p>VAT registered in the UK</p>
            </div>
          </div>
        </footer>
        <CookieBanner />
      </body>
    </html>
  );
}
