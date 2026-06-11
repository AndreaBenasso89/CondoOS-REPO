// Resident Portal — landing. Residents ask questions (routed to the Concierge agent), view
// documents, balances, and tickets. Outbound replies are always firewall-gated server-side.

export default function Home() {
  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="text-2xl font-semibold">Il tuo condominio, semplice.</h1>
      <p className="mt-2 text-gray-600">
        Fai una domanda, segnala un guasto, consulta documenti e pagamenti. Rispondiamo in pochi
        minuti.
      </p>
      <section className="mt-6 grid grid-cols-2 gap-4">
        <a className="rounded-xl border p-4 hover:shadow" href="/ask">Fai una domanda</a>
        <a className="rounded-xl border p-4 hover:shadow" href="/tickets">Segnala un guasto</a>
        <a className="rounded-xl border p-4 hover:shadow" href="/documents">Documenti</a>
        <a className="rounded-xl border p-4 hover:shadow" href="/payments">Pagamenti</a>
      </section>
    </main>
  );
}
