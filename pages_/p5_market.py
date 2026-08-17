import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils import (apply_layout, fmt_currency, kpi_html, kpi_card_css,
                   PALETTE, BLUE, TEAL, AMBER, RED, GREY)


def render(df, filters):
    st.markdown(kpi_card_css(), unsafe_allow_html=True)
    st.markdown("## 🌍 Market & Regional Profit Analysis")
    st.markdown("Profitability across global markets, order regions, and countries.")
    st.divider()

    # ── All aggregations live ────────────────────────
    mkt_df = df.groupby("Market").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count"),
    ).reset_index()
    mkt_df["Margin %"] = (mkt_df["Profit"] / mkt_df["Revenue"] * 100).round(2)
    mkt_df = mkt_df.sort_values("Profit", ascending=False)

    reg_df = df.groupby("Order Region").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count"),
    ).reset_index()
    reg_df["Margin %"] = (reg_df["Profit"] / reg_df["Revenue"] * 100).round(2)
    reg_df = reg_df.sort_values("Profit", ascending=False)

    cty_df = df.groupby("Order Country").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count"),
    ).reset_index()
    cty_df["Margin %"] = (cty_df["Profit"] / cty_df["Revenue"] * 100).round(2)

    best_mkt  = mkt_df.iloc[0]
    worst_mkt = mkt_df.iloc[-1]
    best_reg  = reg_df.iloc[0]
    # Correct: highest margin market (computed live, not assumed)
    highest_margin_mkt = mkt_df.sort_values("Margin %", ascending=False).iloc[0]

    # ── KPIs ─────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Highest Profit Market", best_mkt["Market"],
                             f"{fmt_currency(best_mkt['Profit'], 0)} total profit", "teal"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Highest Margin Market", highest_margin_mkt["Market"],
                             f"{highest_margin_mkt['Margin %']:.2f}% profit margin", "blue"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Active Markets", str(len(mkt_df)),
                             " · ".join(mkt_df["Market"].tolist()), "amber"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_html("Lowest Profit Market", worst_mkt["Market"],
                             f"{fmt_currency(worst_mkt['Profit'], 0)} profit · {worst_mkt['Margin %']:.2f}% margin", "red"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Market revenue vs profit ─────────────────────
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_bar(name="Revenue ($M)", x=mkt_df["Market"], y=mkt_df["Revenue"] / 1e6,
                    marker_color="rgba(30,64,175,0.35)", marker_line_color=BLUE, marker_line_width=1)
        fig.add_bar(name="Profit ($M)", x=mkt_df["Market"], y=mkt_df["Profit"] / 1e6,
                    marker_color=TEAL)
        fig.update_layout(barmode="group")
        apply_layout(fig, "Revenue vs Profit by Market ($M)")
        fig.update_yaxes(tickprefix="$", ticksuffix="M")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Margin bar — sorted by actual margin value
        mkt_sorted = mkt_df.sort_values("Margin %")
        # Color: highest margin = teal, rest = blue gradient
        max_m = mkt_sorted["Margin %"].max()
        colors = [TEAL if m == max_m else BLUE for m in mkt_sorted["Margin %"]]
        fig2 = go.Figure(go.Bar(
            x=mkt_sorted["Margin %"],
            y=mkt_sorted["Market"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.2f}%" for v in mkt_sorted["Margin %"]],
            textposition="outside"
        ))
        apply_layout(fig2, "Profit Margin % by Market (Sorted)")
        fig2.update_xaxes(ticksuffix="%",
                          range=[mkt_sorted["Margin %"].min() - 0.3, mkt_sorted["Margin %"].max() + 0.3])
        st.plotly_chart(fig2, use_container_width=True)

    # ── Top 12 regions bar ───────────────────────────
    st.markdown("#### Top 12 Regions by Profit")
    top_reg = reg_df.head(12)

    # Highlight outliers: below 10% = red, above 12% = teal
    bar_colors = []
    for _, r in top_reg.iterrows():
        if r["Margin %"] < 10:
            bar_colors.append(RED)
        elif r["Margin %"] > 12:
            bar_colors.append(TEAL)
        else:
            bar_colors.append(BLUE)

    fig3 = go.Figure(go.Bar(
        x=top_reg["Order Region"],
        y=top_reg["Profit"] / 1e3,
        marker_color=bar_colors,
        text=[f"{fmt_currency(v*1000,0)}<br>{m:.1f}%" for v, m in zip(top_reg["Profit"]/1e3, top_reg["Margin %"])],
        textposition="outside",
        textfont=dict(size=10)
    ))
    apply_layout(fig3, "Profit by Region ($K) — Red = margin <10%, Teal = margin >12%", height=360)
    fig3.update_xaxes(tickangle=-30)
    fig3.update_yaxes(tickprefix="$", ticksuffix="K")
    st.plotly_chart(fig3, use_container_width=True)

    # ── Market table + choropleth ────────────────────
    col3, col4 = st.columns([2, 3])

    with col3:
        st.markdown("#### Market Summary Table")
        mkt_show = mkt_df.copy()
        mkt_show["Revenue"]  = mkt_show["Revenue"].apply(lambda x: fmt_currency(x, 0))
        mkt_show["Profit"]   = mkt_show["Profit"].apply(lambda x: fmt_currency(x, 0))
        mkt_show["Margin %"] = mkt_show["Margin %"].apply(lambda x: f"{x:.2f}%")
        mkt_show["Orders"]   = mkt_show["Orders"].apply(lambda x: f"{x:,}")
        st.dataframe(mkt_show[["Market", "Revenue", "Profit", "Margin %", "Orders"]],
                     hide_index=True, use_container_width=True)

        # Region margin spread with outlier callout
        st.markdown("<br>**Region Margin Spread**")
        fig4 = go.Figure()
        fig4.add_trace(go.Box(
            y=reg_df["Margin %"], name="All Regions",
            marker_color=BLUE, line_color=BLUE,
            fillcolor="rgba(30,64,175,0.15)", boxmean=True,
            boxpoints="outliers", pointpos=0,
        ))
        apply_layout(fig4, "Margin % Distribution — All Regions (outliers shown)", height=300)
        fig4.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig4, use_container_width=True)

        # Highlight outlier regions
        low_regions  = reg_df[reg_df["Margin %"] < 10][["Order Region", "Margin %"]]
        high_regions = reg_df[reg_df["Margin %"] > 12][["Order Region", "Margin %"]]
        if len(low_regions):
            st.markdown(f"""<div class="insight-box danger">
                🔴 <strong>Below 10% margin:</strong> {', '.join(low_regions['Order Region'].tolist())}
                — review pricing and discount policy in these regions.</div>""", unsafe_allow_html=True)
        if len(high_regions):
            st.markdown(f"""<div class="insight-box teal">
                ✨ <strong>Above 12% margin:</strong> {', '.join(high_regions['Order Region'].tolist())}
                — star regions to learn from and scale.</div>""", unsafe_allow_html=True)

    with col4:
        st.markdown("#### Country-Level Profit Map")
        fig5 = px.choropleth(
            cty_df,
            locations="Order Country",
            locationmode="country names",
            color="Profit",
            hover_name="Order Country",
            hover_data={"Revenue": ":,.0f", "Profit": ":,.0f", "Margin %": ":.2f"},
            color_continuous_scale=[[0, "#EFF6FF"], [0.4, BLUE], [1, TEAL]],
            labels={"Profit": "Profit ($)"}
        )

        fig5.update_layout(
            paper_bgcolor="white",
            geo=dict(bgcolor="white", showframe=False, showcoastlines=True,
                     coastlinecolor="#E2E8F0", showland=True, landcolor="#F8FAFC",
                     showocean=True, oceancolor="#EFF6FF"),
            coloraxis_colorbar=dict(title="Profit", thickness=12),
            margin=dict(l=0, r=0, t=30, b=0),
            height=440
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""
    <div class="insight-box teal">
        💡 <strong>Volume, not efficiency, drives the profit gap:</strong>
        Margins are nearly identical across all 5 markets (within 1.2% of each other).
        Europe leads in profit purely because it has the highest order volume.
        The strategic lever is <strong>growing order volume in lower-volume markets</strong> — not improving margins.
    </div>
    """, unsafe_allow_html=True)
