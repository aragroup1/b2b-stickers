export interface Product {
  id: number;
  slug: string;
  title: string;
  description: string | null;
  tags: string[];
  status: string;
  imageUrl: string;
  industryId: number | null;
  createdAt: string;
}

export interface StickerVariant {
  id: number;
  productId: number;
  sizeInches: number;
  material: string;
  shape: string;
  packQuantity: number;
  retailPrice: number;
  sku: string;
}

export interface Subscription {
  id: number;
  customerId: number;
  variantId: number;
  stripeSubscriptionId: string;
  recurringAmount: number;
  discountPercent: number;
  status: string;
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
}

export interface Customer {
  id: number;
  email: string;
  name: string | null;
  companyName: string | null;
  shippingAddress: Record<string, unknown> | null;
}

export interface Trend {
  id: number;
  keyword: string;
  industryId: number | null;
  searchVolume: number | null;
  trendScore: number | null;
  category: string | null;
  region: string;
}
