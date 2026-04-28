"""
app.py — Agentic IA Refactoring Pro
Corrections : bouton copie JS (base64), DiffAgent séparé, diff coloré vert/rouge.
Ajout : Authentification via token depuis Coach Advisor
"""

import streamlit as st
import streamlit.components.v1 as components
import traceback, os, sys, base64, time
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Agentic IA Refactoring Pro",
    page_icon="⚡", layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main-header{font-size:2.5rem;color:#1E3A8A;text-align:center;margin-bottom:1rem;}
.patch-note{background:#0D0E29;color:#e2e8f0;padding:8px;border-radius:4px;margin:4px 0;}
</style>
""", unsafe_allow_html=True)

# ── Authentification ──────────────────────────────────────────────────────────
def check_auth():
    """Vérifier l'authentification via token dans les paramètres de requête"""
    query_params = st.query_params
    token = query_params.get("token")
    email = query_params.get("email")
    
    if token and email:
        # Stocker dans la session
        st.session_state.authenticated = True
        st.session_state.user_token = token
        st.session_state.user_email = email
        return True
    
    # Vérifier si déjà authentifié en session
    if st.session_state.get("authenticated", False):
        return True
    
    # Afficher un message d'erreur avec lien vers l'auth
    st.warning("⚠️ Authentification requise")
    st.markdown("""
    ### Accès non autorisé
    
    Veuillez vous connecter via l'application principale :
    
    [Se connecter à Coach Advisor](http://localhost:3000/auth)
    
    Ou utilisez l'application de refactoring depuis la navigation de Coach Advisor.
    """)
    return False

# Vérifier l'authentification au début
if not check_auth():
    st.stop()

# Afficher l'utilisateur connecté dans la sidebar
st.sidebar.markdown(f"""
<div style="background: linear-gradient(135deg, #f0a50020, #00d4ff20); padding: 12px; border-radius: 8px; margin-bottom: 16px;">
    <div style="font-size: 12px; color: #3d5570;">✅ Connecté en tant que</div>
    <div style="font-weight: bold; color: #f0a500;">{st.session_state.get('user_email', 'Utilisateur')}</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.divider()

st.markdown('<h1 class="main-header">⚡ Agentic IA Refactoring Pro</h1>', unsafe_allow_html=True)
st.markdown("**Système intelligent de refactoring multi-agents avec LangGraph, validation automatique et contrôle de température.**")

# ── Constants & helpers ──────────────────────────────────────────────────────
SPECIAL_AGENTS = {"TestAgent", "PatchAgent", "MergeAgent"}
LANGUAGE_MAP   = {
    ".py":("Python","python"), ".js":("JavaScript","javascript"),
    ".ts":("TypeScript","typescript"), ".java":("Java","java"),
    ".cpp":("C++","cpp"), ".c":("C","c"), ".cs":("C#","csharp"),
    ".go":("Go","go"), ".rb":("Ruby","ruby"),
    ".rs":("Rust","rust"), ".php":("PHP","php"),
}

def format_duration(s):
    if s<1:  return f"{s*1000:.0f}ms"
    if s<60: return f"{s:.2f}s"
    return f"{int(s//60)}m {s%60:.2f}s"

def detect_language(fn):
    return LANGUAGE_MAP.get(os.path.splitext(fn)[1].lower(), ("Python","python"))

def init_system():
    try:
        from core.ollama_llm_client   import OllamaLLMClient
        from core.langgraph_orchestrator import LangGraphOrchestrator
        llm = OllamaLLMClient(st.session_state.get("model_name","mistral:latest"))
        orc = LangGraphOrchestrator(llm)
        return llm, orc, orc.get_available_agents()
    except Exception as e:
        st.error(f"❌ Initialisation : {e}")
        st.text(traceback.format_exc())
        return None, None, []

def _bootstrap():
    for k,v in dict(
        initialized=False, available_agents=[], agent_temperatures={},
        agent_enabled={}, result_code=None, result_original=None,
        result_filename=None, result_language=None, result_report=None,
        show_diff=False, model_name="mistral:latest",
    ).items():
        st.session_state.setdefault(k, v)

_bootstrap()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuration")
    st.subheader("🔧 Paramètres LLM")
    st.session_state.model_name = st.selectbox(
        "🤖 Modèle Ollama",
        ["mistral:latest","llama2:latest","codellama:latest","phi:latest","qwen2.5-coder:latest"],
    )
    st.divider()

    # Init système une seule fois
    if not st.session_state.initialized:
        with st.spinner("Initialisation…"):
            llm, orc, agents = init_system()
            if orc and agents:
                st.session_state.llm_client      = llm
                st.session_state.orchestrator    = orc
                st.session_state.available_agents = agents
                from core.temperature_config import TemperatureConfig
                tc = TemperatureConfig()
                for a in agents:
                    if a not in SPECIAL_AGENTS:
                        st.session_state.agent_temperatures.setdefault(a, tc.get_temperature(a))
                        st.session_state.agent_enabled.setdefault(a, True)
                st.session_state.initialized = True

    st.subheader("🤖 Agents de refactoring")
    for ag in [a for a in st.session_state.available_agents if a not in SPECIAL_AGENTS]:
        c1, c2 = st.columns([2,1])
        with c1:
            v = st.checkbox(f"**{ag}**",
                value=st.session_state.agent_enabled.get(ag,True), key=f"sb_{ag}")
            st.session_state.agent_enabled[ag] = v
        with c2:
            if v:
                t = st.slider("🌡️",0.0,1.0,
                    value=st.session_state.agent_temperatures.get(ag,0.3),
                    step=0.1, key=f"sbt_{ag}")
                st.session_state.agent_temperatures[ag] = t

    st.divider()
    st.subheader("✅ Validation automatique")
    auto_patch = st.checkbox("🩹 PatchAgent automatique", value=True, key="auto_patch")
    auto_test  = st.checkbox("🧪 TestAgent automatique",  value=True, key="auto_test")
    st.divider()
    st.subheader("🎯 Mode")
    use_workflow = st.checkbox("🔄 Workflow LangGraph (recommandé)", value=True, key="use_wf")
    st.divider()
    if st.button("🔄 Réinitialiser"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        _bootstrap(); st.rerun()
    st.divider()
    if st.button("🚪 Se déconnecter"):
        # Nettoyer la session et rediriger vers l'auth
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.query_params.clear()
        st.rerun()

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.initialized:
    st.warning("⏳ Initialisation en cours…"); st.stop()

orchestrator     = st.session_state.orchestrator
available_agents = st.session_state.available_agents

# ── Upload + exemple ──────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📂 Téléchargez un fichier de code",
    type=["py","js","ts","java","cpp","c","cs","go","rb","rs","php"],
)

EXAMPLE_CODE = '''\
# Exemple Python avec problèmes typiques
import os, sys, math, datetime

x = 10
y = 20

def calc(a, b):
    result = a + b
    if result > 10:
        if result < 20:
            if result % 2 == 0:
                return result * 2
            else:
                return result * 3
        else:
            return result
    return result

def process_items(items):
    output = []
    for item in items:
        if item > 0:
            output.append(item * 2)
    return output

def transform_data(data):
    result = []
    for d in data:
        if d > 0:
            result.append(d * 2)
    return result
'''

with st.expander("📝 Exemple de code avec problèmes", expanded=False):
    st.code(EXAMPLE_CODE, language="python")
    with st.form("ex_form"):
        if st.form_submit_button("📥 Tester avec cet exemple"):
            st.session_state["_ex_pending"] = EXAMPLE_CODE

if "_ex_pending" in st.session_state:
    st.session_state.result_code = None
    st.session_state.show_diff   = False
    st.session_state["_ex_code"] = st.session_state.pop("_ex_pending")

# Résoudre source
if uploaded_file:
    source_code = uploaded_file.read().decode("utf-8")
    source_fn   = uploaded_file.name
    lang_name, lang_code = detect_language(source_fn)
elif "_ex_code" in st.session_state:
    source_code = st.session_state["_ex_code"]
    source_fn   = "example.py"
    lang_name, lang_code = "Python","python"
else:
    st.info("👋 Téléchargez un fichier ou testez avec l'exemple ci-dessus.")
    st.stop()

# ── Code source ───────────────────────────────────────────────────────────────
st.subheader("📄 Code original")
c1, c2 = st.columns([3,1])
with c1: st.code(source_code, language=lang_code)
with c2:
    st.metric("Lignes",     len(source_code.split("\n")))
    st.metric("Caractères", len(source_code))

# ── Sélection agents ──────────────────────────────────────────────────────────
st.subheader("🎯 Sélection des agents")
active_agents = []
cols = st.columns(2)
ref_agents = [a for a in available_agents if a not in SPECIAL_AGENTS]
for idx, ag in enumerate(ref_agents):
    with cols[idx % 2]:
        temp  = st.session_state.agent_temperatures.get(ag, 0.3)
        emoji = "🟦" if temp < 0.3 else "🟨" if temp < 0.7 else "🟥"
        sel = st.checkbox(
            f"{emoji} **{ag}** (🌡️ {temp})",
            value=st.session_state.agent_enabled.get(ag, True),
            key=f"main_{ag}",
        )
        st.session_state.agent_enabled[ag] = sel
        if sel: active_agents.append(ag)

# ── Lancement ─────────────────────────────────────────────────────────────────
st.subheader("🚀 Exécution")
if st.button("LANCER LE REFACTORING COMPLET", type="primary", use_container_width=True):
    if not active_agents:
        st.warning("⚠️ Sélectionnez au moins un agent.")
    else:
        pb = st.progress(0); tx = st.empty(); t0_tot = time.time()
        try:
            if use_workflow:
                tx.text("🔄 Workflow LangGraph…"); pb.progress(20)
                res = orchestrator.run_workflow(
                    code=source_code, language=lang_name,
                    selected_agents=active_agents,
                    auto_patch=auto_patch, auto_test=auto_test,
                    temperature_override={a:st.session_state.agent_temperatures[a] for a in active_agents},
                )
                pb.progress(90)
                if not res.get("success"): st.error(f"❌ {res.get('error')}"); st.stop()
                merged_code = res.get("refactored_code", source_code)
                rr = [{"name":r["name"],"analysis":r.get("analysis",[]),
                       "proposal":merged_code,
                       "temperature_used":r.get("temperature_used","N/A"),
                       "execution_time":r.get("duration",0)}
                      for r in res.get("agent_results",[]) if r["name"] not in SPECIAL_AGENTS]
                pr=res.get("patch_result"); tr=res.get("test_result"); merd=0
            else:
                rr=[]; n=len(active_agents)
                for i,ag in enumerate(active_agents):
                    tx.text(f"⚡ {ag}…")
                    agent=orchestrator.agent_instances.get(ag)
                    if agent:
                        t0=time.time()
                        r=agent.apply(source_code,lang_name,
                                      temperature=st.session_state.agent_temperatures.get(ag,0.3))
                        r["execution_time"]=time.time()-t0; rr.append(r)
                    pb.progress(int((i+1)/n*50))
                tx.text("🔄 Fusion…"); t0=time.time()
                merged_code = orchestrator.merge_results(source_code,rr) if rr else source_code
                merd=time.time()-t0; pb.progress(60)
                pr=tr=None
                if auto_patch:
                    tx.text("🩹 PatchAgent…"); pa=orchestrator.agent_instances.get("PatchAgent")
                    if pa:
                        t0=time.time(); pr=pa.apply(merged_code,lang_name)
                        pr["execution_time"]=time.time()-t0; merged_code=pr["proposal"]
                pb.progress(80)
                if auto_test:
                    tx.text("🧪 TestAgent…"); ta=orchestrator.agent_instances.get("TestAgent")
                    if ta:
                        t0=time.time(); tr=ta.apply(merged_code,lang_name)
                        tr["execution_time"]=time.time()-t0

            pb.progress(100); tx.empty(); pb.empty()
            st.session_state.update(
                result_code=merged_code, result_original=source_code,
                result_filename=source_fn, result_language=(lang_name,lang_code),
                show_diff=False,
                result_report=dict(rr=rr, pr=pr, tr=tr, merd=merd,
                                   totd=time.time()-t0_tot,
                                   mode="LangGraph" if use_workflow else "Séquentiel"),
            )
        except Exception as e:
            st.error(f"❌ {e}"); st.text(traceback.format_exc())

# ── Résultats persistants ─────────────────────────────────────────────────────
if st.session_state.result_code is None: st.stop()

rep         = st.session_state.result_report
merged_code = st.session_state.result_code
orig_code   = st.session_state.result_original
filename    = st.session_state.result_filename
lng_name, lng_code = st.session_state.result_language
rr,pr,tr    = rep["rr"], rep["pr"], rep["tr"]
merd,totd   = rep["merd"], rep["totd"]

st.success(f"✅ Refactoring terminé en {format_duration(totd)} — Mode : {rep['mode']}")

# Tableau
st.subheader("📊 Rapport de performances")
rows=[]
for r in rr:
    rows.append({"Agent":r.get("name","?"),
                 "🌡️ Temp":str(r.get("temperature_used","N/A")),
                 "🔍 Problèmes":len(r.get("analysis",[])),
                 "⏱️ Durée":format_duration(r.get("execution_time",0)),
                 "📝":"✅" if r.get("analysis") else "⚪"})
if pr: rows.append({"Agent":"PatchAgent","🌡️ Temp":"N/A","🔍 Problèmes":len(pr.get("analysis",[])),"⏱️ Durée":format_duration(pr.get("execution_time",0)),"📝":"✅"})
if tr:
    ts=tr.get("status","N/A")
    rows.append({"Agent":"TestAgent","🌡️ Temp":"N/A","🔍 Problèmes":ts,"⏱️ Durée":format_duration(tr.get("execution_time",0)),"📝":"✅" if ts=="SUCCESS" else "❌"})
if rows:
    df=pd.DataFrame(rows); df["🌡️ Temp"]=df["🌡️ Temp"].astype(str)
    st.dataframe(df,use_container_width=True,hide_index=True)
    a,b,c=st.columns(3)
    avg=sum(r.get("execution_time",0) for r in rr)/max(len(rr),1)
    a.metric("⏱️ Moyen/agent",format_duration(avg))
    b.metric("🔄 Fusion",format_duration(merd))
    c.metric("⏱️ Total",format_duration(totd))

# Détails
st.subheader("📈 Résultats détaillés")
for r in rr:
    with st.expander(f"{r.get('name','?')} (🌡️ {r.get('temperature_used','N/A')} | ⏱️ {format_duration(r.get('execution_time',0))})", expanded=False):
        t1,t2=st.tabs(["📋 Analyse","💡 Proposition"])
        with t1:
            for iss in r.get("analysis",[]): st.code(str(iss))
            if not r.get("analysis"): st.info("Aucun problème détecté")
        with t2:
            p=r.get("proposal","")
            if p and p!=orig_code: st.code(p,language=lng_code)
            else: st.info("Aucune modification proposée")

if pr:
    st.subheader(f"🩹 PatchAgent (⏱️ {format_duration(pr.get('execution_time',0))})")
    for note in pr.get("analysis",[]): st.markdown(f"<div class='patch-note'>{note.get('note','') if isinstance(note,dict) else str(note)}</div>",unsafe_allow_html=True)
    for ch in pr.get("changes_applied",[]): st.markdown(f"- {ch}")

if tr:
    st.subheader(f"🧪 TestAgent (⏱️ {format_duration(tr.get('execution_time',0))})")
    ts=tr.get("status","N/A")
    st.markdown(f"**Statut :** {'✅' if ts=='SUCCESS' else '❌'} **{ts}**")
    for ln in tr.get("summary",[]): st.markdown(f"- {ln}")
    for ti in tr.get("details",[]):
        tl,stl,out=ti.get("tool","?"),ti.get("status","N/A"),ti.get("output","")
        icon="✅" if stl=="SUCCESS" else ("⚠️" if stl=="WARNING" else "❌")
        with st.expander(f"{icon} {tl} | {stl}"):
            lns=out.splitlines()
            if lns: st.markdown(f"**Message :** {lns[0]}")
            if len(lns)>1: st.code("\n".join(lns[1:]))

# ── Code final + boutons ───────────────────────────────────────────────────────
st.subheader("📝 Code final refactoré")

dl_col, cp_col, _ = st.columns([1, 1, 5])

with dl_col:
    st.download_button(
        "⬇️ Télécharger", data=merged_code,
        file_name=f"refactored_{filename}", mime="text/plain",
        key="dl_final", help="Télécharger le code refactoré",
    )

with cp_col:
    # ⭐ Encodage base64 pour éviter tout problème d'échappement JS
    code_b64 = base64.b64encode(merged_code.encode("utf-8")).decode("ascii")
    components.html(f"""
    <div style="position:relative; display:inline-block;">
        <button id="cpb" onclick="copyCode()">
            📋 Copier
        </button>
        <div id="tip">Copié !</div>
    </div>
    <script>
        function copyCode() {{
            const code = atob("{code_b64}");
            navigator.clipboard.writeText(code).then(() => {{
                const btn = document.getElementById('cpb');
                const tip = document.getElementById('tip');
                btn.classList.add('ok');
                tip.style.display = 'block';
                setTimeout(() => {{
                    btn.classList.remove('ok');
                    tip.style.display = 'none';
                }}, 2000);
            }});
        }}
    </script>
    <style>
        #cpb{{
            height:38px;padding:0 14px;border:1px solid #d1d5db;
            border-radius:6px;background:#fff;color:#374151;
            font-size:14px;cursor:pointer;white-space:nowrap;
            display:inline-flex;align-items:center;gap:6px;
            transition:all .2s;position:relative;
        }}
        #cpb:hover{{background:#f3f4f6;border-color:#9ca3af;}}
        #cpb.ok{{background:#10b981!important;color:#fff!important;border-color:#10b981!important;}}
        #tip{{
            display:none;position:absolute;bottom:110%;left:50%;
            transform:translateX(-50%);background:#1e293b;color:#fff;
            font-size:11px;padding:3px 8px;border-radius:4px;white-space:nowrap;
            pointer-events:none;z-index:1000;
        }}
    </style>
    """, height=80, scrolling=False)

st.code(merged_code, language=lng_code)

# ── Diff coloré ────────────────────────────────────────────────────────────────
st.subheader("🔍 Différences")

diff_toggle = st.toggle(
    "Afficher les différences (original ↔ refactoré)",
    value=st.session_state.show_diff, key="diff_toggle",
)
st.session_state.show_diff = diff_toggle

if diff_toggle:
    try:
        from agents.diff_agent import DiffAgent
        diff_agent = DiffAgent()
        diff_result = diff_agent.apply(orig_code, merged_code, filename=filename)
        diff_html_fn = diff_agent.to_html
    except ImportError:
        import difflib as _dl
        class _DA:
            @staticmethod
            def apply(o,n,filename="f",context_lines=3):
                ls=list(_dl.unified_diff(o.splitlines(),n.splitlines(),
                    fromfile=f"original/{filename}",tofile=f"refactoré/{filename}",lineterm="",n=context_lines))
                dt="\n".join(ls)
                a=sum(1 for l in ls if l.startswith("+") and not l.startswith("+++"))
                r=sum(1 for l in ls if l.startswith("-") and not l.startswith("---"))
                blk=sum(1 for l in ls if l.startswith("@@"))
                return {"diff_text":dt,"has_changes":bool(dt.strip()),
                        "stats":{"added":a,"removed":r,"delta":a-r,"changed_blocks":blk}}
        diff_agent=_DA(); diff_result=diff_agent.apply(orig_code,merged_code,filename=filename)
        def diff_html_fn(dt): return None

    if not diff_result["has_changes"]:
        st.info("ℹ️ Aucune différence — code identique.")
    else:
        s=diff_result["stats"]
        s1,s2,s3,s4=st.columns(4)
        s1.metric("➕ Ajoutées",    s["added"])
        s2.metric("➖ Supprimées",  s["removed"])
        s3.metric("📊 Delta",       s["delta"])
        s4.metric("📦 Blocs",       s["changed_blocks"])

        # Légende
        st.markdown(
            '<div style="display:flex;gap:12px;margin:8px 0;">'
            '<span style="background:#14532d;color:#86efac;padding:3px 12px;border-radius:4px;font-size:13px;">＋ Ligne ajoutée</span>'
            '<span style="background:#7f1d1d;color:#fca5a5;padding:3px 12px;border-radius:4px;font-size:13px;">－ Ligne supprimée</span>'
            '<span style="background:#1e3a5f;color:#7dd3fc;padding:3px 12px;border-radius:4px;font-size:13px;">@@ Bloc modifié</span>'
            '</div>', unsafe_allow_html=True,
        )

        # Construire le HTML coloré
        dt = diff_result["diff_text"]
        if hasattr(diff_agent, "to_html"):
            html_out = diff_agent.to_html(dt)
        else:
            lh=[]
            for line in dt.splitlines():
                esc=line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                if line.startswith("+++") or line.startswith("---"):  s_="background:#1e293b;color:#94a3b8;font-weight:bold;"
                elif line.startswith("@@"):  s_="background:#1e3a5f;color:#7dd3fc;"
                elif line.startswith("+"):   s_="background:#14532d;color:#86efac;"
                elif line.startswith("-"):   s_="background:#7f1d1d;color:#fca5a5;"
                else:                        s_="background:#0f172a;color:#cbd5e1;"
                lh.append(f'<span style="{s_}padding:2px 8px;display:block;font-family:monospace;font-size:13px;">{esc}</span>')
            html_out=('<div style="border-radius:8px;border:1px solid #1e293b;background:#0f172a;'
                      'overflow-x:auto;max-height:600px;overflow-y:auto;">'+"\n".join(lh)+"</div>")

        components.html(html_out, height=520, scrolling=True)