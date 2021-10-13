import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
import time
import os
import plotly.express as px
import plotly.graph_objects as go

#---------------------------------#
st.set_page_config(layout="wide") #st.beta_set_page_config(layout="wide")
#---------------------------------#

image = Image.open('logo.jpg')

#---------------------------------#
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.beta_columns((2,1))

pages = ['Home','Visualization of Cryptocurrency']
page = st.sidebar.selectbox('choose a page', pages)

# Web scraping of CoinMarketCap data
@st.cache
def load_data(currency_price_unit):
    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    for i in listings:
      coins[str(i['id'])] = i['slug']

    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []

    for i in listings:
      coin_name.append(i['slug'])
      coin_symbol.append(i['symbol'])
      price.append(i['quote'][currency_price_unit]['price'])
      percent_change_1h.append(i['quote'][currency_price_unit]['percentChange1h']) # percent_change_1h
      percent_change_24h.append(i['quote'][currency_price_unit]['percentChange24h']) #percent_change_24h
      percent_change_7d.append(i['quote'][currency_price_unit]['percentChange7d']) # percent_change_7d
      market_cap.append(i['quote'][currency_price_unit]['marketCap']) # market_cap
      volume_24h.append(i['quote'][currency_price_unit]['volume24h']) # volume_24h

    df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'marketCap', 'percentChange1h', 'percentChange24h', 'percentChange7d', 'price', 'volume24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percentChange1h'] = percent_change_1h
    df['percentChange24h'] = percent_change_24h
    df['percentChange7d'] = percent_change_7d
    df['marketCap'] = market_cap
    df['volume24h'] = volume_24h
    return df

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

@st.cache
def load(name):
    return pd.read_csv('data/coin_'+name+'.csv', parse_dates=['Date'])

files = os.listdir('data')
files = [i.split('.')[0].split('_')[1] for i in files]
col_list = ['Low','Close','High','Open','Marketcap']

def home():
    st.image(image, width = 500)
    st.title('Crypto Price App')
    st.markdown("""
    This app shows analysis and visualization of cryptocurrency!
    """)
    #---------------------------------#
    # About
    expander_bar = st.beta_expander("About")
    expander_bar.markdown("""
    * **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time, plotly, os
    * **Data source:** [CoinMarketCap](http://coinmarketcap.com).
    """)
    
    expander_bar = st.beta_expander("What is Cryptocurrency?",expanded=True)
    expander_bar.markdown("""
    - Cryptocurrency takes the form of digital assets

    - Buyers use money to buy assets (or a part of an asset)

    - Buyers than exchange the assets online for goods or services

    ### Think of an asset like a chip at a casino.
    When you get to a casino (or Chuck E. Cheese, if that's more your vibe), you exchange your money for chips. You can then use your chips to play the games.

    In this case, the casino chips are the assets, and the games are the good you are purchasing.
    """)

    expander_bar = st.beta_expander("How Does It Work?",expanded=True)
    expander_bar.markdown("""
    - ### Transactions are verified using Blockchain

- Blockchain transactions are decentralized, meaning they're spread across many computers to manage and record transactions 

- Because Blockchain transactions rely on many computers, they are considered more secure than centralized currencies 


    """)


def plots_page():
    st.title(pages[1])
    file = st.sidebar.selectbox('select a cryptocurrency', files)
    dfc = load(file)
    grid = st.beta_columns([3,1])
    plots = {
        'See Line Plot': px.line(dfc,x='Date',y='Close'),
        'See Candlestick Plot': go.Figure(data=[go.Candlestick(x=dfc['Date'],open=dfc['Open'],high=dfc['High'],low=dfc['Low'],close=dfc['Close'])]),
        'See Histogram PLot': px.histogram(dfc,x='Date',y='Close')
        }
    plot = grid[1].radio('Choose a type of plot', list(plots.keys()))
    grid[0].plotly_chart(plots[plot])

if page == pages[0]:
    home()

if page == pages[1]:
    plots_page()
