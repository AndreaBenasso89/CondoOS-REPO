// Admin Portal — Amministratore (AoR) cockpit: registry, accounting, assemblies, compliance.
// The AoR is the legal principal and supervises the agent fleet across their portfolio.

export default function Home() {
  return (
    <main className="mx-auto max-w-4xl p-6">
      <h1 className="text-2xl font-semibold">Amministrazione</h1>
      <section className="mt-6 grid grid-cols-3 gap-4">
        <a className="rounded-xl border p-4 hover:shadow" href="/buildings">Condomìni</a>
        <a className="rounded-xl border p-4 hover:shadow" href="/accounting">Contabilità</a>
        <a className="rounded-xl border p-4 hover:shadow" href="/assemblies">Assemblee</a>
        <a className="rounded-xl border p-4 hover:shadow" href="/compliance">Scadenze</a>
        <a className="rounded-xl border p-4 hover:shadow" href="/collections">Solleciti</a>
        <a className="rounded-xl border p-4 hover:shadow" href="/documents">Documenti</a>
      </section>
    </main>
  );
}
