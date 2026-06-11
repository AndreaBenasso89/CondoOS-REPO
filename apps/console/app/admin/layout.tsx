import { AuthedShell } from "@/components/AuthedShell";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <AuthedShell allow="admin">{children}</AuthedShell>;
}
