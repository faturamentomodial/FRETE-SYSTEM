import type { PropsWithChildren } from "react";
import { Card } from "../../components/ui";

export const inputClass = "h-9 w-full rounded border border-border bg-surface2 px-3 text-sm text-text-primary outline-none focus:ring-1 focus:ring-state-info";
export const buttonPrimary = "h-9 rounded bg-state-info px-4 text-sm text-white disabled:opacity-50";

export function Section({ title, description, children }: PropsWithChildren<{ title: string; description: string }>) {
  return <Card><h2 className="text-sm font-medium">{title}</h2><p className="mt-1 text-xs text-text-secondary">{description}</p><div className="mt-5">{children}</div></Card>;
}
export function Feedback({ error, success }: { error?: unknown; success?: boolean }) {
  return <>{error && <p className="text-xs text-state-error">{error instanceof Error ? error.message : "Não foi possível salvar."}</p>}{success && <p className="text-xs text-state-success">Alterações salvas.</p>}</>;
}
export function Toggle({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) {
  return <label className="flex cursor-pointer items-center gap-2 text-sm"><button type="button" role="switch" aria-checked={checked} onClick={() => onChange(!checked)} className={`relative h-5 w-9 rounded-full transition ${checked ? "bg-state-success" : "bg-border"}`}><span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition ${checked ? "left-[18px]" : "left-0.5"}`} /></button>{label}</label>;
}
