import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { savedCompsHeaders, savedCompsUrl } from "@/lib/backend";

export async function DELETE(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  const email = session?.user?.email;
  if (!email) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  const { id } = await params;
  const res = await fetch(savedCompsUrl(`/${encodeURIComponent(id)}`), {
    method: "DELETE",
    headers: savedCompsHeaders(email),
  });
  return NextResponse.json(await res.json(), { status: res.status });
}
