"""Autenticação de usuários — KCS News Generator.

A tabela `usuarios` usa senha_hash + senha_salt (PBKDF2-SHA256).
Compatível com o esquema do AuditAI.
"""

import hashlib
import hmac
import streamlit as st


# ─────────────────────────────────────────────────────────────
#  Hash
# ─────────────────────────────────────────────────────────────

def _hash_password(password: str, salt: str) -> str:
    """Retorna PBKDF2-HMAC-SHA256 hex com 260 000 iterações."""
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        260_000,
    )
    return dk.hex()


def _verify(password: str, salt: str, stored_hash: str) -> bool:
    computed = _hash_password(password, salt)
    return hmac.compare_digest(computed, stored_hash)


# ─────────────────────────────────────────────────────────────
#  Garantia de usuário admin inicial
# ─────────────────────────────────────────────────────────────

def _ensure_admin(sb) -> None:
    """Cria o usuário admin com senha '1234' se não existir."""
    try:
        res = sb.table("usuarios").select("id").eq("usuario", "admin").execute()
        if not res.data:
            import os
            salt = os.urandom(32).hex()
            h    = _hash_password("1234", salt)
            sb.table("usuarios").insert({
                "usuario":      "admin",
                "nome_exibicao": "Administrador",
                "senha_hash":   h,
                "senha_salt":   salt,
                "perfil":       "admin",
                "trocar_senha": True,
            }).execute()
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
#  Autenticação
# ─────────────────────────────────────────────────────────────

def authenticate(sb, usuario: str, senha: str) -> dict | None:
    """
    Verifica credenciais.
    Retorna o dict do usuário se válido e ativo, None caso contrário.
    """
    try:
        res = (
            sb.table("usuarios")
            .select("id, usuario, nome_exibicao, senha_hash, senha_salt, perfil, ativo, trocar_senha")
            .eq("usuario", usuario.strip().lower())
            .eq("ativo", True)
            .execute()
        )
        if not res.data:
            return None

        user = res.data[0]
        if not _verify(senha, user["senha_salt"], user["senha_hash"]):
            return None

        # Atualiza ultimo_acesso
        from datetime import datetime, timezone
        sb.table("usuarios").update(
            {"ultimo_acesso": datetime.now(timezone.utc).isoformat()}
        ).eq("id", user["id"]).execute()

        return user
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
#  Troca de senha
# ─────────────────────────────────────────────────────────────

def change_password(sb, user_id: str, nova_senha: str) -> bool:
    try:
        import os
        salt = os.urandom(32).hex()
        h    = _hash_password(nova_senha, salt)
        sb.table("usuarios").update({
            "senha_hash":   h,
            "senha_salt":   salt,
            "trocar_senha": False,
        }).eq("id", user_id).execute()
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────
#  Gestão de usuários (admin)
# ─────────────────────────────────────────────────────────────

def list_users(sb):
    """Retorna DataFrame com todos os usuários."""
    import pandas as pd
    try:
        res = sb.table("usuarios").select(
            "id, usuario, nome_exibicao, perfil, ativo, criado_em, ultimo_acesso, trocar_senha"
        ).order("criado_em").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception:
        return __import__("pandas").DataFrame()


PERFIS_VALIDOS = ["kcseditor", "admin"]

def create_user(sb, usuario: str, nome_exibicao: str, senha: str, perfil: str) -> bool:
    if perfil not in PERFIS_VALIDOS:
        return False
    try:
        import os
        salt = os.urandom(32).hex()
        h    = _hash_password(senha, salt)
        sb.table("usuarios").insert({
            "usuario":       usuario,
            "nome_exibicao": nome_exibicao,
            "senha_hash":    h,
            "senha_salt":    salt,
            "perfil":        perfil,
            "trocar_senha":  True,
        }).execute()
        return True
    except Exception:
        return False


def toggle_user(sb, user_id: str, ativo: bool) -> bool:
    try:
        sb.table("usuarios").update({"ativo": ativo}).eq("id", user_id).execute()
        return True
    except Exception:
        return False


def reset_password(sb, user_id: str) -> bool:
    """Reseta senha para '1234' e força troca no próximo acesso."""
    return change_password(sb, user_id, "1234") and bool(
        sb.table("usuarios").update({"trocar_senha": True}).eq("id", user_id).execute()
    )
