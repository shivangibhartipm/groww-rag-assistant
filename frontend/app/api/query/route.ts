import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

// Vercel caps how long a route handler may run; exceeding it kills the
// function and the browser gets a platform error page instead of our JSON.
export const maxDuration = 60;

// Abort before maxDuration so a slow backend surfaces as a handled 503
const UPSTREAM_TIMEOUT_MS = 55_000;

/** Proxies the assistant query so the backend stays server-side and CORS-free. */
export async function POST(request: Request) {
  let query: unknown;
  try {
    ({ query } = await request.json());
  } catch {
    return NextResponse.json({ detail: "Invalid request body." }, { status: 400 });
  }

  if (typeof query !== "string" || !query.trim()) {
    return NextResponse.json({ detail: "A question is required." }, { status: 400 });
  }

  try {
    const upstream = await fetch(`${BACKEND_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
      // Retrieval plus generation can take a while on a cold model
      signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
      cache: "no-store",
    });

    if (!upstream.ok) {
      return NextResponse.json(
        { detail: `The assistant returned status ${upstream.status}.` },
        { status: 502 },
      );
    }
    return NextResponse.json(await upstream.json());
  } catch {
    return NextResponse.json(
      { detail: `Could not reach the assistant API at ${BACKEND_URL}.` },
      { status: 503 },
    );
  }
}
