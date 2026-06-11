"use client";
// Resident "ask a question" page — posts to the gateway webhook and shows what the pipeline did.
// This is the simplest way to user-test the resident experience against the live backend.

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

type PipelineResult = {
  intent: string;
  confidence: number;
  escalated: boolean;
  trail: string[];
  drafts: number;
};

// A fixed demo tenant/unit so repeated questions land in the same condominium.
const DEMO_TENANT = "00000000-0000-0000-0000-000000000001";
const DEMO_UNIT = "00000000-0000-0000-0000-000000000010";

export default function AskPage() {
  const [text, setText] = useState("Quali sono gli orari del portiere?");
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    const res = await fetch(`${API}/v1/webhooks/whatsapp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tenant_id: DEMO_TENANT,
        channel: "whatsapp",
        unit_id: DEMO_UNIT,
        text,
      }),
    });
    setResult(await res.json());
    setLoading(false);
  }

  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}>
      <h1>Fai una domanda</h1>
      <p style={{ color: "#666" }}>
        La tua domanda passa dall’assistente, viene verificata dal Reputation Firewall e — se
        sicura — risposta automaticamente. Altrimenti la rivede una persona.
      </p>
      <form onSubmit={submit} style={{ display: "flex", gap: 8 }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={{ flex: 1, padding: 8, border: "1px solid #ccc", borderRadius: 6 }}
        />
        <button disabled={loading} style={{ padding: "8px 16px", borderRadius: 6 }}>
          {loading ? "..." : "Invia"}
        </button>
      </form>

      {result && (
        <section style={{ marginTop: 24, padding: 16, border: "1px solid #eee", borderRadius: 12 }}>
          <div style={{ fontSize: 13, color: "#666" }}>
            intent: <b>{result.intent}</b> · confidence: <b>{result.confidence.toFixed(2)}</b> ·{" "}
            esito:{" "}
            <b style={{ color: result.escalated ? "#b45309" : "#15803d" }}>
              {result.escalated
                ? "inoltrata a una persona"
                : result.drafts > 0
                ? "gestita automaticamente"
                : "elaborata"}
            </b>
          </div>
          <ol style={{ marginTop: 12, fontSize: 14 }}>
            {result.trail.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
          <p style={{ fontSize: 12, color: "#999" }}>
            (In questa demo il backend gira con stub offline: vedi il <i>percorso</i>, non ancora la
            qualità della risposta AI.)
          </p>
        </section>
      )}
    </main>
  );
}
