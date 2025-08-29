import type { TripRequest, Plan } from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  body?: unknown;
  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

/**
 * Call FastAPI POST /plan to create an itinerary.
 * Works from both client and server components.
 */
export async function createPlan(req: TripRequest): Promise<Plan> {
  const res = await fetch(`${API_BASE}/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    // Important for Next.js caching on the server:
    cache: "no-store",
  });

  if (!res.ok) {
    let body: unknown = undefined;
    try {
      body = await res.json();
    } catch {
      // ignore parse errors
    }
    throw new ApiError(`/plan request failed`, res.status, body);
  }

  const data = (await res.json()) as Plan;
  return data;
}
