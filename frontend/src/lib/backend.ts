/**
 * Server-only helpers for talking to the FastAPI saved-comps endpoints.
 * The X-User-Email header is the trust boundary: it must only ever be set
 * here, after reading the NextAuth session — never from browser input.
 */
const API_URL = process.env.API_URL ?? "http://localhost:8000";

export function savedCompsUrl(path = ""): string {
  return `${API_URL}/api/saved-comps${path}`;
}

export function savedCompsHeaders(email: string): Record<string, string> {
  const headers: Record<string, string> = {
    "X-User-Email": email,
    "Content-Type": "application/json",
  };
  if (process.env.BACKEND_SHARED_SECRET) {
    headers["X-Backend-Secret"] = process.env.BACKEND_SHARED_SECRET;
  }
  return headers;
}
