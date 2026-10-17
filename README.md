# Supermarket Sales Dashboard

A simple Streamlit dashboard for exploring supermarket order sales and profit.

## Run the App

Python 3.9 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## Dashboard

- Filter orders by date, category, and region.
- View total sales, total profit, order count, and average order value.
- Compare weekly or monthly sales trends, sales by category, and the top eight sub-categories.
- Expand the filtered order table and download its contents as a CSV file.

## Data

Keep `supermarket_sales.csv` in the same folder as `app.py`. The dashboard reads the CSV directly and parses both date formats present in the dataset. Sales and profit are shown without a currency symbol because the data does not specify a currency.