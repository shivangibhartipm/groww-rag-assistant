import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

// Matches the query route. This call is what wakes a spun-down backend on page
// load, and the sidebar renders without it, so a long ceiling costs the user
// nothing and lets the count fill in once the instance is up.
export const maxDuration = 120;

const UPSTREAM_TIMEOUT_MS = 115_000;

/** Corpus size shown in the sidebar. */
export async function GET() {
  try {
    const upstream = await fetch(`${BACKEND_URL}/stats`, {
      signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
      cache: "no-store",
    });
    if (!upstream.ok) throw new Error(String(upstream.status));
    return NextResponse.json(await upstream.json());
  } catch {
    return NextResponse.json({ indexed_chunks: 0, schemes: 0 });
  }
}
