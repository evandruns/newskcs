"""Conexão com Supabase — KCS News Generator."""

import streamlit as st


@st.cache_resource
def init_supabase():
    """Inicializa e retorna o cliente Supabase usando st.secrets."""
    try:
        from supabase import create_client
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao conectar com Supabase: {e}")
        return None
