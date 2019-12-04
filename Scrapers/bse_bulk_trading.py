from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def main():
	profile = webdriver.FirefoxProfile()
	profile.set_preference("browser.download.folderList", 2)
	profile.set_preference("browser.download.manager.showWhenStarting", False)
	profile.set_preference("browser.download.dir", '/Users/300006804/Desktop/MyWork/algotrading/Downloads/')
	profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv;application/vnd.ms-excel.sheet.binary.macroenabled.12")
	driver = webdriver.Firefox(executable_path='/Library/geckodriver',firefox_profile=profile)
	driver.get('http://www.bseindia.com/markets/equity/EQReports/BulknBlockDeals.aspx')
	from_text = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtDate")
	to_text = driver.find_element_by_id("ctl00_ContentPlaceHolder1_txtToDate")
	all_market_tick = driver.find_element_by_id("ctl00_ContentPlaceHolder1_chkAllMarket")
	from_text.send_keys("23/01/2018")
	to_text.send_keys("25/01/2018")
	all_market_tick.click()
	submit_button = driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSubmit")
	submit_button.click()
	print driver.page_source
	download_button = driver.find_element_by_id("ctl00_ContentPlaceHolder1_btndownload1")
	download_button.click()
	driver.close()	

if __name__ == '__main__':
	main()