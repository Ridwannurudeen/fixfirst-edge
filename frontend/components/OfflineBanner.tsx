"use client";

import useSWR from "swr";

import { fetchHealth } from "@/lib/api";

export function OfflineBanner() {
  const { data, error } = useSWR("health", fetchHealth, {
    refreshInterval: 5000,
    revalidateOnFocus: false
  });

  if (error !== undefined) {
    return (
      <div className="inline-flex items-center rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-300">
        OFFLINE - Local API unavailable
      </div>
    );
  }

  if (data === undefined) {
    return (
      <div className="inline-flex items-center rounded-full border border-zinc-700 bg-zinc-900/60 px-4 py-2 text-sm font-medium text-zinc-400">
        Checking local status
      </div>
    );
  }

  const ready = data.collection_ready === true;
  const label = ready ? "OFFLINE - Ready locally" : "OFFLINE - Local DB not initialized";
  const tone = ready
    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
    : "border-amber-500/30 bg-amber-500/10 text-amber-300";
  return (
    <div className={`inline-flex items-center rounded-full border px-4 py-2 text-sm font-medium ${tone}`}>
      {label}
    </div>
  );
}
