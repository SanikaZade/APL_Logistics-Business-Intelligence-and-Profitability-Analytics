# 🚢 Customer, Product, and Profitability Performance Analysis in Supply Chain Operations

> **APL Logistics Business Intelligence & Profitability Analytics Dashboard**  
> An interactive, enterprise-grade data analytics application engineered with **Streamlit**, **Pandas**, and **Plotly** to evaluate supply chain efficiency, customer lifetime value, product margin health, discount erosion, and regional logistics performance across **180,519+ order records**.

---

## 📋 Executive Overview

In global supply chain management, driving revenue without granular profitability visibility often obscures critical margin leakage caused by unoptimized discounting, high delivery delay risks, and underperforming product lines. 

This project delivers a multi-page interactive **Executive Business Intelligence Dashboard** tailored for supply chain executives, logistics planners, and financial analysts at **APL Logistics (KWE Group)**. By synthesizing complex transactional data into actionable strategic insights, the dashboard empowers decision-makers to optimize pricing strategies, mitigate operational bottlenecks, refine customer targeting, and reclaim lost profitability.

---

## 💡 Key Business Findings & Strategic Impact

* **Financial Summary:** Analyzed **$36.8M+ in total revenue** across **180,519 order transactions**, uncovering **$3.97M in net profit** (overall profit margin of **10.8%**).
* **Critical Operational Risk:** Identified a **54.8% Late Delivery Risk** rate across shipments, signaling a severe logistics bottleneck that directly threatens customer retention and service-level agreement (SLA) compliance.
* **Product Profit Drivers:** **Fishing equipment** emerged as the top-performing category contributing **$756K in net profit**, whereas specific fitness lines (e.g., **SOLE E35 & E25 Ellipticals**) consistently generated net losses due to excessive promotional discounting.
* **Regional Insights:** Profit margins remain strikingly uniform (~10.8%) across all geographic markets. This proves that regional profit disparities are driven strictly by **order volume and product mix**, rather than localized pricing power.
* **Discount Erosion:** Discount rates exceeding **15%** cause a steep drop in margin efficiency without yielding proportional volume lift, highlighting an immediate opportunity for discount governance.

---

## 🛠️ Tech Stack & Engineering Architecture

| Layer | Technologies Used | Description & Implementation Details |
| :--- | :--- | :--- |
| **Language** | `Python 3.9+` | Core programming engine powering data processing & UI rendering. |
| **Data Processing & Analytics** | `Pandas`, `NumPy` | Vectorized operations, missing value handling, dynamic filtering, numeric coercion, and custom KPI feature engineering. |
| **UI & Application Framework** | `Streamlit (v1.32+)` | Modular dashboard framework with custom CSS styling, responsive layout containers, stateful sidebar controls, and dynamic tab routing. |
| **Data Visualization** | `Plotly (v5.18+)` | Interactive visual components: Choropleth maps, treemaps, multi-axis scatter plots, waterfall charts, and real-time scorecards. |
| **Caching & Optimization** | `@st.cache_data` | In-memory data caching for zero-latency filter recalculations across 180,000+ records. |

---

## 📁 Repository Structure

```
apl_dashboard/
├── app.py                  # Main entry point: Global styles, stateful filters & page router
├── data_loader.py          # Data ingestion, vectorized cleaning, feature engineering & caching
├── utils.py                # Reusable UI cards, custom CSS themes, color tokens & chart wrappers
├── requirements.txt        # Project dependencies (Streamlit, Pandas, NumPy, Plotly)
├── APL_Logistics.csv       # Primary supply chain dataset (180,519 transactional records)
├── .streamlit/
│   └── config.toml         # Custom Streamlit theme configurations
└── pages_/                 # Modular analytical dashboard pages
    ├── __init__.py
    ├── p1_overview.py      # Revenue & Profit Overview Dashboard
    ├── p2_customer.py      # Customer Segmentation & Lifetime Value Analytics
    ├── p3_product.py       # Product Category Profitability & Margin Treemaps
    ├── p4_discount.py      # Discount Sensitivity Curve & What-If Simulator
    ├── p5_market.py        # Global Logistics, Shipping & Regional Choropleth Maps
    └── p6_executive.py     # Executive Scorecard & Strategic Action Plan
```

