import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import (apply_layout, fmt_currency, kpi_html, kpi_card_css,
                   PALETTE, BLUE, TEAL, AMBER, RED, GREY)


def render(df, filters):
    st.markdown(kpi_card_css(), unsafe_allow_html=True)
    st.markdown("## 🏷️ Discount Impact Analyzer")
    st.markdown("Understanding how discounting erodes margins — and where the tipping point lies.")
    st.divider()

    avg_disc   = df["Order Item Discount Rate"].mean() * 100
    avg_pr     = df["Order Item Profit Ratio"].mean() * 100
    total_disc = df["Order Item Discount"].sum()
    total_rev  = df["Sales"].sum()
    max_disc   = df["Order Item Discount Rate"].max() * 100

    # ── KPIs ─────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Avg Discount Rate", f"{avg_disc:.1f}%", f"Max observed: {max_disc:.1f}%", "amber"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Avg Profit Ratio", f"{avg_pr:.1f}%", "Net item-level margin", "blue"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Total Discounts Given", fmt_currency(total_disc), "Revenue surrendered via discounts", "red"), unsafe_allow_html=True)
    with c4:
        impact_pct = total_disc / (total_rev + total_disc) * 100
        st.markdown(kpi_html("Discount as % of Gross", f"{impact_pct:.1f}%", "Of pre-discount gross revenue", "teal"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Build discount bins from ACTUAL data range ───
    # Data only goes 0–25%, no orders above 25%
    bins   = [0, 0.05, 0.10, 0.15, 0.20, 0.25]
    labels = ["0–5%", "5–10%", "10–15%", "15–20%", "20–25%"]
    df2 = df.copy()
    df2["DiscBin"] = pd.cut(df2["Order Item Discount Rate"], bins=bins,
                             labels=labels, include_lowest=True)
    disc_agg = df2.groupby("DiscBin", observed=True).agg(
        AvgProfitRatio=("Order Item Profit Ratio", "mean"),
        OrderCount=("Sales", "count"),
        AvgProfit=("Order Profit Per Order", "mean")
    ).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        # ── Actual curve shape (non-monotonic) ──────
        fig = go.Figure()
        colors_line = [TEAL if v >= disc_agg["AvgProfitRatio"].mean() else AMBER
                       for v in disc_agg["AvgProfitRatio"]]
        fig.add_trace(go.Scatter(
            x=disc_agg["DiscBin"].astype(str),
            y=disc_agg["AvgProfitRatio"] * 100,
            mode="lines+markers",
            line=dict(color=BLUE, width=3),
            marker=dict(size=10, color=colors_line, line=dict(color="white", width=2)),
            name="Avg Profit Ratio %",
            fill="tozeroy",
            fillcolor="rgba(30,64,175,0.1)"
        ))
        # Annotate the dip zone
        fig.add_vrect(x0="10–15%", x1="15–20%",
                      fillcolor=AMBER, opacity=0.08,
                      annotation_text="Margin dip zone", annotation_position="top left")
        apply_layout(fig, "Discount Rate Band vs Avg Profit Ratio (Actual Shape)")
        fig.update_yaxes(ticksuffix="%", title="Avg Profit Ratio %", range=[11, 13])
        fig.update_xaxes(title="Discount Rate Bracket")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <div class="insight-box warn">
            ⚠️ <strong>Non-monotonic erosion pattern:</strong>
            Margin dips at 10–20% discount bands, then partially recovers at 20–25%.
            The 10–15% and 15–20% brackets are the highest-risk zones.
            Recommend tightening approval for discounts in this range rather than a blanket cap.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # ── Distribution — only real buckets (0–25%) ──
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=disc_agg["DiscBin"].astype(str),
            y=disc_agg["OrderCount"],
            marker_color=[TEAL if i < 2 else AMBER if i < 4 else RED
                          for i in range(len(disc_agg))],
            text=disc_agg["OrderCount"].apply(lambda x: f"{x:,}"),
            textposition="outside"
        ))

        apply_layout(fig2, "Order Volume by Discount Bracket (5 real buckets only)")
        fig2.update_yaxes(title="Number of Orders")
        fig2.update_xaxes(title="Discount Rate Bracket")
        st.plotly_chart(fig2, use_container_width=True)

        # Scatter: category avg discount vs avg profit ratio
        cat_disc = df.groupby("Category Name").agg(
            AvgDiscount=("Order Item Discount Rate", "mean"),
            AvgProfitRatio=("Order Item Profit Ratio", "mean"),
            TotalProfit=("Order Profit Per Order", "sum")
        ).reset_index()
        cat_disc = cat_disc[cat_disc["TotalProfit"] > 0]
        fig3 = go.Figure(go.Scatter(
            x=cat_disc["AvgDiscount"] * 100,
            y=cat_disc["AvgProfitRatio"] * 100,
            mode="markers+text",
            marker=dict(
                size=cat_disc["TotalProfit"] / cat_disc["TotalProfit"].max() * 40 + 8,
                color=BLUE, opacity=0.65,
                line=dict(color="white", width=1)
            ),
            text=cat_disc["Category Name"].str[:14],
            textposition="top center",
            textfont=dict(size=8, color=GREY)
        ))
        apply_layout(fig3, "Category — Avg Discount vs Avg Profit Ratio", height=340)
        fig3.update_xaxes(ticksuffix="%", title="Avg Discount Rate %")
        fig3.update_yaxes(ticksuffix="%", title="Avg Profit Ratio %")
        st.plotly_chart(fig3, use_container_width=True)

    # ── What-If Scenario (data-driven) ──────────────
    st.divider()
    st.markdown("### 💡 What-If Discount Scenario Simulator")
    st.markdown("Simulate profit impact of applying a max discount cap. Impact calculated from **actual affected order rows** — not a linear estimate.")

    cap_val = st.slider("Maximum Allowed Discount Rate", min_value=0, max_value=25, value=15,
                        step=1, format="%d%%")

    base_profit = df["Order Profit Per Order"].sum()
    base_rev    = df["Sales"].sum()
    cap_f       = cap_val / 100

    # Data-driven: compute actual excess discount on affected rows
    affected    = df[df["Order Item Discount Rate"] > cap_f].copy()
    excess_disc = ((df["Order Item Discount Rate"] - cap_f).clip(lower=0) *
                   pd.to_numeric(df["Order Item Product Price"], errors="coerce") *
                   pd.to_numeric(df["Order Item Quantity"], errors="coerce")).fillna(0)
    recovered   = excess_disc.sum() * 0.85   # ~85% flows to profit after variable costs
    sim_profit  = base_profit + recovered
    sim_margin  = sim_profit / base_rev * 100
    delta       = sim_profit - base_profit

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        color = "teal" if delta >= 0 else "red"
        st.markdown(kpi_html("Simulated Profit", fmt_currency(sim_profit),
                             "After applying cap to affected rows", color), unsafe_allow_html=True)
    with sc2:
        st.markdown(kpi_html("Simulated Margin", f"{sim_margin:.2f}%",
                             f"vs current {base_profit/base_rev*100:.2f}%", "blue"), unsafe_allow_html=True)
    with sc3:
        sign = "+" if delta >= 0 else ""
        st.markdown(kpi_html("Profit Delta", f"{sign}{fmt_currency(delta)}",
                             "Estimated gain from capping", "teal" if delta >= 0 else "red"), unsafe_allow_html=True)
    with sc4:
        st.markdown(kpi_html("Affected Orders", f"{len(affected):,}",
                             f"{len(affected)/len(df)*100:.1f}% of all orders above cap", "amber"), unsafe_allow_html=True)

    # Waterfall
    st.markdown("<br>", unsafe_allow_html=True)
    fig4 = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "total"],
        x=["Current Profit", f"Recovery at {cap_val}% Cap", "Simulated Profit"],
        y=[base_profit, recovered, 0],
        text=[fmt_currency(base_profit, 0), f"+{fmt_currency(recovered, 0)}", fmt_currency(sim_profit, 0)],
        textposition="outside",
        connector=dict(line=dict(color=GREY, width=1)),
        increasing=dict(marker=dict(color=TEAL)),
        decreasing=dict(marker=dict(color=RED)),
        totals=dict(marker=dict(color=BLUE))
    ))
    apply_layout(fig4, "Profit Impact Waterfall (Data-Driven Estimate)", height=340)
    fig4.update_yaxes(tickprefix="$")
    st.plotly_chart(fig4, use_container_width=True)
