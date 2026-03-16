#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KCS News Generator — Athena Support
Gera HTML idêntico ao modelo de referência + publica no GitHub Pages
"""

import re
import base64
import requests
import streamlit as st
from datetime import datetime
from html import escape
from urllib.parse import unquote
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="KCS News Generator",
    page_icon="KCS",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ── Paleta TOTVS / Athena Support ───────────────────────────
   Cores extraídas do styles.css do sistema:
   --color-primary:   #002233  (azul-marinho escuro)
   --color_paleta_a:  #004c6d  (azul principal)
   --color_paleta_d:  #5383a1  (azul médio)
   --color_paleta_i:  #abd2ec  (azul claro / hover)
   --color_paleta_j:  #c1e7ff  (azul muito claro)
   --color_paleta2_a: #f1e702  (amarelo destaque)
─────────────────────────────────────────────────────────── */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

/* ── Fundo geral ─────────────────────────────────────────── */
.stApp { background-color: #f3f3f3 !important; }

/* ── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #002233 !important;
    border-right: 1px solid #004c6d !important;
}
section[data-testid="stSidebar"] * { color: #c1e7ff !important; }
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stTextArea textarea,
section[data-testid="stSidebar"] .stSelectbox select {
    background: #004c6d !important;
    border: 1px solid #5383a1 !important;
    border-radius: 8px !important;
    color: #f3f3f3 !important;
}
section[data-testid="stSidebar"] .stTextInput input:focus,
section[data-testid="stSidebar"] .stTextArea textarea:focus {
    border-color: #abd2ec !important;
    background: #004c6d !important;
}
section[data-testid="stSidebar"] label { color: #abd2ec !important; font-size: 0.78rem !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] .stMarkdown p { color: #7faac6 !important; font-size: 0.8rem !important; }
section[data-testid="stSidebar"] hr { border-color: #225e7e !important; margin: 1rem 0 !important; }
section[data-testid="stSidebar"] code {
    background: #004c6d !important;
    color: #c1e7ff !important;
    border: 1px solid #5383a1 !important;
    border-radius: 4px !important;
}

/* ── Cabeçalho do app ────────────────────────────────────── */
.app-header {
    background: linear-gradient(135deg, #002233 0%, #004c6d 100%);
    color: white; padding: 1.6rem 2rem; border-radius: 16px;
    margin-bottom: 1.8rem; display: flex; align-items: center; gap: 1.2rem;
    border: 1px solid #225e7e;
    box-shadow: 0 4px 20px rgba(0,76,109,0.3);
}
.app-header h1 { font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; color: #fff; }
.app-header p  { margin: 0.25rem 0 0; color: #7faac6; font-size: 0.83rem; }
.hi { color: #abd2ec; }

/* ── Cards de preview de artigos ─────────────────────────── */
.art-item {
    display: flex; align-items: flex-start; gap: 8px;
    padding: 7px 10px; border-radius: 8px;
    background: #fff; border: 1px solid #c1e7ff;
    margin-bottom: 5px; font-size: 0.82rem;
}
.art-tag {
    font-size: 0.65rem; font-weight: 700; padding: 2px 7px;
    border-radius: 6px; white-space: nowrap; flex-shrink: 0; margin-top: 2px;
}
.art-tag.blue { background: #c1e7ff; color: #004c6d; }
.art-tag.teal { background: #d1fae5; color: #065f46; }
.art-title { color: #002233; flex: 1; line-height: 1.45; }

/* ── Cards de contagem ───────────────────────────────────── */
.count-card {
    text-align: center; padding: 0.9rem 0.5rem;
    background: #fff; border: 1.5px solid #abd2ec; border-radius: 14px;
    box-shadow: 0 2px 8px rgba(0,76,109,0.08);
}
.count-card .num { font-size: 1.8rem; font-weight: 800; line-height: 1; }
.count-card .lbl { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
                   letter-spacing: .08em; color: #5383a1; margin-top: 3px; }
.blue   .num { color: #004c6d; }
.teal   .num { color: #0d9488; }
.purple .num { color: #3d788f; }
.dark   .num { font-size: 0.9rem !important; color: #002233; }

/* ── Inputs e textareas da área principal ────────────────── */
.stTextArea textarea {
    border: 1.5px solid #abd2ec !important;
    border-radius: 10px !important;
    background: #fff !important;
    font-size: 0.83rem !important;
    color: #002233 !important;
}
.stTextArea textarea:focus {
    border-color: #004c6d !important;
    box-shadow: 0 0 0 3px rgba(0,76,109,0.12) !important;
}

/* ── Botão principal ─────────────────────────────────────── */
div.stButton > button {
    background: linear-gradient(135deg, #004c6d, #002233) !important;
    color: #f3f3f3 !important; border: none !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    border-radius: 10px !important; width: 100%;
    box-shadow: 0 4px 14px rgba(0,76,109,0.35) !important;
    transition: all .2s !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #225e7e, #004c6d) !important;
    box-shadow: 0 6px 20px rgba(0,76,109,0.45) !important;
}
div.stButton > button:disabled {
    background: #94bed9 !important; box-shadow: none !important; opacity: 0.6 !important;
}

/* ── Botão de download ───────────────────────────────────── */
div.stDownloadButton > button {
    background: #3d788f !important; color: #fff !important;
    border: none !important; font-weight: 600 !important;
    border-radius: 10px !important; width: 100% !important;
}
div.stDownloadButton > button:hover {
    background: #225e7e !important;
}

/* ── Títulos das seções ──────────────────────────────────── */
.stMarkdown h4 { color: #004c6d !important; font-weight: 700 !important; }

/* ── Separador ───────────────────────────────────────────── */
hr { border-color: #abd2ec !important; margin: 1rem 0 !important; }

/* ── Banners de sucesso / erro ───────────────────────────── */
.ok-box {
    background: linear-gradient(135deg, #e0f4e8, #c6edd6);
    border: 1.5px solid #6ee7b7; border-radius: 14px;
    padding: 1.1rem 1.4rem; margin: 0.8rem 0;
    display: flex; gap: 12px; align-items: center;
}
.ok-box .icon { font-size: 1.7rem; }
.ok-box strong { display: block; color: #065f46; font-size: 1rem; }
.ok-box span   { color: #047857; font-size: 0.82rem; }

.err-box {
    background: #fef2f2; border: 1.5px solid #fca5a5;
    border-radius: 14px; padding: 1rem 1.3rem; margin: 0.8rem 0;
}
.err-box strong { color: #991b1b; }
.err-box p { color: #b91c1c; font-size: 0.82rem; margin: 3px 0 0; }

/* ── Status do token ─────────────────────────────────────── */
.token-ok {
    background: #c1e7ff; border: 1px solid #5383a1;
    border-radius: 8px; padding: .5rem .9rem;
    font-size: .8rem; color: #002233; font-weight: 600;
    margin-bottom: .5rem;
}
.token-err {
    background: #fff0c1; border: 1px solid #f1e702;
    border-radius: 8px; padding: .5rem .9rem;
    font-size: .8rem; color: #5a4a00; font-weight: 600;
    margin-bottom: .5rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────────────
GITHUB_USER = "evandruns"
GITHUB_REPO = "newskcs"
GITHUB_API  = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"
PAGES_BASE  = f"https://{GITHUB_USER}.github.io/{GITHUB_REPO}"

EQUIPES = {
    "ativo-contabil": "Ativo & Contábil",
    "trade":          "Trade",
    "advpl":          "AdvPL",
}

# ─────────────────────────────────────────────────────
#  Token via Secrets
# ─────────────────────────────────────────────────────
def get_token() -> str:
    try:
        return st.secrets["GITHUB_TOKEN"]
    except Exception:
        return ""

# ─────────────────────────────────────────────────────
#  GitHub API
# ─────────────────────────────────────────────────────
def gh_headers(token):
    return {"Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"}

def github_upload(token, path, content, msg):
    url = f"{GITHUB_API}/{path}"
    sha = None
    r = requests.get(url, headers=gh_headers(token), timeout=10)
    if r.status_code == 200:
        sha = r.json().get("sha")
    payload = {"message": msg,
               "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
               "branch": "main"}
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=gh_headers(token), json=payload, timeout=15)
    if r.status_code in (200, 201):
        return True, "atualizado" if sha else "criado"
    try:
        return False, r.json().get("message", r.text)
    except Exception:
        return False, r.text

# ─────────────────────────────────────────────────────
#  Processamento de artigos
# ─────────────────────────────────────────────────────
URL_RE  = re.compile(r'(https?://\S+)', re.IGNORECASE)
MODULOS = ['SIGACTB','SIGAATF','SIGAFIN','SIGACOM','SIGAEST','SIGATEC','KCS','RH','FISCAL','FOLHA']

def detectar_modulo(txt: str) -> str:
    up = txt.upper()
    for m in MODULOS:
        if m in up: return m
    return "TOTVS"

def slug_para_titulo(url: str) -> str:
    """Extrai título legível do slug da URL."""
    slug = url.rstrip('/').split('/')[-1]
    slug = unquote(slug)                    # %C3%A7 → ç
    slug = re.sub(r'^\d+-', '', slug)       # remove ID numérico do início
    slug = slug.replace('-', ' ')
    return slug.strip()

@st.cache_data(show_spinner=False, ttl=3600)
def buscar_titulo_web(url: str) -> str:
    try:
        r = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("title")
        if tag:
            t = tag.get_text(strip=True)
            t = re.sub(r'\s*[|\-–—]\s*(TOTVS|Central de Atendimento|Help Center|Support).*$', '', t, flags=re.I)
            if t.strip(): return t.strip()
        og = soup.find("meta", property="og:title")
        if og and og.get("content"): return og["content"].strip()
        h1 = soup.find("h1")
        if h1: return h1.get_text(strip=True)
    except Exception: pass
    return ""

def extrair_linha(linha: str):
    linha = linha.strip().lstrip('*•-– ').strip()
    m = URL_RE.search(linha)
    if not m: return None, None
    url = m.group(1).rstrip('.,;)')
    titulo_raw = linha[:m.start()].strip().rstrip('.,;:- ')
    return url, titulo_raw

def processar_bloco(bloco: str, data_padrao: str, buscar_web: bool) -> list:
    artigos = []
    linhas = [l.strip() for l in bloco.strip().splitlines() if l.strip()]
    if not linhas: return []
    prog = st.progress(0, text="Processando...")
    for i, linha in enumerate(linhas):
        prog.progress((i + 1) / len(linhas), text=f"Processando {i+1}/{len(linhas)}...")
        url, titulo_raw = extrair_linha(linha)
        if not url: continue

        modulo = detectar_modulo(linha)

        if titulo_raw:
            # Usa o texto digitado como título (mantém completo, igual ao modelo)
            titulo = titulo_raw
        else:
            # Só URL: tenta buscar na web primeiro, senão usa slug
            titulo_web = buscar_titulo_web(url)
            if titulo_web:
                titulo = titulo_web
            else:
                titulo = slug_para_titulo(url)

        artigos.append({"url": url, "title": titulo, "tag": modulo, "date": data_padrao})
    prog.empty()
    return artigos

def contar_links(bloco: str) -> int:
    return sum(1 for l in bloco.strip().splitlines() if URL_RE.search(l.strip()))

def render_preview(bloco: str, cor: str):
    if not bloco.strip(): return
    arts = []
    for linha in bloco.strip().splitlines():
        url, titulo_raw = extrair_linha(linha.strip())
        if url:
            titulo = titulo_raw if titulo_raw else slug_para_titulo(url)
            arts.append((titulo, detectar_modulo(linha)))
    if arts:
        html = "".join(
            f'<div class="art-item"><span class="art-tag {cor}">{mod}</span>'
            f'<span class="art-title">{t[:85]}{"…" if len(t)>85 else ""}</span></div>'
            for t, mod in arts)
        st.markdown(html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
#  Geração de HTML — idêntico ao modelo Athena Support
# ─────────────────────────────────────────────────────
def gerar_html(cfg: dict, novos: list, atualizados: list) -> str:
    hoje  = datetime.now().strftime("%d/%m/%Y")
    mm    = cfg["mm"]
    yyyy  = cfg["yyyy"]
    qn, qa = len(novos), len(atualizados)

    t_r   = escape(cfg["titulo"])
    edi   = escape(cfg["edicao"])       # ex: "02/2026"
    per   = escape(cfg["periodo"])
    mt    = escape(cfg["manchete_titulo"])
    mx    = escape(cfg["manchete_texto"])
    eq    = escape(cfg["equipe_label"])
    ekey  = cfg["equipe_key"]

    # ── Cards novos ──────────────────────────────────
    cards_novos = ""
    for a in novos:
        t   = escape(a["title"])
        url = escape(a["url"])
        tag = escape(a["tag"])
        dt  = escape(a["date"])
        cards_novos += f"""
            <article class="article-card bg-slate-50 p-6 rounded-2xl border border-slate-200 flex flex-col justify-between">
                <div>
                    <div class="flex justify-between items-start mb-4">
                        <span class="text-[10px] font-bold tracking-widest uppercase" style="color:#2563eb;">{tag}</span>
                        <span class="text-[10px] text-slate-400 font-medium">{dt}</span>
                    </div>
                    <h3 class="font-bold text-lg mb-3 leading-snug">{t}</h3>
                </div>
                <a href="{url}" target="_blank"
                   class="font-bold text-sm flex items-center gap-2 group mt-2" style="color:#2563eb;">
                    Ver Documenta&#231;&#227;o <span class="group-hover:translate-x-1 transition-transform">&#8594;</span>
                </a>
            </article>"""

    secao_novos = ""
    if novos:
        secao_novos = f"""
        <section id="novos" class="mb-24">
            <div class="flex items-center gap-4 mb-10">
                <h2 class="text-3xl font-800" style="font-family:'Montserrat',sans-serif;font-weight:800;color:#0f172a;">Artigos Novos</h2>
                <div class="h-1 flex-grow bg-slate-100 rounded-full"></div>
                <span class="text-white px-3 py-1 rounded text-xs font-bold" style="background:#2563eb;">{qn} NOVO{"S" if qn!=1 else ""}</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cards_novos}
            </div>
        </section>"""

    # ── Cards atualizados ────────────────────────────
    cards_atu = ""
    for a in atualizados:
        t   = escape(a["title"])
        url = escape(a["url"])
        dt  = escape(a["date"])
        cards_atu += f"""
            <div class="group bg-white p-6 rounded-xl hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div class="flex gap-4 items-center">
                    <div class="w-2 h-2 rounded-full flex-shrink-0" style="background:#0d9488;"></div>
                    <h3 class="font-bold text-base">{t}</h3>
                </div>
                <div class="flex items-center gap-6 flex-shrink-0">
                    <span class="text-sm text-slate-400">Atualizado em {dt}</span>
                    <a href="{url}" target="_blank"
                       class="p-2 bg-slate-100 rounded-full transition-colors hover:bg-blue-600 hover:text-white">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                        </svg>
                    </a>
                </div>
            </div>"""

    secao_atu = ""
    if atualizados:
        secao_atu = f"""
        <section id="atualizados" class="mb-24 py-12 border-y border-slate-100">
            <div class="flex items-center gap-4 mb-10">
                <h2 class="text-3xl font-800" style="font-family:'Montserrat',sans-serif;font-weight:800;color:#0f172a;">Manuten&#231;&#227;o &amp; Atualiza&#231;&#245;es</h2>
                <div class="h-1 flex-grow bg-slate-100 rounded-full"></div>
                <span class="text-white px-3 py-1 rounded text-xs font-bold" style="background:#0d9488;">{qa} ATUALIZADO{"S" if qa!=1 else ""}</span>
            </div>
            <div class="space-y-4">
                {cards_atu}
            </div>
        </section>"""

    # ── Destaques ────────────────────────────────────
    d1, d2 = "", ""
    if novos:
        a = novos[0]
        t   = escape(a["title"])
        url = escape(a["url"])
        tag = escape(a["tag"])
        d1 = f"""
                <div class="text-white p-10 rounded-3xl relative overflow-hidden group" style="background:#0a0f1e;">
                    <div class="absolute bottom-0 right-0 opacity-10 group-hover:opacity-20 transition-opacity">
                        <svg class="w-48 h-48 translate-x-12 translate-y-12" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                    <span class="font-bold uppercase text-xs tracking-[0.2em] mb-4 block" style="color:#3b82f6;">Novo Artigo &#183; {tag}</span>
                    <h3 class="text-2xl font-bold mb-4 leading-tight">{t}</h3>
                    <p class="mb-6" style="color:rgba(255,255,255,0.4);">Documenta&#231;&#227;o criada recentemente &#8212; confira todos os detalhes e orienta&#231;&#245;es t&#233;cnicas.</p>
                    <a href="{url}" target="_blank"
                       class="inline-flex items-center justify-center px-6 py-3 text-white rounded-xl font-bold transition-all hover:opacity-90" style="background:#2563eb;">
                        Ver Detalhes
                    </a>
                </div>"""
    if atualizados:
        a = atualizados[0]
        t   = escape(a["title"])
        url = escape(a["url"])
        tag = escape(a["tag"])
        d2 = f"""
                <div class="p-10 rounded-3xl border border-slate-200" style="background:#f8fafc;">
                    <span class="font-bold uppercase text-xs tracking-[0.2em] mb-4 block" style="color:#0d9488;">Atualiza&#231;&#227;o &#183; {tag}</span>
                    <h3 class="text-2xl font-bold mb-4 leading-tight" style="color:#0f172a;">{t}</h3>
                    <p class="mb-6 text-slate-500">Artigo atualizado com novas informa&#231;&#245;es e corre&#231;&#245;es relevantes.</p>
                    <a href="{url}" target="_blank"
                       class="inline-flex items-center justify-center px-6 py-3 rounded-xl font-bold transition-all border-2 hover:text-white" style="border-color:#0f172a;color:#0f172a;">
                        Saber Mais
                    </a>
                </div>"""

    secao_dest = ""
    if d1 or d2:
        secao_dest = f"""
        <section id="destaques" class="mb-24">
            <h2 class="text-3xl font-800 mb-10 flex items-center gap-3" style="font-family:'Montserrat',sans-serif;font-weight:800;color:#0f172a;">
                <span style="color:#dc2626;">&#9733;</span> Destaques da Edi&#231;&#227;o
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                {d1}
                {d2}
            </div>
        </section>"""

    # ── Timeline ─────────────────────────────────────
    def li_timeline(arts, cor):
        itens = ""
        for a in arts:
            t   = escape(a["title"])
            url = escape(a["url"])
            itens += f"""
                            <li class="flex gap-2"><span style="color:{cor};">&#8226;</span><a href="{url}" target="_blank" style="color:#475569;" onmouseover="this.style.color='{cor}'" onmouseout="this.style.color='#475569'">{t}</a></li>"""
        return itens

    bloco_novos_tl = ""
    if novos:
        bloco_novos_tl = f"""
                <div class="relative">
                    <div class="timeline-dot"></div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-50">
                        <span class="font-bold text-sm block mb-3" style="color:#2563eb;">Cria&#231;&#227;o de Documenta&#231;&#227;o</span>
                        <ul class="text-sm space-y-2 text-slate-600">
                            {li_timeline(novos, "#2563eb")}
                        </ul>
                    </div>
                </div>"""

    bloco_atu_tl = ""
    if atualizados:
        bloco_atu_tl = f"""
                <div class="relative">
                    <div class="timeline-dot"></div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-50">
                        <span class="font-bold text-sm block mb-3" style="color:#0d9488;">Manuten&#231;&#227;o Evolutiva</span>
                        <ul class="text-sm space-y-2 text-slate-600">
                            {li_timeline(atualizados, "#0d9488")}
                        </ul>
                    </div>
                </div>"""

    nav_n = '<a href="#novos" class="hover:text-accent transition-colors">Novos</a>' if novos else ""
    nav_a = '<a href="#atualizados" class="hover:text-accent transition-colors">Atualizados</a>' if atualizados else ""

    return f"""<!DOCTYPE html>
<html lang="pt-br" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t_r} &#8212; {edi} | Athena Support</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&family=Montserrat:wght@400;700;800&family=Noto+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans', sans-serif; background: #fff; color: #1e293b; line-height: 1.6; }}
        .top-nav {{
            position: fixed; top: 0; left: 0; right: 0; z-index: 100;
            background: rgba(10,15,30,0.96); backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(255,255,255,0.06);
            padding: 0 2rem; height: 60px;
            display: flex; align-items: center; justify-content: space-between;
        }}
        .nav-brand {{ font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1rem; color: #fff; letter-spacing: -0.02em; text-decoration: none; }}
        .nav-brand span {{ color: #3b82f6; }}
        .nav-links {{ display: flex; align-items: center; gap: 0.25rem; }}
        .nav-links a {{
            font-family: 'DM Sans', sans-serif; font-size: 0.78rem; font-weight: 500;
            color: rgba(255,255,255,0.55); text-decoration: none;
            padding: 0.35rem 0.85rem; border-radius: 6px; transition: all 0.2s;
        }}
        .nav-links a:hover {{ color: #fff; background: rgba(255,255,255,0.07); }}
        .nav-links a.active {{ color: #fff; background: rgba(59,130,246,0.2); }}
        .nav-badge {{
            font-size: 0.6rem; font-weight: 700; letter-spacing: 0.05em;
            background: #1d4ed8; color: #fff;
            padding: 0.15rem 0.45rem; border-radius: 99px;
            margin-left: 0.3rem; vertical-align: middle;
        }}
        .hero-gradient {{ background: radial-gradient(circle at top right, #f1f5f9 0%, #fff 100%); }}
        .article-card {{ transition: all .3s cubic-bezier(.4,0,.2,1); }}
        .article-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 24px -10px rgba(0,0,0,.12); }}
        .timeline-dot::before {{ content: ''; position: absolute; left: -9px; top: 4px; width: 18px; height: 18px; background: #2563eb; border: 4px solid #fff; border-radius: 50%; box-shadow: 0 0 0 2px #2563eb; }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #f1f5f9; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 10px; }}
        .breadcrumb {{
            padding: 1rem 0; max-width: 960px; margin: 0 auto;
            font-size: 0.78rem; color: #94a3b8;
            display: flex; align-items: center; gap: 0.5rem;
        }}
        .breadcrumb a {{ color: #2563eb; text-decoration: none; }}
        .breadcrumb a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body class="antialiased overflow-x-hidden">

    <nav class="top-nav">
        <a href="/newskcs/" class="nav-brand">Athena <span>Support</span></a>
        <div class="nav-links">
            <a href="/newskcs/">In&#237;cio</a>
            <a href="/newskcs/manual.html">Manual</a>
            <a href="/newskcs/{ekey}/{mm}-{yyyy}.html" class="active">KCS News <span class="nav-badge">NEW</span></a>
        </div>
    </nav>

    <main class="max-w-5xl mx-auto px-6" style="padding-top: 76px;">

        <div class="breadcrumb">
            <a href="/newskcs/">In&#237;cio</a>
            <span>&#8250;</span>
            <span>KCS News</span>
            <span>&#8250;</span>
            <span>{eq}</span>
            <span>&#8250;</span>
            <span>{edi}</span>
        </div>

        <header class="text-center mb-20 space-y-4" style="padding-top: 2rem;">
            <div class="inline-block px-4 py-1 rounded-full text-sm font-bold tracking-wide uppercase" style="background:#eff6ff;color:#2563eb;">
                {edi}
            </div>
            <h1 class="text-4xl md:text-6xl font-800 leading-tight tracking-tight" style="font-family:'Montserrat',sans-serif;font-weight:800;color:#0f172a;">
                {t_r}<br/>
                <span style="background:linear-gradient(to right,#2563eb,#1e40af);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Artigos KCS</span>
            </h1>
            <p class="text-lg text-slate-500 font-medium">Periodo: {per}</p>
        </header>

        <section id="manchete" class="mb-24 hero-gradient rounded-3xl p-8 md:p-16 border border-slate-100 shadow-sm relative overflow-hidden">
            <div class="absolute top-0 right-0 w-64 h-64 rounded-full -mr-20 -mt-20 blur-3xl" style="background:rgba(37,99,235,0.05);"></div>
            <div class="relative z-10">
                <span class="font-bold uppercase tracking-widest text-sm mb-4 block" style="color:#2563eb;">Manchete em Foco</span>
                <h2 class="text-3xl md:text-5xl font-700 mb-6 leading-tight" style="font-family:'Montserrat',sans-serif;font-weight:700;color:#0f172a;">{mt}</h2>
                <p class="text-xl text-slate-600 leading-relaxed max-w-3xl">{mx}</p>
                <div class="mt-8 flex flex-wrap gap-4 text-sm font-semibold">
                    <span class="px-4 py-2 rounded-full" style="background:rgba(37,99,235,0.1);color:#2563eb;">{qn} artigo{"s" if qn!=1 else ""} novo{"s" if qn!=1 else ""}</span>
                    <span class="px-4 py-2 rounded-full" style="background:rgba(13,148,136,0.1);color:#0d9488;">{qa} atualiza&#231;&#227;o{"&#245;es" if qa!=1 else ""}</span>
                    <span class="px-4 py-2 bg-slate-100 text-slate-600 rounded-full">Gerado em {hoje}</span>
                </div>
            </div>
        </section>

        {secao_novos}
        {secao_atu}
        {secao_dest}

        <section id="timeline" class="mb-24">
            <h2 class="text-3xl font-800 mb-12 text-center" style="font-family:'Montserrat',sans-serif;font-weight:800;color:#0f172a;">Linha do Tempo</h2>
            <div class="max-w-2xl mx-auto pl-8 space-y-12" style="border-left: 2px solid #f1f5f9;">
                {bloco_novos_tl}
                {bloco_atu_tl}
            </div>
        </section>

        <section class="mb-12 text-center py-20 bg-slate-50 rounded-3xl border border-slate-200">
            <h2 class="text-2xl font-800 mb-6" style="font-family:'Montserrat',sans-serif;font-weight:800;color:#0f172a;">Fechamento Editorial</h2>
            <div class="max-w-2xl mx-auto px-6">
                <p class="text-slate-600 leading-loose">
                    Este relat&#243;rio consolida as principais movimenta&#231;&#245;es de documenta&#231;&#227;o KCS
                    do per&#237;odo <strong>{per}</strong>. O objetivo &#233; manter a equipe informada
                    e preparada para as constantes evolu&#231;&#245;es e corre&#231;&#245;es documentadas.
                </p>
                <div class="mt-10 flex flex-col items-center gap-4">
                    <div class="w-12 h-1 rounded-full" style="background:#2563eb;"></div>
                    <div class="flex gap-4">
                        <a href="/newskcs/" class="text-slate-500 font-bold hover:text-blue-600 transition-colors text-sm">&#8592; Voltar ao In&#237;cio</a>
                        <span class="text-slate-300">|</span>
                        <a href="#manchete" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false;"
                           class="font-bold hover:text-blue-600 transition-colors text-sm flex items-center gap-1" style="color:#0f172a;">
                            Voltar ao Topo &#8593;
                        </a>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <footer style="background:#0a0f1e;color:rgba(255,255,255,0.3);text-align:center;padding:2rem;font-size:0.78rem;font-family:'DM Sans',sans-serif;">
        Athena <span style="color:#3b82f6;">Support</span> &mdash; Central de Conhecimento Interno &mdash; TOTVS
    </footer>

    <script>
        document.querySelectorAll('a[href^="#"]').forEach(function(a) {{
            a.addEventListener('click', function(e) {{
                var href = a.getAttribute('href');
                if (href === '#') return;
                e.preventDefault();
                var el = document.querySelector(href);
                if (el) el.scrollIntoView({{ behavior: 'smooth' }});
            }});
        }});
    </script>
</body>
</html>"""

