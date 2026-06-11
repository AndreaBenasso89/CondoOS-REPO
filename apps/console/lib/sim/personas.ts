import type { Persona } from "./types";

// Seeded demo identities you can log in as / switch between to assess each experience.
export const PERSONAS: Persona[] = [
  // Residents & owners
  {
    id: "p_giulia",
    name: "Giulia Conti",
    role: "resident",
    title: "Residente · Interno 3",
    email: "giulia.conti@example.it",
    unitId: "u3",
    avatarHue: 18,
  },
  {
    id: "p_marco",
    name: "Marco Rossi",
    role: "resident",
    title: "Proprietario · Interno 5",
    email: "marco.rossi@example.it",
    unitId: "u5",
    avatarHue: 210,
  },
  {
    id: "p_anna",
    name: "Anna Verdi",
    role: "resident",
    title: "Residente · Interno 2",
    email: "anna.verdi@example.it",
    unitId: "u2",
    avatarHue: 140,
  },
  // Operations
  {
    id: "p_luca",
    name: "Luca Ferrari",
    role: "operator",
    title: "Operations Specialist",
    email: "luca.ferrari@condominioos.eu",
    avatarHue: 265,
  },
  // Admin (Amministratore of Record)
  {
    id: "p_sara",
    name: "Avv. Sara Bianchi",
    role: "admin",
    title: "Amministratore (AoR)",
    email: "sara.bianchi@condominioos.eu",
    avatarHue: 330,
  },
];

export const personaById = (id: string) => PERSONAS.find((p) => p.id === id);
export const personasByRole = (role: Persona["role"]) => PERSONAS.filter((p) => p.role === role);
