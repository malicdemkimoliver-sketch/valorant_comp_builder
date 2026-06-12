import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { savedCompsHeaders, savedCompsUrl } from "@/lib/backend";

export async function GET() {
  const session = await auth();
  const email = session?.user?.email;
  if (!email) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  const res = await fetch(savedCompsUrl(), {
    headers: savedCompsHeaders(email),
    cache: "no-store",
  });
  return NextResponse.json(await res.json(), { status: res.status });
}

export async function POST(req: Request) {
  const session = await auth();
  const email = session?.user?.email;
  if (!email) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  const body = await req.json();
  const res = await fetch(savedCompsUrl(), {
    method: "POST",
    headers: savedCompsHeaders(email),
    // Display name goes in the body (headers reject non-ASCII)
    body: JSON.stringify({ ...body, user_name: session.user?.name ?? "" }),
  });
  return NextResponse.json(await res.json(), { status: res.status });
}
