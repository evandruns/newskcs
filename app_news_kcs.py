#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KCS News Generator — Interface Web
Token GitHub via st.secrets (Streamlit Cloud)
"""

import re
import base64
import requests
import streamlit as st
from datetime import datetime
from html import escape
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="KCS News Generator",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

.app-header {
    background: linear-gradient(135deg, #0a0f1e 0%, #1e3a6e 100%);
    color: white; padding: 1.6rem 2rem; border-radius: 18px; margin-bottom: 1.8rem;
    display: flex; align-items: center; gap: 1.2rem;
}
.app-header h1 { font-size: 1.7rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
.app-header p  { margin: 0.25rem 0 0; opacity: 0.6; font-size: 0.83rem; }
.hi { color: #60a5fa; }

.step-label {
    font-size: 0.7rem; font-weight: 800; letter-spacing: .14em;
    text-transform: uppercase; color: #2563eb;
    display: flex; align-items: center; gap: 0.7rem; margin: 1.6rem 0 0.8rem;
}
.step-label::after { content: ''; flex: 1; height: 1px; background: #e2e8f0; }

.art-item {
    display: flex; align-items: flex-start; gap: 8px;
    padding: 7px 10px; border-radius: 8px;
    background: #f8fafc; border: 1px solid #e2e8f0;
    margin-bottom: 5px; font-size: 0.82rem;
}
.art-tag {
    font-size: 0.65rem; font-weight: 700; padding: 2px 7px;
    border-radius: 6px; white-space: nowrap; flex-shrink: 0; margin-top: 2px;
}
.art-tag.blue { background: #dbeafe; color: #1d4ed8; }
.art-tag.teal { background: #ccfbf1; color: #0f766e; }
.art-title { color: #1e293b; flex: 1; line-height: 1.45; }

.count-card {
    text-align: center; padding: 0.9rem 0.5rem;
    background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 14px;
}
.count-card .num { font-size: 1.8rem; font-weight: 800; line-height: 1; }
.count-card .lbl { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
                   letter-spacing: .08em; color: #94a3b8; margin-top: 3px; }
.blue  .num { color: #2563eb; }
.teal  .num { color: #0d9488; }
.purple .num { color: #7c3aed; }
.dark   .num { font-size: 0.9rem !important; color: #334155; }

.dest-box {
    background: #f0f9ff; border: 1.5px solid #bae6fd;
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.8rem 0;
    font-size: 0.83rem; color: #0369a1;
}
.dest-box code {
    font-family: monospace; background: #e0f2fe;
    padding: 2px 8px; border-radius: 5px;
}

div.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important; border: none !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    border-radius: 12px !important; width: 100%;
    box-shadow: 0 4px 14px rgba(37,99,235,.3) !important;
}
div.stButton > button:disabled { background: #cbd5e1 !important; box-shadow: none !important; }
div.stDownloadButton > button {
    background: #475569 !important; color: white !important;
    border: none !important; font-weight: 600 !important;
    border-radius: 10px !important; width: 100% !important;
}

.ok-box {
    background: linear-gradient(135deg,#ecfdf5,#d1fae5);
    border: 1.5px solid #6ee7b7; border-radius: 14px;
    padding: 1.1rem 1.4rem; margin: 0.8rem 0;
    display: flex; gap: 12px; align-items: center;
}
.ok-box .icon { font-size: 1.7rem; }
.ok-box strong { display: block; color: #065f46; }
.ok-box span   { color: #047857; font-size: 0.82rem; }

.err-box {
    background: #fef2f2; border: 1.5px solid #fca5a5;
    border-radius: 14px; padding: 1rem 1.3rem; margin: 0.8rem 0;
}
.err-box strong { color: #991b1b; }
.err-box p { color: #b91c1c; font-size: 0.82rem; margin: 3px 0 0; }

.token-ok {
    background: #f0fdf4; border: 1px solid #86efac;
    border-radius: 8px; padding: 0.5rem 0.9rem;
    font-size: 0.8rem; color: #166534; margin-bottom: 0.5rem;
}
.token-err {
    background: #fef2f2; border: 1px solid #fca5a5;
    border-radius: 8px; padding: 0.5rem 0.9rem;
    font-size: 0.8rem; color: #991b1b; margin-bottom: 0.5rem;
}
section[data-testid="stSidebar"] { background: #f8fafc !important; }
hr { border-color: #e2e8f0 !important; margin: 1rem 0 !important; }
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
#  Token via Secrets (configurado uma vez no Streamlit Cloud)
# ─────────────────────────────────────────────────────
def get_token() -> str:
    """Lê o token de st.secrets. Retorna string vazia se não configurado."""
    try:
        return st.secrets["GITHUB_TOKEN"]
    except Exception:
        return ""

# ─────────────────────────────────────────────────────
#  GitHub API
# ─────────────────────────────────────────────────────
def gh_headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def github_upload(token: str, path: str, content: str, msg: str):
    url = f"{GITHUB_API}/{path}"
    sha = None
    r = requests.get(url, headers=gh_headers(token), timeout=10)
    if r.status_code == 200:
        sha = r.json().get("sha")
    payload = {
        "message": msg,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": "main",
    }
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
    return "KCS"

def limpar_titulo(t: str) -> str:
    t = re.sub(r'^(Cross Segmento\s*[-–]\s*)?(TOTVS\s+)?Backoffice\s+(Linha\s+)?Protheus\s*[-–]\s*', '', t, flags=re.I).strip()
    t = re.sub(r'^Cross Segmento\s*[-–]\s*', '', t, flags=re.I).strip()
    t = re.sub(r'^TOTVS\s+Backoffice\s*\([^)]*\)\s*[-–]\s*', '', t, flags=re.I).strip()
    return t

def extrair_linha(linha: str):
    linha = linha.strip().lstrip('*•-– ').strip()
    m = URL_RE.search(linha)
    if not m: return None, None
    url = m.group(1).rstrip('.,;)')
    titulo_raw = linha[:m.start()].strip().rstrip('.,;:- ')
    return url, titulo_raw

@st.cache_data(show_spinner=False, ttl=3600)
def buscar_titulo_web(url: str) -> str:
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("title")
        if tag:
            t = tag.get_text(strip=True)
            return re.sub(r'\s*[|\-–]\s*(TOTVS|Central de Atendimento|Help).*$', '', t, flags=re.I).strip()
        og = soup.find("meta", property="og:title")
        if og and og.get("content"): return og["content"].strip()
        h1 = soup.find("h1")
        if h1: return h1.get_text(strip=True)
    except Exception: pass
    return ""

def processar_bloco(bloco: str, data_padrao: str, buscar_web: bool) -> list:
    artigos = []
    linhas = [l.strip() for l in bloco.strip().splitlines() if l.strip()]
    if not linhas: return []
    prog = st.progress(0, text="Processando...")
    for i, linha in enumerate(linhas):
        prog.progress((i + 1) / len(linhas), text=f"Processando {i+1}/{len(linhas)}...")
        url, titulo_raw = extrair_linha(linha)
        if not url: continue
        titulo = limpar_titulo(titulo_raw) if titulo_raw else ""
        modulo = detectar_modulo(linha)
        if not titulo and buscar_web:
            titulo = limpar_titulo(buscar_titulo_web(url)) or f"Artigo {i+1}"
        elif not titulo:
            titulo = url.split("/")[-1] or f"Artigo {i+1}"
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
            titulo = limpar_titulo(titulo_raw) if titulo_raw else url.split("/")[-1]
            arts.append((titulo, detectar_modulo(linha)))
    if arts:
        html = "".join(
            f'<div class="art-item"><span class="art-tag {cor}">{mod}</span>'
            f'<span class="art-title">{t[:80]}{"…" if len(t)>80 else ""}</span></div>'
            for t, mod in arts)
        st.markdown(html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
#  Geração de HTML
# ─────────────────────────────────────────────────────
SETA = ('<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
        'd="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>')

def card_novo(a: dict) -> str:
    t,url,tag,dt = escape(a["title"]),escape(a["url"]),escape(a["tag"]),escape(a["date"])
    return f'''
      <article class="article-card bg-surface p-6 rounded-2xl border border-border flex flex-col justify-between">
        <div>
          <div class="flex justify-between items-start mb-4">
            <span class="text-[10px] font-bold tracking-widest text-accent uppercase">{tag}</span>
            <span class="text-[10px] text-slate-400 font-medium">{dt}</span>
          </div>
          <h3 class="font-bold text-lg mb-3 leading-snug">{t}</h3>
        </div>
        <a href="{url}" target="_blank" class="text-accent font-bold text-sm flex items-center gap-2 group mt-2">
          Ver Documenta&#231;&#227;o <span class="group-hover:translate-x-1 transition-transform">&#8594;</span>
        </a>
      </article>'''

def card_atualizado(a: dict) -> str:
    t,url,dt = escape(a["title"]),escape(a["url"]),escape(a["date"])
    return f'''
      <div class="group bg-white p-6 rounded-xl hover:bg-slate-50 border border-transparent hover:border-border transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex gap-4 items-center">
          <div class="w-2 h-2 rounded-full bg-brand-teal flex-shrink-0"></div>
          <h3 class="font-bold text-lg">{t}</h3>
        </div>
        <div class="flex items-center gap-6 flex-shrink-0">
          <span class="text-sm text-slate-400">Atualizado em {dt}</span>
          <a href="{url}" target="_blank" class="p-2 bg-slate-100 rounded-full group-hover:bg-accent group-hover:text-white transition-colors">{SETA}</a>
        </div>
      </div>'''

def gerar_html(cfg: dict, novos: list, atualizados: list) -> str:
    hoje = datetime.now().strftime("%d/%m/%Y")
    qn, qa = len(novos), len(atualizados)
    t_r, sub = escape(cfg["titulo"]),   escape(cfg["subtitulo"])
    edi, per = escape(cfg["edicao"]),   escape(cfg["periodo"])
    mt,  mx  = escape(cfg["manchete_titulo"]), escape(cfg["manchete_texto"])
    eq       = escape(cfg["equipe_label"])

    s_novos = ""
    if novos:
        cards = "".join(card_novo(a) for a in novos)
        s_novos = f'''
    <section id="novos" class="mb-24">
      <div class="flex items-center gap-4 mb-10">
        <h2 class="font-display text-3xl font-800 text-primary">Artigos Novos</h2>
        <div class="h-1 flex-grow bg-slate-100 rounded-full"></div>
        <span class="bg-accent text-white px-3 py-1 rounded text-xs font-bold">{qn} NOVO{"S" if qn!=1 else ""}</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{cards}</div>
    </section>'''

    s_atu = ""
    if atualizados:
        itens = "".join(card_atualizado(a) for a in atualizados)
        s_atu = f'''
    <section id="atualizados" class="mb-24 py-12 border-y border-slate-100">
      <div class="flex items-center gap-4 mb-10">
        <h2 class="font-display text-3xl font-800 text-primary">Manuten&#231;&#227;o &amp; Atualiza&#231;&#245;es</h2>
        <div class="h-1 flex-grow bg-slate-100 rounded-full"></div>
        <span class="bg-brand-teal text-white px-3 py-1 rounded text-xs font-bold">{qa} ATUALIZADO{"S" if qa!=1 else ""}</span>
      </div>
      <div class="space-y-4">{itens}</div>
    </section>'''

    def li(arts, cor):
        return "".join(
            f'<li><span style="color:{cor}">&#8226;</span> '
            f'<a href="{escape(a["url"])}" target="_blank" style="color:#475569">{escape(a["title"])}</a></li>'
            for a in arts)

    bn = f'''<div class="relative"><div class="timeline-dot"></div>
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-50">
        <span class="text-accent font-bold text-sm block mb-3">Cria&#231;&#227;o de Documenta&#231;&#227;o</span>
        <ul class="text-sm space-y-2">{li(novos,"#2563eb")}</ul>
      </div></div>''' if novos else ""

    ba = f'''<div class="relative"><div class="timeline-dot"></div>
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-50">
        <span class="text-brand-teal font-bold text-sm block mb-3">Manuten&#231;&#227;o Evolutiva</span>
        <ul class="text-sm space-y-2">{li(atualizados,"#0d9488")}</ul>
      </div></div>''' if atualizados else ""

    d1, d2 = "", ""
    if novos:
        a = novos[0]
        d1 = f'''<div class="bg-primary text-white p-10 rounded-3xl">
          <span class="text-accent font-bold uppercase text-xs tracking-[0.2em] mb-4 block">Novo &#183; {escape(a["tag"])}</span>
          <h3 class="text-2xl font-bold mb-4 leading-tight">{escape(a["title"])}</h3>
          <p class="text-slate-400 mb-6">Documenta&#231;&#227;o criada recentemente &#8212; confira os detalhes t&#233;cnicos.</p>
          <a href="{escape(a["url"])}" target="_blank"
             class="inline-flex items-center px-6 py-3 bg-accent hover:bg-accentHover text-white rounded-xl font-bold transition-all">Ver Detalhes</a>
        </div>'''
    if atualizados:
        a = atualizados[0]
        d2 = f'''<div class="bg-surface p-10 rounded-3xl border border-border">
          <span class="text-brand-teal font-bold uppercase text-xs tracking-[0.2em] mb-4 block">Atualiza&#231;&#227;o &#183; {escape(a["tag"])}</span>
          <h3 class="text-2xl font-bold mb-4 leading-tight text-primary">{escape(a["title"])}</h3>
          <p class="text-slate-500 mb-6">Artigo atualizado com novas informa&#231;&#245;es e corre&#231;&#245;es relevantes.</p>
          <a href="{escape(a["url"])}" target="_blank"
             class="inline-flex items-center px-6 py-3 border-2 border-primary text-primary hover:bg-primary hover:text-white rounded-xl font-bold transition-all">Saber Mais</a>
        </div>'''

    s_dest = f'''<section id="destaques" class="mb-24">
      <h2 class="font-display text-3xl font-800 text-primary mb-10 flex items-center gap-3">
        <span class="text-brand-crimson">&#9733;</span> Destaques da Edi&#231;&#227;o
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">{d1}{d2}</div>
    </section>''' if (d1 or d2) else ""

    nav_n = '<a href="#novos" class="hover:text-accent transition-colors">Novos</a>' if novos else ""
    nav_a = '<a href="#atualizados" class="hover:text-accent transition-colors">Atualizados</a>' if atualizados else ""

    return f"""<!DOCTYPE html>
