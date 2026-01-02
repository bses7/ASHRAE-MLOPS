export async function GET() {
  const baseUrl = process.env.BACKEND_URL || "http://localhost:8000";

  try {
    const response = await fetch(`${baseUrl}/health`, {
      method: "GET",
    });

    if (response.ok) {
      return Response.json({ status: "online" });
    }
    return Response.json({ status: "offline" }, { status: 503 });
  } catch {
    return Response.json({ status: "offline" }, { status: 503 });
  }
}
