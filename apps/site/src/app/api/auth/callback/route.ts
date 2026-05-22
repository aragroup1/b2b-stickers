import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get("token");
  
  if (!token) {
    return NextResponse.redirect(new URL("/account?error=missing_token", request.url));
  }

  // Redirect to the API's magic link callback endpoint
  const apiBase = process.env.API_BASE_URL || "http://localhost:8000";
  return NextResponse.redirect(`${apiBase}/api/v1/customers/auth/callback?token=${token}`);
}
