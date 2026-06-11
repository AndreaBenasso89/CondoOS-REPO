"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { chainHash, runConcierge } from "./engine";
import { seedState } from "./seed";
import type {
  ActivityEvent,
  AppState,
  Conversation,
  Persona,
  ReviewItem,
  Ticket,
} from "./types";

const STORAGE_KEY = "condominioos.sim.v1";

interface StoreApi {
  state: AppState;
  reset: () => void;
  ask: (persona: Persona, text: string, channel?: Conversation["channel"]) => string; // conversationId
  decideReview: (
    id: string,
    decision: "approved" | "rejected" | "escalated",
    reviewer: Persona,
    opts?: { editedText?: string; note?: string },
  ) => void;
  reportTicket: (persona: Persona, description: string) => void;
  log: (e: Omit<ActivityEvent, "id" | "at" | "hash" | "prevHash">) => void;
}

const StoreContext = createContext<StoreApi | null>(null);

let counter = 0;
const uid = (p: string) => `${p}_${Date.now().toString(36)}_${(counter++).toString(36)}`;

export function StoreProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AppState>(seedState);
  const [hydrated, setHydrated] = useState(false);

  // Hydrate from localStorage so actions persist and are visible across role switches.
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setState(JSON.parse(raw));
      else setState(withSeedActivity(seedState()));
    } catch {
      setState(withSeedActivity(seedState()));
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state, hydrated]);

  const api = useMemo<StoreApi>(() => {
    const appendActivity = (
      s: AppState,
      e: Omit<ActivityEvent, "id" | "at" | "hash" | "prevHash">,
    ): AppState => {
      const prev = s.activity[0]?.hash ?? "00000000";
      const ev: ActivityEvent = {
        ...e,
        id: uid("ev"),
        at: new Date().toISOString(),
        prevHash: prev,
        hash: chainHash(prev, `${e.actor}:${e.action}:${e.entity}`),
      };
      return { ...s, activity: [ev, ...s.activity] };
    };

    return {
      state,
      reset: () => setState(withSeedActivity(seedState())),

      log: (e) => setState((s) => appendActivity(s, e)),

      ask: (persona, text, channel = "web") => {
        const conversationId = uid("c");
        const outcome = runConcierge(text);
        const unitId = persona.unitId ?? "u3";
        setState((s) => {
          const messages: Conversation["messages"] = [
            { id: uid("m"), authorId: persona.id, role: "resident", text, at: new Date().toISOString() },
          ];
          if (outcome.disposition === "sent" && outcome.answer) {
            messages.push({
              id: uid("m"), authorId: "agent:concierge", role: "agent", text: outcome.answer,
              at: new Date().toISOString(), citations: outcome.citations, status: "sent",
            });
          }
          const convo: Conversation = {
            id: conversationId, unitId, residentName: persona.name, channel,
            subject: text.length > 48 ? text.slice(0, 46) + "…" : text,
            intent: outcome.intent,
            state: outcome.disposition === "sent" ? "answered"
              : outcome.disposition === "escalated" ? "escalated" : "awaiting_review",
            messages, updatedAt: new Date().toISOString(),
          };
          let next: AppState = { ...s, conversations: [convo, ...s.conversations] };

          // Held / escalated → create a review item for the operator.
          if (outcome.disposition !== "sent") {
            const review: ReviewItem = {
              id: uid("r"),
              kind: outcome.intent === "legal" || outcome.intent === "complaint" ? "escalation" : "firewall_hold",
              priority: outcome.tier === "A0" ? "high" : "normal",
              tenant: s.building.name, conversationId,
              title: `${outcome.intent} · ${persona.name}`,
              draftText: outcome.answer ?? `(Richiesta del residente) "${text}"`,
              recipient: `${persona.name} (${persona.title})`,
              verdict: outcome.verdict, tier: outcome.tier, confidence: outcome.confidence,
              trippedLayers: outcome.trippedLayers, citations: outcome.citations,
              riskNote: outcome.riskNote, status: "pending",
              createdAt: new Date().toISOString(),
            };
            next = { ...next, reviews: [review, ...next.reviews] };
          }

          next = appendActivity(next, {
            actor: persona.name, actorRole: "resident",
            action: outcome.disposition === "sent" ? "Domanda risolta automaticamente" : "Richiesta inoltrata a revisione",
            detail: `"${text}" → intent=${outcome.intent}, verdict=${outcome.verdict}, tier=${outcome.tier}`,
            entity: `conversation:${conversationId.slice(0, 8)}`,
          });
          if (outcome.disposition === "sent") {
            next = appendActivity(next, {
              actor: "Concierge Agent", actorRole: "agent", action: "Messaggio inviato (Firewall APPROVE)",
              detail: outcome.answer ?? "", entity: `conversation:${conversationId.slice(0, 8)}`,
            });
          }
          return next;
        });
        return conversationId;
      },

      decideReview: (id, decision, reviewer, opts) => {
        setState((s) => {
          const review = s.reviews.find((r) => r.id === id);
          if (!review) return s;
          const reviews = s.reviews.map((r) =>
            r.id === id
              ? { ...r, status: decision, decidedBy: reviewer.name, decidedAt: new Date().toISOString(), note: opts?.note }
              : r,
          );
          let conversations = s.conversations;
          if (decision === "approved" && review.conversationId) {
            const text = opts?.editedText ?? review.draftText;
            conversations = s.conversations.map((c) =>
              c.id === review.conversationId
                ? {
                    ...c, state: "answered", updatedAt: new Date().toISOString(),
                    messages: [
                      ...c.messages,
                      { id: uid("m"), authorId: reviewer.id, role: "operator" as const, text, at: new Date().toISOString(), status: "sent" as const, citations: review.citations },
                    ],
                  }
                : c,
            );
          }
          let next: AppState = { ...s, reviews, conversations };
          next = appendActivity(next, {
            actor: reviewer.name, actorRole: reviewer.role,
            action: `Revisione ${decision === "approved" ? "approvata e inviata" : decision === "rejected" ? "respinta" : "riassegnata"}`,
            detail: `${review.title}${opts?.note ? ` — nota: ${opts.note}` : ""}`,
            entity: `review:${id.slice(0, 8)}`,
          });
          return next;
        });
      },

      reportTicket: (persona, description) => {
        setState((s) => {
          const emergency = /gas|fumo|incendio|allag|crollo/i.test(description);
          const ticket: Ticket = {
            id: uid("t"), unitId: persona.unitId ?? "u3", category: "Da classificare",
            severity: emergency ? "emergency" : "medium", description,
            status: emergency ? "open" : "triaged", createdAt: new Date().toISOString(),
          };
          let next: AppState = { ...s, tickets: [ticket, ...s.tickets] };
          next = appendActivity(next, {
            actor: persona.name, actorRole: "resident", action: "Segnalazione guasto creata",
            detail: `${description}${emergency ? " — EMERGENZA, on-call + notifica umana" : ""}`,
            entity: `ticket:${ticket.id.slice(0, 8)}`,
          });
          return next;
        });
      },
    };
  }, [state]);

  return <StoreContext.Provider value={api}>{children}</StoreContext.Provider>;
}

