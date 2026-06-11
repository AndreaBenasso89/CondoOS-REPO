// Ops Console — Human Review Queue (the human-in-the-loop control surface, docs/07 §6).
// Renders firewall HOLD items with the draft + grounding + recipient + risk, and 1-click actions.

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

type LayerResult = { layer: string; passed: boolean; reasons?: string[] };
type ReviewItem = {
  id: string;
  kind: string;
  priority: string;
  payload: {
    draft?: { text: string; recipient?: { type: string }; citations?: unknown[] };
    verdict?: { verdict: string; autonomy_tier: string; layer_results?: LayerResult[] };
    trail?: string[];
  };
};

async function getReviews(): Promise<ReviewItem[]> {
  const res = await fetch(`${API}/v1/reviews`, { cache: "no-store" });
  if (!res.ok) return [];
  const data = await res.json();
  return data.items ?? [];
}

export default async function ReviewQueuePage() {
  const items = await getReviews();
  return (
    <main className="mx-auto max-w-4xl p-6">
      <h1 className="text-2xl font-semibold">Human Review Queue</h1>
      <p className="text-sm text-gray-500">
        Items held by the Reputation Firewall. Nothing is sent without your approval.
      </p>
      <ul className="mt-6 space-y-4">
        {items.length === 0 && <li className="text-gray-400">Queue empty — agents handling autonomously.</li>}
        {items.map((item) => (
          <li key={item.id} className="rounded-xl border p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="rounded bg-amber-100 px-2 py-0.5 text-xs">{item.kind}</span>
              <span className="text-xs uppercase text-gray-500">priority: {item.priority}</span>
            </div>
            <blockquote className="mt-3 whitespace-pre-wrap rounded bg-gray-50 p-3 text-sm">
              {item.payload.draft?.text ?? "(no draft)"}
            </blockquote>
            <div className="mt-2 text-xs text-gray-600">
              Verdict: <b>{item.payload.verdict?.verdict}</b> · Tier:{" "}
              <b>{item.payload.verdict?.autonomy_tier}</b> · Recipient:{" "}
              {item.payload.draft?.recipient?.type ?? "—"} · Citations:{" "}
              {item.payload.draft?.citations?.length ?? 0}
            </div>
            <form action={`${API}/v1/reviews/${item.id}/approve`} method="post" className="mt-3 flex gap-2">
              <button className="rounded bg-green-600 px-3 py-1 text-sm text-white">Approve</button>
              <button className="rounded border px-3 py-1 text-sm">Edit</button>
              <button className="rounded bg-red-600 px-3 py-1 text-sm text-white">Reject</button>
            </form>
          </li>
        ))}
      </ul>
    </main>
  );
}
