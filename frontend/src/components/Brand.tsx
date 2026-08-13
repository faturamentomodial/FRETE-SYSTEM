export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex h-8 w-8 items-center justify-center rounded-md bg-state-info text-xs font-bold tracking-tight text-white shadow-sm shadow-state-info/20">
        FW
      </div>
      {!compact && <span className="text-sm font-semibold tracking-tight text-text-primary">FreteWay</span>}
    </div>
  );
}
