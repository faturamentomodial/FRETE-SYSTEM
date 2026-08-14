import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { Field, Input } from "../../components/ui";
import { Brand } from "../../components/Brand";
import { useAuth } from "../../hooks/useAuth";

export function Login() {
  const { isAuthenticated, isCheckingAuth, login, isLoggingIn, loginError } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");

  if (!isCheckingAuth && isAuthenticated) return <Navigate to="/dashboard" replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await login({ email, password, otp: otp || undefined });
    navigate("/dashboard");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg text-text-primary">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 p-6 rounded-lg bg-surface border border-border">
        <div className="mb-2"><Brand /></div>
        <Field label="E-mail">
          <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </Field>
        <Field label="Senha">
          <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </Field>
        <Field label="Código 2FA (se habilitado)">
          <Input inputMode="numeric" autoComplete="one-time-code" maxLength={6} value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))} />
        </Field>
        {loginError && <p className="text-xs text-state-error">{loginError.message}</p>}
        <button
          type="submit"
          disabled={isLoggingIn}
          className="w-full h-9 rounded text-sm font-medium bg-state-info text-white disabled:opacity-60"
        >
          {isLoggingIn ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
