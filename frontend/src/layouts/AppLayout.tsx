import { Bell, LayoutDashboard, ListChecks, Menu, PlusCircle, Plug, Settings, Truck, User, History as HistoryIcon, Wifi, WifiOff } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { apiClient } from "../api/client";
import { Brand } from "../components/Brand";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/cotacoes/nova", label: "Nova cotação", icon: PlusCircle },
  { to: "/cotacoes", label: "Cotações", icon: ListChecks },
  { to: "/transportadoras", label: "Transportadoras", icon: Truck },
  { to: "/historico", label: "Histórico", icon: HistoryIcon },
  { to: "/integracoes", label: "Integrações", icon: Plug },
  { to: "/configuracoes", label: "Configurações", icon: Settings },
];

function useBackendStatus() {
  const [online, setOnline] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function check() {
      try {
        await apiClient.get("/health");
        if (mounted) setOnline(true);
      } catch {
        if (mounted) setOnline(false);
      }
    }
    check();
    const interval = setInterval(check, 15_000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return online;
}

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const backendOnline = useBackendStatus();

  return (
    <div className="flex min-h-screen bg-bg text-text-primary">
      {mobileOpen && (
        <div className="fixed inset-0 z-20 bg-black/50 md:hidden" onClick={() => setMobileOpen(false)} />
      )}
      <aside
        className={`fixed md:static z-30 top-0 left-0 h-full w-64 flex flex-col bg-surface border-r border-border transition-transform duration-200 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="flex h-14 items-center px-4 border-b border-border"><Brand /></div>
        <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `w-full flex items-center gap-2.5 px-3 py-2 rounded text-sm transition-colors ${
                  isActive ? "bg-surface2 text-text-primary font-medium" : "text-text-secondary"
                }`
              }
            >
              <item.icon size={16} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 flex items-center gap-3 px-4 sticky top-0 z-10 bg-bg border-b border-border">
          <button className="md:hidden" onClick={() => setMobileOpen(true)}>
            <Menu size={20} />
          </button>
          <div className="flex-1" />
          <div className={`flex items-center gap-1.5 text-xs ${backendOnline ? "text-state-success" : "text-state-error"}`}>
            {backendOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
            <span className="hidden sm:inline">{backendOnline ? "Backend conectado" : "Backend indisponível"}</span>
          </div>
          <Bell size={17} className="text-text-secondary" />
          <div className="w-7 h-7 rounded-full flex items-center justify-center bg-surface2">
            <User size={14} className="text-text-secondary" />
          </div>
        </header>
        <main className="flex-1 p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
