from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Indonesia Exchange Rates Dashboard",
    page_icon="💱",
    layout="wide",
)

# App Title & Description
st.title("💱 Indonesian Rupiah (IDR) Exchange Rates Dashboard")
st.markdown(
    "This interactive dashboard tracks historical exchange rates of major"
    " global currencies against the Indonesian Rupiah (IDR) using live and"
    " historical public financial data."
)


# Function to fetch or load exchange rate dataset
@st.cache_data
def load_exchange_data():
  # Try loading local generated CSV if available
  try:
    df = pd.read_csv("indonesia_exchange_rates_timeseries.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df
  except FileNotFoundError:
    # Fallback: fetch fresh data dynamically if CSV is not found
    base_currency = "IDR"
    target_currencies = ["USD", "EUR", "SGD", "JPY", "GBP", "AUD", "CNY", "MYR"]
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    all_records = []
    for currency in target_currencies:
      url = f"https://api.frankfurter.app/{start_date}..{end_date}"
      params = {"from": currency, "to": base_currency}
      response = requests.get(url, params=params)
      if response.status_code == 200:
        data = response.json()
        rates_history = data.get("rates", {})
        for date_str, rate_dict in rates_history.items():
          exchange_rate = rate_dict.get(base_currency)
          if exchange_rate:
            all_records.append({
                "date": date_str,
                "base_currency": currency,
                "target_currency": base_currency,
                "exchange_rate": exchange_rate,
            })
    if all_records:
      df = pd.DataFrame(all_records)
      df["date"] = pd.to_datetime(df["date"])
      return df
    return pd.DataFrame()


# Load data
df = load_exchange_data()

if df.empty:
  st.error(
      "Failed to load or fetch exchange rate data. Please check your network or"
      " CSV file."
  )
else:
  # Sidebar filters
  st.sidebar.header("📊 Filter Options")
  available_currencies = sorted(df["base_currency"].unique())
  selected_currencies = st.sidebar.multiselect(
      "Select Currencies:",
      options=available_currencies,
      default=(
          ["USD", "SGD", "EUR"]
          if "USD" in available_currencies
          else available_currencies[:3]
      ),
  )

  # Filter dataframe based on user selection
  filtered_df = df[df["base_currency"].isin(selected_currencies)]

  # Main Layout - Metrics Overview
  st.subheader("📈 Latest Exchange Rate Summary")
  latest_date = df["date"].max()
  latest_df = df[df["date"] == latest_date]

  cols = st.columns(min(len(selected_currencies), 4))
  for i, currency in enumerate(selected_currencies):
    curr_data = latest_df[latest_df["base_currency"] == currency]
    if not curr_data.empty:
      rate = curr_data["exchange_rate"].values[0]
      col_idx = i % len(cols)
      with cols[col_idx]:
        st.metric(label=f"1 {currency} to IDR", value=f"Rp {rate:,.2f}")

  st.markdown("---")

  # Time-Series Line Chart
  st.subheader("📉 Historical Trend Analysis")
  if not filtered_df.empty:
    fig = px.line(
        filtered_df,
        x="date",
        y="exchange_rate",
        color="base_currency",
        markers=True,
        title="Exchange Rate Trend against Indonesian Rupiah (IDR)",
        labels={
            "date": "Date",
            "exchange_rate": "Exchange Rate (IDR)",
            "base_currency": "Currency",
        },
    )
    fig.update_layout(
        xaxis_title="Date", yaxis_title="Rate in IDR", hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
  else:
    st.warning("Please select at least one currency from the sidebar.")

  # Raw Data View
  with st.expander("🔍 View Raw Dataset Table"):
    st.dataframe(df, use_container_width=True)