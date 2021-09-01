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
    
    #---------------------------------#
    # Sidebar + Main panel
    col1.header('Input Options')

    ## Sidebar - Currency price unit
    currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))
    df = load_data(currency_price_unit)
    sorted_coin = sorted( df['coin_symbol'] )
    selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)
    
    ## Sidebar - Cryptocurrency selections
    df_selected_coin = df[ (df['coin_symbol'].isin(selected_coin)) ] # Filtering data

    ## Sidebar - Number of coins to display
    num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
    df_coins = df_selected_coin[:num_coin]

    ## Sidebar - Percent change timeframe
    percent_timeframe = col1.selectbox('Percent change time frame',
                                        ['7d','24h', '1h'])
    percent_dict = {"7d":'percentChange7d',"24h":'percentChange24h',"1h":'percentChange1h'}
    selected_percent_timeframe = percent_dict[percent_timeframe]

    ## Sidebar - Sorting values
    sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

    col2.subheader('Price Data of Selected Cryptocurrency')
    col2.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

    col2.dataframe(df_coins)

    # Download CSV data
    # https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806

    col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

    #---------------------------------#
    # Preparing data for Bar plot of % Price change
    col2.subheader('Table of % Price Change')
    df_change = pd.concat([df_coins.coin_symbol, df_coins.percentChange1h, df_coins.percentChange24h, df_coins.percentChange7d], axis=1)
    df_change = df_change.set_index('coin_symbol')
    df_change['positive_percent_change_1h'] = df_change['percentChange1h'] > 0
    df_change['positive_percent_change_24h'] = df_change['percentChange24h'] > 0
    df_change['positive_percent_change_7d'] = df_change['percentChange7d'] > 0
    col2.dataframe(df_change)

    # Conditional creation of Bar plot (time frame)
    col3.subheader('Bar plot of % Price Change')

    if percent_timeframe == '7d':
        if sort_values == 'Yes':
            df_change = df_change.sort_values(by=['percentChange7d'])
        col3.write('*7 days period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1, bottom = 0)
        df_change['percentChange7d'].plot(kind='barh', color=df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    elif percent_timeframe == '24h':
        if sort_values == 'Yes':
            df_change = df_change.sort_values(by=['percentChange24h'])
        col3.write('*24 hour period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1, bottom = 0)
        df_change['percentChange24h'].plot(kind='barh', color=df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    else:
        if sort_values == 'Yes':
            df_change = df_change.sort_values(by=['percentChange1h'])
        col3.write('*1 hour period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1, bottom = 0)
        df_change['percentChange1h'].plot(kind='barh', color=df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)

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
