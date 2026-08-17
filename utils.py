import plotly.graph_objects as go
import plotly.express as px

# ── Colour palette (white theme) ──────────────────
BLUE       = "#1E40AF"
BLUE_LIGHT = "#3B82F6"
BLUE_PALE  = "#DBEAFE"
TEAL       = "#0D9488"
TEAL_PALE  = "#CCFBF1"
AMBER      = "#D97706"
AMBER_PALE = "#FEF3C7"
RED        = "#DC2626"
RED_PALE   = "#FEE2E2"
GREY       = "#64748B"
GREY_PALE  = "#F1F5F9"
TEXT_DARK  = "#0F172A"
TEXT_MID   = "#475569"

PALETTE = [BLUE, TEAL, AMBER, "#7C3AED", "#DB2777", "#059669", "#EA580C", "#0369A1"]

def hex_to_rgba(hex_str, opacity):
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return f"rgba({r}, {g}, {b}, {opacity})"

LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color=TEXT_DARK, size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    legend=dict(bgcolor="white", bordercolor="#E2E8F0", borderwidth=1),
    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#E2E8F0", tickfont=dict(size=11)),
    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#E2E8F0", tickfont=dict(size=11)),
)


def apply_layout(fig, title="", height=380):
    fig.update_layout(
        **LAYOUT,
        title=dict(text=title, font=dict(size=14, color=TEXT_DARK), x=0, xanchor="left"),
        height=height,
    )
    return fig


def fmt_currency(val, decimals=2):
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:.{decimals}f}M"
    if abs(val) >= 1_000:
        return f"${val/1_000:.{decimals}f}K"
    return f"${val:.{decimals}f}"


def kpi_card_css():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .kpi-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        border-radius: 12px 12px 0 0;
    }
    .kpi-card.blue::before  { background: #1E40AF; }
    .kpi-card.teal::before  { background: #0D9488; }
    .kpi-card.amber::before { background: #D97706; }
    .kpi-card.red::before   { background: #DC2626; }
    .kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.7px; color: #64748B; margin-bottom: 8px; }
    .kpi-value { font-size: 28px; font-weight: 700; letter-spacing: -0.8px; margin-bottom: 4px; }
    .kpi-value.blue  { color: #1E40AF; }
    .kpi-value.teal  { color: #0D9488; }
    .kpi-value.amber { color: #D97706; }
    .kpi-value.red   { color: #DC2626; }
    .kpi-sub { font-size: 12px; color: #94A3B8; }

    .insight-box {
        background: #EFF6FF;
        border-left: 3px solid #1E40AF;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin-top: 12px;
        font-size: 13px;
        color: #1E3A8A;
    }
    .insight-box.warn  { background:#FFFBEB; border-color:#D97706; color:#78350F; }
    .insight-box.danger{ background:#FEF2F2; border-color:#DC2626; color:#7F1D1D; }
    .insight-box.teal  { background:#F0FDFA; border-color:#0D9488; color:#134E4A; }

    .tag {
        display: inline-block; padding: 2px 10px;
        border-radius: 9999px; font-size: 11px; font-weight: 600;
    }
    .tag-green  { background:#DCFCE7; color:#166534; }
    .tag-red    { background:#FEE2E2; color:#991B1B; }
    .tag-amber  { background:#FEF3C7; color:#92400E; }
    .tag-blue   { background:#DBEAFE; color:#1E3A8A; }
    .tag-grey   { background:#F1F5F9; color:#475569; }
    </style>
    """


def kpi_html(label, value, sub, color="blue"):
    return f"""
    <div class="kpi-card {color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {color}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """
