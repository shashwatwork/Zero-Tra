from unicodedata import name
import streamlit as st

import pandas as pd
from PIL import Image
from zipfile import ZipFile
import emoji

import cufflinks as cf

import yfinance as yf
from nsetools import Nse
from nsepy import get_history
from datetime import date
cf.set_config_file(theme='white',sharing='public',offline=True)

nse = Nse()


@st.cache
def load_stocks():
    return pd.read_csv('./datasets/stocks.csv',usecols=[0,1])



@st.cache
def get_ticker_base():

	ticker_df = load_stocks()

	ticker_list = ticker_df['Name'].tolist()
	return ticker_list


@st.cache(allow_output_mutation=True)
def get_ticker(name):

	ticker_df = load_stocks()

	sdict = dict(zip(ticker_df.Name,ticker_df.Symbol))
	ticker_data = sdict.get(str(name))
	ticker = yf.Ticker(ticker_data)
	return ticker,ticker_data

def get_hist_data(ticker,period):
	data = ticker.history(period = period)

	return data

def get_hist_data_period(ticker,start_date,end_date):
	print(ticker)
	data = yf.download(tickers = ticker,start  = start_date,end = end_date)

	return data

def get_stock_chart(data,name):
	qf = cf.QuantFig(data,legend='top',name=name,up_color='green', down_color='red')
	# qf.add_bollinger_bands(periods=20, boll_std=2, colors=['cyan','grey'], fill=True,)
	# qf.add_volume(name='Volume',up_color='green', down_color='red')
	chart = qf.iplot(asFigure=True)
	return chart

def get_detailed_chart(data,name):
	qf = cf.QuantFig(data, name=name)
	qf.add_sma([10, 50], width=2, color=['green', 'red'])
	qf.add_rsi(periods=14, color='blue')
	qf.add_bollinger_bands(periods=20, boll_std=2 ,colors=['orange','grey'], fill=True)
	qf.add_volume()
	qf.add_macd()
	chart = qf.iplot(asFigure= True)

def get_detailed_chart_copy(data,name):
	qf = cf.QuantFig(data,legend = "top",up_color='green', down_color='red', name=name)
	qf.add_sma([10,20],width=2,color=['blue','lightblue'],legendgroup=True	)
	qf.add_bollinger_bands(colors = ['cyan','grey'],fill=True)
	qf.add_volume(name = 'Volume',up_color='green', down_color='red')
	chart = qf.iplot(asFigure= True)


	return chart

@st.cache(allow_output_mutation=True)
def get_nse_names():
	names = []

	all_stock_codes = nse.get_stock_codes()
	
	for k,v in all_stock_codes.items():
		names.append(v)
	return names


def get_ticker_nse(name):

	all_stock_codes = nse.get_stock_codes()
	ticker_data = all_stock_codes.get(str(name))
	for key, value in all_stock_codes.items():
		if name == value:
			ticker_data =  key
	return ticker_data


@st.cache(allow_output_mutation=True)
def get_top_ten_gainers_loosers(flag):

	if flag == 'Top Gainers':

		data = nse.get_top_gainers()

		data = pd.DataFrame.from_dict(data)

		data  = data.iloc[:10,:10]

		return data
	else:
		data = nse.get_top_losers()
		data = pd.DataFrame.from_dict(data)

		data  = data.iloc[:10,:10]

		return data

st.cache(allow_output_mutation=True)
def get_hist_data_nse(symbol,start_date,end_date):
	data = get_history(symbol=symbol, start=start_date, end=end_date)

	return data



