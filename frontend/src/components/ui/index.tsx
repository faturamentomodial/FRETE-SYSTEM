import type { PropsWithChildren, InputHTMLAttributes } from "react";

export function Card({ children, className = "" }: PropsWithChildren<{ className?: string }>) {
  return <div className={`rounded-lg p-4 bg-surface border border-border ${className}`}>{children}</div>;
}

export function Badge({
  tone = "default",
  children,
}: PropsWithChildren<{ tone?: "default" | "success" | "warning" | "error" | "info" }>) {
  const tones: Record<string, string> = {
    default: "bg-surface2 text-text-secondary border-border",
    success: "bg-state-success/10 text-state-success border-state-success/30",
    warning: "bg-state-warning/10 text-state-warning border-state-warning/30",
    error: "bg-state-error/10 text-state-error border-state-error/30",
    info: "bg-state-info/10 text-state-info border-state-info/30",
  };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium border ${tones[tone]}`}>
      {children}
    </span>
  );
}

export function Field({ label, children }: PropsWithChildren<{ label: string }>) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-text-secondary">{label}</span>
      {children}
    </label>
  );
}

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={`h-9 rounded px-3 text-sm outline-none bg-surface2 border border-border text-text-primary focus:ring-1 focus:ring-state-info ${props.className || ""}`}
    />
  );
}
