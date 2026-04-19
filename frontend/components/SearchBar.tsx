"use client";

type SearchBarProps = {
  query: string;
  onQueryChange: (value: string) => void;
  onSubmit: () => void;
};

export function SearchBar({ query, onQueryChange, onSubmit }: SearchBarProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm text-zinc-400" htmlFor="search">
        Search
      </label>
      <input
        id="search"
        className="w-full rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm outline-none transition focus:border-emerald-500"
        onChange={(event) => {
          onQueryChange(event.target.value);
        }}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            onSubmit();
          }
        }}
        placeholder="E04 motor overload"
        type="text"
        value={query}
      />
    </div>
  );
}
