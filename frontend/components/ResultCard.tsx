type ResultCardProps = {
  title: string;
  body: string;
  meta?: string;
};

export function ResultCard({ title, body, meta }: ResultCardProps) {
  return (
    <article className="rounded-2xl border border-zinc-800 bg-zinc-900 p-4">
      <h3 className="text-sm font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-zinc-300">{body}</p>
      {meta ? <p className="mt-3 text-xs uppercase tracking-[0.2em] text-zinc-500">{meta}</p> : null}
    </article>
  );
}
