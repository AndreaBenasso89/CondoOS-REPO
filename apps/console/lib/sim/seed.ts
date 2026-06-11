import type { AppState } from "./types";

const now = Date.now();
const iso = (minsAgo: number) => new Date(now - minsAgo * 60_000).toISOString();

// A realistic small Milanese condominium used across all three experiences.
export function seedState(): AppState {
  return {
    building: {
      name: "Condominio Via Dante 12",
      address: "Via Dante 12, 20121 Milano (MI)",
      units: 8,
      plan: "Managed Core",
    },
    units: [
      { id: "u1", identifier: "Interno 1, Scala A", floor: "Piano terra", ownerName: "Elena Greco", residentName: "Elena Greco", millesimi: 110, balanceEur: 0 },
      { id: "u2", identifier: "Interno 2, Scala A", floor: "1° piano", ownerName: "Famiglia Verdi", residentName: "Anna Verdi", millesimi: 120, balanceEur: 0 },
      { id: "u3", identifier: "Interno 3, Scala A", floor: "1° piano", ownerName: "Giulia Conti", residentName: "Giulia Conti", millesimi: 125, balanceEur: -45 },
      { id: "u4", identifier: "Interno 4, Scala A", floor: "2° piano", ownerName: "Paolo Neri", residentName: "Inquilino (locato)", millesimi: 130, balanceEur: 0 },
      { id: "u5", identifier: "Interno 5, Scala A", floor: "2° piano", ownerName: "Marco Rossi", residentName: "Marco Rossi", millesimi: 135, balanceEur: -240 },
      { id: "u6", identifier: "Interno 6, Scala A", floor: "3° piano", ownerName: "Chiara Lombardi", residentName: "Chiara Lombardi", millesimi: 120, balanceEur: 0 },
      { id: "u7", identifier: "Interno 7, Scala A", floor: "3° piano", ownerName: "Davide Costa", residentName: "Davide Costa", millesimi: 70, balanceEur: 0 },
      { id: "u8", identifier: "Negozio, Scala A", floor: "Piano terra", ownerName: "Bottega S.r.l.", residentName: "Bottega S.r.l.", millesimi: 190, balanceEur: -120 },
    ],
    conversations: [
      {
        id: "c1",
        unitId: "u2",
        residentName: "Anna Verdi",
        channel: "whatsapp",
        subject: "Orari raccolta differenziata",
        intent: "info_request",
        state: "answered",
        updatedAt: iso(180),
        messages: [
          { id: "m1", authorId: "p_anna", role: "resident", text: "Buongiorno, dove vanno conferiti i rifiuti?", at: iso(182) },
          { id: "m2", authorId: "agent:concierge", role: "agent", text: "Buongiorno Sig.ra Verdi, la raccolta differenziata va conferita negli appositi bidoni nel cortile interno (art. 9 del regolamento).", at: iso(181), citations: [{ docId: "regolamento", span: "art. 9" }], status: "sent" },
        ],
      },
    ],
    reviews: [
      {
        id: "r1",
        kind: "collections_approval",
        priority: "high",
        tenant: "Via Dante 12",
        title: "Sollecito morosità · Interno 5 (Marco Rossi)",
        draftText:
          "Gentile Sig. Rossi,\nle ricordiamo gentilmente che risulta un saldo a Suo carico di € 240,00 relativo alle spese condominiali del periodo. La invitiamo a regolarizzare entro 14 giorni. Per qualsiasi chiarimento siamo a disposizione.\nCordiali saluti,\nAmministrazione Condominio Via Dante 12",
        recipient: "Marco Rossi (proprietario · Int. 5)",
        verdict: "HOLD",
        tier: "A1",
        confidence: 0.88,
        trippedLayers: [],
        citations: [],
        riskNote: "Reconciliation confermata (€240 = saldo a registro). Tier A1: i solleciti richiedono approvazione umana.",
        status: "pending",
        createdAt: iso(40),
      },
      {
        id: "r2",
        kind: "convocation_approval",
        priority: "normal",
        tenant: "Via Dante 12",
        title: "Convocazione assemblea ordinaria",
        draftText:
          "CONVOCAZIONE ASSEMBLEA ORDINARIA\nÈ convocata l'assemblea ordinaria del Condominio Via Dante 12 per il giorno 28/06/2026 in prima convocazione (ore 18:00) e 29/06/2026 in seconda convocazione (ore 18:00), presso la sala riunioni.\nOrdine del giorno:\n1. Approvazione rendiconto consuntivo;\n2. Approvazione preventivo;\n3. Rinnovo polizza globale fabbricato;\n4. Varie ed eventuali.",
        recipient: "Tutti i proprietari (8 unità)",
        verdict: "HOLD",
        tier: "A1",
        confidence: 0.91,
        trippedLayers: ["L5_legal"],
        citations: [{ docId: "cc", span: "art. 66 disp. att." }],
        riskNote: "Preavviso ≥ 5 giorni e contenuto legale verificati. Richiede firma/approvazione dell'AoR prima dell'invio.",
        status: "pending",
        createdAt: iso(90),
      },
    ],
    tickets: [
      { id: "t1", unitId: "u4", category: "Idraulica", severity: "high", description: "Perdita d'acqua sotto il lavello, interno 4.", status: "scheduled", vendor: "Idraulica Milano S.r.l.", costEur: 180, createdAt: iso(300) },
      { id: "t2", unitId: "u1", category: "Illuminazione", severity: "low", description: "Lampada vano scale piano terra non funziona.", status: "triaged", createdAt: iso(120) },
    ],
    invoices: [
      { id: "i1", vendor: "Enel Energia", number: "2026/00451", amountGross: 612.4, dueDate: iso(-7 * 1440), status: "posted", coa: "60.10 Utenze" },
      { id: "i2", vendor: "Pulizie Splendor", number: "FT-118", amountGross: 240.0, dueDate: iso(-14 * 1440), status: "validated", coa: "62.30 Pulizie" },
      { id: "i3", vendor: "Idraulica Milano S.r.l.", number: "2026-77", amountGross: 180.0, dueDate: iso(-21 * 1440), status: "anomaly", coa: "62.10 Manutenzioni" },
    ],
    documents: [
      { id: "d1", type: "Regolamento", title: "Regolamento di condominio", updatedAt: iso(60 * 24 * 200) },
      { id: "d2", type: "Polizza", title: "Polizza globale fabbricato 2025/26", expiry: iso(-30 * 1440), updatedAt: iso(60 * 24 * 60) },
      { id: "d3", type: "Verbale", title: "Verbale assemblea ordinaria 2025", updatedAt: iso(60 * 24 * 300) },
      { id: "d4", type: "Contratto", title: "Contratto pulizie Splendor", expiry: iso(-90 * 1440), updatedAt: iso(60 * 24 * 120) },
    ],
    compliance: [
      { id: "a1", kind: "Rinnovo polizza globale fabbricato", dueDate: iso(-30 * 1440), severity: "high", status: "remediating" },
      { id: "a2", kind: "Verifica periodica ascensore", dueDate: iso(-75 * 1440), severity: "medium", status: "open" },
      { id: "a3", kind: "Assemblea ordinaria annuale", dueDate: iso(-17 * 1440), severity: "medium", status: "open" },
    ],
    assemblies: [
      {
        id: "as1",
        type: "ordinary",
        scheduledAt: iso(-17 * 1440),
        status: "convoked",
        agenda: ["Approvazione rendiconto consuntivo", "Approvazione preventivo", "Rinnovo polizza globale fabbricato", "Varie ed eventuali"],
      },
    ],
    activity: [], // populated at runtime; the engine seeds a few entries on first load
  };
}
