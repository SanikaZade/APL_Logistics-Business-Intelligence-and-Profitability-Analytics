import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import (apply_layout, fmt_currency, kpi_html, kpi_card_css,
                   PALETTE, BLUE, TEAL, AMBER, RED, GREY)

STATUS_LABELS = {
    'COMPLETE': 'Complete', 'PENDING_PAYMENT': 'Pending Payment',
    'PROCESSING': 'Processing', 'PENDING': 'Pending',
    'CLOSED': 'Closed', 'ON_HOLD': 'On Hold',
    'SUSPECTED_FRAUD': 'Suspected Fraud', 'CANCELED': 'Canceled',
    'PAYMENT_REVIEW': 'Payment Review'
}

def render(df, filters):
    st.markdown(kpi_card_css(), unsafe_allow_html=True)
    st.markdown("## 📊 Revenue & Profit Overview")
    st.markdown(f"Aggregate financial performance across **{len(df):,} orders** — APL Logistics global operations.")
    st.divider()

    total_rev    = df["Sales"].sum()
    total_profit = df["Order Profit Per Order"].sum()
    margin       = total_profit / total_rev * 100
    late_pct     = df["Late_delivery_risk"].mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Total Revenue", fmt_currency(total_rev), "Across all markets & segments", "blue"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Total Profit", fmt_currency(total_profit), "Net after discounts & costs", "teal"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Profit Margin", f"{margin:.1f}%", "Revenue-to-profit efficiency", "amber"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_html("Late Delivery Risk", f"{late_pct:.1f}%", "Orders flagged for late delivery", "red"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Delivery status breakdown (ALL 4 statuses) ──
    col1, col2 = st.columns([3, 2])

    with col1:
        mkt = df.groupby("Market").agg(
            Revenue=("Sales", "sum"),
            Profit=("Order Profit Per Order", "sum")
        ).reset_index().sort_values("Revenue", ascending=False)

        fig = go.Figure()
        fig.add_bar(name="Revenue", x=mkt["Market"], y=mkt["Revenue"]/1e6,
                    marker_color="rgba(30,64,175,0.35)", marker_line_color=BLUE, marker_line_width=1)
        fig.add_bar(name="Profit", x=mkt["Market"], y=mkt["Profit"]/1e6,
                    marker_color=TEAL)
        fig.update_layout(barmode="group")
        apply_layout(fig, "Revenue vs Profit by Market ($M)")
        fig.update_yaxes(tickprefix="$", ticksuffix="M")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Delivery status - all 4 actual values with correct labels
        del_counts = df["Delivery Status"].value_counts().reset_index()
        del_counts.columns = ["Status", "Count"]
        color_map_del = {
            "Late delivery":       RED,
            "Advance shipping":    TEAL,
            "Shipping on time":    BLUE,
            "Shipping canceled":   AMBER,
        }
        fig2 = go.Figure(go.Pie(
            labels=del_counts["Status"],
            values=del_counts["Count"],
            hole=0.58,
            marker=dict(
                colors=[color_map_del.get(s, GREY+"CC") for s in del_counts["Status"]],
                line=dict(color="white", width=2)
            ),
            textinfo="percent+label",
            textfont_size=11,
        ))
        apply_layout(fig2, "Delivery Status — All 4 Outcomes")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Shipping mode + Order status + Segment ──
    col3, col4, col5 = st.columns(3)

    with col3:
        ship = df.groupby("Shipping Mode")["Order Profit Per Order"].sum().reset_index()
        ship = ship.sort_values("Order Profit Per Order", ascending=True)
        fig3 = go.Figure(go.Bar(
            x=ship["Order Profit Per Order"] / 1e3,
            y=ship["Shipping Mode"],
            orientation="h",
            marker_color=PALETTE[:len(ship)],
            text=[fmt_currency(v * 1000, 0) for v in ship["Order Profit Per Order"] / 1e3],
            textposition="outside",
        ))
        apply_layout(fig3, "Profit by Shipping Mode ($K)")
        fig3.update_xaxes(tickprefix="$", ticksuffix="K")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Order status with readable labels and ALL 9 statuses
        status_counts = df["Order Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        status_counts["Label"] = status_counts["Status"].map(STATUS_LABELS).fillna(status_counts["Status"])
        fig4 = go.Figure(go.Pie(
            labels=status_counts["Label"],
            values=status_counts["Count"],
            hole=0.55,
            marker=dict(colors=PALETTE * 2, line=dict(color="white", width=1)),
            textinfo="percent",
            textfont_size=10,
        ))
        apply_layout(fig4, "Order Status — All 9 Statuses")
        fig4.update_layout(legend=dict(font=dict(size=9)))
        st.plotly_chart(fig4, use_container_width=True)

    with col5:
        seg = df.groupby("Customer Segment")["Order Profit Per Order"].sum().reset_index()
        fig5 = go.Figure(go.Pie(
            labels=seg["Customer Segment"],
            values=seg["Order Profit Per Order"],
            hole=0.6,
            marker=dict(colors=[BLUE, TEAL, AMBER], line=dict(color="white", width=2)),
            textinfo="label+percent",
            textfont_size=12,
        ))
        apply_layout(fig5, "Profit by Customer Segment")
        fig5.update_layout(showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

    # ── Delivery KPI callout boxes ──────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    dc1, dc2, dc3, dc4 = st.columns(4)
    del_data = df["Delivery Status"].value_counts().to_dict()
    total_orders = len(df)

    with dc1:
        v = del_data.get("Late delivery", 0)
        st.markdown(kpi_html("Late Delivery", f"{v:,}", f"{v/total_orders*100:.1f}% of orders", "red"), unsafe_allow_html=True)
    with dc2:
        v = del_data.get("Advance shipping", 0)
        st.markdown(kpi_html("Shipped Early ✨", f"{v:,}", f"{v/total_orders*100:.1f}% of orders", "teal"), unsafe_allow_html=True)
    with dc3:
        v = del_data.get("Shipping on time", 0)
        st.markdown(kpi_html("On Time", f"{v:,}", f"{v/total_orders*100:.1f}% of orders", "blue"), unsafe_allow_html=True)
    with dc4:
        v = del_data.get("Shipping canceled", 0)
        st.markdown(kpi_html("Canceled", f"{v:,}", f"{v/total_orders*100:.1f}% of orders", "amber"), unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box warn" style="margin-top:14px">
        ⚠️ <strong>Late Delivery is the #1 operational risk:</strong>
        54.8% of orders face late delivery risk. However, 23.1% of orders ship <em>early</em> (advance shipping) —
        showing the logistics network can perform well. Focus on reducing the late segment, not just the average.
    </div>
    """, unsafe_allow_html=True)
