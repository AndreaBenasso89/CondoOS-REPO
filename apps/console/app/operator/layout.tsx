import { AuthedShell } from "@/components/AuthedShell";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <AuthedShell allow="operator">{children}</AuthedShell>;
}
