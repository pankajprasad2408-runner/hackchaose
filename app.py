from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).with_name("supermarket_sales.csv")


@st.cache_data
def load_sales_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    for column in ["Order ID", "Customer Name", "Category", "Sub Category", "City", "Region"]:
        data[column] = data[column].astype(str).str.strip()

    date_text = data["Order Date"].astype(str).str.strip()
    slash_dates = date_text.str.contains("/", regex=False)
    data["Order Date"] = pd.concat(
        [
            pd.to_datetime(date_text[slash_dates], format="%m/%d/%Y"),
            pd.to_datetime(date_text[~slash_dates], format="%m-%d-%Y"),
        ]
    ).sort_index()
    data["Sales"] = pd.to_numeric(data["Sales"], errors="coerce")
    data["Profit"] = pd.to_numeric(data["Profit"], errors="coerce")
    return data.dropna(subset=["Order Date", "Sales", "Profit"])


st.set_page_config(page_title="Supermarket Sales", page_icon="📊", layout="wide")
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    h1 { color: #183c31; font-size: 2.2rem !important; }
    [data-testid="stCaptionContainer"] { color: #62766d; }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dce8e2;
        border-left: 4px solid #27805d;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        box-shadow: 0 2px 8px rgba(24, 60, 49, 0.05);
    }
    [data-testid="stMetricLabel"] { color: #62766d; }
    [data-testid="stMetricValue"] { color: #183c31; }
    </style>
    """,
    unsafe_allow_html=True,
)

sales = load_sales_data()
st.title("Supermarket Sales")
st.caption("Explore order performance across time, categories, and regions.")

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Order dates",
        value=(sales["Order Date"].min().date(), sales["Order Date"].max().date()),
        min_value=sales["Order Date"].min().date(),
        max_value=sales["Order Date"].max().date(),
    )
    categories = st.multiselect("Categories", sorted(sales["Category"].unique()))
    regions = st.multiselect("Regions", sorted(sales["Region"].unique()))
    interval = st.selectbox("Sales trend", ["Weekly", "Monthly"], index=1)

filtered = sales
if len(date_range) == 2:
    start_date, end_date = date_range
    order_dates = filtered["Order Date"]
    filtered = filtered.loc[
        order_dates.ge(pd.Timestamp(start_date))
        & order_dates.lt(pd.Timestamp(end_date) + pd.Timedelta(days=1))
    ]
if categories:
    filtered = filtered.loc[filtered["Category"].isin(categories)]
if regions:
    filtered = filtered.loc[filtered["Region"].isin(regions)]

if filtered.empty:
    st.info("No orders match these filters. Try widening the date range or clearing a selection.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
order_count = len(filtered)
average_order = filtered["Sales"].mean()

metric_columns = st.columns(4)
metric_columns[0].metric("Total sales", f"{total_sales / 1_000_000:.2f}M")
metric_columns[1].metric("Total profit", f"{total_profit / 1_000_000:.2f}M")
metric_columns[2].metric("Orders", f"{order_count:,}")
metric_columns[3].metric("Average order", f"{average_order:,.2f}")

st.subheader(f"{interval} sales")
period = "W-SUN" if interval == "Weekly" else "MS"
sales_trend = filtered.set_index("Order Date")["Sales"].resample(period).sum().rename("Sales")
trend_data = sales_trend.rename_axis("Order Date").reset_index()
trend_figure = px.area(
    trend_data,
    x="Order Date",
    y="Sales",
    template="plotly_white",
    labels={"Order Date": "Date", "Sales": "Sales"},
)
trend_figure.update_traces(line={"color": "#27805d", "width": 2.5}, fillcolor="rgba(39, 128, 93, 0.14)")
trend_figure.update_layout(
    height=340,
    margin={"l": 12, "r": 12, "t": 18, "b": 8},
    hovermode="x unified",
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis={"rangemode": "tozero", "gridcolor": "#e7eeea", "zeroline": False},
    xaxis={"showgrid": False},
)
st.plotly_chart(trend_figure, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Sales by category")
    category_sales = filtered.groupby("Category")["Sales"].sum().sort_values()
    category_data = category_sales.rename_axis("Category").reset_index(name="Sales")
    category_figure = px.bar(
        category_data,
        x="Sales",
        y="Category",
        orientation="h",
        template="plotly_white",
        color_discrete_sequence=["#27805d"],
        labels={"Sales": "Sales", "Category": ""},
    )
    category_figure.update_layout(
        height=330,
        margin={"l": 8, "r": 12, "t": 12, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"rangemode": "tozero", "gridcolor": "#e7eeea", "zeroline": False},
        yaxis={"categoryorder": "total ascending", "showgrid": False},
    )
    category_figure.update_traces(hovertemplate="%{y}<br>Sales: %{x:,.0f}<extra></extra>")
    st.plotly_chart(category_figure, use_container_width=True)

with right:
    st.subheader("Top sub-categories")
    subcategory_sales = (
        filtered.groupby("Sub Category")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(8)
        .sort_values()
    )
    subcategory_data = subcategory_sales.rename_axis("Sub-category").reset_index(name="Sales")
    subcategory_figure = px.bar(
        subcategory_data,
        x="Sales",
        y="Sub-category",
        orientation="h",
        template="plotly_white",
        color_discrete_sequence=["#d88744"],
        labels={"Sales": "Sales", "Sub-category": ""},
    )
    subcategory_figure.update_layout(
        height=330,
        margin={"l": 8, "r": 12, "t": 12, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"rangemode": "tozero", "gridcolor": "#e7eeea", "zeroline": False},
        yaxis={"categoryorder": "total ascending", "showgrid": False},
    )
    subcategory_figure.update_traces(hovertemplate="%{y}<br>Sales: %{x:,.0f}<extra></extra>")
    st.plotly_chart(subcategory_figure, use_container_width=True)

with st.expander(f"View {order_count:,} filtered orders"):
    st.dataframe(filtered.sort_values("Order Date", ascending=False), use_container_width=True, hide_index=True)
    st.download_button(
        "Download filtered orders",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_supermarket_sales.csv",
        mime="text/csv",
    )