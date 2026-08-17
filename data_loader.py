import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("APL_Logistics.csv", encoding="latin-1")

    # Clean numeric columns
    num_cols = [
        "Benefit per order", "Sales per customer", "Order Item Discount",
        "Order Item Discount Rate", "Order Item Product Price",
        "Order Item Profit Ratio", "Order Item Quantity", "Sales",
        "Order Item Total", "Order Profit Per Order", "Product Price",
        "Days for shipping (real)", "Days for shipment (scheduled)"
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Sales", "Order Profit Per Order"])
    df = df[df["Sales"] > 0]

    # Derived columns
    df["Profit Margin %"] = (df["Order Profit Per Order"] / df["Sales"] * 100).round(2)
    df["Shipping Delay"] = df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]

    return df


def get_kpis(df):
    return {
        "total_revenue": df["Sales"].sum(),
        "total_profit": df["Order Profit Per Order"].sum(),
        "profit_margin": df["Order Profit Per Order"].sum() / df["Sales"].sum() * 100,
        "total_orders": len(df),
        "avg_discount": df["Order Item Discount Rate"].mean() * 100,
        "avg_profit_ratio": df["Order Item Profit Ratio"].mean() * 100,
        "late_delivery_pct": df["Late_delivery_risk"].mean() * 100,
        "unique_customers": df["Customer Id"].nunique(),
    }
