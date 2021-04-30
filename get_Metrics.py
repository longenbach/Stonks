import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

class Metrics():
	def __init__(self, header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',} ):
		self.header = header

	def get_overview(self, ticker:str):
		url_overview = 'https://www.zacks.com/stock/quote/' + ticker

		r = urllib.request.Request(url_overview, headers = self.header)
		the_page = urlopen(r).read()
		zack_soup = BeautifulSoup(the_page, 'html.parser')

		zack_section1 = zack_soup.find_all("section",id='stock_activity')[0]
		zack_section2 = zack_soup.find_all("section",id='stock_key_earnings')[0]

		stock_activity = zack_section1.find_all('dd')
		stock_key_earnings = zack_section2.find_all('dd')

		stats = {} 
		stats["Stock"] = [ticker]
		stats["EPS_Qtr_estMA"] = [self.__clean_val(stock_key_earnings[1].get_text())] ## Zacks Most Accurate -> Estimate Quarterly Earnings per Share 
		stats["EPS_Qtr_est"] = [self.__clean_val(stock_key_earnings[2].get_text())] ## Consensus Estimate Quarterly Earnings per Share 
		stats["EPS_Yr_est"] = [self.__clean_val(stock_key_earnings[3].get_text())] ## Consensus Estimate Yearly Earnings per Share (also F1 = 1 year forward looking)
		stats["Exp_Earnings_Date"] = [self.__clean_val(stock_key_earnings[4].get_text(),isDate=True)] ## Expected Earnings Date
		stats["Exp_EPS_Growth_3-5yr"] = [self.__clean_val(stock_key_earnings[6].get_text())] ## Zacks Expected Earnings per Share 3-5 Year Growth Rate
		stats["PE_f1"] = [self.__clean_val(stock_key_earnings[7].get_text())] ## Price / Earnings where Earnings is Consensus F1 Estimate
		stats["PEG_f1"] = [self.__clean_val(stock_key_earnings[8].get_text())] ## PEG F1 = ( Price / EPS-F1 ) / (Exp EPS Growth Rate )
		return stats


	def get_details(self, ticker:str):
		url_details = 'https://www.zacks.com/stock/quote/' + ticker + '/detailed-estimates'

		r = urllib.request.Request(url_details, headers = self.header)
		the_page = urlopen(r).read()
		zack_soup = BeautifulSoup(the_page, 'html.parser')

		## EPS F1 & F2 
		zack_estimates = zack_soup.find_all("div", {"class":"two_col"})[0].find_all("section")
		zack_estimates_col2 = zack_estimates[1].find('tbody').find_all('th')

		stats = {}
		stats["Stock"] = [ticker]
		stats["EPS_Yr_est"] = [self.__clean_val(zack_estimates_col2[1].get_text())] ## Consensus Estimate Yearly Earnings per Share (also F1 = 1 year forward looking)
		stats["EPS_NxtYr_est"] = [self.__clean_val(zack_estimates_col2[2].get_text())] ## Consensus Estimate Yearly Earnings per Share (also F2 = 2 year forward looking)
		stats["EPS_LastYr"] = [self.__clean_val(zack_estimates_col2[3].get_text())] ## TTM Earnings per Share 
		#stats["PE_f1"] = self.__clean_val(zack_estimates_col2[4].get_text()) ## Price / Earnings where Earnings is Consensus F1 Estimate
		
		## Growth Rates
		zack_growth_est = zack_soup.find_all("div", id = 'earnings_growth_estimates')[0].find('tbody')
		zack_growth_est_rows = zack_growth_est.find_all('tr')

		# Stock
		stats["Growth_Qtr_est"] = [self.__clean_val( zack_growth_est_rows[0].find_all('td')[1].get_text())]
		stats["Growth_Next_Qtr_est"] = [self.__clean_val( zack_growth_est_rows[1].find_all('td')[1].get_text())]
		stats["Growth_Yr_est"] = [self.__clean_val( zack_growth_est_rows[2].find_all('td')[1].get_text())]
		stats["Growth_Next_Yr_est"] = [self.__clean_val( zack_growth_est_rows[3].find_all('td')[1].get_text())]
		stats["Growth_Past_5Yr"] = [self.__clean_val( zack_growth_est_rows[4].find_all('td')[1].get_text())]
		stats["Growth_Next_5Yr"] = [self.__clean_val( zack_growth_est_rows[5].find_all('td')[1].get_text())]
		stats["PE_f1"] = [self.__clean_val( zack_growth_est_rows[6].find_all('td')[1].get_text())]
		stats["PEG_f1"] = [self.__clean_val( zack_growth_est_rows[7].find_all('td')[1].get_text())]

		# Industry
		stats["Ind_Growth_Qtr_est"] = [self.__clean_val( zack_growth_est_rows[0].find_all('td')[2].get_text())]
		stats["Ind_Growth_Next_Qtr_est"] = [self.__clean_val( zack_growth_est_rows[1].find_all('td')[2].get_text())]
		stats["Ind_Growth_Yr_est"] = [self.__clean_val( zack_growth_est_rows[2].find_all('td')[2].get_text())]
		stats["Ind_Growth_Next_Yr_est"] = [self.__clean_val( zack_growth_est_rows[3].find_all('td')[2].get_text())]
		stats["Ind_Growth_Past_5Yr"] = [self.__clean_val( zack_growth_est_rows[4].find_all('td')[2].get_text())]
		stats["Ind_Growth_Next_5Yr"] = [self.__clean_val( zack_growth_est_rows[5].find_all('td')[2].get_text())]
		stats["Ind_PE_f1"] = [self.__clean_val( zack_growth_est_rows[6].find_all('td')[2].get_text())]
		stats["Ind_PEG_f1"] = [self.__clean_val( zack_growth_est_rows[7].find_all('td')[2].get_text())]
		# print(stats["PEG_f1"] - self.__clean_val( zack_growth_est_rows[7].find_all('td')[2].get_text()))
		return stats

	def get_price(self, ticker:str):
		url = 'https://www.zacks.com/stock/quote/' + ticker

		r = urllib.request.Request(url, headers = self.header)
		the_page = urlopen(r).read()
		zack_soup = BeautifulSoup(the_page, 'html.parser')

		price = zack_soup.find_all("div",id='get_last_price')[0]

		return self.__clean_val(price.get_text())

	def __clean_val(self, value:str, isDate = False):
		"""
		Takes in string value, cleans it of non float characters ('%','$',',') and returns it as a float.
		"""
		value = value.strip()
		if value in ['NA','N/A','--','-','']:
			return np.nan
		else:
			if isDate:
				return pd.to_datetime(value)
			else:
				return float(value.replace('$',"").replace('%',"").replace(',',''))
		