# ─────────────────────────────────────────────────────
#  CSS DA TELA DE LOGIN
# ─────────────────────────────────────────────────────
LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

div.block-container { padding: 0rem !important; max-width: 100% !important; }
header, footer, [data-testid="stSidebar"] { display: none !important; }

.split-left {
    position: fixed; top: 0; left: 0;
    width: 55vw; height: 100vh;
    background: linear-gradient(135deg, #002233 0%, #004c6d 60%, #3d788f 100%);
    z-index: 0;
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
}
.split-left::before {
    content: '';
    position: absolute; inset: 0;
    background-image: radial-gradient(circle, rgba(255,255,255,0.07) 1px, transparent 1px);
    background-size: 22px 22px;
}
.brand-content { color: white; text-align: center; padding: 40px; z-index: 2; position: relative; }
.brand-title {
    font-family: 'Inter', sans-serif;
    font-size: 3.8rem; font-weight: 800;
    letter-spacing: -2px; margin-bottom: 8px;
    background: linear-gradient(to right, #fff, #abd2ec);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-sub {
    font-family: 'Inter', sans-serif;
    font-size: 1rem; opacity: 0.75;
    max-width: 340px; line-height: 1.6;
}
.brand-badge {
    display: inline-block; margin-top: 20px;
    background: rgba(171,210,236,0.15);
    border: 1px solid rgba(171,210,236,0.3);
    color: #abd2ec; font-size: 0.72rem;
    font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase;
    padding: 5px 14px; border-radius: 99px;
}

.login-title {
    font-family: 'Inter', sans-serif;
    font-size: 2rem; font-weight: 700;
    color: #002233; margin: 0 0 6px;
}
.login-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem; color: #5383a1;
    margin: 0 0 28px;
}

div[data-testid="stTextInput"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    color: #004c6d !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .06em !important;
}
div[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1.5px solid #abd2ec !important;
    padding: 12px 14px !important;
    color: #002233 !important;
    font-size: 0.95rem !important;
    background: #f3f3f3 !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #004c6d !important;
    box-shadow: 0 0 0 3px rgba(0,76,109,0.12) !important;
    background: #fff !important;
}
div.stButton > button {
    width: 100%; border-radius: 8px !important;
    background: linear-gradient(to right, #002233, #004c6d) !important;
    color: #f3f3f3 !important; border: none !important;
    padding: 0.75rem 1rem !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    margin-top: 0.8rem !important;
    letter-spacing: .02em;
    box-shadow: 0 4px 14px rgba(0,76,109,0.3) !important;
    transition: all .2s !important;
}
div.stButton > button:hover {
    background: linear-gradient(to right, #004c6d, #225e7e) !important;
    box-shadow: 0 6px 20px rgba(0,76,109,0.4) !important;
}
.login-error {
    padding: 10px 14px;
    background: #fff5e0; color: #7a4f00;
    border: 1px solid #f1e702;
    border-radius: 7px; margin-bottom: 16px;
    font-family: 'Inter', sans-serif; font-size: 0.87rem;
}
.login-footer {
    margin-top: 36px; text-align: center;
    font-family: 'Inter', sans-serif;
    color: #94bed9; font-size: 0.72rem;
}
@media (max-width: 768px) { .split-left { display: none; } }
</style>
<div class="split-left">
    <div class="brand-content">
        <div class="brand-title">KCS News</div>
        <div class="brand-sub">Gerador de boletins de documentação para o Athena Support</div>
        <div class="brand-badge">TOTVS Backoffice</div>
    </div>
</div>
"""


# ─────────────────────────────────────────────────────
#  TELAS DE LOGIN E TROCA DE SENHA
# ─────────────────────────────────────────────────────
def render_login(sb):
    from auth import _ensure_admin, authenticate
    _ensure_admin(sb)
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    col_vazia, col_form = st.columns([1, 1])
    with col_form:
        for _ in range(5):
            st.write("")
        with st.container():
            _, cc, _ = st.columns([1, 5, 1])
            with cc:
                st.markdown('<div class="login-title">Bem-vindo</div>', unsafe_allow_html=True)
                st.markdown('<div class="login-sub">Insira suas credenciais para continuar.</div>', unsafe_allow_html=True)

                usuario = st.text_input("Usuário", placeholder="nome.sobrenome", key="_lu")
                senha   = st.text_input("Senha",   type="password", placeholder="••••••", key="_ls")

                err = st.session_state.get("_lerr", "")
                if err:
                    st.markdown(f'<div class="login-error">{err}</div>', unsafe_allow_html=True)

                if st.button("Acessar", key="btn_login"):
                    if not usuario.strip() or not senha:
                        st.session_state["_lerr"] = "Preencha usuário e senha."
                        st.rerun()
                    else:
                        user = authenticate(sb, usuario, senha)
                        if user:
                            st.session_state["_user"] = user
                            st.session_state["_lerr"] = ""
                            st.rerun()
                        else:
                            st.session_state["_lerr"] = "Credenciais inválidas ou usuário inativo."
                            st.rerun()

                st.markdown('<div class="login-footer">KCS News Generator &mdash; TOTVS &copy; 2026</div>', unsafe_allow_html=True)


def render_change_password(sb):
    from auth import change_password
    user = st.session_state["_user"]
    st.markdown("""<style>
    div.block-container{padding:3rem 1rem !important;}
    [data-testid="stSidebar"]{display:none!important;}
    </style>""", unsafe_allow_html=True)
    _, cc, _ = st.columns([1, 2, 1])
    with cc:
        st.markdown("### Definir nova senha")
        st.info(f"Ola **{user.get('nome_exibicao') or user['usuario']}**, defina sua senha pessoal para continuar.")
        nova     = st.text_input("Nova senha",      type="password", key="_np", placeholder="Minimo 6 caracteres")
        confirma = st.text_input("Confirmar senha", type="password", key="_cp")
        if st.button("Salvar senha", use_container_width=True):
            if len(nova) < 6:
                st.error("Minimo 6 caracteres.")
            elif nova != confirma:
                st.error("As senhas nao conferem.")
            elif nova == "1234":
                st.error("Escolha uma senha diferente da inicial.")
            else:
                if change_password(sb, user["id"], nova):
                    st.session_state["_user"]["trocar_senha"] = False
                    st.success("Senha alterada! Redirecionando...")
                    st.rerun()
                else:
                    st.error("Erro ao salvar. Tente novamente.")


# ─────────────────────────────────────────────────────
#  PAINEL ADMIN — GESTÃO DE USUÁRIOS
# ─────────────────────────────────────────────────────
def render_admin(sb):
    from auth import list_users, create_user, toggle_user, reset_password
    import re as _re

    st.markdown("### Gestão de Usuários")
    st.caption("Senhas são criptografadas — ninguém consegue visualizar.")

    users_df = list_users(sb)
    total  = len(users_df)
    ativos = len(users_df[users_df["ativo"] == True]) if not users_df.empty else 0

    m1, m2, _ = st.columns([1, 1, 4])
    m1.metric("Total", total)
    m2.metric("Ativos", ativos)
    st.markdown("---")

    tab_list, tab_add = st.tabs(["Usuarios", "Novo Usuario"])

    with tab_list:
        if users_df.empty:
            st.info("Nenhum usuario cadastrado.")
        else:
            for _, u in users_df.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 1])
                with c1:
                    status = "Ativo" if u["ativo"] else "Inativo"
                    cor    = "#0d9488" if u["ativo"] else "#991b1b"
                    st.markdown(f'<span style="color:{cor};font-weight:700">{status}</span> — <b>{u["usuario"]}</b>', unsafe_allow_html=True)
                with c2:
                    st.caption(u.get("nome_exibicao") or "—")
                with c3:
                    st.caption(u["perfil"])
                with c4:
                    if u["usuario"] != "admin":
                        lbl = "Desativar" if u["ativo"] else "Ativar"
                        if st.button(lbl, key=f"ut_{u['id']}"):
                            toggle_user(sb, u["id"], not u["ativo"])
                            st.rerun()
                with c5:
                    if u["usuario"] != "admin":
                        if st.button("Reset senha", key=f"ur_{u['id']}"):
                            reset_password(sb, u["id"])
                            st.success(f"Senha de '{u['usuario']}' resetada para 1234.")
                            st.rerun()

    with tab_add:
        st.markdown("#### Novo Usuario")
        ac1, ac2 = st.columns(2)
        with ac1:
            new_user  = st.text_input("Usuario", key="_au", placeholder="nome.sobrenome")
        with ac2:
            new_nome  = st.text_input("Nome exibicao", key="_an", placeholder="Nome Completo")
        new_perfil = st.selectbox("Perfil", ["auditor", "admin"], key="_ap")
        st.caption("Senha inicial: **1234** — usuario obrigado a trocar no primeiro acesso.")
        if st.button("Criar Usuario", key="btn_create"):
            u = new_user.strip().lower()
            if not u:
                st.error("Preencha o usuario.")
            elif not _re.fullmatch(r"[a-z\u00e0-\u00fc]+(\.[a-z\u00e0-\u00fc]+)+|admin", u):
                st.error("Formato: nome.sobrenome")
            else:
                if create_user(sb, u, new_nome, "1234", new_perfil):
                    st.success(f"Usuario '{u}' criado. Senha inicial: 1234")
                    st.rerun()
                else:
                    st.error("Erro ao criar (usuario ja existe?)")


# ─────────────────────────────────────────────────────
#  APP PRINCIPAL (gerador de news)
# ─────────────────────────────────────────────────────
def render_app():
    token = get_token()
    user  = st.session_state.get("_user", {})
    nome  = user.get("nome_exibicao") or user.get("usuario", "")
    is_admin = user.get("perfil") == "admin"

    # Cabeçalho
    st.markdown(f"""
    <div class="app-header">
      <div style="font-size:1.5rem;font-weight:800;color:#abd2ec;letter-spacing:-1px">KCS</div>
      <div>
        <h1>KCS <span class="hi">News</span> Generator</h1>
        <p>Ola, <b>{nome}</b> — Cole os artigos e publique direto no GitHub Pages</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if token:
        st.markdown('<div class="token-ok">GitHub conectado — publicacao automatica disponivel</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="token-err">Token GitHub nao configurado — so sera possivel baixar o HTML</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown(f"**{nome}** — {user.get('perfil','')}")
        if st.button("Sair", key="btn_logout"):
            st.session_state.pop("_user", None)
            st.rerun()
        st.markdown("---")
        st.markdown("### Configuracoes da Edicao")
        hoje  = datetime.now()
        mm    = hoje.strftime("%m")
        yyyy  = hoje.strftime("%Y")

        equipe_key   = st.selectbox("Equipe", options=list(EQUIPES.keys()),
                                    format_func=lambda k: EQUIPES[k])
        equipe_label = EQUIPES[equipe_key]

        titulo_r = st.text_input("Titulo principal", value="Documentacoes criadas e atualizadas")
        edicao   = st.text_input("Edicao (ex: 02/2026)", value=f"{mm}/{yyyy}")
        periodo  = st.text_input("Periodo", value=f"01/{mm}/{yyyy} a {hoje.strftime('%d/%m/%Y')}")
        data_pad = st.text_input("Data padrao dos artigos", value=hoje.strftime("%d/%m/%Y"))

        st.markdown("---")
        st.markdown("### Manchete")
        m_titulo = st.text_input("Titulo da manchete", value="EXTRA! EXTRA! KCS NOVOS E AJUSTADOS")
        m_texto  = st.text_area("Texto da manchete",
            value=f"Veja os KCS criados e atualizados no periodo — Equipe {equipe_label}.",
            height=80)

        st.markdown("---")
        st.markdown("### Opcoes")
        buscar_web = st.toggle("Buscar titulo na web (quando so URL)", value=True,
            help="Acessa a pagina para pegar o titulo real.")

        nome_arquivo = f"{mm}-{yyyy}.html"
        pub_url      = f"{PAGES_BASE}/{equipe_key}/{nome_arquivo}"

        st.markdown("---")
        st.markdown("**Vai publicar em:**")
        st.code(f"{equipe_key}/{nome_arquivo}", language=None)
        st.caption(pub_url)

    # Abas — admin tem aba extra
    if is_admin:
        tab_gen, tab_adm = st.tabs(["Gerador de News", "Administracao"])
    else:
        tab_gen = st.tabs(["Gerador de News"])[0]

    with tab_gen:
        st.markdown("#### Cole os artigos abaixo")
        st.caption("Formato: `Descricao do artigo https://link` ou so a URL — um por linha")

        col1, col2 = st.columns(2, gap="large")

        PH_N = (
            "Cross Segmento - Backoffice Linha Protheus - SIGACTB - CTBA940 - Conciliador nao realiza o match automatico "
            "https://centraldeatendimento.totvs.com/hc/pt-br/articles/38486359011351\n"
            "https://centraldeatendimento.totvs.com/hc/pt-br/articles/38585578167447-Cross-Segmento-Backoffice-Linha-Protheus-SIGACTB-CTBA960"
        )
        PH_A = "Cross Segmento - SIGACTB - Funcoes ApExcel https://centraldeatendimento.totvs.com/hc/pt-br/articles/360007113531"

        with col1:
            st.markdown("#### Artigos Novos")
            txt_novos = st.text_area("novos", label_visibility="collapsed", height=280, placeholder=PH_N, key="n")
        with col2:
            st.markdown("#### Artigos Atualizados")
            txt_atu = st.text_area("atualizados", label_visibility="collapsed", height=280, placeholder=PH_A, key="a")

        qn = contar_links(txt_novos)
        qa = contar_links(txt_atu)

        if txt_novos.strip() or txt_atu.strip():
            st.markdown("---")
            st.markdown("#### Artigos detectados")
            pv1, pv2 = st.columns(2, gap="large")
            with pv1:
                if qn:
                    st.caption(f"**{qn} novo(s)**")
                    render_preview(txt_novos, "blue")
            with pv2:
                if qa:
                    st.caption(f"**{qa} atualizado(s)**")
                    render_preview(txt_atu, "teal")

        st.markdown("---")
        cc1, cc2, cc3, cc4 = st.columns(4, gap="small")
        with cc1:
            st.markdown(f'<div class="count-card blue"><div class="num">{qn}</div><div class="lbl">Novos</div></div>', unsafe_allow_html=True)
        with cc2:
            st.markdown(f'<div class="count-card teal"><div class="num">{qa}</div><div class="lbl">Atualizados</div></div>', unsafe_allow_html=True)
        with cc3:
            st.markdown(f'<div class="count-card purple"><div class="num">{qn+qa}</div><div class="lbl">Total</div></div>', unsafe_allow_html=True)
        with cc4:
            st.markdown(f'<div class="count-card dark"><div class="num">{equipe_label}</div><div class="lbl">Equipe</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        sem_artigos = (qn + qa == 0)

        if token:
            b1, b2 = st.columns([3, 1], gap="medium")
            with b1:
                publicar  = st.button("Gerar e Publicar no GitHub Pages", disabled=sem_artigos, use_container_width=True)
            with b2:
                so_baixar = st.button("Baixar HTML", disabled=sem_artigos, use_container_width=True)
        else:
            publicar  = False
            so_baixar = st.button("Gerar e Baixar HTML", disabled=sem_artigos, use_container_width=True)

        if publicar or so_baixar:
            cfg = {
                "titulo": titulo_r, "edicao": edicao, "periodo": periodo,
                "manchete_titulo": m_titulo, "manchete_texto": m_texto,
                "equipe_label": equipe_label, "equipe_key": equipe_key,
                "mm": mm, "yyyy": yyyy,
            }
            with st.spinner("Processando artigos..."):
                novos  = processar_bloco(txt_novos, data_pad, buscar_web) if txt_novos.strip() else []
                artupd = processar_bloco(txt_atu,   data_pad, buscar_web) if txt_atu.strip()   else []

            html_out   = gerar_html(cfg, novos, artupd)
            nome_final = nome_arquivo
            kb         = len(html_out.encode("utf-8")) // 1024

            st.download_button(
                label=f"Baixar {nome_final}",
                data=html_out.encode("utf-8"),
                file_name=nome_final,
                mime="text/html",
                use_container_width=True,
            )

            if publicar:
                with st.spinner(f"Publicando {equipe_key}/{nome_final}..."):
                    commit_msg = f"KCS News {equipe_label} {mm}/{yyyy} — {len(novos)}N + {len(artupd)}A"
                    ok, detalhe = github_upload(token, f"{equipe_key}/{nome_final}", html_out, commit_msg)
                if ok:
                    st.markdown(f"""
                    <div class="ok-box">
                      <div>
                        <strong>Publicado com sucesso! ({detalhe})</strong>
                        <span>{len(novos)} novo(s) + {len(artupd)} atualizado(s) &nbsp;·&nbsp; {kb} KB &nbsp;·&nbsp; {equipe_label} {mm}/{yyyy}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
                    st.markdown(f"**URL publica:** [{pub_url}]({pub_url})")
                    st.caption("O GitHub Pages pode levar ate 1 minuto para refletir.")
                else:
                    st.markdown(f"""
                    <div class="err-box">
                      <strong>Falha no upload</strong>
                      <p>{detalhe}</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.success(f"HTML gerado: {len(novos)} novo(s) + {len(artupd)} atualizado(s) — {kb} KB")

    if is_admin:
        with tab_adm:
            sb = st.session_state.get("_sb")
            if sb:
                render_admin(sb)


# ─────────────────────────────────────────────────────
#  PONTO DE ENTRADA
# ─────────────────────────────────────────────────────
def main():
    from database import init_supabase
    sb = init_supabase()
    if not sb:
        return
    st.session_state["_sb"] = sb

    # 1. Login
    if not st.session_state.get("_user"):
        render_login(sb)
        return

    # 2. Troca de senha obrigatória
    if st.session_state["_user"].get("trocar_senha", False):
        render_change_password(sb)
        return

    # 3. App principal
    render_app()


main()
