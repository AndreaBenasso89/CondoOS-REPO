// Decision engine — a faithful TypeScript port of the backend's orchestrator + Reputation Firewall
// logic (services/condominioos/agents + firewall). Keeps the simulated console behaving like the
// real system so what you test here reflects the architecture.

import type { Citation, Tier, Verdict } from "./types";

const KNOWLEDGE: { q: string[]; answer: string; cite: Citation }[] = [
  {
    q: ["portiere", "orari"],
    answer:
      "Gli orari del portiere sono dalle 8:00 alle 12:00 dal lunedì al venerdì; riceve al piano terra (artt. 3–4 del regolamento).",
    cite: { docId: "regolamento", span: "artt. 3–4" },
  },
  {
    q: ["rifiuti", "differenziata", "raccolta", "spazzatura"],
    answer:
      "La raccolta differenziata va conferita negli appositi bidoni nel cortile interno (art. 9 del regolamento).",
    cite: { docId: "regolamento", span: "art. 9" },
  },
  {
    q: ["assemblea", "quando", "convocazione"],
    answer:
      "La prossima assemblea ordinaria è convocata per il 28/06/2026 (prima convocazione); riceverà la convocazione formale via email/PEC.",
    cite: { docId: "convocazione", span: "assemblea 2026" },
  },
];

export interface Classification {
  intent: string;
  confidence: number;
}

const RULES: Record<string, string[]> = {
  maintenance: ["perdita", "guasto", "rotto", "ascensore", "riscaldamento", "citofono", "non funziona", "tecnico"],
  arrears: ["sollecito", "insoluto", "morosità", "non ho pagato", "saldo", "importo"],
  payment: ["pagamento", "bonifico", "ricevuta", "quota", "rata"],
  assembly: ["assemblea", "convocazione", "delega", "verbale", "ordine del giorno"],
  document: ["documento", "regolamento", "polizza", "contratto"],
  legal: ["avvocato", "diffida", "causa", "legale", "denuncia"],
  complaint: ["reclamo", "vergogna", "inaccettabile", "scandalo"],
};

export function classify(text: string): Classification {
  const t = text.toLowerCase();
  for (const [intent, kws] of Object.entries(RULES)) {
    if (kws.some((k) => t.includes(k))) return { intent, confidence: 0.88 };
  }
  return text.trim() ? { intent: "info_request", confidence: 0.82 } : { intent: "unknown", confidence: 0 };
}

export interface AgentOutcome {
  intent: string;
  confidence: number;
  answer?: string;
  citations: Citation[];
  verdict: Verdict;
  tier: Tier;
  trippedLayers: string[];
  riskNote: string;
  disposition: "sent" | "held" | "escalated";
}

// Mirrors: orchestrator → concierge (grounded RAG) → Reputation Firewall (8 layers) → gate.
export function runConcierge(text: string): AgentOutcome {
  const { intent, confidence } = classify(text);

  if (intent === "legal" || intent === "complaint") {
    return {
      intent, confidence, citations: [], verdict: "HOLD", tier: "A0",
      trippedLayers: ["L5_legal"],
      riskNote: intent === "legal"
        ? "Interpretazione legale: mai automatizzata — inoltrata all'Amministratore (A0)."
        : "Reclamo / sentiment negativo: gestione umana (A0).",
      disposition: "escalated",
    };
  }

  const t = text.toLowerCase();
  const hit = KNOWLEDGE.find((k) => k.q.some((kw) => t.includes(kw)));
  if (!hit) {
    return {
      intent, confidence, citations: [], verdict: "HOLD", tier: "A1",
      trippedLayers: ["L2_grounding"],
      riskNote: "Nessuna fonte attendibile (knowledge miss): l'assistente non improvvisa, inoltra a una persona.",
      disposition: "escalated",
    };
  }

  // Grounded + low risk → APPROVE (A2/A3). Coverage drives confidence.
  const conf = Math.min(0.95, confidence + 0.08);
  return {
    intent, confidence: conf, answer: hit.answer, citations: [hit.cite],
    verdict: "APPROVE", tier: conf >= 0.85 ? "A3" : "A2", trippedLayers: [],
    riskNote: "Risposta ancorata e citata, basso rischio: inviata automaticamente.",
    disposition: "sent",
  };
}

// Simulated hash-chain (audit-by-design): hash_n = sha-ish(prev + payload).
export function chainHash(prev: string, payload: string): string {
  let h = 0;
  const s = prev + "|" + payload;
  for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return (h >>> 0).toString(16).padStart(8, "0") + prev.slice(0, 8);
}

export const LAYER_LABELS: Record<string, string> = {
  L1_schema_policy: "Schema & Policy",
  L2_grounding: "Grounding / Anti-hallucination",
  L3_pii_recipient: "PII & Recipient",
  L4_financial: "Financial Integrity",
  L5_legal: "Legal Safety",
  L6_tone: "Tone & Brand",
  L7_risk: "Risk Scoring",
  L8_autonomy: "Confidence & Autonomy Gate",
};
