"""
Real-Time Market Movement Prediction System - Streamlit Frontend
Professional dark trading dashboard
"""

import streamlit as st
from api_client import get_api_client

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MarketMind AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ── CSS Variables ── */
:root {
    --bg-base:      #EEF2F9;
    --bg-surface:   #FFFFFF;
    --bg-sidebar:   #1E3A5F;
    --accent-blue:  #2563EB;
    --accent-light: #3B82F6;
    --accent-sky:   #0EA5E9;
    --text-primary: #0F172A;
    --text-secondary: #475569;
    --text-muted:   #94A3B8;
    --border:       #CBD5E1;
    --border-light: #E2E8F0;
    --green:        #10B981;
    --red:          #EF4444;
    --amber:        #F59E0B;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
}

.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1400px;
    background-color: var(--bg-base);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] .status-dot {
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; margin-right: 8px; vertical-align: middle;
}
[data-testid="stSidebar"] .dot-green  { background: #34D399; box-shadow: 0 0 6px #34D399; }
[data-testid="stSidebar"] .dot-red    { background: #F87171; box-shadow: 0 0 6px #F87171; }
[data-testid="stSidebar"] .dot-yellow { background: #FCD34D; box-shadow: 0 0 6px #FCD34D; }
[data-testid="stSidebar"] .sidebar-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: #64748B !important;
    margin-bottom: 3px;
}
[data-testid="stSidebar"] .sidebar-value {
    font-size: 0.92rem; font-weight: 600; color: #F1F5F9 !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Header ── */
.page-header {
    display: flex; align-items: center; gap: 1rem;
    padding: 1.5rem 2rem;
    background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
    border-radius: 14px;
    margin-bottom: 1.5rem;
}
.header-logo { font-size: 2.4rem; line-height: 1; }
.header-title {
    font-size: 1.9rem; font-weight: 800;
    letter-spacing: -0.02em; color: #FFFFFF; line-height: 1.1;
}
.header-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: rgba(255,255,255,0.55);
    margin-top: 5px;
}

/* ── Section Labels ── */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent-blue);
    margin-bottom: 0.9rem; margin-top: 0.3rem;
    display: flex; align-items: center; gap: 8px;
}
.section-label::after {
    content: ''; flex: 1;
    height: 1px; background: var(--border-light);
}

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 10px !important;
    padding: 1.2rem 1.4rem !important;
    position: relative; overflow: hidden;
    box-shadow: 0 1px 4px rgba(37,99,235,0.06);
    transition: box-shadow 0.2s, border-color 0.2s;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 16px rgba(37,99,235,0.12) !important;
    border-color: var(--accent-light) !important;
}
[data-testid="stMetric"]::before {
    content: ''; position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    background: linear-gradient(180deg, var(--accent-sky), var(--accent-blue));
    border-radius: 10px 0 0 10px;
}
[data-testid="stMetricLabel"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}

/* ── Info alerts (data sources) ── */
[data-testid="stAlert"] {
    background: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 8px !important;
    color: var(--accent-blue) !important;
    font-weight: 600;
    font-size: 0.82rem;
}

/* ── Button ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-sky)) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    padding: 0.65rem 1.4rem !important;
    box-shadow: 0 2px 10px rgba(37,99,235,0.25) !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] > button:hover {
    box-shadow: 0 4px 20px rgba(37,99,235,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Divider ── */
hr { border-color: var(--border-light) !important; margin: 1.5rem 0 !important; }

