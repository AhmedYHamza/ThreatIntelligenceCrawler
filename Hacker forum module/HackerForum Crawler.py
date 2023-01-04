import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from python3_anticaptcha import ImageToTextTask
from selenium.common.exceptions import NoSuchElementException
from random import randint
import time
import pymongo
from pymongo import MongoClient

def smartScroll(page_height,driver,start=0):
    tmp=start
    while(tmp<page_height):
        tmp+=randint(20,60) 
        if(tmp>page_height):
            tmp=page_height
        driver.execute_script("window.scrollTo(0, "+str(tmp)+")") 
        time.sleep(randint(1,5)/10)

def readScroll(driver):
    start=0
    tmp=0
    page_height=driver.execute_script("return document.body.scrollHeight")
    time.sleep(randint(3,7)) 
    while(tmp<page_height):
        start=tmp
        tmp+=randint(200,400)   
        if(tmp>page_height):
            tmp=page_height
        smartScroll(tmp,driver,start)
        time.sleep(randint(2,7))    

def input(xpath,text,driver):
    textbox=driver.find_element('xpath',xpath)
    for i in text:
        textbox.send_keys(i)
        time.sleep(randint(0,9)/10)

def click(xpath,driver):
    item=driver.find_element('xpath',xpath)
    driver.execute_script("arguments[0].click();", item)

def login(username,password,driver):
    # Click the login button
    click('/html/body/div[1]/div[1]/a[1]',driver)

    time.sleep(randint(1,3))

    # Input credentials and click login
    input('//*[@id="quick_login_username"]',username,driver)
    input('//*[@id="quick_login_password"]',password,driver)
    click('/html/body/div[5]/div/form/input[7]',driver)

    time.sleep(randint(2,4)) 

def search(keyword, driver):
    # Click the search button
    click('/html/body/div[2]/ul/li[4]/a',driver)

    time.sleep(randint(3,5))

    # Input the search keyword and scroll to the bottom of the page and click the search button
    input('/html/body/div[3]/div[2]/form/table/tbody/tr[3]/td[1]/table/tbody/tr[1]/td/input',keyword,driver)
    smartScroll(driver.execute_script("return document.body.scrollHeight"),driver)
    click('/html/body/div[3]/div[2]/form/div/input',driver)

    time.sleep(randint(3,5))

def checkNameExists(name,driver):
    try:
        driver.find_element(By.CLASS_NAME,name)
    except NoSuchElementException:
        return False
    return True

def findLinks(links,driver):
    flg=0
    tmp_set=[] 
    while(flg==0):
        elems = driver.find_elements('xpath',"//a[@href]")
        for elem in elems:
            tmp=elem.get_attribute("href")
            if("ly/Thread-Leak" in tmp):
                tmp_set.append(tmp)
                links.append(tmp)
        smartScroll(driver.execute_script("return document.body.scrollHeight"),driver)
        tmp_set=set(tmp_set)
        for link in tmp_set:
            driver.get(link)
            readScroll(driver)
            crawl(link,driver)
            driver.back()
        tmp_set=[]
        if not checkNameExists('pagination_next',driver):
            flg=1
        else:
            item=driver.find_element(By.CLASS_NAME,'pagination_next')
            driver.execute_script("arguments[0].click();", item)
    links=set(links)

def crawl(link,driver):
    # Data extraction and parsing code
    title=driver.find_element(By.XPATH, '//*[@id="content"]/table/tbody/tr[1]/td').text
    user=driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[6]/div[1]/div[1]/div[2]/strong/span/a/span').text
    postDate=driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[6]/div[1]/div[2]/div[1]/span[2]/span').text
    stars=driver.find_element(By.CLASS_NAME, 'postbit_usertitle').text#/html/body/div[3]/div[2]/div[6]/div[1]/div[1]/div[2]/span[1]/span
    
    #numberOfPosts=int(driver.find_element(By.CLASS_NAME, "//div[@class='author_statstics smalltext']//div[2]//span[1]").text)#"//div[@class='author_statstics smalltext']//div[2]//span[1]
    #numberOfThreads=int(driver.find_element(By.XPATH, "//div[@class='author_statistics smalltext']//div[2]//span[2]").text)
    #reputation=int(float(driver.find_element(By.CLASS_NAME, "reputation_positive").text))
    currency=driver.find_element(By.XPATH, "//div[@class='smalltext']//span[@class='float_right']").text
    #print(title,user,numberOfPosts,numberOfThreads,reputation,currency,stars,postDate)
    #content=driver.find_element(By.CLASS_NAME, 'post_body scaleimages').text # 'post_body scaleimages'#/html/body/div[3]/div[2]/div[6]/div[1]/div[2]/div[2])
    
    
    if(collection.find_one({'title':title,'user':user,'postDate':postDate})): #if this record already exists in the database
        return 0
    else: #it is not in the database yet
        item_object = {'title':title,
            'user':user,
            #'numberOfPosts':numberOfPosts,
            #'numberOfThreads':numberOfThreads,
            #'reputation':reputation,
            #'currency':currency,
            'stars':stars,
            'postDate':postDate,
            'URL':link,
            "Crawler_Type":2,
            #'content':content.replace("<br>", "\n")
            }
        collection.insert_one(item_object)
    
    

    
    return 0

#Defining the cluster and the collection for saving the data to the database
cluster=MongoClient('AddYourClusterLink')
db=cluster["AddClusterName"]
collection=db["AddCollectionName"]

# Credentials for hacker forum
username = 'AddYourAccount' 
password = 'AddYourPassword' 

driver = uc.Chrome(use_subprocess=True)

url='https://sinister.ly'
driver.get(url)

# login
login(username,password,driver)

# Click the search button
search("egypt",driver)

# Find the links
links=[]
findLinks(links,driver)

time.sleep(10)