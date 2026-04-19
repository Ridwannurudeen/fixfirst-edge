"use client";

type SaveIncidentModalProps = {
  disabled: boolean;
  onSave: () => void;
};

export function SaveIncidentModal({ disabled, onSave }: SaveIncidentModalProps) {
  return (
    <button
      className="inline-flex rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-300 transition hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-50"
      disabled={disabled}
      onClick={onSave}
      type="button"
    >
      Save as new incident
    </button>
  );
}
