import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Cookie Policy",
  description:
    "B2B Stickers UK cookie policy. Learn about the cookies we use and how to manage them.",
  alternates: {
    canonical: "/legal/cookies",
  },
};

export default function CookiesPage() {
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
            Cookie Policy
          </li>
        </ol>
      </nav>

      <h1 className="text-3xl font-bold mb-2">Cookie Policy</h1>
      <p className="text-sm text-muted-foreground mb-8">
        Last updated: {new Date().toLocaleDateString("en-GB")}
      </p>

      <div className="prose prose-sm max-w-none space-y-8">
        <section>
          <h2 className="text-xl font-semibold mb-3">What Are Cookies?</h2>
          <p>
            Cookies are small text files that are placed on your computer or mobile device when you
            visit a website. They are widely used to make websites work more efficiently and to
            provide information to website owners.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">How We Use Cookies</h2>
          <p>
            B2B Stickers uses only essential cookies that are necessary for the website to function
            properly. We do not use analytics, advertising, or third-party tracking cookies.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">Essential Cookies</h2>
          <p>These cookies are necessary for the website to function and cannot be disabled:</p>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-sm border rounded-lg">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">Cookie Name</th>
                  <th className="px-4 py-3 text-left font-medium">Purpose</th>
                  <th className="px-4 py-3 text-left font-medium">Duration</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t">
                  <td className="px-4 py-3 font-mono text-xs">session</td>
                  <td className="px-4 py-3">Maintains your login session and authentication status</td>
                  <td className="px-4 py-3">30 days</td>
                </tr>
                <tr className="border-t">
                  <td className="px-4 py-3 font-mono text-xs">cookie-consent</td>
                  <td className="px-4 py-3">Records your cookie consent preference</td>
                  <td className="px-4 py-3">1 year</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">Stripe Cookies</h2>
          <p>
            Stripe, our payment processor, may set cookies during the checkout process to prevent
            fraud and ensure payment security. These cookies are managed by Stripe and are subject
            to{" "}
            <a
              href="https://stripe.com/gb/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Stripe&apos;s Privacy Policy
            </a>
            .
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">No Tracking Cookies</h2>
          <p>We explicitly do not use:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>Google Analytics or any analytics cookies</li>
            <li>Facebook Pixel or social media tracking</li>
            <li>Advertising or retargeting cookies</li>
            <li>Third-party marketing cookies</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">Managing Cookies</h2>
          <p>
            You can manage or delete cookies through your browser settings. Please note that
            disabling essential cookies will prevent you from logging in or checking out.
          </p>
          <p className="mt-2">Here are links to cookie management instructions for popular browsers:</p>
          <ul className="list-disc pl-5 space-y-1 mt-2">
            <li>
              <a
                href="https://support.google.com/chrome/answer/95647"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Google Chrome
              </a>
            </li>
            <li>
              <a
                href="https://support.mozilla.org/en-US/kb/cookies-information-websites-store-on-your-computer"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Mozilla Firefox
              </a>
            </li>
            <li>
              <a
                href="https://support.apple.com/en-gb/guide/safari/sfri11471/mac"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Safari
              </a>
            </li>
            <li>
              <a
                href="https://support.microsoft.com/en-gb/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Microsoft Edge
              </a>
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-3">Contact Us</h2>
          <p>
            If you have any questions about our Cookie Policy, please contact us at:{" "}
            <a href="mailto:hello@b2b-stickers.co.uk" className="text-primary hover:underline">
              hello@b2b-stickers.co.uk
            </a>
          </p>
        </section>
      </div>
    </div>
  );
}
