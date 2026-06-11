// Root layout for the Ops Console (human-in-the-loop control surface).
import type { ReactNode } from "react";

export const metadata = { title: "CondominioOS — Ops Console" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="it">
      <body style={{ fontFamily: "system-ui, sans-serif", margin: 0 }}>
        <header style={{ borderBottom: "1px solid #eee", padding: "12px 24px" }}>
          <strong>CondominioOS</strong> · Ops Console
          <a href="/reviews" style={{ marginLeft: 16, fontSize: 14 }}>Review queue</a>
        </header>
        {children}
      </body>
    </html>
  );
}
