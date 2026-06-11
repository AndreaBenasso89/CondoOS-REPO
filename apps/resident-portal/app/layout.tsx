// Root layout for the Resident Portal.
import type { ReactNode } from "react";

export const metadata = { title: "CondominioOS — Il tuo condominio" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="it">
      <body style={{ fontFamily: "system-ui, sans-serif", margin: 0 }}>
        <header style={{ borderBottom: "1px solid #eee", padding: "12px 24px" }}>
          <strong>CondominioOS</strong>
          <a href="/" style={{ marginLeft: 16, fontSize: 14 }}>Home</a>
          <a href="/ask" style={{ marginLeft: 12, fontSize: 14 }}>Fai una domanda</a>
        </header>
        {children}
      </body>
    </html>
  );
}
