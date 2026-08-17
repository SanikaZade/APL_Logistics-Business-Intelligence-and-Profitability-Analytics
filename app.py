import streamlit as st
import sys
import os

# ── path so sub-modules resolve ─────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_data, get_kpis
from utils import kpi_card_css, fmt_currency, BLUE, TEAL, AMBER, RED

# ── Streamlit page config ────────────────────────────
st.set_page_config(
    page_title="APL Logistics — Profitability Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS overrides ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #F8FAFC !important;
    border-right: 1px solid #E2E8F0 !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

/* Main content */
.block-container { padding-top: 2rem !important; max-width: 1300px; }

/* Metric cards (native streamlit) */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 16px;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* Divider */
hr { border-color: #E2E8F0 !important; margin: 1.2rem 0 !important; }

/* Tabs */
.stTabs [role="tab"] { font-weight: 500; font-size: 14px; }
.stTabs [aria-selected="true"] { color: #1E40AF !important; border-bottom-color: #1E40AF !important; }

/* Selectbox / multiselect */
.stSelectbox > div, .stMultiSelect > div { border-radius: 8px !important; }

/* Slider */
.stSlider [data-baseweb="slider"] { padding: 0 4px; }

/* Remove Streamlit branding */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F1F5F9; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────
with st.spinner("Loading APL Logistics dataset…"):
    df = load_data()

# ── Sidebar ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:24px;">
        <div style="background:#1E40AF;border-radius:8px;width:36px;height:36px;
                    display:flex;align-items:center;justify-content:center;font-size:20px;">🚢</div>
        <div>
            <div style="font-weight:700;font-size:16px;color:#0F172A;">APL Logistics</div>
            <div style="font-size:11px;color:#64748B;">KWE Group Analytics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔽 Global Filters")
    st.markdown("<br>", unsafe_allow_html=True)

    # Market filter
    markets = ["All Markets"] + sorted(df["Market"].dropna().unique().tolist())
    sel_market = st.selectbox("🌍 Market", markets)

    # Segment filter
    segments = ["All Segments"] + sorted(df["Customer Segment"].dropna().unique().tolist())
    sel_segment = st.selectbox("👤 Customer Segment", segments)

    # Shipping mode filter
    ship_modes = ["All Modes"] + sorted(df["Shipping Mode"].dropna().unique().tolist())
    sel_ship = st.selectbox("🚚 Shipping Mode", ship_modes)

    # Category filter (multiselect)
    all_cats = sorted(df["Category Name"].dropna().unique().tolist())
    sel_cats = st.multiselect("📦 Product Categories", all_cats, placeholder="All categories")

    # Discount rate range
    st.markdown("**🏷️ Discount Rate Range**")
    disc_range = st.slider("", 0, 30, (0, 25), format="%d%%", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    # Apply filters
    filt = df.copy()
    if sel_market  != "All Markets":  filt = filt[filt["Market"] == sel_market]
    if sel_segment != "All Segments": filt = filt[filt["Customer Segment"] == sel_segment]
    if sel_ship    != "All Modes":    filt = filt[filt["Shipping Mode"] == sel_ship]
    if sel_cats:                      filt = filt[filt["Category Name"].isin(sel_cats)]
    filt = filt[
        (filt["Order Item Discount Rate"] * 100 >= disc_range[0]) &
        (filt["Order Item Discount Rate"] * 100 <= disc_range[1])
    ]

    # Mini KPI summary in sidebar
    st.divider()
    st.markdown("**📌 Filtered Summary**")
    kpis = get_kpis(filt)
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Orders",  f"{kpis['total_orders']:,}")
        st.metric("Revenue", fmt_currency(kpis['total_revenue'], 1))
    with col_b:
        st.metric("Profit",  fmt_currency(kpis['total_profit'], 1))
        st.metric("Margin",  f"{kpis['profit_margin']:.1f}%")

    st.divider()
    st.markdown(f"""
    <div style="font-size:11px;color:#94A3B8;text-align:center;">
        Showing <strong style="color:#1E40AF">{len(filt):,}</strong> of {len(df):,} orders
    </div>
    """, unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────
PAGES = {
    "📊 Revenue & Profit":    "p1_overview",
    "👤 Customer Value":      "p2_customer",
    "📦 Product & Category":  "p3_product",
    "🏷️ Discount Impact":     "p4_discount",
    "🌍 Market & Region":     "p5_market",
    "📋 Executive Summary":   "p6_executive",
}

# Tab-based navigation at the top
tabs = st.tabs(list(PAGES.keys()))

page_modules = {}
for mod_name in PAGES.values():
    module = __import__(f"pages_.{mod_name}", fromlist=[mod_name])
    page_modules[mod_name] = module

filters = {
    "market": sel_market,
    "segment": sel_segment,
    "ship_mode": sel_ship,
    "categories": sel_cats,
    "disc_range": disc_range,
}

for tab, (page_label, mod_name) in zip(tabs, PAGES.items()):
    with tab:
        page_modules[mod_name].render(filt, filters)