/* ── Signal Badge ── */
.signal-badge {
    display: inline-block;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.08em;
}
.signal-bull    { background: #DCFCE7; color: #15803D; border: 1px solid #BBF7D0; }
.signal-bear    { background: #FEE2E2; color: #B91C1C; border: 1px solid #FECACA; }
.signal-neutral { background: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }

/* ── Text ── */
p, .stMarkdown p { color: var(--text-secondary); font-size: 0.9rem; }
strong { color: var(--text-primary) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-blue); }

/* ── Footer ── */
.footer {
    text-align: center;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.12em;
    color: var(--text-muted);
    padding: 2rem 0 1rem;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================

api = get_api_client()

def fmt(val, d=3):
    try: return f"{float(val):.{d}f}"
    except: return "—"

def status_dot(s):
    s = str(s).lower()
    if s in ("active","running","online","ok","loaded"): return "dot-green", s.upper()
    if s in ("inactive","offline","error"):              return "dot-red",   s.upper()
    return "dot-yellow", s.upper()

def safe_get(endpoint_fn):
    try:
        r = endpoint_fn()
        return None if r.get("status") == "error" else r, r.get("message","") if r.get("status")=="error" else ""
    except Exception as e:
        return None, str(e)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">System Status</div>', unsafe_allow_html=True)
    st.markdown("---")

    # API
    st.markdown('<div class="sidebar-label">API</div>', unsafe_allow_html=True)
    try:
        h = api.health_check()
        if h.get("status") == "error": raise Exception()
        css, lbl = status_dot(h.get("api","ok"))
        st.markdown(f'<div class="sidebar-value"><span class="status-dot {css}"></span>{lbl}</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="sidebar-value"><span class="status-dot dot-red"></span>OFFLINE</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Model
    st.markdown('<div class="sidebar-label">Model</div>', unsafe_allow_html=True)
    try:
        mi = api.get_model_info()
        if mi.get("status") == "error": raise Exception()
        st.markdown(f'<div class="sidebar-value"><span class="status-dot dot-green"></span>{mi.get("model_name","—")}</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="sidebar-value"><span class="status-dot dot-red"></span>OFFLINE</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Pipeline
    st.markdown('<div class="sidebar-label">Pipeline</div>', unsafe_allow_html=True)
    try:
        pl = api.get_pipeline_status()
        if pl.get("status") == "error": raise Exception()
        css, lbl = status_dot(pl.get("model_status","unknown"))
        st.markdown(f'<div class="sidebar-value"><span class="status-dot {css}"></span>{lbl}</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="sidebar-value"><span class="status-dot dot-red"></span>OFFLINE</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sidebar-label">Last refreshed · just now</div>', unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="page-header">
  <div class="header-logo">⚡</div>
  <div>
    <div class="header-title">MarketMind AI</div>
    <div class="header-sub">LSTM · Multi-Source Fusion · Real-Time Prediction</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# PERFORMANCE METRICS
# ============================================================

st.markdown('<div class="section-label">▸ Model Performance</div>', unsafe_allow_html=True)

metrics, err = safe_get(api.get_metrics)
if not metrics:
    st.error(f"Could not load metrics{': ' + err if err else ''}")
else:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Test Accuracy",   fmt(metrics.get("final_test_accuracy",0), 4))
    with c2: st.metric("F1 Score",        fmt(metrics.get("final_test_f1_score",0), 4))
    with c3: st.metric("RMSE",            fmt(metrics.get("final_test_rmse",0),     4))
    with c4: st.metric("Status", "READY")

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# MARKET SNAPSHOT
# ============================================================

st.markdown('<div class="section-label">▸ Latest Market Snapshot</div>', unsafe_allow_html=True)

mkt, err = safe_get(api.get_latest_market_data)
if not mkt:
    st.error(f"Could not load market data{': ' + err if err else ''}")
else:
    signal = mkt.get("market_signal", "NEUTRAL")
    sig_cls = "signal-bull" if signal == "Bullish" else ("signal-bear" if signal == "Bearish" else "signal-neutral")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Symbol",      mkt.get("symbol","—"))
    with c2:
        ts = mkt.get("timestamp","—")
        st.metric("Date", ts[:10] if isinstance(ts, str) else str(ts))
    with c3: st.metric("Close Price", f"${float(mkt.get('close_price',0)):.2f}")
    with c4:
        st.metric("Signal", signal)
        st.markdown(f'<span class="signal-badge {sig_cls}">{signal.upper()}</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Technical Indicators**")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("RSI (14)",      fmt(mkt.get("RSI",0),          2))
    with c2: st.metric("MACD",          fmt(mkt.get("MACD",0),         4))
    with c3: st.metric("Reddit Hype",   fmt(mkt.get("reddit_hype",0),  3))
    with c4: st.metric("News Count",    int(mkt.get("news_count",0)))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Sentiment**")
    c1, c2, *_ = st.columns(4)
    with c1: st.metric("Market Sentiment", fmt(mkt.get("market_sentiment",0), 3))

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# DATASET INFO
# ============================================================

st.markdown('<div class="section-label">▸ Dataset Information</div>', unsafe_allow_html=True)

ds, err = safe_get(api.get_dataset_info)
if not ds:
    st.error(f"Could not load dataset info{': ' + err if err else ''}")
else:
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Rows",       f"{int(ds.get('total_rows',0)):,}")
    with c2: st.metric("Total Features",   int(ds.get("total_features",0)))
    with c3: st.metric("Sequence Length",  int(ds.get("sequence_length",0)))

    symbols = ds.get("market_symbols",[])
    if symbols:
        sym_str = "  ·  ".join(str(s) for s in symbols[:12])
        if len(symbols) > 12: sym_str += f"  ·  +{len(symbols)-12} more"
        st.markdown(f"<br><small style='font-family:Space Mono,monospace;color:#3A5570;font-size:0.7rem;letter-spacing:0.1em'>{sym_str}</small>", unsafe_allow_html=True)

    sources = ds.get("data_sources",[])
    if sources:
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(len(sources))
        for i, src in enumerate(sources):
            with cols[i]: st.info(f"✦  {src}")

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# PREDICTION
# ============================================================

st.markdown('<div class="section-label">▸ Prediction Engine</div>', unsafe_allow_html=True)

c1, c2 = st.columns([4, 1])
with c1:
    st.markdown("Run inference using live sample data pulled from the backend pipeline.")
with c2:
    run_pred = st.button("⚡ Run Inference", use_container_width=True)

if run_pred:
    with st.spinner("Fetching sample · Running LSTM inference..."):
        try:
            sample = api.get_sample_input()
            if sample.get("status") == "error":
                st.error(f"Sample fetch failed: {sample.get('message','')}")
            else:
                features = sample.get("features", [])
                result   = api.predict(features)

                if result.get("status") == "error":
                    st.error(f"Inference failed: {result.get('message','')}")
                else:
                    pred  = result.get("prediction","—")
                    conf  = result.get("confidence", 0)
                    model = result.get("model","—")

                    sig_cls = "signal-bull" if pred == "UP" else "signal-bear"
                    arrow   = "▲" if pred == "UP" else "▼"

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<div class="section-label">▸ Inference Result</div>', unsafe_allow_html=True)

                    rc1, rc2, rc3 = st.columns(3)
                    with rc1:
                        st.metric("Prediction", pred)
                        st.markdown(f'<span class="signal-badge {sig_cls}">{arrow} {pred}</span>', unsafe_allow_html=True)
                    with rc2:
                        st.metric("Confidence", fmt(conf, 4))
                    with rc3:
                        st.metric("Model", model)

                    st.success("Inference complete.")

        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# MODEL ARCHITECTURE
# ============================================================

st.markdown('<div class="section-label">▸ Model Architecture</div>', unsafe_allow_html=True)

mi, err = safe_get(api.get_model_info)
if not mi:
    st.error(f"Could not load model info{': ' + err if err else ''}")
else:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**Core**")
        st.metric("Architecture",   mi.get("architecture","—"))
        st.metric("Sequence Len",   mi.get("sequence_length","—"))
    with c2:
        st.markdown("**Layers**")
        st.metric("Hidden Size",    mi.get("hidden_size","—"))
        st.metric("Num Layers",     mi.get("num_layers","—"))
    with c3:
        st.markdown("**Training**")
        st.metric("Optimizer",      mi.get("optimizer","—"))
        st.metric("Loss Function",  mi.get("loss_function","—"))
    with c4:
        st.markdown("**Config**")
        st.metric("Dropout",        mi.get("dropout","—"))
        st.metric("Epochs",         mi.get("epochs","—"))


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
  ⚡ MarketMind AI &nbsp;·&nbsp; LSTM Financial Prediction &nbsp;·&nbsp;
  FastAPI + Streamlit &nbsp;·&nbsp; Yahoo Finance · Reddit · Finnhub · Alpha Vantage
</div>
""", unsafe_allow_html=True)