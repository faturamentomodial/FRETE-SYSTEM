import { Edit3, Plus, Power, X } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Badge, Field, Input } from "../../components/ui";
import {
  useAtualizarUsuario,
  useCriarUsuario,
  useRoles,
  useStatusUsuario,
  useUsuarios,
} from "../../hooks/useConfiguracoes";
import type { Usuario, UsuarioInput } from "../../types/configuracoes";
import { buttonPrimary, Feedback, Section } from "./shared";

export function UsuariosSection() {
  const usuarios = useUsuarios();
  const roles = useRoles();
  const criar = useCriarUsuario();
  const atualizar = useAtualizarUsuario();
  const status = useStatusUsuario();
  const [editando, setEditando] = useState<Usuario | null>(null);
  const [form, setForm] = useState(false);
  const [d, setD] = useState<UsuarioInput>({
    nome: "",
    email: "",
    password: "",
    role_ids: [],
  });
  const abrir = (u: Usuario | null) => {
    setEditando(u);
    setD(
      u
        ? {
            nome: u.nome,
            email: u.email,
            password: "",
            role_ids: u.roles.map((r) => r.id),
          }
        : {
            nome: "",
            email: "",
            password: "",
            role_ids: roles.data?.slice(0, 1).map((r) => r.id) ?? [],
          },
    );
    setForm(true);
  };
  const role = (id: string) =>
    setD((v) => ({
      ...v,
      role_ids: v.role_ids.includes(id)
        ? v.role_ids.filter((x) => x !== id)
        : [...v.role_ids, id],
    }));
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!editando && !d.password) return;
    const payload = { ...d, password: d.password || undefined };
    if (editando)
      await atualizar.mutateAsync({ id: editando.id, dados: payload });
    else await criar.mutateAsync(payload);
    setForm(false);
  }
  const erro = criar.error || atualizar.error;
  return (
    <div className="space-y-4">
      <Section
        title="Usuários e permissões"
        description="Administra acesso sem excluir o histórico associado a cada usuário."
      >
        <div className="mb-4 flex justify-end">
          <button
            onClick={() => abrir(null)}
            className={`${buttonPrimary} inline-flex items-center gap-2`}
          >
            <Plus size={14} />
            Novo usuário
          </button>
        </div>
        {form && (
          <form
            onSubmit={submit}
            className="mb-5 rounded border border-border bg-surface2 p-4"
          >
            <div className="mb-3 flex justify-between">
              <strong className="text-sm">
                {editando ? "Editar usuário" : "Novo usuário"}
              </strong>
              <button type="button" onClick={() => setForm(false)}>
                <X size={15} />
              </button>
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              <Field label="Nome">
                <Input
                  required
                  minLength={2}
                  value={d.nome}
                  onChange={(e) => setD({ ...d, nome: e.target.value })}
                />
              </Field>
              <Field label="E-mail">
                <Input
                  required
                  type="email"
                  value={d.email}
                  onChange={(e) => setD({ ...d, email: e.target.value })}
                />
              </Field>
              <Field label={editando ? "Nova senha (opcional)" : "Senha"}>
                <Input
                  required={!editando}
                  minLength={12}
                  type="password"
                  value={d.password ?? ""}
                  onChange={(e) => setD({ ...d, password: e.target.value })}
                />
              </Field>
            </div>
            <div className="mt-4">
              <p className="mb-2 text-xs font-medium text-text-secondary">
                Perfis de acesso
              </p>
              <div className="flex flex-wrap gap-3">
                {roles.data?.map((r) => (
                  <label key={r.id} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={d.role_ids.includes(r.id)}
                      onChange={() => role(r.id)}
                    />
                    {r.nome}
                  </label>
                ))}
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <Feedback error={erro} />
              <button
                disabled={
                  !d.role_ids.length || criar.isPending || atualizar.isPending
                }
                className={buttonPrimary}
              >
                Salvar usuário
              </button>
            </div>
          </form>
        )}
        <div className="grid gap-3 xl:grid-cols-2">
          {usuarios.data?.map((u) => (
            <div
              key={u.id}
              className="rounded border border-border bg-surface2 p-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <strong className="text-sm">{u.nome}</strong>
                  <p className="mt-1 text-xs text-text-secondary">{u.email}</p>
                </div>
                <Badge tone={u.ativa ? "success" : "warning"}>
                  {u.ativa ? "Ativo" : "Inativo"}
                </Badge>
              </div>
              <div className="mt-3 flex flex-wrap gap-1">
                {u.roles.map((r) => (
                  <Badge key={r.id} tone="info">
                    {r.nome}
                  </Badge>
                ))}
              </div>
              <p className="mt-3 text-xs text-text-secondary">
                Último acesso:{" "}
                {u.last_login_at
                  ? new Date(u.last_login_at).toLocaleString("pt-BR")
                  : "Nunca"}
              </p>
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => abrir(u)}
                  className="inline-flex h-8 items-center gap-2 rounded border border-border px-3 text-xs"
                >
                  <Edit3 size={13} />
                  Editar
                </button>
                <button
                  disabled={status.isPending}
                  onClick={() => status.mutate({ id: u.id, ativa: !u.ativa })}
                  className={`inline-flex h-8 items-center gap-2 rounded border px-3 text-xs ${u.ativa ? "border-state-error/40 text-state-error" : "border-state-success/40 text-state-success"}`}
                >
                  <Power size={13} />
                  {u.ativa ? "Desativar" : "Ativar"}
                </button>
              </div>
            </div>
          ))}
        </div>
        <Feedback error={usuarios.error || status.error} />
      </Section>
    </div>
  );
}
