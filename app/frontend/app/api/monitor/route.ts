// app/api/monitor/route.ts
import { NextResponse } from "next/server";

export async function GET() {
  const baseUrl = process.env.BACKEND_URL || "http://localhost:8000";

  try {
    const response = await fetch(`${baseUrl}/api/v1/monitoring/report`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to fetch report" },
        { status: response.status }
      );
    }

    const htmlContent = await response.text();

    return new Response(htmlContent, {
      headers: {
        "Content-Type": "text/html",
      },
    });
  } catch (error) {
    console.error("Monitoring API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
