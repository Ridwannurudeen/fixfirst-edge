"use client";

export type FilterValues = {
  machineType: string;
  severity: string;
  docType: string;
};

type FilterPanelProps = {
  values: FilterValues;
  onChange: (value: FilterValues) => void;
};

const machineTypes = ["", "Conveyor", "Compressor", "Pump"];
const severities = ["", "low", "medium", "high", "critical"];
const docTypes = ["", "manual", "incident", "part", "error_code", "voice_note"];

export function FilterPanel({ values, onChange }: FilterPanelProps) {
  return (
    <div className="grid gap-3 md:grid-cols-3">
      <select
        className="rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm"
        onChange={(event) => {
          onChange({ ...values, machineType: event.target.value });
        }}
        value={values.machineType}
      >
        <option value="">Any machine</option>
        {machineTypes.filter(Boolean).map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>
      <select
        className="rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm"
        onChange={(event) => {
          onChange({ ...values, severity: event.target.value });
        }}
        value={values.severity}
      >
        <option value="">Any severity</option>
        {severities.filter(Boolean).map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>
      <select
        className="rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm"
        onChange={(event) => {
          onChange({ ...values, docType: event.target.value });
        }}
        value={values.docType}
      >
        <option value="">Any type</option>
        {docTypes.filter(Boolean).map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>
    </div>
  );
}
