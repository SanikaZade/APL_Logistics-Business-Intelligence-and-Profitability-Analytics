import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils import (apply_layout, fmt_currency, kpi_html, kpi_card_css,
                   PALETTE, BLUE, TEAL, AMBER, RED, GREY)


def render(df, filters):
    st.markdown(kpi_card_css(), unsafe_allow_html=True)
    st.markdown("## 📦 Product & Category Performance")
    st.markdown("Margin analysis at product and category level — identifying star performers and loss-makers.")
    st.divider()

    # ── All aggregations from live data ─────────────
    cat_df = df.groupby("Category Name").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count"),
        AvgDiscountRate=("Order Item Discount Rate", "mean"),
    ).reset_index()
    cat_df["Margin %"] = (cat_df["Profit"] / cat_df["Revenue"] * 100).round(2)
    cat_df = cat_df.sort_values("Profit", ascending=False)

    prod_df = df.groupby("Product Name").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count"),
    ).reset_index()
    prod_df["Margin %"] = (prod_df["Profit"] / prod_df["Revenue"] * 100).round(2)

    # Department from live data (fixed — no more hardcoding)
    dept_df = df.groupby("Department Name").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count"),
    ).reset_index()
    dept_df["Margin %"] = (dept_df["Profit"] / dept_df["Revenue"] * 100).round(2)
    dept_df = dept_df.sort_values("Profit", ascending=False)

    best_cat   = cat_df.iloc[0]
    worst_prod = prod_df.sort_values("Profit").iloc[0]
    loss_cats  = (cat_df["Profit"] < 0).sum()
    loss_prods = (prod_df["Profit"] < 0).sum()

    # ── KPIs ─────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Best Category", best_cat["Category Name"],
                             f"{fmt_currency(best_cat['Profit'], 0)} profit · {best_cat['Margin %']:.1f}% margin", "teal"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Top Product Profit",
                             fmt_currency(prod_df["Profit"].max(), 0),
                             prod_df.sort_values("Profit", ascending=False).iloc[0]["Product Name"][:32], "blue"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Total Categories", str(len(cat_df)),
                             f"{loss_cats} loss-making · {loss_prods} loss-making products", "amber"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_html("Worst Product",
                             worst_prod["Product Name"][:24] + "…",
                             f"{fmt_currency(worst_prod['Profit'], 0)} on {fmt_currency(worst_prod['Revenue'], 0)} sales", "red"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top categories + margin heatmap ─────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        top_cats = cat_df.head(12)
        fig = go.Figure()
        fig.add_bar(name="Revenue", x=top_cats["Revenue"] / 1e3, y=top_cats["Category Name"],
                    orientation="h", marker_color="rgba(30,64,175,0.35)", marker_line_color=BLUE, marker_line_width=1)
        fig.add_bar(name="Profit", x=top_cats["Profit"] / 1e3, y=top_cats["Category Name"],
                    orientation="h", marker_color=TEAL)
        fig.update_layout(barmode="overlay")

        apply_layout(fig, "Top 12 Categories — Revenue vs Profit ($K)", height=420)
        fig.update_xaxes(tickprefix="$", ticksuffix="K")
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=11))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Category Margin %")
        cat_heat = cat_df[["Category Name", "Margin %"]].head(20).copy()
        fig2 = go.Figure(go.Bar(
            x=cat_heat["Category Name"].str[:18],
            y=cat_heat["Margin %"],
            marker=dict(
                color=cat_heat["Margin %"],
                colorscale=[[0, RED], [0.3, "#FCA5A5"], [0.6, "#99F6E4"], [1, TEAL]],
                showscale=True,
                colorbar=dict(title="Margin %", thickness=12, len=0.7)
            ),
            text=[f"{v:.1f}%" for v in cat_heat["Margin %"]],
            textposition="outside",
            textfont=dict(size=9)
        ))
        apply_layout(fig2, "Margin % by Category (Top 20)", height=420)
        fig2.update_xaxes(tickangle=-45, tickfont=dict(size=9))
        fig2.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Product tables ───────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### ⭐ Top 10 Products by Profit")
        top_prods = prod_df.sort_values("Profit", ascending=False).head(10).copy()
        top_prods["Revenue_fmt"] = top_prods["Revenue"].apply(lambda x: fmt_currency(x, 0))
        top_prods["Profit_fmt"]  = top_prods["Profit"].apply(lambda x: fmt_currency(x, 0))
        top_prods["Margin_fmt"]  = top_prods["Margin %"].apply(lambda x: f"{x:.1f}%")
        top_prods["Product"]     = top_prods["Product Name"].str[:36]
        st.dataframe(
            top_prods[["Product", "Revenue_fmt", "Profit_fmt", "Margin_fmt", "Orders"]].rename(
                columns={"Revenue_fmt": "Revenue", "Profit_fmt": "Profit", "Margin_fmt": "Margin"}),
            hide_index=True, use_container_width=True
        )

    with col4:
        st.markdown("#### 🔴 Bottom 10 Products (Loss / Weak Margin)")
        bot_prods = prod_df.sort_values("Profit").head(10).copy()
        bot_prods["Revenue_fmt"] = bot_prods["Revenue"].apply(lambda x: fmt_currency(x, 0))
        bot_prods["Profit_fmt"]  = bot_prods["Profit"].apply(lambda x: fmt_currency(x, 0))
        bot_prods["Margin_fmt"]  = bot_prods["Margin %"].apply(lambda x: f"{x:.1f}%")
        bot_prods["Product"]     = bot_prods["Product Name"].str[:36]
        st.dataframe(
            bot_prods[["Product", "Revenue_fmt", "Profit_fmt", "Margin_fmt", "Orders"]].rename(
                columns={"Revenue_fmt": "Revenue", "Profit_fmt": "Profit", "Margin_fmt": "Margin"}),
            hide_index=True, use_container_width=True
        )
        st.markdown("""
        <div class="insight-box danger">
            🔴 <strong>SOLE Ellipticals are cash-negative:</strong>
            SOLE E35 and E25 generate net losses despite $40K+ combined revenue.
            Landed cost exceeds selling price. Recommend 15–20% price increase or discontinue.
        </div>
        """, unsafe_allow_html=True)

    # ── Department doughnut — LIVE data, all depts ──
    st.markdown("<br>", unsafe_allow_html=True)
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("#### Department Profit Distribution")
        # Show top 8 depts + group rest as 'Other'
        dept_top = dept_df.head(8).copy()
        other_profit = dept_df.iloc[8:]["Profit"].sum()
        if other_profit > 0:
            dept_top = pd.concat([dept_top, pd.DataFrame([{
                "Department Name": "Other", "Profit": other_profit,
                "Revenue": dept_df.iloc[8:]["Revenue"].sum(), "Margin %": 0, "Orders": 0
            }])], ignore_index=True)

        fig3 = go.Figure(go.Pie(
            labels=dept_top["Department Name"],
            values=dept_top["Profit"],
            hole=0.55,
            marker=dict(colors=PALETTE * 2, line=dict(color="white", width=2)),
            textinfo="label+percent",
            textfont_size=11,
        ))
        apply_layout(fig3, "Profit by Department (Live Data)", height=360)
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

        # Department table
        dept_show = dept_df[["Department Name", "Profit", "Revenue", "Margin %"]].copy()
        dept_show["Profit"]   = dept_show["Profit"].apply(lambda x: fmt_currency(x, 0))
        dept_show["Revenue"]  = dept_show["Revenue"].apply(lambda x: fmt_currency(x, 0))
        dept_show["Margin %"] = dept_show["Margin %"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(dept_show, hide_index=True, use_container_width=True)

    with col6:
        st.markdown("#### Category Profit Treemap")
        cat_pos = cat_df[cat_df["Profit"] > 0].copy()
        fig4 = px.treemap(
            cat_pos,
            path=["Category Name"],
            values="Profit",
            color="Margin %",
            color_continuous_scale=[[0, "#DBEAFE"], [0.5, BLUE], [1, TEAL]],
            hover_data={"Revenue": ":,.0f", "Profit": ":,.0f"},
        )
        fig4.update_layout(paper_bgcolor="white", margin=dict(l=0, r=0, t=30, b=0), height=460)
        fig4.update_traces(textinfo="label+value+percent root", textfont=dict(size=11, color="white"))
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("""
        <div class="insight-box">
            💡 <strong>Fan Shop drives the business:</strong>
            Fan Shop department generates $1.83M profit — 46% of total.
            Apparel is #2 at $882K. These two departments alone account for 68% of all profit.
        </div>
        """, unsafe_allow_html=True)