---

## 📊 Detailed Dashboard Features & Analytics Modules

### 1. 📊 Revenue & Profitability Overview (`p1_overview.py`)
* **Executive Metrics:** High-level KPIs displaying Revenue, Total Profit, Net Margin %, Total Orders, and Average Discount.
* **Market & Channel Breakdowns:** Bar and line charts evaluating revenue distribution and shipping mode margins.
* **Order Status Analytics:** Financial impact analysis grouped by order status (Complete, Pending, Closed, On Hold).

### 2. 👤 Customer Value & Segmentation (`p2_customer.py`)
* **Customer LTV Matrix:** Interactive scatter plot comparing overall sales volume vs. profit contribution by customer.
* **Segment Analysis:** Profitability split across Consumer, Corporate, and Home Office segments.
* **Top & Bottom Analysis:** Identifies high-value enterprise accounts and loss-inducing customer profiles.

### 3. 📦 Product & Category Performance (`p3_product.py`)
* **Category Treemaps:** Visual hierarchy mapping sales volume and profit margins by product category.
* **Loss-Making Product Detection:** Automated identification of products operating at negative net margins.
* **Price vs. Profit Margin Curves:** Scatter plot correlating item unit prices with realized profit ratios.

### 4. 🏷️ Discount Impact & What-If Simulator (`p4_discount.py`)
* **Margin Erosion Waterfall Chart:** Quantifies exact revenue loss attributed to order item discounts.
* **Interactive What-If Profit Simulator:** Slider-based interactive model allowing decision-makers to simulate the financial return of capping discount rates at 5%, 10%, or 15%.
* **Discount vs. Profitability Curve:** Line analysis showing the exact tipping point where discounts degrade total net return.

### 5. 🌍 Market & Regional Logistics (`p5_market.py`)
* **Global Geographic Choropleth Map:** Color-coded country map illustrating sales volume and regional profitability.
* **Late Delivery Risk Radar:** Operational delivery performance metric cross-referenced with shipping modes (Standard Class, First Class, Same Day, Second Class).
* **Shipping Delay Calculator:** Variance metrics comparing actual vs. scheduled shipping days.

### 6. 📋 Executive Summary & Recommendations (`p6_executive.py`)
* **Operational Health Scorecard:** Integrated radial gauges measuring SLA compliance, discount health, and category risk.
* **Strategic Action Plans:** 6 structured operational recommendations for supply chain turnaround, pricing governance, and logistics optimization.

---

## ⚙️ Data Pipeline & Engineering Methodology

1. **Ingestion & Data Cleansing (`data_loader.py`):**
   * Loaded large-scale supply chain transactional dataset (`180,519` records, `APL_Logistics.csv`).
   * Enforced explicit type casting across 13 numeric financial metrics (Sales, Profit, Discounts, Days for Shipping).
   * Filtered out corrupted records with zero or negative sales values.
2. **Feature Engineering:**
   * **Profit Margin %:** Realized profit expressed as a percentage of total gross sales.
   * **Shipping Delay:** Calculated metric `Days for shipping (real) - Days for shipment (scheduled)`.
   * **Late Delivery Risk Indicator:** Binary flags aggregated to measure SLA non-compliance rates.
3. **Interactive Filter Engine (`app.py`):**
   * Real-time multi-variable filtering across Market, Customer Segment, Shipping Mode, Category, and Discount Rate Range sliders.
   * Universal state propagation across all 6 analytical pages without reloading raw datasets.

---

## 🚀 Quickstart & Local Setup Guide

### Prerequisites
* Python `3.9` or higher installed on your system.

### 1. Clone Repository & Navigate
```bash
git clone https://github.com/SanikaZade/APL_Logistics-Business-Intelligence-and-Profitability-Analytics.git
cd APL_Logistics-Business-Intelligence-and-Profitability-Analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
Open your browser at **`http://localhost:8501`** to view the live dashboard.

---
