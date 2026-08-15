import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nassau Candy Sales Dashboard",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background: #0e1117;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #151a23;
    }

    /* Main title */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 20px;
        color: #aab2c0;
        margin-bottom: 25px;
    }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #171d28, #202938);
        border: 1px solid #303a4d;
        border-radius: 15px;
        padding: 20px;
        min-height: 125px;
        box-shadow: 0px 5px 20px rgba(0,0,0,0.20);
    }

    .kpi-title {
        color: #aab2c0;
        font-size: 15px;
        font-weight: 600;
    }

    .kpi-value {
        color: #ffffff;
        font-size: 30px;
        font-weight: 800;
        margin-top: 8px;
    }

    .section-title {
        font-size: 26px;
        font-weight: 750;
        color: #ffffff;
        margin-top: 35px;
        margin-bottom: 10px;
    }

    /* Download button */
    .stDownloadButton button {
        border-radius: 10px;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)

# =========================================================
# FIND DATASET
# =========================================================

possible_files = [
    "Nassau Candy Distributor (1).csv",
    "Nassau Candy Distributor (1).csv",
    "Nassau Candy Distributor.xlsx",
    "Nassau Candy Distributor.csv",
    "nassau_candy.csv",
    "nassau_candy.xlsx",
    "dataset.csv",
    "data.csv",
    "sales.csv"
]

file_path = None

for file in possible_files:
    if os.path.exists(file):
        file_path = file
        break

# =========================================================
# FILE UPLOAD FALLBACK
# =========================================================

if file_path is None:

    st.sidebar.header("📂 Upload Dataset")

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is None:

        st.markdown(
            '<div class="main-title">🍫 Nassau Candy Sales Dashboard</div>',
            unsafe_allow_html=True
        )

        st.info(
            "Please upload your Nassau Candy dataset from the sidebar."
        )

        st.stop()

    file_path = uploaded_file


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data(source):

    if hasattr(source, "name"):
        filename = source.name.lower()

        if filename.endswith(".csv"):
            return pd.read_csv(source)

        return pd.read_excel(source)

    if str(source).lower().endswith(".csv"):
        return pd.read_csv(source)

    return pd.read_excel(source)


df = load_data(file_path)

# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)

# Create lowercase mapping
column_map = {
    col.lower().strip(): col
    for col in df.columns
}


def find_column(names):

    for name in names:
        if name.lower() in column_map:
            return column_map[name.lower()]

    return None


# =========================================================
# IDENTIFY IMPORTANT COLUMNS
# =========================================================

sales_col = find_column([
    "Sales",
    "Total Sales",
    "Revenue"
])

profit_col = find_column([
    "Profit",
    "Total Profit"
])

cost_col = find_column([
    "Cost",
    "Total Cost"
])

units_col = find_column([
    "Units",
    "Quantity",
    "Units Sold"
])

region_col = find_column([
    "Region"
])

division_col = find_column([
    "Division"
])

state_col = find_column([
    "State/Province",
    "State",
    "Province"
])

city_col = find_column([
    "City"
])

product_col = find_column([
    "Product Name",
    "Product",
    "Product Name "
])

order_date_col = find_column([
    "Order Date",
    "OrderDate"
])


# =========================================================
# NUMERIC CONVERSION
# =========================================================