<html lang="pt-br" class="scroll-smooth">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t_r} &mdash; {edi} &mdash; {eq}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&family=Noto+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
  <script>tailwind.config={{theme:{{extend:{{colors:{{primary:'#0f172a',accent:'#2563eb',accentHover:'#1d4ed8',surface:'#f8fafc',border:'#e2e8f0',brand:{{teal:'#0d9488',crimson:'#dc2626',sapphire:'#1e40af'}}}},fontFamily:{{display:['Montserrat','sans-serif'],body:['Noto Sans','sans-serif']}}}}}}}}</script>
  <style>
    body{{font-family:'Noto Sans',sans-serif;background:#fff;color:#1e293b;line-height:1.6}}
    .glass-nav{{background:rgba(255,255,255,.88);backdrop-filter:blur(12px);border-bottom:1px solid rgba(226,232,240,.8)}}
    .hero-gradient{{background:radial-gradient(circle at top right,#f1f5f9,#fff)}}
    .article-card{{transition:all .3s cubic-bezier(.4,0,.2,1)}}
    .article-card:hover{{transform:translateY(-4px);box-shadow:0 12px 24px -10px rgba(0,0,0,.12)}}
    .timeline-dot::before{{content:'';position:absolute;left:-9px;top:4px;width:18px;height:18px;background:#2563eb;border:4px solid #fff;border-radius:50%;box-shadow:0 0 0 2px #2563eb}}
    ::-webkit-scrollbar{{width:8px}}::-webkit-scrollbar-track{{background:#f1f5f9}}::-webkit-scrollbar-thumb{{background:#cbd5e1;border-radius:10px}}
  </style>
</head>
<body class="antialiased overflow-x-hidden">
  <nav class="glass-nav sticky top-0 z-50 py-4 px-6">
    <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
      <div class="font-display font-800 text-xl tracking-tighter text-primary uppercase">
        KCS <span class="text-accent">News</span>
        <span class="ml-2 text-xs font-normal text-slate-400 normal-case">{eq}</span>
      </div>
      <div class="flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs font-semibold uppercase tracking-widest">
        <a href="#manchete" class="hover:text-accent transition-colors">Manchete</a>
        {nav_n}{nav_a}
        <a href="#destaques" class="hover:text-accent transition-colors">Destaques</a>
        <a href="#timeline" class="hover:text-accent transition-colors">Timeline</a>
        <a href="../../index.html" class="text-slate-400 hover:text-accent transition-colors">&#8592; Voltar</a>
      </div>
    </div>
  </nav>
  <main class="max-w-5xl mx-auto px-6 py-12 md:py-20">
    <header class="text-center mb-20 space-y-4">
      <div class="inline-block px-4 py-1 bg-accent/10 text-accent rounded-full text-sm font-bold tracking-wide uppercase">{edi}</div>
      <h1 class="font-display text-4xl md:text-6xl font-800 text-primary leading-tight tracking-tight">
        {t_r}<br><span class="text-transparent bg-clip-text bg-gradient-to-r from-accent to-brand-sapphire">{sub}</span>
      </h1>
      <p class="text-lg text-slate-500 font-medium">Per&#237;odo: {per} &middot; {eq}</p>
    </header>
    <section id="manchete" class="mb-24 hero-gradient rounded-3xl p-8 md:p-16 border border-slate-100 shadow-sm relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full -mr-20 -mt-20 blur-3xl"></div>
      <div class="relative z-10">
        <span class="text-accent font-bold uppercase tracking-widest text-sm mb-4 block">Manchete em Foco</span>
        <h2 class="font-display text-3xl md:text-5xl font-700 text-primary mb-6 leading-tight">{mt}</h2>
        <p class="text-xl text-slate-600 leading-relaxed max-w-3xl">{mx}</p>
        <div class="mt-8 flex flex-wrap gap-4 text-sm font-semibold">
          <span class="px-4 py-2 bg-accent/10 text-accent rounded-full">{qn} artigo{"s" if qn!=1 else ""} novo{"s" if qn!=1 else ""}</span>
          <span class="px-4 py-2 bg-brand-teal/10 text-brand-teal rounded-full">{qa} atualiza&#231;&#227;o{"&#245;es" if qa!=1 else ""}</span>
          <span class="px-4 py-2 bg-slate-100 text-slate-600 rounded-full">Gerado em {hoje}</span>
        </div>
      </div>
    </section>
    {s_novos}{s_atu}{s_dest}
    <section id="timeline" class="mb-24">
      <h2 class="font-display text-3xl font-800 text-primary mb-12 text-center">Linha do Tempo</h2>
      <div class="max-w-2xl mx-auto border-l-2 border-slate-100 pl-8 space-y-12">{bn}{ba}</div>
    </section>
    <section class="mb-12 text-center py-20 bg-surface rounded-3xl border border-border">
      <h2 class="font-display text-2xl font-800 text-primary mb-6">Fechamento Editorial</h2>
      <p class="text-slate-600 leading-loose max-w-2xl mx-auto px-6">
        Este relat&#243;rio consolida as principais movimenta&#231;&#245;es de documenta&#231;&#227;o KCS
        do per&#237;odo <strong>{per}</strong> &mdash; Equipe {eq}.
      </p>
      <div class="mt-10 flex flex-col items-center gap-4">
        <div class="w-12 h-1 bg-accent rounded-full"></div>
        <div class="flex gap-6">
          <a href="#" class="text-primary font-bold hover:text-accent transition-colors">Voltar ao Topo &#8593;</a>
          <a href="../../index.html" class="text-slate-400 hover:text-accent transition-colors">&#8592; Central KCS</a>
        </div>
      </div>
    </section>
  </main>
  <script>document.querySelectorAll('a[href^="#"]').forEach(function(el){{el.addEventListener('click',function(e){{e.preventDefault();var t=document.querySelector(el.getAttribute('href'));if(t)t.scrollIntoView({{behavior:'smooth'}})}})}})</script>
</body></html>"""

# ─────────────────────────────────────────────────────
#  INTERFACE PRINCIPAL
# ─────────────────────────────────────────────────────

# Cabeçalho
st.markdown("""
<div class="app-header">
  <div style="font-size:2.2rem;line-height:1">📰</div>
  <div>
    <h1>KCS <span class="hi">News</span> Generator</h1>
    <p>Cole os artigos, configure a edição e publique direto no GitHub Pages com um clique</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Token ─────────────────────────────────────────────
token = get_token()
if token:
    st.markdown('<div class="token-ok">🔑 GitHub conectado — publicação automática disponível</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="token-err">⚠️ Token GitHub não configurado — só será possível baixar o HTML</div>', unsafe_allow_html=True)

# ── SIDEBAR: configurações ────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações da Edição")
    hoje = datetime.now()
    mm   = hoje.strftime("%m")
    yyyy = hoje.strftime("%Y")

    equipe_key   = st.selectbox("Equipe", options=list(EQUIPES.keys()),
                                format_func=lambda k: EQUIPES[k])
    equipe_label = EQUIPES[equipe_key]

    titulo_r  = st.text_input("Título principal", value="Reporte de Documentação")
    subtitulo = st.text_input("Subtítulo",         value="Artigos KCS")
    edicao    = st.text_input("Edição",            value=f"Edição {mm}/{yyyy}")
    periodo   = st.text_input("Período",           value=f"01/{mm}/{yyyy} a {hoje.strftime('%d/%m/%Y')}")
    data_pad  = st.text_input("Data padrão",       value=hoje.strftime("%d/%m/%Y"))

    st.markdown("---")
    st.markdown("### 📣 Manchete")
    m_titulo = st.text_input("Título da manchete", value=f"Novos Artigos KCS — {equipe_label}")
    m_texto  = st.text_area("Texto da manchete",
        value="Esta edição reúne os principais artigos criados e atualizados no período, cobrindo correções, melhorias e novas documentações técnicas.",
        height=85)

    st.markdown("---")
    st.markdown("### 🔧 Opções")
    buscar_web = st.toggle("Buscar título na web", value=False,
        help="Acessa cada URL para pegar o título oficial. Mais lento.")

    nome_arquivo = f"{mm}-{yyyy}.html"
    pub_url      = f"{PAGES_BASE}/{equipe_key}/{nome_arquivo}"

    st.markdown("---")
    st.markdown("**📤 Destino da publicação:**")
    st.code(f"{equipe_key}/{nome_arquivo}", language=None)
    st.caption(f"🌐 {pub_url}")

# ── ÁREA CENTRAL: artigos ─────────────────────────────
st.markdown('<div class="step-label">Cole os artigos abaixo</div>', unsafe_allow_html=True)
st.caption("Formato: `Descrição do artigo https://link.com/123` — pode colar vários de uma vez, um por linha")

col1, col2 = st.columns(2, gap="large")

PH_N = (
    "Cross Segmento - SIGACTB - CTBR040 - Como emitir o balancete anual https://centraldeatendimento.totvs.com/hc/pt-br/articles/360055860033\n"
    "Cross Segmento - SIGAATF - ATFA012 - Alteração de valores de bens https://centraldeatendimento.totvs.com/hc/pt-br/articles/38393605639191\n"
    "Cross Segmento - SIGACTB - Campos não visíveis no Módulo Contábil https://centraldeatendimento.totvs.com/hc/pt-br/articles/38394509442071"
)
PH_A = (
    "Cross Segmento - SIGACTB - Funções ApExcel na Gestão Contábil https://centraldeatendimento.totvs.com/hc/pt-br/articles/360007113531\n"
    "Cross Segmento - SIGACTB - Reprocessamento de saldos (CTBA960) https://centraldeatendimento.totvs.com/hc/pt-br/articles/37723395292567"
)

with col1:
    st.markdown("#### 📄 Artigos Novos")
    txt_novos = st.text_area("novos", label_visibility="collapsed",
                             height=280, placeholder=PH_N, key="n")

with col2:
    st.markdown("#### 🔄 Artigos Atualizados")
    txt_atu = st.text_area("atualizados", label_visibility="collapsed",
                           height=280, placeholder=PH_A, key="a")

# ── Preview live ──────────────────────────────────────
qn = contar_links(txt_novos)
qa = contar_links(txt_atu)

if txt_novos.strip() or txt_atu.strip():
    st.markdown("---")
    st.markdown("#### 👁️ Artigos detectados")
    pv1, pv2 = st.columns(2, gap="large")
    with pv1:
        if qn:
            st.caption(f"**{qn} novo(s)**")
            render_preview(txt_novos, "blue")
    with pv2:
        if qa:
            st.caption(f"**{qa} atualizado(s)**")
            render_preview(txt_atu, "teal")

# ── Contadores ────────────────────────────────────────
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

# ── Botões ────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
sem_artigos = (qn + qa == 0)

if token:
    b1, b2 = st.columns([3, 1], gap="medium")
    with b1:
        publicar = st.button("🚀  Gerar e Publicar no GitHub Pages",
                             disabled=sem_artigos, use_container_width=True)
    with b2:
        so_baixar = st.button("⬇️  Só baixar", disabled=sem_artigos, use_container_width=True)
else:
    publicar  = False
    so_baixar = st.button("⬇️  Gerar e Baixar HTML",
                          disabled=sem_artigos, use_container_width=True)

# ── Processamento ─────────────────────────────────────
if publicar or so_baixar:
    cfg = {
        "titulo": titulo_r, "subtitulo": subtitulo,
        "edicao": edicao,   "periodo": periodo,
        "manchete_titulo": m_titulo, "manchete_texto": m_texto,
        "equipe_label": equipe_label,
    }
    with st.spinner("Processando artigos..."):
        novos  = processar_bloco(txt_novos, data_pad, buscar_web) if txt_novos.strip() else []
        artupd = processar_bloco(txt_atu,   data_pad, buscar_web) if txt_atu.strip()   else []

    html_out = gerar_html(cfg, novos, artupd)
    kb = len(html_out.encode("utf-8")) // 1024

    # Download sempre disponível
    st.download_button(
        label=f"⬇️  Baixar {nome_arquivo}",
        data=html_out.encode("utf-8"),
        file_name=nome_arquivo,
        mime="text/html",
        use_container_width=True,
    )

    if publicar:
        with st.spinner(f"Publicando {equipe_key}/{nome_arquivo} no GitHub..."):
            commit_msg = f"KCS News {equipe_label} {mm}/{yyyy} — {len(novos)}N + {len(artupd)}A"
            ok, detalhe = github_upload(token, f"{equipe_key}/{nome_arquivo}", html_out, commit_msg)

        if ok:
            st.markdown(f"""
            <div class="ok-box">
              <div class="icon">✅</div>
              <div>
                <strong>Publicado com sucesso! ({detalhe})</strong>
                <span>{len(novos)} novo(s) + {len(artupd)} atualizado(s) &nbsp;·&nbsp; {kb} KB &nbsp;·&nbsp; {equipe_label} {mm}/{yyyy}</span>
              </div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"🌐 **URL pública:** [{pub_url}]({pub_url})")
            st.caption("⏱️ O GitHub Pages pode levar até 1 minuto para refletir.")
        else:
            st.markdown(f"""
            <div class="err-box">
              <strong>❌ Falha no upload</strong>
              <p>{detalhe}</p>
            </div>""", unsafe_allow_html=True)
    else:
        st.success(f"HTML gerado: {len(novos)} novo(s) + {len(artupd)} atualizado(s) — {kb} KB")
