import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Page Not Found",
  robots: {
    index: false,
    follow: true,
  },
};

export default function NotFound() {
  return (
    <div className="mx-auto max-w-md px-4 py-24 text-center">
      <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-muted">
        <svg className="h-10 w-10 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h1 className="text-3xl font-bold mb-4">Page Not Found</h1>
      <p className="text-muted-foreground mb-8">
        The page you are looking for does not exist or has been moved. Check out our shop instead.
      </p>
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          href="/shop"
          className="inline-flex h-11 items-center justify-center rounded-lg bg-primary px-8 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Browse Shop
        </Link>
        <Link
          href="/"
          className="inline-flex h-11 items-center justify-center rounded-lg border px-8 text-sm font-semibold hover:bg-accent transition-colors"
        >
          Go Home
        </Link>
      </div>
    </div>
  );
}
