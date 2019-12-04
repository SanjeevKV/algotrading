from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import numpy as np
import pandas as pd
import datetime

def main():
	profile = webdriver.FirefoxProfile()
	profile.set_preference("browser.download.folderList", 2)
	profile.set_preference("browser.download.manager.showWhenStarting", False)
	profile.set_preference("browser.download.dir", '/Users/300006804/Desktop/MyWork/algotrading/Downloads/')
	profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv;application/vnd.ms-excel.sheet.binary.macroenabled.12")
	driver = webdriver.Firefox(executable_path='/Library/geckodriver',firefox_profile=profile)
	driver.get('http://subscribers.capitalmarket.com/')
	userName = driver.find_element_by_name("UN")
	password = driver.find_element_by_name("PW")
	submit = driver.find_element_by_xpath("//input[@src='images/submit.gif']")
	userName.send_keys("SANK186")
	password.send_keys("5E5A6Y")
	submit.click()
	driver.get('http://subscribers.capitalmarket.com/Index.asp')
	corporate_scoreboard=driver.find_element_by_xpath("//*[text()='Corporate Scoreboard']")
	corporate_scoreboard.click()
	companies = []
	for i in range(2,35):
		driver.get('http://subscribers.capitalmarket.com/Index.asp')
		corporate_scoreboard=driver.find_element_by_xpath("//*[text()='Corporate Scoreboard']")
		corporate_scoreboard.click()
		industry = driver.find_element_by_xpath('/html/body/table/tbody/tr/td/center/table/tbody/tr/td[2]/table/tbody/tr[3]/td[1]/table[1]/tbody/tr[1]/td[2]/table[3]/tbody/tr['+str(i)+']/td[1]/a')
		print industry.text
		industry.click()
		total_rows = len(driver.find_elements_by_xpath('/html/body/table/tbody/tr/td/center/table/tbody/tr/td[2]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/form/table[2]/tbody/tr'))
		for i in range(1,total_rows+1):
			if(i%19 < 1 or i%19 > 3):
				company = []
				row = driver.find_elements_by_xpath('/html/body/table/tbody/tr/td/center/table/tbody/tr/td[2]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/form/table[2]/tbody/tr['+str(i)+']/td')
				for data in row:
					company.append(data.text)
				companies.append(company)
	heads = open('headers.csv','r')
	columns = heads.readline().split(',')
	heads.close()
	df = pd.DataFrame(data=companies,columns=columns)
	instant = datetime.datetime.now()
	df.to_csv('CorporateScoreboard_'+instant.strftime("%Y_%m_%d")+'.csv')
	driver.close()

if __name__ == '__main__':
	main()