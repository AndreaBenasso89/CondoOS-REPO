import clsx from "clsx";
import type { ReactNode } from "react";

export const cn = clsx;

export function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.round(diff / 60000);
  if (m < 1) return "ora";
  if (m < 60) return `${m} min fa`;
  const h = Math.round(m / 60);
  if (h < 24) return `${h} h fa`;
  const d = Math.round(h / 24);
  return `${d} g fa`;
}

export function Avatar({ name, hue = 20, size = 36 }: { name: string; hue?: number; size?: number }) {
  const initials = name.split(" ").filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase();
  return (
    <span
      className="inline-flex shrink-0 items-center justify-center rounded-full font-semibold text-white"
      style={{
        width: size, height: size, fontSize: size * 0.36,
        background: `linear-gradient(135deg, hsl(${hue} 55% 52%), hsl(${(hue + 35) % 360} 50% 42%))`,
      }}
    >
      {initials}
    </span>
  );
}

type Tone = "neutral" | "clay" | "sage" | "gold" | "red" | "blue";
const TONES: Record<Tone, string> = {
  neutral: "bg-cream-100 text-ink-soft",
  clay: "bg-clay-50 text-clay-700",
  sage: "bg-sage-50 text-sage",
  gold: "bg-gold-50 text-gold",
  red: "bg-red-50 text-red-700",
  blue: "bg-blue-50 text-blue-700",
};

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: Tone }) {
  return <span className={cn("chip", TONES[tone])}>{children}</span>;
}

export function VerdictBadge({ verdict }: { verdict: string }) {
  const tone: Tone = verdict === "APPROVE" ? "sage" : verdict === "BLOCK" ? "red" : "gold";
  return <Badge tone={tone}>{verdict}</Badge>;
}

export function TierBadge({ tier }: { tier: string }) {
  const tone: Tone = tier === "A3" ? "sage" : tier === "A2" ? "blue" : tier === "A1" ? "gold" : "red";
  return <Badge tone={tone}>{tier}</Badge>;
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("card p-5", className)}>{children}</div>;
}

export function StatCard({ label, value, hint, tone = "neutral" }: { label: string; value: ReactNode; hint?: string; tone?: Tone }) {
  return (
    <div className="card p-5 animate-fade-up">
      <div className="label">{label}</div>
      <div className="mt-1.5 text-3xl font-semibold tracking-tight">{value}</div>
      {hint && <div className={cn("mt-1 text-xs", TONES[tone].split(" ")[1])}>{hint}</div>}
    </div>
  );
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4">
      <div>
        <h1 className="font-serif text-2xl font-semibold tracking-tight">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-ink-soft">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="card flex flex-col items-center justify-center gap-1 p-12 text-center">
      <p className="font-medium text-ink-soft">{title}</p>
      {hint && <p className="text-sm text-ink-faint">{hint}</p>}
    </div>
  );
}

export function Money({ value }: { value: number }) {
  const neg = value < 0;
  return (
    <span className={neg ? "font-medium text-red-600" : ""}>
      {neg ? "−" : ""}€{Math.abs(value).toLocaleString("it-IT", { minimumFractionDigits: 2 })}
    </span>
  );
}
