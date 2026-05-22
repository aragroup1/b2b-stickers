import { Metadata } from "next";

export const OrganizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "B2B Stickers UK",
  alternateName: "B2B Stickers Ltd",
  url: "https://b2b-stickers.co.uk",
  logo: "https://b2b-stickers.co.uk/images/logo.png",
  sameAs: [],
  contactPoint: {
    "@type": "ContactPoint",
    contactType: "customer service",
    email: "hello@b2b-stickers.co.uk",
    areaServed: "GB",
    availableLanguage: ["English"],
  },
};

export function ProductSchema(product: {
  title: string;
  description: string;
  image: string;
  slug: string;
  price: number;
  currency: string;
  availability: string;
  sku: string;
  brand?: string;
  category?: string;
}) {
  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.title,
    description: product.description,
    image: product.image,
    sku: product.sku,
    brand: {
      "@type": "Brand",
      name: product.brand || "B2B Stickers",
    },
    category: product.category || "Stickers & Labels",
    offers: {
      "@type": "Offer",
      url: `https://b2b-stickers.co.uk/product/${product.slug}`,
      priceCurrency: product.currency,
      price: product.price.toFixed(2),
      availability: product.availability,
      seller: {
        "@type": "Organization",
        name: "B2B Stickers UK",
      },
      shippingDetails: {
        "@type": "OfferShippingDetails",
        shippingRate: {
          "@type": "MonetaryAmount",
          value: "0.00",
          currency: "GBP",
        },
        shippingDestination: {
          "@type": "DefinedRegion",
          addressCountry: "GB",
        },
        doesNotShip: "false",
      },
      hasMerchantReturnPolicy: {
        "@type": "MerchantReturnPolicy",
        returnPolicyCategory: "https://schema.org/MerchantReturnNotPermitted",
        returnMethod: "https://schema.org/ReturnByMail",
        returnFees: "https://schema.org/FreeReturn",
      },
    },
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: "4.8",
      reviewCount: "127",
    },
  };
}

export function LocalBusinessSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    name: "B2B Stickers UK",
    image: "https://b2b-stickers.co.uk/images/logo.png",
    url: "https://b2b-stickers.co.uk",
    telephone: "",
    email: "hello@b2b-stickers.co.uk",
    address: {
      "@type": "PostalAddress",
      addressCountry: "GB",
      addressRegion: "England",
    },
    geo: {
      "@type": "GeoCoordinates",
      latitude: "51.5074",
      longitude: "-0.1278",
    },
    areaServed: {
      "@type": "Country",
      name: "United Kingdom",
    },
    priceRange: "£",
    openingHoursSpecification: [
      {
        "@type": "OpeningHoursSpecification",
        dayOfWeek: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        opens: "09:00",
        closes: "17:00",
      },
    ],
    paymentAccepted: "Card, Stripe",
    currenciesAccepted: "GBP",
  };
}

export function FAQSchema(faqs: Array<{ question: string; answer: string }>) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((faq) => ({
      "@type": "Question",
      name: faq.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: faq.answer,
      },
    })),
  };
}

export function BreadcrumbSchema(items: Array<{ name: string; url: string }>) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}

export function WebSiteSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "B2B Stickers UK",
    url: "https://b2b-stickers.co.uk",
    potentialAction: {
      "@type": "SearchAction",
      target: {
        "@type": "EntryPoint",
        urlTemplate: "https://b2b-stickers.co.uk/shop?q={search_term_string}",
      },
      "query-input": "required name=search_term_string",
    },
  };
}
