import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description:
    "B2B Stickers UK privacy policy. Learn how we collect, use, and protect your personal data. GDPR compliant.",
  alternates: {
    canonical: "/legal/privacy",
  },
};

export default function PrivacyPage() {
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
            Privacy Policy
          </li>
        </ol>
      </nav>

      <h1 className="text-3xl font-bold mb-2">Privacy Policy</h1>
      <p className="text-sm text-muted-foreground mb-8">
        Last updated: {new Date().toLocaleDateString("en-GB")}
      </p>

      <div className="prose prose-sm max-w-none space-y-8">
        <section>
          <h2 className="text-xl font-semibold mb-3">1. Who We Are</h2>
          <p>
            B2B Stickers Ltd (&ldquo;we&rdquo;, &ldquo;us&rdquo;, or &ldquo;our&rdquo;) is a UK-based company
            providing custom stickers and labels for small businesses. Our registered office is in the
            United Kingdom. We are committed to protecting your personal data and respecting your privacy.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">2. Data We Collect</h2>
          <p>We collect and process the following personal data:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>
              <strong>Contact Information:</strong> Email address, name, and phone number (if provided)
            </li>
            <li>
              <strong>Shipping Address:</strong> Delivery address for order fulfilment
            </li>
            <li>
              <strong>Payment Information:</strong> Processed securely by Stripe. We do not store card details.
            </li>
            <li>
              <strong>Company Information:</strong> Company name and registration number (optional, for B2B verification)
            </li>
            <li>
              <strong>Usage Data:</strong> Information about how you use our website (via essential cookies only)
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">3. How We Use Your Data</h2>
          <p>Your personal data is used for the following purposes:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Processing and fulfilling your orders</li>
            <li>Managing your subscription and recurring payments</li>
            <li>Sending transactional emails (order confirmations, shipping updates)</li>
            <li>Providing customer support</li>
            <li>Complying with legal obligations (tax, accounting)</li>
          </ul>
          <p className="mt-2">
            We do not use your data for marketing purposes without your explicit consent. We do not sell
            or share your data with third parties for advertising.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">4. Legal Basis for Processing</h2>
          <p>Under GDPR, we process your data on the following legal bases:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>
              <strong>Contract:</strong> Processing necessary to fulfil our contract with you (order fulfilment)
            </li>
            <li>
              <strong>Legal Obligation:</strong> Compliance with tax and accounting laws
            </li>
            <li>
              <strong>Legitimate Interests:</strong> Fraud prevention and website security
            </li>
            <li>
              <strong>Consent:</strong> Where you have explicitly opted in (e.g., marketing emails)
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">5. Data Sharing</h2>
          <p>We share your data only with trusted service providers necessary to operate our business:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>
              <strong>Stripe:</strong> Payment processing (PCI DSS compliant)
            </li>
            <li>
              <strong>Prodigi:</strong> Print-on-demand fulfilment (shipping address only)
            </li>
            <li>
              <strong>Resend:</strong> Transactional email delivery
            </li>
          </ul>
          <p className="mt-2">
            All third-party providers are GDPR compliant and process data only on our instructions.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">6. Data Retention</h2>
          <p>
            We retain your personal data for as long as necessary to fulfil the purposes outlined above:
          </p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Order and subscription data: 7 years (for tax and accounting compliance)</li>
            <li>Customer account data: Until you request deletion</li>
            <li>Payment records: 7 years (as required by HMRC)</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">7. Your Rights</h2>
          <p>Under GDPR, you have the following rights:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>
              <strong>Right to Access:</strong> Request a copy of your personal data
            </li>
            <li>
              <strong>Right to Rectification:</strong> Correct inaccurate or incomplete data
            </li>
            <li>
              <strong>Right to Erasure:</strong> Request deletion of your data (&ldquo;right to be forgotten&rdquo;)
            </li>
            <li>
              <strong>Right to Restrict Processing:</strong> Limit how we use your data
            </li>
            <li>
              <strong>Right to Data Portability:</strong> Receive your data in a structured format
            </li>
            <li>
              <strong>Right to Object:</strong> Object to processing based on legitimate interests
            </li>
          </ul>
          <p className="mt-2">
            To exercise any of these rights, please contact us at{" "}
            <a href="mailto:privacy@b2b-stickers.co.uk" className="text-primary hover:underline">
              privacy@b2b-stickers.co.uk
            </a>
            .
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">8. Cookies</h2>
          <p>
            We use only essential cookies necessary for the website to function (authentication,
            session management, and checkout). We do not use analytics, advertising, or third-party
            tracking cookies. See our{" "}
            <Link href="/legal/cookies" className="text-primary hover:underline">
              Cookie Policy
            </Link>{" "}
            for more details.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">9. Security</h2>
          <p>
            We implement appropriate technical and organisational measures to protect your personal
            data against unauthorised access, alteration, disclosure, or destruction. All data is
            transmitted over HTTPS and stored in secure, access-controlled environments.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">10. Contact Us</h2>
          <p>
            If you have any questions about this Privacy Policy or how we handle your data, please
            contact us:
          </p>
          <address className="not-italic mt-2">
            <p>B2B Stickers Ltd</p>
            <p>Email:{" "}
              <a href="mailto:privacy@b2b-stickers.co.uk" className="text-primary hover:underline">
                privacy@b2b-stickers.co.uk
              </a>
            </p>
          </address>
        </section>
      </div>
    </div>
  );
}
