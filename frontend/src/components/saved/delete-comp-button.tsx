"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function DeleteCompButton({ id }: { id: string }) {
  const router = useRouter();
  const [deleting, setDeleting] = useState(false);

  async function remove() {
    setDeleting(true);
    try {
      const res = await fetch(`/api/saved/${encodeURIComponent(id)}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error(`delete failed: ${res.status}`);
      router.refresh();
    } catch {
      setDeleting(false);
    }
  }

  return (
    <button
      type="button"
      onClick={remove}
      disabled={deleting}
      className="text-[11px] font-bold tracking-wider text-slate-500 uppercase transition-colors hover:text-vred disabled:opacity-40"
    >
      {deleting ? "Deleting…" : "Delete"}
    </button>
  );
}
