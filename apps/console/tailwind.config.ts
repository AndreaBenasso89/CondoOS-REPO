import type { Config } from "tailwindcss";

/**
 * CondominioOS design system — a warm, calm, trustworthy palette suited to a regulated
 * property/fintech service. Cream surfaces, a clay/terracotta brand accent, warm neutral inks.
 */
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: { DEFAULT: "#FAF8F3", 100: "#F4F1E9", 200: "#EAE5D9" },
        ink: { DEFAULT: "#211C16", soft: "#544C40", faint: "#8A8072" },
        clay: { DEFAULT: "#C2613D", 50: "#FBF1EC", 100: "#F3D9CD", 600: "#A94E2E", 700: "#8A3F25" },
        sage: { DEFAULT: "#4F7A5B", 50: "#EEF4EF" },
        gold: { DEFAULT: "#B98326", 50: "#FAF2E1" },
        line: "#E7E1D5",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        serif: ["var(--font-serif)", "ui-serif", "Georgia", "serif"],
      },
      boxShadow: {
        soft: "0 1px 2px rgba(33,28,22,0.04), 0 6px 24px -12px rgba(33,28,22,0.12)",
        lift: "0 2px 6px rgba(33,28,22,0.06), 0 18px 40px -20px rgba(33,28,22,0.22)",
      },
      borderRadius: { xl: "0.875rem", "2xl": "1.125rem" },
      keyframes: {
        "fade-up": { from: { opacity: "0", transform: "translateY(6px)" }, to: { opacity: "1", transform: "none" } },
      },
      animation: { "fade-up": "fade-up 0.35s ease both" },
    },
  },
  plugins: [],
};
export default config;
