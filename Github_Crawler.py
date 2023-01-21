import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os

#Defining the cluster and the collection for saving the data to the database
cluster          = MongoClient(os.environ['MONGO_CLIENT'])
db               = cluster[os.environ['MONGO_DB_NAME']]
collection       = db[os.environ['MONGO_GITHUB_COLLECTION']]
domainscollection= db[os.environ['MONGO_DOMAINS_COLLECTION']]

# Constants
sensitive_domains = domainscollection.find()
pass_keywords = ['password', 'credential']


options = Options()
options.headless = True
driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
driver.implicitly_wait(5)

actions = ActionChains(driver)

# Step1: LOGIN TO GITHUB
driver.get('https://github.com/login')

username = os.environ['GITHUB_USERNAME']
password = os.environ['GITHUB_PASSWORD']

driver.find_element("id", 'login_field').send_keys(username)
driver.find_element("id", 'password').send_keys(password)
driver.find_element("name", 'commit').click()

try:
    # Check if we logged successfully
    logout_button = driver.find_element("link text", "Create repository")
    print('Successfully logged in')
    while True:
        # Step2: Search by every domain and Collect data
        for domain in sensitive_domains:
            for keyword in pass_keywords:
                try:
                    data = []
                    driver.find_element(By.XPATH, "//a[@class='Header-link']").click()

                    # Locate the search box, input the query, then press enter
                    search_query = domain['Domain'] + ' ' + keyword
                    driver.find_element("name", 'q').send_keys(search_query)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(5)

                    # Get total number of search results
                    results_count = int(driver.find_element(By.XPATH, "//a[text()='Code'][@class='menu-item']/span[@data-search-type='Code']").text)
                    print("results count:", results_count)

                    # Download results if any
                    if results_count > 0:
                        # Click on the code tab
                        driver.find_element(By.XPATH, "//a[text()='Code'][@class='menu-item']").click()
                        time.sleep(5)

                        # Start crawling the items in every page.
                        while True:
                            results_html = driver.find_elements(By.CLASS_NAME, 'code-list-item')

                            for item in results_html:
                                file = item.find_element(By.XPATH, ".//div[@class='f4 text-normal']/a")
                                html_page = requests.get(url=file.get_attribute('href')).text

                                if '@'+domain['Domain'] in html_page:
                                    Repository = item.find_element(By.XPATH, ".//a[@class='Link--secondary']")

                                    UpdatedDate1 = item.find_element(By.XPATH, ".//relative-time").get_attribute('title').split(' ')
                                    UpdatedDate1.pop()
                                    if len(UpdatedDate1[1]) < 3: # if the day is 1 digit, we add a '0' in the beginning
                                        UpdatedDate1[1] = '0' + UpdatedDate1[1]
                                    UpdatedDate = ' '.join(map(str, UpdatedDate1))

                                    if(collection.find_one({'RepoLink': Repository.get_attribute('href'),'FileName': file.text.split('/').pop(), 'domain': domain['Domain']})):
                                            continue
                                    else:
                                        item_object = {
                                            'RepoFullName': Repository.text,
                                            'RepoLink': Repository.get_attribute('href'),
                                            'FilePath': file.get_attribute('href'),
                                            'FileName': file.text.split('/').pop(),
                                            'UpdatedDate': datetime.strptime(UpdatedDate, '%b %d, %Y, %I:%M %p'),
                                            'domain': domain['Domain']
                                         }
                                        collection.insert_one(item_object)
                                        data.append(item_object)

                            # Go to the next page if any
                            next_btn_existed = len(driver.find_elements(By.CLASS_NAME, "next_page")) > 0
                            if next_btn_existed:
                                next_btn = driver.find_element(By.CLASS_NAME, "next_page")
                                if not (next_btn.get_attribute('class').__contains__('disabled')):
                                    next_btn.click()
                                    time.sleep(10)
                                else:
                                    break
                            else:
                                break

                except Exception as e:
                    print(e)
                    time.sleep(5 * 60)

except Exception as e:
    print('Incorrect login/password')
