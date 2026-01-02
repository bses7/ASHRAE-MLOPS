export async function GET() {

  const baseUrl = process.env.BACKEND_URL || "http://localhost:8000";

  try {
    const response = await fetch(`${baseUrl}/metadata`,{
      cache: "no-store",
    });

    if (!response.ok)
      return Response.json({ status: "offline" }, { status: 503 });

    const data = await response.json();
    return Response.json(data);
  } catch {
    return Response.json({ status: "offline" }, { status: 503 });
  }
}
