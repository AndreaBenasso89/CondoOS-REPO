// Ops Console landing — sends you to the review queue.
export default function Home() {
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}>
      <h1>Ops Console</h1>
      <p>
        The human-in-the-loop control surface. The <a href="/reviews">review queue</a> shows every
        artifact the Reputation Firewall held for a human decision — approve, edit, or reject.
      </p>
    </main>
  );
}
