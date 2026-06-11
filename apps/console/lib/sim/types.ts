// Domain types for the simulated CondominioOS backend (mirrors services/condominioos models).

export type Role = "resident" | "operator" | "admin";

export interface Persona {
  id: string;
  name: string;
  role: Role;
  title: string; // e.g. "Proprietario · Int. 5" or "Operations Specialist"
  email: string;
  unitId?: string; // residents/owners
  avatarHue: number; // for generated avatar color
}

export interface Unit {
  id: string;
  identifier: string; // "Interno 5, Scala A"
  floor: string;
  ownerName: string;
  residentName: string;
  millesimi: number;
  balanceEur: number; // negative = arrears
}

export type Tier = "A3" | "A2" | "A1" | "A0";
export type Verdict = "APPROVE" | "HOLD" | "BLOCK" | "REVISE";

export interface Citation { docId: string; span: string }

export interface Message {
  id: string;
  authorId: string; // persona id, or "agent:concierge", "system"
  role: "resident" | "agent" | "operator";
  text: string;
  at: string; // ISO
  citations?: Citation[];
  status?: "sent" | "held" | "draft";
}

export interface Conversation {
  id: string;
  unitId: string;
  residentName: string;
  channel: "whatsapp" | "email" | "web";
  subject: string;
  intent: string;
  messages: Message[];
  state: "answered" | "awaiting_review" | "escalated" | "open";
  updatedAt: string;
}

export type ReviewKind =
  | "firewall_hold"
  | "escalation"
  | "collections_approval"
  | "convocation_approval";

export interface ReviewItem {
  id: string;
  kind: ReviewKind;
  priority: "high" | "normal";
  tenant: string;
  conversationId?: string;
  title: string;
  draftText: string;
  recipient: string;
  verdict: Verdict;
  tier: Tier;
  confidence: number;
  trippedLayers: string[];
  citations: Citation[];
  riskNote: string;
  status: "pending" | "approved" | "rejected" | "escalated";
  decidedBy?: string;
  decidedAt?: string;
  note?: string;
  createdAt: string;
}

export interface Ticket {
  id: string;
  unitId: string;
  category: string;
  severity: "low" | "medium" | "high" | "emergency";
  description: string;
  status: "open" | "triaged" | "scheduled" | "resolved";
  vendor?: string;
  costEur?: number;
  createdAt: string;
}

export interface Invoice {
  id: string;
  vendor: string;
  number: string;
  amountGross: number;
  dueDate: string;
  status: "extracted" | "validated" | "posted" | "paid" | "anomaly";
  coa: string;
}

export interface DocItem {
  id: string;
  type: string;
  title: string;
  expiry?: string;
  updatedAt: string;
}

export interface ComplianceAlert {
  id: string;
  kind: string;
  dueDate: string;
  severity: "high" | "medium" | "low";
  status: "open" | "remediating" | "resolved";
}

export interface Assembly {
  id: string;
  type: "ordinary" | "extraordinary";
  scheduledAt: string;
  status: "scheduled" | "convoked" | "held";
  agenda: string[];
}

export interface ActivityEvent {
  id: string;
  at: string;
  actor: string; // human-readable
  actorRole: Role | "agent" | "system";
  action: string;
  detail: string;
  entity: string;
  hash: string; // simulated audit hash chain
  prevHash: string;
}

export interface AppState {
  building: { name: string; address: string; units: number; plan: string };
  units: Unit[];
  conversations: Conversation[];
  reviews: ReviewItem[];
  tickets: Ticket[];
  invoices: Invoice[];
  documents: DocItem[];
  compliance: ComplianceAlert[];
  assemblies: Assembly[];
  activity: ActivityEvent[];
}
