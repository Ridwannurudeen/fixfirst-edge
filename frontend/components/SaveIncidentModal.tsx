"use client";

import { useEffect, useMemo, useState } from "react";

export type SaveIncidentDraft = {
  machine_type: string;
  model_no: string;
  fault_code: string;
  fix_applied: string;
  downtime_min: string;
  part_no: string;
  parts_used: string;
  severity: string;
  symptom: string;
};

type SaveIncidentModalProps = {
  disabled: boolean;
  defaults: SaveIncidentDraft;
  onSave: (draft: SaveIncidentDraft) => Promise<void>;
};

function isComplete(value: SaveIncidentDraft): boolean {
  const requiredFields = [
    value.machine_type,
    value.model_no,
    value.fault_code,
    value.fix_applied,
    value.downtime_min,
    value.symptom,
  ];
  if (requiredFields.some((field) => field.trim() === "")) {
    return false;
  }
  const downtime = Number(value.downtime_min);
  return Number.isInteger(downtime) && downtime >= 0;
}

export function SaveIncidentModal({ disabled, defaults, onSave }: SaveIncidentModalProps) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<SaveIncidentDraft>(defaults);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setDraft(defaults);
      setError(null);
    }
  }, [defaults, open]);

  const canSubmit = useMemo(() => isComplete(draft), [draft]);

  async function handleSave(): Promise<void> {
    if (!canSubmit) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await onSave(draft);
      setOpen(false);
    } catch (saveError) {
      const message = saveError instanceof Error ? saveError.message : "Save failed";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <button
        className="inline-flex rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-300 transition hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-50"
        disabled={disabled}
        onClick={() => {
          setDraft(defaults);
          setError(null);
          setOpen(true);
        }}
        type="button"
      >
        Save as new incident
      </button>
      {open ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-2xl rounded-2xl border border-zinc-800 bg-zinc-950 p-5 shadow-2xl">
            <div className="mb-4 space-y-1">
              <p className="text-sm uppercase tracking-[0.2em] text-zinc-500">Verified Incident Capture</p>
              <h3 className="text-xl font-semibold text-zinc-100">Confirm the resolved case before saving</h3>
              <p className="text-sm text-zinc-400">
                The diagnose output is not saved automatically. Confirm the real fix details first.
              </p>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <label className="space-y-1 text-sm">
                <span className="text-zinc-400">Machine type</span>
                <input
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none transition focus:border-emerald-500"
                  onChange={(event) => {
                    setDraft({ ...draft, machine_type: event.target.value });
                  }}
                  value={draft.machine_type}
                />
              </label>
              <label className="space-y-1 text-sm">
                <span className="text-zinc-400">Model no.</span>
                <input
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none transition focus:border-emerald-500"
                  onChange={(event) => {
                    setDraft({ ...draft, model_no: event.target.value });
                  }}
                  value={draft.model_no}
                />
              </label>
              <label className="space-y-1 text-sm">
                <span className="text-zinc-400">Fault code</span>
                <input
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none transition focus:border-emerald-500"
                  onChange={(event) => {
                    setDraft({ ...draft, fault_code: event.target.value });
                  }}
                  value={draft.fault_code}
                />
              </label>
              <label className="space-y-1 text-sm">
                <span className="text-zinc-400">Downtime (min)</span>
                <input
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none transition focus:border-emerald-500"
                  min="0"
                  onChange={(event) => {
                    setDraft({ ...draft, downtime_min: event.target.value });
                  }}
                  type="number"
                  value={draft.downtime_min}
                />
              </label>
              <label className="space-y-1 text-sm md:col-span-2">
                <span className="text-zinc-400">Symptom</span>
                <input
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none transition focus:border-emerald-500"
                  onChange={(event) => {
                    setDraft({ ...draft, symptom: event.target.value });
                  }}
                  value={draft.symptom}
                />
              </label>
              <label className="space-y-1 text-sm md:col-span-2">
                <span className="text-zinc-400">Fix applied</span>
                <textarea
                  className="min-h-24 w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none transition focus:border-emerald-500"
                  onChange={(event) => {
                    setDraft({ ...draft, fix_applied: event.target.value });
                  }}
                  value={draft.fix_applied}
                />
              </label>
              <label className="space-y-1 text-sm md:col-span-2">
                <span className="text-zinc-400">Primary part no. (optional)</span>
                <input
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none transition focus:border-emerald-500"
                  onChange={(event) => {
                    setDraft({ ...draft, part_no: event.target.value });
                  }}
                  value={draft.part_no}
                />
              </label>
              <label className="space-y-1 text-sm md:col-span-2">
                <span className="text-zinc-400">Parts used (optional, free text)</span>
                <input
                  className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-zinc-100 outline-none transition focus:border-emerald-500"
                  onChange={(event) => {
                    setDraft({ ...draft, parts_used: event.target.value });
                  }}
                  value={draft.parts_used}
                />
              </label>
            </div>
            {error ? <p className="mt-3 text-sm text-red-400">{error}</p> : null}
            <div className="mt-5 flex items-center justify-end gap-3">
              <button
                className="rounded-xl border border-zinc-800 px-4 py-2 text-sm text-zinc-300 transition hover:bg-zinc-900"
                onClick={() => {
                  setOpen(false);
                }}
                type="button"
              >
                Cancel
              </button>
              <button
                className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-medium text-black transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
                disabled={!canSubmit || submitting}
                onClick={() => {
                  void handleSave();
                }}
                type="button"
              >
                {submitting ? "Saving..." : "Save verified incident"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
