export async function GET() {
  try {
    const response = await fetch("http://localhost:8000/health", {
      method: "GET",
    })

    if (response.ok) {
      return Response.json({ status: "online" })
    }
    return Response.json({ status: "offline" }, { status: 503 })
  } catch {
    return Response.json({ status: "offline" }, { status: 503 })
  }
}
