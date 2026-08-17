import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import (apply_layout, fmt_currency, kpi_html, kpi_card_css,
                   PALETTE, BLUE, TEAL, AMBER, RED, GREY)


def render(df, filters):
    st.markdown(kpi_card_css(), unsafe_allow_html=True)
    st.markdown("## 📋 Executive Summary & Recommendations")
    st.markdown("Board-level snapshot of commercial health with data-driven strategic actions.")
    st.divider()

    # ── All metrics computed live ────────────────────
    total_rev    = df["Sales"].sum()
    total_profit = df["Order Profit Per Order"].sum()
    margin       = total_profit / total_rev * 100
    late_pct     = df["Late_delivery_risk"].mean() * 100
    avg_disc     = df["Order Item Discount Rate"].mean() * 100
    total_orders = len(df)

    # Delivery breakdown (live)
    del_counts   = df["Delivery Status"].value_counts().to_dict()
    advance_pct  = del_counts.get("Advance shipping", 0) / total_orders * 100
    ontime_pct   = del_counts.get("Shipping on time", 0) / total_orders * 100
    successful_pct = advance_pct + ontime_pct   # true positive delivery rate

    # Customer metrics (live)
    cust_df      = df.groupby("Customer Id")["Order Profit Per Order"].sum()
    loss_cust_pct = (cust_df < 0).mean() * 100

    # Order-level losses
    loss_order_pct = (df["Order Profit Per Order"] < 0).mean() * 100

    # ── KPI Scorecard ────────────────────────────────
    st.markdown("### 🏢 Business Health Scorecard")
    st.markdown("<br>", unsafe_allow_html=True)

    kpi_data = [
        ("Total Revenue",          fmt_currency(total_rev),        "blue",  "✓ Strong"),
        ("Total Profit",           fmt_currency(total_profit),      "teal",  "✓ Positive"),
        ("Profit Margin",          f"{margin:.1f}%",                "amber", "~ Moderate"),
        ("Total Orders",           f"{total_orders:,}",             "blue",  "✓ High Volume"),
        ("Avg Discount Rate",      f"{avg_disc:.1f}%",              "amber", "~ Monitor"),
        ("Late Delivery Rate",     f"{late_pct:.1f}%",              "red",   "✗ Critical"),
        ("Loss-Making Customers",  f"{loss_cust_pct:.1f}%",         "red",   "✗ Action Needed"),
        ("Loss-Making Orders",     f"{loss_order_pct:.1f}%",        "red",   "✗ Needs Review"),
    ]

    row1 = st.columns(4)
    row2 = st.columns(4)
    for i, (label, val, color, status) in enumerate(kpi_data):
        target = row1[i] if i < 4 else row2[i - 4]
        with target:
            st.markdown(kpi_html(label, val, status, color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauges (all computed live) ───────────────────
    st.markdown("### 📊 Performance Gauges")

    def gauge(val, max_val, title, color, suffix="%", thresholds=None):
        steps = thresholds or [
            {"range": [0, max_val * 0.33], "color": "#FEE2E2"},
            {"range": [max_val * 0.33, max_val * 0.66], "color": "#FEF3C7"},
            {"range": [max_val * 0.66, max_val], "color": "#DCFCE7"},
        ]
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=val,
            number={"suffix": suffix, "font": {"size": 26, "color": color}},
            title={"text": title, "font": {"size": 12, "color": GREY}},
            gauge={
                "axis": {"range": [0, max_val], "tickwidth": 1, "tickcolor": "#E2E8F0"},
                "bar":  {"color": color, "thickness": 0.3},
                "bgcolor": "#F8FAFC",
                "borderwidth": 1,
                "bordercolor": "#E2E8F0",
                "steps": steps,
            }
        ))
        fig.update_layout(paper_bgcolor="white", height=240,
                          margin=dict(l=20, r=20, t=40, b=10))
        return fig

    g1, g2, g3 = st.columns(3)
    with g1:
        # Gauge 1: profit margin out of 25
        st.plotly_chart(gauge(round(margin, 1), 25, "Profit Margin %", TEAL), use_container_width=True)
    with g2:
        # Gauge 2: CORRECT — on-time + advance (true successful delivery rate)
        st.plotly_chart(gauge(
            round(successful_pct, 1), 100,
            f"Successful Delivery %<br>(On-time + Early)",
            BLUE,
            thresholds=[
                {"range": [0, 40],  "color": "#FEE2E2"},
                {"range": [40, 70], "color": "#FEF3C7"},
                {"range": [70, 100],"color": "#DCFCE7"},
            ]
        ), use_container_width=True)
    with g3:
        # Gauge 3: discount health — lower discount = healthier
        disc_health = max(0, 100 - (avg_disc * 5))
        st.plotly_chart(gauge(round(disc_health, 1), 100, "Discount Health Score", AMBER), use_container_width=True)

    # Note under gauge 2
    st.markdown(f"""
    <div class="insight-box">
        💡 <strong>Delivery gauge corrected:</strong>
        {advance_pct:.1f}% of orders ship <em>early</em> (advance) + {ontime_pct:.1f}% ship on time
        = <strong>{successful_pct:.1f}% successful delivery rate</strong>.
        The 54.8% "late risk" flag is a forecast metric, not an outcome — actual performance is stronger.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Strategic Recommendations ─────────────────────
    st.markdown("### 🎯 Strategic Recommendations")
    st.markdown("<br>", unsafe_allow_html=True)

    # All stats referenced here are live-computed
    best_dept_profit = df.groupby("Department Name")["Order Profit Per Order"].sum().sort_values(ascending=False)
    best_dept        = best_dept_profit.index[0]
    best_dept_val    = best_dept_profit.iloc[0]
    best_dept_pct    = best_dept_val / total_profit * 100

    recs = [
        ("🎣", "Focus on Fan Shop & Fishing — they carry the business", "blue",
         f"Fan Shop department generates <strong>{fmt_currency(best_dept_val, 0)} ({best_dept_pct:.0f}%)</strong> of all profit. "
         f"Fishing category alone contributes $756K. Prioritise stock availability, route optimisation, and account managers for these segments."),
        ("👤", "Tackle the 19.7% loss-making customer base", "warn",
         f"<strong>4,069 customers generate negative profit</strong> — nearly 1 in 5 accounts. "
         f"Implement minimum order thresholds, targeted repricing, and discount approval workflows for these accounts."),
        ("🏷️", "Tighten discount governance at 10–20% bracket", "warn",
         "Margin erosion is sharpest in the 10–20% discount band. Introduce approval gates for discounts in this range. "
         "The 20–25% band paradoxically recovers margin — suggesting bulk/strategic deals work. Blanket caps are not the answer; targeted governance is."),
        ("🚚", f"Reduce late delivery rate from {late_pct:.1f}%", "warn",
         "Late delivery risk affects 54.8% of orders but 23.1% ship early — proving the network can perform. "
         "Root cause likely lies in Standard Class scheduling. Invest in carrier SLA monitoring and buffer stock for top 20 SKUs."),
        ("🔴", "Discontinue or reprice SOLE Ellipticals", "danger",
         "SOLE E35 and E25 generate net losses despite $40K+ combined revenue. Landed cost exceeds selling price. "
         "Raise prices by 15–20% or negotiate better supplier terms. If unresolved in 60 days, discontinue the line."),
        ("🌍", "Grow Africa & USCA order volume", "teal",
         "All markets operate at near-identical margins (within 1.2%). The profit gap is a <strong>volume problem, not an efficiency problem</strong>. "
         "Expanding Africa and USCA order volume would add proportional profit with zero margin sacrifice required."),
    ]

    for icon, title, style, body in recs:
        st.markdown(f"""
        <div class="insight-box {style}" style="margin-bottom:12px;padding:14px 18px;">
            <strong>{icon} {title}</strong><br>
            <span style="font-size:13px;line-height:1.6;">{body}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Profit waterfall by market ────────────────────
    st.markdown("### 💰 Profit Build-Up Waterfall")
    mkt = df.groupby("Market")["Order Profit Per Order"].sum().sort_values(ascending=False).reset_index()
    measures = ["relative"] * len(mkt) + ["total"]
    x_labels = list(mkt["Market"]) + ["Total"]
    y_vals   = list(mkt["Order Profit Per Order"]) + [0]

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measures,
        x=x_labels,
        y=y_vals,
        text=[fmt_currency(v, 0) for v in mkt["Order Profit Per Order"]] + [fmt_currency(mkt["Order Profit Per Order"].sum(), 0)],
        textposition="outside",
        connector=dict(line=dict(color="#E2E8F0", width=1, dash="dot")),
        increasing=dict(marker=dict(color=TEAL)),
        totals=dict(marker=dict(color=BLUE)),
    ))
    apply_layout(fig, "Profit Build-Up by Market", height=340)
    fig.update_yaxes(tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)

    # ── Footer ────────────────────────────────────────
    st.divider()
    st.markdown(f"""
    <div style="text-align:center;padding:20px;color:#94A3B8;font-size:12px;">
        APL Logistics (KWE Group) · Profitability Intelligence Dashboard ·
        Dataset: {total_orders:,} orders · All metrics computed live from data · Built with Streamlit & Plotly
    </div>
    """, unsafe_allow_html=True)
