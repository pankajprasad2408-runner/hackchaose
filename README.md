# Supermarket Sales Forecasting & Dashboard

End-to-end analysis of 9,994 supermarket orders (2015–2018): cleaned the raw data, ran exploratory analysis, engineered a weekly time-series feature set, benchmarked forecasting models against naive baselines, and shipped an interactive dashboard.

**Result: the final Linear Regression model reached R² 0.679, MAE 20,300 and RMSE 24,172 on held-out 2018 weekly sales — an 8% error reduction over the best naive baseline.**

---

## What's in here

| File | What it is |
|---|---|
| `PS03_Sales_Forecasting.ipynb` | The full analysis — 14 steps, from raw CSV to forecast and business insights |
| `app.py` | Streamlit dashboard for exploring sales and profit interactively |
| `supermarket_sales.csv` | The dataset (9,994 orders) |
| `SourceCode.ipynb` | Supporting notebook |

## The problem

The dataset has no `Quantity` or `Price` column, so revenue cannot be rebuilt from units — `Sales` is the only target. Two conflicting date formats appear in `Order Date` (`m/d/Y` and `m-d-Y`), `State` has a single value, and `Region` is not tied to `City`. Any forecast built on this data has to survive those constraints, and the notebook documents each one rather than hiding it.

## Approach

**1. Cleaning.** Resolved the two mixed date formats, validated ranges (no negative sales or profit, discounts within 0–1), and profiled every column before modelling.

**2. Exploratory analysis.** Sales and profit broken down by category, region and sub-category, plus distribution and box plots to check spread within each category.

**3. Time-series preparation.** Resampled to weekly total sales and engineered eight features: `lag_1`, `lag_2`, `lag_4`, `lag_52` (seasonal), a 4-week rolling mean, a linear trend term, and Fourier seasonality (`season_sin`, `season_cos`).

**4. Baselines first.** Four naive forecasts were evaluated before any model, so the ML results have something honest to beat:

| Model | MAE | RMSE | R² | MAPE |
|---|---|---|---|---|
| Naive (last week) | 22,118 | 29,373 | 0.526 | 19.7% |
| Moving average (4 weeks) | 33,838 | 39,037 | 0.162 | 27.6% |
| Seasonal naive (lag_52) | 32,064 | 37,901 | 0.210 | 26.3% |
| Seasonal naive × growth | 22,039 | 28,728 | 0.546 | 19.4% |

**5. Models.** Linear Regression and Random Forest (`n_estimators=300`, `min_samples_leaf=2`) trained on the same features:

| Model | MAE | RMSE | R² | MAPE |
|---|---|---|---|---|
| **Linear Regression** | **20,300** | **24,172** | **0.679** | **18.5%** |
| Seasonal naive × growth | 22,039 | 28,728 | 0.546 | 19.4% |
| Random Forest | 28,647 | 34,051 | 0.363 | 23.1% |

Mean weekly sales in the test window: **122,412**. Linear Regression cut MAE by 8% against the best baseline and 18% against the naive last-week forecast.

**6. Validation beyond one split.** The result was re-checked on four rolling test windows rather than a single train/test split:

| Test window | LinReg MAE | Baseline MAE | Beats baseline |
|---|---|---|---|
| 2017-01-08 → 2017-07-02 | 50,952 | 15,919 | ✗ |
| 2017-07-09 → 2017-12-31 | 20,714 | 23,212 | ✓ |
| 2018-01-07 → 2018-07-01 | 17,357 | 19,740 | ✓ |
| 2018-07-08 → 2018-12-30 | 20,300 | 22,039 | ✓ |

The first window fails — 52 training weeks is not enough history for a model that relies on `lag_52`. That limitation is stated in the notebook rather than left out.

**7. Forecast and insights.** A recursive 4-week-ahead forecast, error broken down by month to show where the model under-predicts, and category/region performance summaries.

## Honest limitations

- Order values are close to uniformly distributed, so the dataset looks synthetic; the model's accuracy should not be read as evidence of real-world supermarket forecasting skill.
- `Region` is not tied to `City` and `State` is constant, so no genuine geographic signal could be extracted.
- One rolling window shows the model underperforming a naive baseline when training history is short.

## Run the dashboard

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`. Keep `supermarket_sales.csv` beside `app.py`.

**Dashboard features:** filter orders by date, category and region · total sales, total profit, order count and average order value · weekly or monthly sales trends · sales by category and top 8 sub-categories · download the filtered table as CSV.

## Stack

Python · Pandas · NumPy · Scikit-learn · Matplotlib · Seaborn · Streamlit · Plotly · Jupyter

---

*Built by [Pankaj Prasad](https://github.com/pankajprasad2408-runner) — 2nd-year B.Tech (AI & Data Science), Arya College of Engineering, Jaipur.*
