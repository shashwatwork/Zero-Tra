import streamlit as st
import pandas as pd
from PIL import Image
import cufflinks as cf
import time
import yfinance as yf
from nsetools import Nse
from nsepy import get_history
from datetime import date
cf.set_config_file(theme='white', sharing='public', offline=True)


@st.cache
def load_stocks():
    return pd.read_csv('./datasets/stocks.csv', usecols=[0, 1])


@st.cache
def get_ticker_base():

    ticker_df = load_stocks()

    ticker_list = ticker_df['Name'].tolist()
    return ticker_list


@st.cache(allow_output_mutation=True)
def get_ticker(name):

    ticker_df = load_stocks()

    sdict = dict(zip(ticker_df.Name, ticker_df.Symbol))
    ticker_data = sdict.get(str(name))
    ticker = yf.Ticker(ticker_data)
    return ticker, ticker_data


def get_hist_data(ticker, period):
    data = ticker.history(period=period)

    return data


def get_hist_data_period(ticker, start_date, end_date):
    print(ticker)
    data = yf.download(tickers=ticker, start=start_date, end=end_date)

    return data


def get_stock_chart(data, name):
    qf = cf.QuantFig(data, legend='top', name=name,
                     up_color='green', down_color='red')
    # qf.add_bollinger_bands(periods=20, boll_std=2, colors=['cyan','grey'], fill=True,)
    # qf.add_volume(name='Volume',up_color='green', down_color='red')
    chart = qf.iplot(asFigure=True)
    return chart


def get_detailed_chart(data, name):
    qf = cf.QuantFig(data, name=name)
    qf.add_sma([10, 50], width=2, color=['green', 'red'])
    qf.add_rsi(periods=14, color='blue')
    qf.add_bollinger_bands(periods=20, boll_std=2, colors=[
                           'orange', 'grey'], fill=True)
    qf.add_volume()
    qf.add_macd()
    chart = qf.iplot(asFigure=True)


def get_detailed_chart_copy(data, name):
    qf = cf.QuantFig(data, legend="top", up_color='green',
                     down_color='red', name=name)
    qf.add_sma([10, 20], width=2, color=[
               'blue', 'lightblue'], legendgroup=True	)
    qf.add_bollinger_bands(colors=['cyan', 'grey'], fill=True)
    qf.add_volume(name='Volume', up_color='green', down_color='red')
    chart = qf.iplot(asFigure=True)

    return chart


def get_nse_names():
    nse = Nse()

    names = []

    all_stock_codes = nse.get_stock_codes()

    for k, v in all_stock_codes.items():
        names.append(v)
    return names


def get_ticker_nse(name):
    nse = Nse()

    all_stock_codes = nse.get_stock_codes()
    ticker_data = all_stock_codes.get(str(name))
    for key, value in all_stock_codes.items():
        if name == value:
            ticker_data = key
    return ticker_data


@st.cache(allow_output_mutation=True)
def get_top_ten_gainers_loosers(flag):
    nse = Nse()

    if flag == 'Top Gainers':

        data = nse.get_top_gainers()

        data = pd.DataFrame.from_dict(data)

        data = data.iloc[:10, :10]

        return data
    else:
        data = nse.get_top_losers()
        data = pd.DataFrame.from_dict(data)

        data = data.iloc[:10, :10]

        return data


@st.cache()
def get_top_ten_gainers_loosers_copy(flag):

    if flag == 'Top Gainers':

        data = pd.read_csv('./datasets/top_gainers.csv')

        data = data.iloc[:10, :10]

        return data
    else:
        data = pd.read_csv('./datasets/top_loosers.csv')
        data = data.iloc[:10, :10]

        return data


def get_hist_data_nse(symbol, start_date, end_date):
    data = get_history(symbol=symbol, start=start_date, end=end_date)

    return data


def get_hist_data_nse_copy():
    data = pd.read_csv('./datasets/tcs.csv', index_col='Date')

    return data


