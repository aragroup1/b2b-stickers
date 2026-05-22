import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms & Conditions",
  description:
    "B2B Stickers UK terms and conditions. Subscription terms, cancellation policy, delivery information, and returns.",
  alternates: {
    canonical: "/legal/terms",
  },
};

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <nav aria-label="Breadcrumb" className="mb-6">
        <ol className="flex items-center gap-2 text-sm text-muted-foreground">
          <li>
            <Link href="/" className="hover:text-foreground transition-colors">
              Home
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li aria-current="page" className="text-foreground font-medium">
            Terms & Conditions
          </li>
        </ol>
      </nav>

      <h1 className="text-3xl font-bold mb-2">Terms & Conditions</h1>
      <p className="text-sm text-muted-foreground mb-8">
        Last updated: {new Date().toLocaleDateString("en-GB")}
      </p>

      <div className="prose prose-sm max-w-none space-y-8">
        <section>
          <h2 className="text-xl font-semibold mb-3">1. Introduction</h2>
          <p>
            These Terms and Conditions govern your use of the B2B Stickers website and the purchase
            of products and subscriptions from B2B Stickers Ltd. By using our website or placing an
            order, you agree to these terms in full.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">2. Definitions</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>
              <strong>&ldquo;We&rdquo;, &ldquo;Us&rdquo;, &ldquo;Our&rdquo;:</strong> B2B Stickers Ltd
            </li>
            <li>
              <strong>&ldquo;You&rdquo;, &ldquo;Your&rdquo;:</strong> The customer using our website or services
            </li>
            <li>
              <strong>&ldquo;Products&rdquo;:</strong> Custom stickers, labels, and related items sold through our website
            </li>
            <li>
              <strong>&ldquo;Subscription&rdquo;:</strong> A recurring monthly order for stickers managed through Stripe
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">3. Subscription Terms</h2>
          <p>
            By subscribing to B2B Stickers, you agree to receive monthly deliveries of your selected
            sticker variant. Subscriptions renew automatically each month on the anniversary of your
            initial purchase until cancelled.
          </p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Subscriptions are billed monthly via Stripe</li>
            <li>You will receive a renewal reminder email 3 days before each charge</li>
            <li>Subscription prices include UK VAT at 20%</li>
            <li>We reserve the right to adjust pricing with 30 days notice</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">4. Cancellation & Refunds</h2>
          <p>
            You may cancel your subscription at any time through your account or the Stripe Customer
            Portal. Cancellations take effect at the end of the current billing period.
          </p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>No refunds for partial subscription periods</li>
            <li>You may pause your subscription for up to 3 months</li>
            <li>You may skip a monthly shipment once per quarter</li>
            <li>One-time purchases may be cancelled before dispatch for a full refund</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">5. Pricing & VAT</h2>
          <p>
            All prices shown on our website include UK VAT at 20% unless otherwise stated. A VAT
            invoice is available for every order in your account dashboard.
          </p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Prices are in GBP (£) unless otherwise stated</li>
            <li>We reserve the right to change prices at any time</li>
            <li>Existing subscriptions are price-protected for 12 months</li>
            <li>Promotional discounts cannot be combined unless stated</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">6. Delivery</h2>
          <p>We currently ship to UK addresses only.</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>
              <strong>Standard Delivery:</strong> 3-5 business days — £3.49 (free over £50)
            </li>
            <li>
              <strong>Express Delivery:</strong> 1-2 business days — £5.99
            </li>
            <li>Delivery times are estimates and not guaranteed</li>
            <li>Risk of loss passes to you upon delivery</li>
            <li>We are not responsible for delays caused by courier services</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">7. Returns & Defective Items</h2>
          <p>
            Due to the custom nature of our products, returns are only accepted for defective or
            damaged items.
          </p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Contact us within 14 days of delivery to report defects</li>
            <li>Provide photos of the defective items</li>
            <li>We will replace defective items at no cost or issue a full refund</li>
            <li>Items damaged in transit must be reported within 48 hours</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">8. Intellectual Property</h2>
          <p>
            All designs, artwork, and content on our website are the property of B2B Stickers Ltd or
            our licensors. You may not reproduce, distribute, or create derivative works without our
            express permission.
          </p>
          <p className="mt-2">
            AI-generated designs are created specifically for our product catalogue. By purchasing,
            you receive a licence to use the physical stickers but not the underlying digital artwork.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">9. Limitation of Liability</h2>
          <p>
            To the maximum extent permitted by law, B2B Stickers Ltd shall not be liable for any
            indirect, incidental, special, consequential, or punitive damages arising from your use
            of our services or products.
          </p>
          <p className="mt-2">
            Our total liability for any claim shall not exceed the total amount paid by you for the
            specific product or subscription giving rise to the claim.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">10. Governing Law</h2>
          <p>
            These Terms and Conditions are governed by and construed in accordance with the laws of
            England and Wales. Any disputes shall be subject to the exclusive jurisdiction of the
            courts of England and Wales.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">11. Changes to Terms</h2>
          <p>
            We may update these Terms and Conditions from time to time. Changes will be posted on
            this page with an updated revision date. Continued use of our services after changes
            constitutes acceptance of the revised terms.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">12. Contact</h2>
          <p>
            For questions about these Terms and Conditions, please contact us at:{" "}
            <a href="mailto:hello@b2b-stickers.co.uk" className="text-primary hover:underline">
              hello@b2b-stickers.co.uk
            </a>
          </p>
        </section>
      </div>
    </div>
  );
}
