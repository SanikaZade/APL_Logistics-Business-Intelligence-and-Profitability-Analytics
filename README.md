# 🚢 APL Logistics — Profitability Intelligence Dashboard

A fully interactive **Streamlit** dashboard for Customer, Product, and Profitability
Performance Analysis in Supply Chain Operations.

---

## 📁 Project Structure

```
apl_dashboard/
├── app.py                  ← Main entry point
├── data_loader.py          ← Data loading & caching
├── utils.py                ← Shared styles, chart helpers, colors
├── requirements.txt        ← Python dependencies
├── APL_Logistics.csv       ← Dataset (180,519 orders)
├── .streamlit/
│   └── config.toml         ← White theme config
└── pages_/
    ├── __init__.py
    ├── p1_overview.py      ← Revenue & Profit Overview
    ├── p2_customer.py      ← Customer Value Dashboard
    ├── p3_product.py       ← Product & Category Performance
    ├── p4_discount.py      ← Discount Impact Analyzer
    ├── p5_market.py        ← Market & Regional Analysis
    └── p6_executive.py     ← Executive Summary & Recommendations
```

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the dashboard
```bash
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

---

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| **Revenue & Profit** | KPIs, market comparison, order status, delivery breakdown |
| **Customer Value** | Top/bottom customers, segment analysis, scatter plot |
| **Product & Category** | Category margins, treemap, top/loss products |
| **Discount Impact** | Discount vs margin curve, what-if simulator, waterfall |
| **Market & Region** | Choropleth map, regional bars, margin comparison |
| **Executive Summary** | Scorecard, gauges, 6 strategic recommendations |

---

## 🔽 Global Filters (Sidebar)
- 🌍 Market selector
- 👤 Customer Segment
- 🚚 Shipping Mode
- 📦 Product Category (multi-select)
- 🏷️ Discount Rate Range slider

All charts update live based on your filter selection.

---

## 🛠️ Tech Stack
- **Streamlit** — UI framework
- **Pandas** — Data processing
- **Plotly** — Interactive charts
- **Python 3.9+**

---

## 📌 Key Findings
- Total Revenue: **$36.8M** | Total Profit: **$3.97M** | Margin: **10.8%**
- Late delivery risk: **54.8%** — critical operational issue
- Best category: **Fishing** ($756K profit)
- Loss-making: **SOLE E35 & E25** Ellipticals
- Margins are uniform across markets — profit gap is a **volume problem**
