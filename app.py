import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# NIFTY 50 components (as of 2024)
nifty50_components = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "KOTAKBANK.NS", "ITC.NS", "SBIN.NS", "LT.NS",
    "AXISBANK.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "HDFC.NS", "BAJFINANCE.NS",
    "HCLTECH.NS", "WIPRO.NS", "MARUTI.NS", "HDFCLIFE.NS", "ADANIGREEN.NS",
    "TECHM.NS", "ULTRACEMCO.NS", "SUNPHARMA.NS", "NTPC.NS", "TITAN.NS",
    "NESTLEIND.NS", "POWERGRID.NS", "JSWSTEEL.NS", "GRASIM.NS", "TATAMOTORS.NS",
    "TATASTEEL.NS", "INDUSINDBK.NS", "HEROMOTOCO.NS", "ONGC.NS", "COALINDIA.NS",
    "BPCL.NS", "UPL.NS", "DRREDDY.NS", "DIVISLAB.NS", "APOLLOHOSP.NS",
    "BRITANNIA.NS", "CIPLA.NS", "M&M.NS", "BAJAJFINSV.NS", "ADANIPORTS.NS",
    "EICHERMOT.NS", "SBILIFE.NS", "TATACONSUM.NS", "HINDALCO.NS", "SHREECEM.NS"
]

# Combine indices into a dictionary
indices = {
    "NIFTY 50": nifty50_components,
}


# Function to fetch stock data
def fetch_stock_data(ticker, period="5y"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    return df


# Function to fetch fundamental details
def get_stock_fundamentals(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    fundamentals = {
        "Company Name": info.get('longName', 'N/A'),
        "Market Cap": info.get('marketCap', 'N/A'),
        "PE Ratio": info.get('trailingPE', 'N/A'),
        "EPS": info.get('trailingEps', 'N/A'),
        "Dividend Yield": info.get('dividendYield', 'N/A'),
        "Beta": info.get('beta', 'N/A'),
        "52 Week High": info.get('fiftyTwoWeekHigh', 'N/A'),
        "52 Week Low": info.get('fiftyTwoWeekLow', 'N/A'),
        "Sector": info.get('sector', 'N/A'),
        "Industry": info.get('industry', 'N/A'),
        "Institutional Holdings": info.get('heldPercentInstitutions', 'N/A')
    }
    return fundamentals


# Create a Streamlit app
st.markdown("""
    <style>
    .main {
        background-image: url("https://images.unsplash.com/photo-1568600918-2e4b7d7c28d1"); 
        background-size: cover;
        color: #fff;
    }
    .title {
        font-size: 2.5em;
        font-weight: bold;
        color: #f8f9fa;
    }
    .stTable {
        color: #f8f9fa;
    }
    .stSelectbox {
        background-color: #343a40;
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Stock Viewer")

# Select the index
selected_index = st.selectbox("Select an Index", list(indices.keys()), key="index_selector")

# Select the stock
selected_stock = st.selectbox(f"Select a Stock from {selected_index}", indices[selected_index], key="stock")

# Fetch data for the selected stock
df = fetch_stock_data(selected_stock)

# Display stock data
st.write(f"Displaying data for {selected_stock}")
st.write(df)

# Create a chart type selection
chart_type = st.selectbox("Select Chart Type", ["Line Chart", "Candlestick Chart", "Bar Chart", "Area Chart"])


# Create the selected charts
def create_chart(df, chart_title):
    if chart_type == "Line Chart":
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], mode='lines')])
    elif chart_type == "Candlestick Chart":
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                                             open=df['Open'],
                                             high=df['High'],
                                             low=df['Low'],
                                             close=df['Close'])])
    elif chart_type == "Bar Chart":
        fig = go.Figure(data=[go.Bar(x=df.index, y=df['Close'])])
    elif chart_type == "Area Chart":
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], fill='tozeroy')])

    fig.update_layout(title=chart_title,
                      yaxis_title='Price',
                      xaxis_title='Date')
    return fig


# Display chart
st.subheader(f"Price Chart for {selected_stock}")
st.plotly_chart(create_chart(df, f'{selected_stock} Stock Prices'))

# Display fundamental details
fundamentals = get_stock_fundamentals(selected_stock)

st.subheader(f"Fundamental Details for {selected_stock}")
fundamentals_df = pd.DataFrame([fundamentals])
st.table(fundamentals_df)


# Graphical representation of stock holding pattern (Institutional Holdings)
def plot_holdings_pattern(fundamentals):
    institutional_holdings = fundamentals['Institutional Holdings']
    if institutional_holdings != 'N/A' and institutional_holdings is not None:
        institutional_holdings = float(institutional_holdings)
    else:
        institutional_holdings = 0  # Default to 0 if unavailable

    labels = ['Institutional Holdings', 'Retail/Other Holdings']
    values = [institutional_holdings, 1 - institutional_holdings]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(title_text="Stock Holding Pattern")
    return fig


st.subheader("Stock Holding Pattern")
st.plotly_chart(plot_holdings_pattern(fundamentals))

# Pros and Cons
st.subheader(f"Pros and Cons for {selected_stock}")
pros_cons = {
    "Pros": [
        "High Institutional Holdings" if fundamentals['Institutional Holdings'] != 'N/A' and float(fundamentals['Institutional Holdings']) > 0.5 else "Strong market position",
        "Stable Dividend Yield" if fundamentals['Dividend Yield'] != 'N/A' and fundamentals['Dividend Yield'] else "Positive earnings growth"
    ],
    "Cons": [
        "High PE Ratio" if fundamentals['PE Ratio'] != 'N/A' and float(fundamentals['PE Ratio']) > 30 else "Low Dividend Yield",
        "Volatile stock" if fundamentals['Beta'] != 'N/A' and float(fundamentals['Beta']) > 1 else "Sector-specific risks"
    ]
}

pros_cons_df = pd.DataFrame([(key, item) for key, items in pros_cons.items() for item in items],
                            columns=['Type', 'Description'])
st.table(pros_cons_df)