def main():
    st.sidebar.header('📈Zero-Tra Proto Trading App by @shashwat 👨‍🔧v0.1')
    st.sidebar.subheader('Choose a page to proceed:')
    page = st.sidebar.selectbox(
        "", ["🚀 Get Started", "📈 U.S. Stock Markets", "📈 Indian Stock Markets - NSE", "⚡ Crypto"])
    if page == '🚀 Get Started':
        st.balloons()
        html_temp = """
		<div style="background-color:#ffffff;"><b><p style="color:#5655a3;font-size:60px;"> Zero-Tra</p></b></div>
		<div style="background-color:#ffffff;"><b><p style="color:#5655a3;font-size:20px;"> 🚀 Zero-Tra is an Proto Trading and Analysis Streamlit App.Application provides Stock analysis for three markets- <b>U.S. Stock markets,Indian Stock Markets & Crypto</b>.<br> <br><b>Application still in development Phase. Do Check it out after sometime for really cool stuffs!!!!😉</b></p></b></div>
		<p align="center"> 			
            <b> 👈Choose the page on the left sidebar to proceed </b>
        </p>
		"""
        st.markdown(html_temp, unsafe_allow_html=True)

        # st.subheader("Let's Trade")
        image = Image.open('images/main.jpg')
        st.markdown("""Please feel free to try it out and provide your feedbacks or suggestions for any improvement.🙏""")
        st.image(image, use_column_width=True)
    elif page == '📈 U.S. Stock Markets':
        ticker_list = get_ticker_base()
        stock_chosen = st.multiselect('Choose Stock', list(
            ticker_list), default='Apple Inc. Common Stock')
        st.info('Please select the Stock')
        if len(stock_chosen) == 1:
            st.success('Stock Selected --> {}'.format(stock_chosen[0]))
            ticker, ticker_data = get_ticker(stock_chosen[0])
            if st.checkbox("Show Company Info",):
                st.info(ticker.info['longBusinessSummary'])
                if st.button("Sector"):
                    st.info(ticker.info['sector'])
                if st.button("Total Revenue"):
                    st.info(str(ticker.info['totalRevenue'])+'💲')
                if st.button("Gross Profit"):
                    st.info(str(ticker.info['grossProfits'])+'💲')
                if st.button("Total Debt"):
                    st.info(str(ticker.info['totalDebt'])+'💲')

                if st.checkbox('Get Stock Charts'):
                    st.subheader("Get Stock Chart")
                    period_option = st.selectbox('Select Period', [
                                                 '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max', 'Custom Period'])
                    if period_option == 'Custom Period':
                        start_period = st.date_input(
                            'Select Start Period', value=date(2022, 1, 1))
                        end_period = st.date_input('Select End Period')
                        data = get_hist_data_period(
                            ticker=ticker_data, start_date=start_period, end_date=end_period)
                        chart = get_stock_chart(data=data, name=ticker_data)
                        st.success('Hooray!!!')
                        st.plotly_chart(chart)

                    else:
                        data = get_hist_data(
                            ticker=ticker, period=period_option)
                        chart = get_stock_chart(
                            data, name=str(stock_chosen[0]))
                        st.plotly_chart(chart, use_container_width=True)
                        if st.button('Show Detailed Chart'):
                            chart = get_detailed_chart_copy(
                                data, name=str(stock_chosen[0]))
                            with st.spinner(text='Hold on....'):
                                time.sleep(5)
                                st.success('Hooray!!!')
                                st.plotly_chart(
                                    chart, use_container_width=True)

        else:
            st.error('Please select at least one Stock in the input above')

    elif page == '📈 Indian Stock Markets - NSE':
        st.markdown(""" ##### Hold On Spoiler Alert!!!""")
        st.markdown("""**This section for NSE is static as of now due current version of scrapper does not work with AWS, Google Cloud and web servers.It is not a problem of Python Request. 
		Nse’s robots.txt has blocked all webservers all together. See below NSE [Robots Txt.](https://www.nseindia.com/robots.txt)**""")
        st.markdown("""** However i am trying to find the solution for the same since this common problems among all python scrappers available till now.Please feel free to provide any suggestions🙏**
		""")
        nse_image = Image.open('images/nse.png')
        st.image(nse_image)
        ticker_list = get_nse_names()
        stock_chosen = st.multiselect('Choose Stock', list(
            ticker_list[1:]), default='Tata Consultancy Services Limited', disabled=True)
        st.info('Please select the Stock')
        if len(stock_chosen) == 1:
            ticker_data = get_ticker_nse(name=stock_chosen[0])
            # quote = nse_obj.get_quote(ticker_data)
            if st.checkbox("Show Stock Info"):
                st.info(
                    'Stock Selected --> {}'.format("Tata Consultancy Services Limited"))
                if st.button("Get Average Price"):
                    st.info("3702.93"+"₹")
                if st.button("Get Open Price"):
                    st.info("3646.0"+"₹")
                if st.button("Get Close Price"):
                    st.info("3690.05"+"₹")
                if st.button("Get Buy Price"):
                    st.info("3690.05"+"₹")
            st.subheader('Get Stock Charts')
            if st.checkbox('Get Stock Charts'):
                start_period = st.date_input(
                    'Select Start Period', value=date(2021, 10, 1), disabled=True)
                end_period = st.date_input(
                    'Select End Period', value=date(2022, 1, 30), disabled=True)
                data = get_hist_data_nse_copy()
                chart = get_stock_chart(data=data, name='TCS')
                st.success('Hooray!!!')
                st.plotly_chart(chart)
                if st.button('Show Detailed Chart'):
                    chart = get_detailed_chart_copy(data, name='TCS')
                    with st.spinner(text='Hold on....'):
                        time.sleep(5)
                        st.success('Hooray!!!')
                        st.plotly_chart(chart, use_container_width=True)
            st.subheader('Get Top Gainers and Loosers')
            slider_val = st.selectbox('Select Top Gainers and Loosers', options=[
                                      'Top Gainers', 'Top Loosers'])
            if slider_val == 'Top Gainers':
                data = get_top_ten_gainers_loosers_copy(flag=slider_val)
                st.write(data)
            elif slider_val == 'Top Loosers':
                data = get_top_ten_gainers_loosers_copy(flag=slider_val)
                st.write(data)
        else:
            st.error('Please select at least one Stock in the input above')
    elif page == '⚡ Crypto':
        st.info('Under Development!!!')


if __name__ == '__main__':
    main()
