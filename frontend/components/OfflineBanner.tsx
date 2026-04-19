"use client";

import useSWR from "swr";

import { fetchHealth } from "@/lib/api";

export function OfflineBanner() {
  const { data } = useSWR("health", fetchHealth, {
    refreshInterval: 5000,
    revalidateOnFocus: false
  });

  const label = data?.online === false ? "OFFLINE - Running locally" : "Checking local status";
  return (
    <div className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-300">
      {label}
    </div>
  );
}
