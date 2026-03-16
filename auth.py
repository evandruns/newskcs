"""Autenticação de usuários — KCS News Generator.

Hash idêntico ao AuditAI: PBKDF2-SHA256, 100 000 iterações + salt aleatório.
A tabela `usuarios` é compartilhada entre os dois sistemas.
"""

import hashlib
import os
import logging
from datetime import datetime, timezone

import streamlit as st
import pandas as pd

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
#  Hash — idêntico ao AuditAI
# ─────────────────────────────────────────────────────────────

def _hash_password(senha: str, salt=None):
    """
    Gera hash PBKDF2-SHA256 (100 000 iterações).
    Retorna (hash_hex, salt_hex) — mesmo comportamento do AuditAI.
    """
    if salt is None:
        salt = os.urandom(32)
    else:
        salt = bytes.fromhex(salt)
    h = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 100_000)
    return h.hex(), salt.hex()


def _verify(senha: str, salt_hex: str, stored_hash: str) -> bool:
    h, _ = _hash_password(senha, salt_hex)
    return h == stored_hash


# ─────────────────────────────────────────────────────────────
#  Garante admin inicial
# ─────────────────────────────────────────────────────────────

def _ensure_admin(sb) -> None:
    """Cria admin com senha '1234' se não existir."""
    try:
        r = sb.table("usuarios").select("id").eq("usuario", "admin").execute()
        if not r.data:
            h, s = _hash_password("1234")
            sb.table("usuarios").insert({
                "usuario":       "admin",
                "nome_exibicao": "Administrador",
                "senha_hash":    h,
                "senha_salt":    s,
                "perfil":        "admin",
                "ativo":         True,
                "trocar_senha":  True,
            }).execute()
            logger.info("Usuário admin criado.")
    except Exception as e:
        logger.error(f"Erro ao verificar admin: {e}")


# ─────────────────────────────────────────────────────────────
#  Autenticação
# ─────────────────────────────────────────────────────────────

def authenticate(sb, usuario: str, senha: str) -> dict | None:
    """Verifica credenciais. Retorna dict do usuário ou None."""
    try:
        r = (
            sb.table("usuarios")
            .select("id, usuario, nome_exibicao, senha_hash, senha_salt, perfil, ativo, trocar_senha")
            .eq("usuario", usuario.strip().lower())
            .eq("ativo", True)
            .execute()
        )
        if not r.data:
            return None
        user = r.data[0]
        if not _verify(senha, user["senha_salt"], user["senha_hash"]):
            return None
        sb.table("usuarios").update(
            {"ultimo_acesso": datetime.now(timezone.utc).isoformat()}
        ).eq("id", user["id"]).execute()
        return user
    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return None


# ─────────────────────────────────────────────────────────────
#  Troca de senha
# ─────────────────────────────────────────────────────────────

def change_password(sb, user_id: str, nova_senha: str) -> bool:
    try:
        h, s = _hash_password(nova_senha)
        sb.table("usuarios").update({
            "senha_hash":   h,
            "senha_salt":   s,
            "trocar_senha": False,
        }).eq("id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        return False


# ─────────────────────────────────────────────────────────────
#  Gestão de usuários (admin)
# ─────────────────────────────────────────────────────────────

PERFIS_VALIDOS = ["kcseditor", "admin"]


def list_users(sb):
    try:
        r = sb.table("usuarios").select(
            "id, usuario, nome_exibicao, perfil, ativo, criado_em, ultimo_acesso, trocar_senha"
        ).order("criado_em").execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame()
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        return pd.DataFrame()


def create_user(sb, usuario: str, nome_exibicao: str, senha: str, perfil: str) -> bool:
    if perfil not in PERFIS_VALIDOS:
        return False
    try:
        h, s = _hash_password(senha)
        sb.table("usuarios").insert({
            "usuario":       usuario.lower().strip(),
            "nome_exibicao": nome_exibicao.strip(),
            "senha_hash":    h,
            "senha_salt":    s,
            "perfil":        perfil,
            "ativo":         True,
            "trocar_senha":  True,
        }).execute()
        return True
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        return False


def toggle_user(sb, user_id: str, ativo: bool) -> bool:
    try:
        sb.table("usuarios").update({"ativo": ativo}).eq("id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Erro ao alterar status: {e}")
        return False


def reset_password(sb, user_id: str) -> bool:
    """Reseta senha para '1234' e força troca no próximo acesso."""
    try:
        h, s = _hash_password("1234")
        sb.table("usuarios").update({
            "senha_hash":   h,
            "senha_salt":   s,
            "trocar_senha": True,
        }).eq("id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Erro ao resetar senha: {e}")
        return False
