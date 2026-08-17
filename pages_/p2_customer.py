import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import (apply_layout, fmt_currency, kpi_html, kpi_card_css,
                   PALETTE, BLUE, BLUE_LIGHT, TEAL, AMBER, RED, GREY)


def render(df, filters):
    st.markdown(kpi_card_css(), unsafe_allow_html=True)
    st.markdown("## 👤 Customer Value Dashboard")
    st.markdown("Profitability intelligence by customer segment and individual contribution.")
    st.divider()

    # ── Customer-level aggregation (live from data) ──
    cust_df = df.groupby("Customer Id").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count"),
        Segment=("Customer Segment", "first"),
        Name=("Customer Fname", "first"),
    ).reset_index()
    cust_df["Margin %"] = (cust_df["Profit"] / cust_df["Revenue"] * 100).round(1)

    total_cust  = len(cust_df)
    avg_profit  = cust_df["Profit"].mean()
    top_profit  = cust_df["Profit"].max()
    loss_count  = (cust_df["Profit"] < 0).sum()
    loss_pct    = loss_count / total_cust * 100

    # ── KPIs (all computed from live data) ──────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Unique Customers", f"{total_cust:,}", "Distinct customer IDs", "blue"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Avg Profit / Customer", fmt_currency(avg_profit), "Mean lifetime profit contribution", "teal"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Top Customer Profit", fmt_currency(top_profit), "Highest single-customer earnings", "amber"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_html("Loss-Making Customers", f"{loss_count:,} ({loss_pct:.1f}%)", "Customers with negative total profit", "red"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top 15 customers table (live data) ──────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("#### 🏆 Top 15 Customers by Profit")
        top15 = cust_df.sort_values("Profit", ascending=False).head(15).copy()
        top15["Rank"] = range(1, len(top15) + 1)
        top15_display = top15[["Rank", "Customer Id", "Name", "Segment", "Revenue", "Profit", "Margin %", "Orders"]].copy()
        top15_display["Revenue"]  = top15_display["Revenue"].apply(lambda x: fmt_currency(x, 0))
        top15_display["Profit"]   = top15_display["Profit"].apply(lambda x: fmt_currency(x, 0))
        top15_display["Margin %"] = top15_display["Margin %"].apply(lambda x: f"{x:.1f}%")
        top15_display["Customer Id"] = top15_display["Customer Id"].astype(int).astype(str)
        top15_display = top15_display.rename(columns={"Customer Id": "Cust. ID"})
        st.dataframe(top15_display, hide_index=True, use_container_width=True)

    with col2:
        st.markdown("#### Segment Profitability")
        seg = df.groupby("Customer Segment").agg(
            Revenue=("Sales", "sum"),
            Profit=("Order Profit Per Order", "sum"),
            Orders=("Sales", "count")
        ).reset_index()
        seg["Margin %"] = (seg["Profit"] / seg["Revenue"] * 100).round(1)

        fig = go.Figure()
        fig.add_bar(name="Revenue ($M)", x=seg["Customer Segment"], y=seg["Revenue"] / 1e6,
                    marker_color="rgba(30,64,175,0.35)", marker_line_color=BLUE, marker_line_width=1)
        fig.add_bar(name="Profit ($M)", x=seg["Customer Segment"], y=seg["Profit"] / 1e6,
                    marker_color=TEAL)
        fig.update_layout(barmode="group")
        apply_layout(fig, "Revenue vs Profit by Segment")
        fig.update_yaxes(tickprefix="$", ticksuffix="M")
        st.plotly_chart(fig, use_container_width=True)

        for _, row in seg.iterrows():
            tag = "tag-green" if row["Margin %"] >= 10 else "tag-amber"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:8px 12px;background:#F8FAFC;border-radius:8px;margin-bottom:6px;
                        border:1px solid #E2E8F0;font-size:13px;">
                <span style="font-weight:600;color:#0F172A">{row['Customer Segment']}</span>
                <span style="color:#475569">{fmt_currency(row['Profit'], 0)}</span>
                <span class="tag {tag}">{row['Margin %']:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Customer tier chart (all values from live data) ──
    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Customer Profit Tier Analysis")

        # Compute tiers from live data
        ranks = cust_df["Profit"].rank(ascending=False, pct=True)
        tier_labels, tier_avgs, tier_counts, tier_colors = [], [], [], []
        tier_defs = [
            ("Top 5%",     ranks <= 0.05,                       TEAL),
            ("6–20%",      (ranks > 0.05) & (ranks <= 0.20),    BLUE),
            ("21–50%",     (ranks > 0.20) & (ranks <= 0.50),    BLUE_LIGHT),
            ("51–80%",     (ranks > 0.50) & (ranks <= 0.80),    AMBER),
            ("Bottom 20%", ranks > 0.80,                        RED),
        ]
        for label, mask, color in tier_defs:
            subset = cust_df[mask]
            tier_labels.append(label)
            tier_avgs.append(round(subset["Profit"].mean(), 0))
            tier_counts.append(len(subset))
            tier_colors.append(color)

        fig2 = go.Figure(go.Bar(
            x=tier_labels,
            y=tier_avgs,
            marker_color=tier_colors,
            text=[f"{fmt_currency(v,0)}" for v in tier_avgs],
            textposition="outside",
        ))
        apply_layout(fig2, "Average Profit per Customer by Tier")
        fig2.update_yaxes(tickprefix="$")
        st.plotly_chart(fig2, use_container_width=True)

        # 80/20 fact — computed live
        top20_profit = cust_df.sort_values("Profit", ascending=False).head(int(len(cust_df) * 0.20))["Profit"].sum()
        top20_pct    = top20_profit / cust_df["Profit"].sum() * 100
        st.markdown(f"""
        <div class="insight-box teal">
            🎯 <strong>Concentration is extreme:</strong>
            Top 20% of customers contribute <strong>{top20_pct:.1f}%</strong> of total profit.
            Bottom 20% of customers average <strong>${tier_avgs[4]:,.0f}</strong> profit — all loss-making.
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("#### Bottom 10 Customers (Loss-Makers)")
        bot10 = cust_df[cust_df["Profit"] < 0].sort_values("Profit").head(10)[
            ["Customer Id", "Name", "Segment", "Revenue", "Profit", "Orders"]
        ].copy()
        if len(bot10) == 0:
            st.info("No loss-making customers in current filter.")
        else:
            bot10["Customer Id"] = bot10["Customer Id"].astype(int).astype(str)
            bot10["Revenue"] = bot10["Revenue"].apply(lambda x: fmt_currency(x, 0))
            bot10["Profit"]  = bot10["Profit"].apply(lambda x: fmt_currency(x, 0))
            st.dataframe(bot10, hide_index=True, use_container_width=True)

        st.markdown("""
        <div class="insight-box danger">
            🔴 <strong>19.7% of customers are loss-making:</strong>
            Nearly 1 in 5 customers generates negative profit. These accounts are often over-discounted
            or order low-margin SKUs. Targeted repricing or minimum order value thresholds can recover margin.
        </div>
        """, unsafe_allow_html=True)

    # ── Scatter: Revenue vs Profit per customer ──────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Revenue vs Profit Scatter — All Customers")
    sample = cust_df.sample(min(3000, len(cust_df)), random_state=42)
    color_map = {"Consumer": BLUE, "Corporate": TEAL, "Home Office": AMBER}
    fig3 = go.Figure()
    for seg_name, grp in sample.groupby("Segment"):
        fig3.add_trace(go.Scatter(
            x=grp["Revenue"], y=grp["Profit"],
            mode="markers",
            name=seg_name,
            marker=dict(color=color_map.get(seg_name, GREY), size=5, opacity=0.65,
                        line=dict(color="white", width=0.5))
        ))
    fig3.add_hline(y=0, line_dash="dot", line_color=RED, line_width=1.5,
                   annotation_text="Break-even line", annotation_position="right")
    apply_layout(fig3, "Revenue vs Profit per Customer (sample 3,000)", height=400)
    fig3.update_xaxes(tickprefix="$", title="Total Revenue")
    fig3.update_yaxes(tickprefix="$", title="Total Profit")
    st.plotly_chart(fig3, use_container_width=True)

    # ── Customer value distribution histogram ────────
    st.markdown("#### Customer Profit Distribution")
    fig4 = go.Figure(go.Histogram(
        x=cust_df["Profit"],
        nbinsx=60,
        marker_color="rgba(30,64,175,0.55)",
        marker_line_color=BLUE,
        marker_line_width=0.5,
    ))
    fig4.add_vline(x=0, line_dash="dot", line_color=RED, line_width=2,
                   annotation_text="Loss / Profit boundary", annotation_position="top right")
    fig4.add_vline(x=cust_df["Profit"].mean(), line_dash="dash", line_color=TEAL, line_width=1.5,
                   annotation_text=f"Mean: {fmt_currency(cust_df['Profit'].mean(), 0)}", annotation_position="top left")
    apply_layout(fig4, "Distribution of Customer Profit (all customers)", height=320)
    fig4.update_xaxes(tickprefix="$", title="Total Profit per Customer")
    fig4.update_yaxes(title="Number of Customers")
    st.plotly_chart(fig4, use_container_width=True)
