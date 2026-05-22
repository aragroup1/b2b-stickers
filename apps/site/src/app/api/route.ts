import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    name: "B2B Stickers UK",
    version: "0.1.0",
    status: "ok",
  });
}