def main():
	st.sidebar.header('📈Zero-Tra Proto Trading App')
	st.sidebar.subheader('Choose a page to proceed:')
	page = st.sidebar.selectbox("", ["🚀 Get Started","📈 U.S. Stock Markets", "📈 Indian Stock Markets - NSE", "⚡ Crypto"])
	if page == '🚀 Get Started':
		st.balloons()
		html_temp = """
		<div style="background-color:#ffffff;"><b><p style="color:#5655a3;font-size:60px;"> Zero-Tra</p></b></div>
		"""
		st.markdown(html_temp,unsafe_allow_html=True)
		
		st.subheader("Let's Trade")
		image = Image.open('images/main.jpg')
		st.markdown(
            """
            🚀 ### To be done
            """
        )

		st.image(image, caption='Zero-Tra',use_column_width=True)
	elif page == '📈 U.S. Stock Markets':
		ticker_list = get_ticker_base()
		stock_chosen = st.multiselect('Choose Stock', list(ticker_list),default= 'Apple Inc. Common Stock')
		st.info('Please select the Stock')
		if len(stock_chosen) == 1:
			st.success('Stock Selected --> {}'.format(stock_chosen[0]))
			ticker,ticker_data  = get_ticker(stock_chosen[0])
			# Show info
			if st.checkbox("Show Company Info",):
				st.info(ticker.info['longBusinessSummary'])		
				if st.button("Sector"):
					st.info(ticker.info['sector'])
				if st.button("Total Revenue"):
					st.info(ticker.info['totalRevenue'])
				if st.button("Gross Profit"):
					st.info(ticker.info['grossProfits'])
				if st.button("Total Debt"):
					st.info(ticker.info['totalDebt'])

				if st.checkbox('Get Stock Charts'):	
					st.subheader("Get Stock Chart")
					period_option = st.selectbox('Select Period',['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max','Custom Period'])
					st.success('Hooray!!!')
					if period_option == 'Custom Period':
						start_period = st.date_input('Select Start Period')
						end_period = st.date_input('Select End Period')
						data = get_hist_data_period(ticker=ticker_data,start_date=start_period,end_date=end_period)
						chart = get_stock_chart(data = data,name = ticker_data)
						st.plotly_chart(chart)

					else:
						data = get_hist_data(ticker=ticker,period=period_option)
						chart = get_stock_chart(data,name=str(stock_chosen[0]))
						st.plotly_chart(chart,use_container_width=True)
						if st.button('Show Detailed Chart'):
							chart = get_detailed_chart_copy(data,name=str(stock_chosen[0]))
							st.plotly_chart(chart)

		else:
			st.error('Please select at least one Stock in the input above')

		
			
	elif page == '📈 Indian Stock Markets - NSE':

		slider_val = st.select_slider('Slide to Select Top Gainers and Loosers', options=['Top Gainers','Top Loosers'])
		if slider_val == 'Top Gainers':
			data = get_top_ten_gainers_loosers(flag=slider_val)
			st.write(data)
		elif slider_val == 'Top Loosers':
			data = get_top_ten_gainers_loosers(flag=slider_val)
			st.write(data)


		
		ticker_list = get_nse_names()
		stock_chosen = st.multiselect('Choose Stock', list(ticker_list[1:]),default= 'TATA CONSUMER PRODUCTS LIMITED')
		st.info('Please select the Stock')
		if len(stock_chosen) == 1:
			ticker_data  = get_ticker_nse(name = stock_chosen[0])
			quote = nse.get_quote(ticker_data)
			st.success('Stock Selected --> {}'.format(quote['companyName']))

			if st.button("Get Average Price"):
				st.info(quote['averagePrice'])
			if st.button("Get Open Price"):
				st.info(quote['open'])
			if st.button("Get Close Price"):
				st.info(quote['closePrice'])
			if st.button("Get Buy Price"):
				st.info(quote['buyPrice1'])
			if st.button("Get Sell Price"):
				st.info(quote['sellPrice1'])

			if st.checkbox('Get Stock Charts'):	
				st.subheader("Get Stock Chart")
				start_period = st.date_input('Select Start Period')
				end_period = st.date_input('Select End Period')
				data = get_hist_data_nse(symbol=ticker_data,start_date=start_period,end_date=end_period)
				chart = get_stock_chart(data = data,name = ticker_data)
				st.plotly_chart(chart)

				# data = get_hist_data(ticker=ticker,period=period_option)
				# chart = get_stock_chart(data,name=str(stock_chosen[0]))
				# st.plotly_chart(chart,use_container_width=True)
				# if st.button('Show Detailed Chart'):
				# 	chart = get_detailed_chart_copy(data,name=str(stock_chosen[0]))
				# 	st.plotly_chart(chart)
		else:
			st.error('Please select at least one Stock in the input above')


		# # Counts Plots
		# if st.checkbox("Plot of Value Counts"):
		# 	st.text("Value Counts By Target/Class")

		# 	all_columns_names = df.columns.tolist()
		# 	primary_col = st.selectbox('Select Primary Column To Group By',all_columns_names)
		# 	selected_column_names = st.multiselect('Select Columns',all_columns_names)
		# 	if st.button("Plot"):
		# 		st.text("Generating Plot for: {} and {}".format(primary_col,selected_column_names))
		# 		if selected_column_names:
		# 			vc_plot = df.groupby(primary_col)[selected_column_names].count()		
		# 		else:
		# 			vc_plot = df.iloc[:,-1].value_counts()
		# 		st.write(vc_plot.plot(kind='bar'))
		# 		st.pyplot()

		# # Pie Plot
		# if st.checkbox("Pie Plot"):
		# 	all_columns_names = df.columns.tolist()
		# 	# st.info("Please Choose Target Column")
		# 	# int_column =  st.selectbox('Select Int Columns For Pie Plot',all_columns_names)
		# 	if st.button("Generate Pie Plot"):
		# 		# cust_values = df[int_column].value_counts()
		# 		# st.write(cust_values.plot.pie(autopct="%1.1f%%"))
		# 		st.write(df.iloc[:,-1].value_counts().plot.pie(autopct="%1.1f%%"))
		# 		st.pyplot()

		# # Barh Plot
		# if st.checkbox("BarH Plot"):
		# 	all_columns_names = df.columns.tolist()
		# 	st.info("Please Choose the X and Y Column")
		# 	x_column =  st.selectbox('Select X Columns For Barh Plot',all_columns_names)
		# 	y_column =  st.selectbox('Select Y Columns For Barh Plot',all_columns_names)
		# 	barh_plot = df.plot.barh(x=x_column,y=y_column,figsize=(10,10))
		# 	if st.button("Generate Barh Plot"):
		# 		st.write(barh_plot)
		# 		st.pyplot()

		# # Custom Plots
		# st.subheader("Customizable Plots")
		# all_columns_names = df.columns.tolist()
		# type_of_plot = st.selectbox("Select the Type of Plot",["area","bar","line","hist","box","kde"])
		# selected_column_names = st.multiselect('Select Columns To Plot',all_columns_names)
		# # plot_fig_height = st.number_input("Choose Fig Size For Height",10,50)
		# # plot_fig_width = st.number_input("Choose Fig Size For Width",10,50)
		# # plot_fig_size =(plot_fig_height,plot_fig_width)
		# cust_target = df.iloc[:,-1].name

		# if st.button("Generate Plot"):
		# 	st.success("Generating A Customizable Plot of: {} for :: {}".format(type_of_plot,selected_column_names))
		# 	# Plot By Streamlit
		# 	if type_of_plot == 'area':
		# 		cust_data = df[selected_column_names]
		# 		st.area_chart(cust_data)
		# 	elif type_of_plot == 'bar':
		# 		cust_data = df[selected_column_names]
		# 		st.bar_chart(cust_data)
		# 	elif type_of_plot == 'line':
		# 		cust_data = df[selected_column_names]
		# 		st.line_chart(cust_data)
		# 	elif type_of_plot == 'hist':
		# 		custom_plot = df[selected_column_names].plot(kind=type_of_plot,bins=2)
		# 		st.write(custom_plot)
		# 		st.pyplot()
		# 	elif type_of_plot == 'box':
		# 		custom_plot = df[selected_column_names].plot(kind=type_of_plot)
		# 		st.write(custom_plot)
		# 		st.pyplot()
		# 	elif type_of_plot == 'kde':
		# 		custom_plot = df[selected_column_names].plot(kind=type_of_plot)
		# 		st.write(custom_plot)
		# 		st.pyplot()
		# 	else:
		# 		cust_plot = df[selected_column_names].plot(kind=type_of_plot)
		# 		st.write(cust_plot)
		# 		st.pyplot()



		# st.subheader("Our Features and Target")

		# if st.checkbox("Show Features"):
		# 	all_features = df.iloc[:,0:-1]
		# 	st.text('Features Names:: {}'.format(all_features.columns[0:-1]))
		# 	st.dataframe(all_features.head(10))

		# if st.checkbox("Show Target"):
		# 	all_target = df.iloc[:,-1]
		# 	st.text('Target/Class Name:: {}'.format(all_target.name))
		# 	st.dataframe(all_target.head(10))


		# # Make Downloadable file as zip,since markdown strips to html
		# st.markdown("""[google.com](iris.zip)""")

		# st.markdown("""[google.com](./iris.zip)""")

		# # def make_zip(data):
		# # 	output_filename = '{}_archived'.format(data)
		# # 	return shutil.make_archive(output_filename,"zip",os.path.join("downloadfiles"))

		# def makezipfile(data):
		# 	output_filename = '{}_zipped.zip'.format(data)
		# 	with ZipFile(output_filename,"w") as z:
		# 		z.write(data)
		# 	return output_filename	
					

		# if st.button("Download File"):
		# 	DOWNLOAD_TPL = f'[{filename}]({makezipfile(filename)})'
		# 	# st.text(DOWNLOAD_TPL)
		# 	st.text(DOWNLOAD_TPL)
		# 	st.markdown(DOWNLOAD_TPL)




if __name__ == '__main__':
	main()