export function useStore() {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error("useStore must be used within StoreProvider");
  return ctx;
}

// Give the activity feed a few realistic entries on first load so cross-visibility isn't empty.
function withSeedActivity(s: AppState): AppState {
  const seedEvents: Omit<ActivityEvent, "id" | "at" | "hash" | "prevHash">[] = [
    { actor: "Compliance Agent", actorRole: "agent", action: "Alert scadenza", detail: "Polizza globale fabbricato scaduta — rinnovo aperto", entity: "obligation:a1" },
    { actor: "Accounting Agent", actorRole: "agent", action: "Fattura registrata", detail: "Enel Energia €612,40 → 60.10 Utenze", entity: "invoice:i1" },
    { actor: "Accounting Agent", actorRole: "agent", action: "Anomalia fattura (HOLD)", detail: "Idraulica Milano FT 2026-77 €180 — possibile duplicato", entity: "invoice:i3" },
    { actor: "Maintenance Agent", actorRole: "agent", action: "Intervento programmato", detail: "Perdita Int. 4 → Idraulica Milano, martedì 9–12", entity: "ticket:t1" },
    { actor: "Concierge Agent", actorRole: "agent", action: "Domanda risolta automaticamente", detail: "Raccolta differenziata (art. 9) → Anna Verdi", entity: "conversation:c1" },
  ];
  let out = s;
  // Insert oldest-first so the chain reads naturally (newest at index 0).
  for (let i = seedEvents.length - 1; i >= 0; i--) {
    const e = seedEvents[i];
    const prev = out.activity[0]?.hash ?? "00000000";
    out = {
      ...out,
      activity: [
        { ...e, id: uid("ev"), at: new Date(Date.now() - (i + 1) * 23 * 60_000).toISOString(), prevHash: prev, hash: chainHash(prev, `${e.actor}:${e.action}:${e.entity}`) },
        ...out.activity,
      ],
    };
  }
  return out;
}