for col in [sales_col, profit_col, cost_col, units_col]:

    if col is not None:

        df[col] = (
            df[col]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# =========================================================
# DATE CONVERSION
# =========================================================

if order_date_col is not None:

    df[order_date_col] = pd.to_datetime(
        df[order_date_col],
        errors="coerce",
        dayfirst=True
    )


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("🎛️ Dashboard Filters")

filtered_df = df.copy()

if region_col is not None:

    regions = sorted(
        filtered_df[region_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_regions = st.sidebar.multiselect(
        "Select Region",
        regions,
        default=regions
    )

    if selected_regions:
        filtered_df = filtered_df[
            filtered_df[region_col].astype(str).isin(selected_regions)
        ]


if division_col is not None:

    divisions = sorted(
        filtered_df[division_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_divisions = st.sidebar.multiselect(
        "Select Division",
        divisions,
        default=divisions
    )

    if selected_divisions:
        filtered_df = filtered_df[
            filtered_df[division_col].astype(str).isin(selected_divisions)
        ]


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🍫 Nassau Candy Sales Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Sales Performance & Business Analytics</div>',
    unsafe_allow_html=True
)


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_sales = (
    filtered_df[sales_col].sum()
    if sales_col
    else 0
)

total_profit = (
    filtered_df[profit_col].sum()
    if profit_col
    else 0
)

total_units = (
    filtered_df[units_col].sum()
    if units_col
    else len(filtered_df)
)

total_cost = (
    filtered_df[cost_col].sum()
    if cost_col
    else total_sales - total_profit
)

profit_margin = (
    (total_profit / total_sales) * 100
    if total_sales != 0
    else 0
)


# =========================================================
# KPI CARDS
# =========================================================

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">💰 Total Sales</div>
            <div class="kpi-value">${total_sales:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">📈 Total Profit</div>
            <div class="kpi-value">${total_profit:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">📦 Total Units</div>
            <div class="kpi-value">{total_units:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">💵 Total Cost</div>
            <div class="kpi-value">${total_cost:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">📊 Profit Margin</div>
            <div class="kpi-value">{profit_margin:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DATASET PREVIEW
# =========================================================

st.markdown(
    '<div class="section-title">📋 Dataset Preview</div>',
    unsafe_allow_html=True
)

st.dataframe(
    filtered_df.head(10),
    use_container_width=True,
    height=300
)


# =========================================================
# DOWNLOAD DATASET
# =========================================================

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv_data,
    file_name="nassau_candy_filtered_dataset.csv",
    mime="text/csv"
)


# =========================================================
# SALES BY REGION
# =========================================================

if region_col is not None and sales_col is not None:

    st.markdown(
        '<div class="section-title">🌎 Sales by Region</div>',
        unsafe_allow_html=True
    )

    region_sales = (
        filtered_df
        .groupby(region_col)[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
    )

    fig = px.bar(
        region_sales,
        x=region_col,
        y=sales_col,
        text_auto=".2s",
        title="Total Sales by Region",
        template="plotly_dark"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Region",
        yaxis_title="Sales ($)",
        showlegend=False,
        margin=dict(l=40, r=30, t=60, b=80)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# SALES BY DIVISION
# =========================================================

if division_col is not None and sales_col is not None:

    st.markdown(
        '<div class="section-title">🏢 Sales by Division</div>',
        unsafe_allow_html=True
    )

    division_sales = (
        filtered_df
        .groupby(division_col)[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
    )

    fig = px.bar(
        division_sales,
        x=division_col,
        y=sales_col,
        text_auto=".2s",
        title="Sales Performance by Division",
        template="plotly_dark"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Division",
        yaxis_title="Sales ($)",
        showlegend=False,
        margin=dict(l=40, r=30, t=60, b=80)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# SALES BY STATE
# =========================================================

if state_col is not None and sales_col is not None:

    st.markdown(
        '<div class="section-title">🗺️ Sales by State</div>',
        unsafe_allow_html=True
    )

    state_sales = (
        filtered_df
        .groupby(state_col)[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
        .head(15)
    )

    fig = px.bar(
        state_sales.sort_values(sales_col),
        x=sales_col,
        y=state_col,
        orientation="h",
        text_auto=".2s",
        title="Top 15 States by Sales",
        template="plotly_dark"
    )

    fig.update_layout(
        height=550,
        xaxis_title="Sales ($)",
        yaxis_title="State",
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# TOP 10 PRODUCTS
# =========================================================

if product_col is not None and sales_col is not None:

    st.markdown(
        '<div class="section-title">🍫 Top 10 Products</div>',
        unsafe_allow_html=True
    )

    product_sales = (
        filtered_df
        .groupby(product_col)[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
        .head(10)
    )

    fig = px.bar(
        product_sales.sort_values(sales_col),
        x=sales_col,
        y=product_col,
        orientation="h",
        text_auto=".2s",
        title="Top 10 Products by Sales",
        template="plotly_dark"
    )

    fig.update_layout(
        height=550,
        xaxis_title="Sales ($)",
        yaxis_title="Product",
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# TOP 10 CITIES
# =========================================================

if city_col is not None and sales_col is not None:

    st.markdown(
        '<div class="section-title">🏙️ Top 10 Cities by Sales</div>',
        unsafe_allow_html=True
    )

    city_sales = (
        filtered_df
        .groupby(city_col)[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
        .head(10)
    )

    fig = px.bar(
        city_sales.sort_values(sales_col),
        x=sales_col,
        y=city_col,
        orientation="h",
        text_auto=".2s",
        title="Top 10 Cities by Sales",
        template="plotly_dark"
    )

    fig.update_layout(
        height=500,
        xaxis_title="Sales ($)",
        yaxis_title="City",
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# MONTHLY SALES TREND
# =========================================================

if order_date_col is not None and sales_col is not None:

    st.markdown(
        '<div class="section-title">📅 Monthly Sales Trend</div>',
        unsafe_allow_html=True
    )

    monthly_df = filtered_df.dropna(
        subset=[order_date_col]
    ).copy()

    monthly_df["Month"] = (
        monthly_df[order_date_col]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_sales = (
        monthly_df
        .groupby("Month")[sales_col]
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly_sales,
        x="Month",
        y=sales_col,
        markers=True,
        text=monthly_sales[sales_col].round(0),
        title="Monthly Sales Performance",
        template="plotly_dark"
    )

    fig.update_traces(
        textposition="top center"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Month",
        yaxis_title="Sales ($)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# PROFIT BY REGION
# =========================================================

if region_col is not None and profit_col is not None:

    st.markdown(
        '<div class="section-title">📈 Profit by Region</div>',
        unsafe_allow_html=True
    )

    region_profit = (
        filtered_df
        .groupby(region_col)[profit_col]
        .sum()
        .reset_index()
        .sort_values(profit_col, ascending=False)
    )

    fig = px.bar(
        region_profit,
        x=region_col,
        y=profit_col,
        text_auto=".2s",
        title="Profit Performance by Region",
        template="plotly_dark"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Region",
        yaxis_title="Profit ($)",
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# BUSINESS INSIGHTS
# =========================================================

st.markdown(
    '<div class="section-title">💡 Business Insights</div>',
    unsafe_allow_html=True
)

insight_col1, insight_col2, insight_col3 = st.columns(3)

# Best region
if region_col is not None and sales_col is not None:

    best_region_row = (
        filtered_df
        .groupby(region_col)[sales_col]
        .sum()
        .sort_values(ascending=False)
    )

    best_region = (
        best_region_row.index[0]
        if len(best_region_row) > 0
        else "N/A"
    )

else:
    best_region = "N/A"


# Best product
if product_col is not None and sales_col is not None:

    best_product_row = (
        filtered_df
        .groupby(product_col)[sales_col]
        .sum()
        .sort_values(ascending=False)
    )

    best_product = (
        best_product_row.index[0]
        if len(best_product_row) > 0
        else "N/A"
    )

else:
    best_product = "N/A"


# Best city
if city_col is not None and sales_col is not None:

    best_city_row = (
        filtered_df
        .groupby(city_col)[sales_col]
        .sum()
        .sort_values(ascending=False)
    )

    best_city = (
        best_city_row.index[0]
        if len(best_city_row) > 0
        else "N/A"
    )

else:
    best_city = "N/A"


with insight_col1:

    st.info(
        f"🌎 **Top Region**\n\n"
        f"{best_region}"
    )


with insight_col2:

    st.info(
        f"🍫 **Top Product**\n\n"
        f"{best_product}"
    )


with insight_col3:

    st.info(
        f"🏙️ **Top City**\n\n"
        f"{best_city}"
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <center>
        <p style="color:#8b93a1;">
        Nassau Candy Sales Analytics Dashboard |
        Built with Python, Pandas, Plotly & Streamlit
        </p>
    </center>
    """,
    unsafe_allow_html=True)
import streamlit as st

# ==========================================
# ADDITIONAL OPTIMIZATION KPIs
# ==========================================

st.subheader("📊 Additional Optimization KPIs")

# Example values
# In your actual project, replace these with values
# calculated from your dataset/model.

current_cost = 125000
recommended_cost = 108000

current_capacity = 68
recommended_capacity = 84

current_shipment_cost = 95000
recommended_shipment_cost = 78000


# Calculations
cost_savings = ((current_cost - recommended_cost) / current_cost) * 100

shipment_cost_reduction = (
    (current_shipment_cost - recommended_shipment_cost)
    / current_shipment_cost
) * 100


# KPI Cards
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 Cost Savings",
        value=f"{cost_savings:.1f}%",
        delta=f"${current_cost - recommended_cost:,.0f} saved"
    )

with col2:
    st.metric(
        label="🏭 Capacity Utilization",
        value=f"{recommended_capacity}%",
        delta=f"+{recommended_capacity - current_capacity}%"
    )

with col3:
    st.metric(
        label="🚚 Shipment Cost Reduction",
        value=f"{shipment_cost_reduction:.1f}%",
        delta=f"${float(current_shipment_cost - recommended_shipment_cost):,.0f} saved"
    )


# ==========================================
# CURRENT VS RECOMMENDED COMPARISON
# ==========================================

st.subheader("📈 Current vs Recommended Scenario")

comparison_data = {
    "Metric": [
        "Operational Cost",
        "Capacity Utilization",
        "Shipment Cost"
    ],
    "Current": [
        current_cost,
        current_capacity,
        current_shipment_cost
    ],
    "Recommended": [
        recommended_cost,
        recommended_capacity,
        recommended_shipment_cost
    ]
}

st.dataframe(
    comparison_data,
    use_container_width=True,
    hide_index=True
)
st.markdown("---")
st.caption("Built with Streamlit • Created by Bhavy Code")