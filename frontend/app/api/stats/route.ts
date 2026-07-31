import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

/** Corpus size shown in the sidebar. */
export async function GET() {
  try {
    const upstream = await fetch(`${BACKEND_URL}/stats`, {
      signal: AbortSignal.timeout(15_000),
      cache: "no-store",
    });
    if (!upstream.ok) throw new Error(String(upstream.status));
    return NextResponse.json(await upstream.json());
  } catch {
    return NextResponse.json({ indexed_chunks: 0, schemes: 0 });
  }
}
