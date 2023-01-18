import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from random import randint
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import pandas as pd



def smartScroll(page_height,driver,start=0):

    tmp=start

    # Until the desired scrolling is acheived
    # Randomly scroll intermittent scrolling
    while(tmp<page_height):

        tmp+=randint(20,60)

        # If the new height exceeds the desired height
        # return it to the desired height
        if(tmp>page_height):
            tmp=page_height

        driver.execute_script("window.scrollTo(0, "+str(tmp)+")") 
        
        time.sleep(randint(1,5)/10)


def readScroll(driver):

    start=0
    tmp=0

    page_height=driver.execute_script("return document.body.scrollHeight")

    time.sleep(randint(3,7))

    # Until the desired scrolling is acheived
    # Randomly scroll intermittent scrolling with pauses for reading
    while(tmp<page_height):

        start=tmp
        tmp+=randint(200,400)

        # If the new height exceeds the desired height
        # return it to the desired height
        if(tmp>page_height):
            tmp=page_height

        smartScroll(tmp,driver,start)

        time.sleep(randint(2,7))


def input(xpath,text,driver):

    # Find the textbox
    textbox=driver.find_element('xpath',xpath)

    # Input letter by letter with random pauses
    for i in text:
        textbox.send_keys(i)
        time.sleep(randint(0,9)/10)


def click(xpath,driver):
    
    # Find button
    item=driver.find_element('xpath',xpath)

    # Click on the button
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


def findLinks(collection,links,driver):

    flg=0
    tmp_set=[] 

    # Until there are no more search result pages
    while(flg==0):

        time.sleep(randint(1,3))

        # Find all links in page
        elems = driver.find_elements('xpath',"//a[@href]")

        # For each link in page
        # check if it is a thread of the category leak
        # and put them in the links to be crawled
        for elem in elems:

            tmp=elem.get_attribute("href")

            if("ly/Thread-Leak" in tmp):
                tmp_set.append(tmp)
                links.append(tmp)

        elems=[]

        # Smart scroll to the end of the page
        smartScroll(driver.execute_script("return document.body.scrollHeight"),driver)

    
        tmp_set=set(tmp_set)

        # For every link found
        for link in tmp_set:

            # Skip the link if it is already in the database
            if(collection.find_one({'url':link})):
                continue

            # If the links is not in the database 
            # go to the link and read scroll it then crawl it 
            # and go back to the search results page
            else:

                try:

                    # Go to the link
                    driver.get(link)

                    # Scroll it as if it is being read
                    readScroll(driver)

                    # Scrape the data from the page
                    crawl(link,driver)

                    # Go back to the results page
                    driver.back()

                except:

                    # If the page wasn't found go back to the search results
                    driver.back()

    
        tmp_set=[]

        # if there is no more pages 
        if not checkNameExists('pagination_next',driver):
            flg=1

        # else click on the next button
        else:
            item=driver.find_element(By.CLASS_NAME,'pagination_next')
            driver.execute_script("arguments[0].click();", item)

    links=set(links)


def crawl(link,driver):
    # Data extraction and parsing code
    title=driver.find_element(By.XPATH, '//*[@id="content"]/table/tbody/tr[1]/td').text
    user=driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[6]/div[1]/div[1]/div[2]/strong/span/a/span').text
    postDate=driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[6]/div[1]/div[2]/div[1]/span[2]/span').text
    postDate=pd.to_datetime(postDate)
    stars=driver.find_element(By.CLASS_NAME, 'postbit_usertitle').text#/html/body/div[3]/div[2]/div[6]/div[1]/div[1]/div[2]/span[1]/span
    print(title,user,stars,postDate)

    #using beautiful soap to get the things that do not have consistent html code id,name,ref,...
    pageSource = driver.page_source
    bsObj = BeautifulSoup(pageSource)
    mydivs = bsObj.find_all("div", {"class": "author_statistics smalltext"})
    authorStuff=str(mydivs[0].text).replace("\n"," ").split()
    print(authorStuff)
    numberOfPosts=int(authorStuff[authorStuff.index('Posts:')+1])
    numberOfThreads=int(authorStuff[authorStuff.index('Threads:')+1])
    reputation=int(authorStuff[authorStuff.index('Reputation:')+1])
    currency=int(authorStuff[authorStuff.index('Currency:')+1])
    print(numberOfPosts,numberOfThreads,reputation,currency)

    content=bsObj.find_all("div", {"class": "post_body scaleimages"})
    for i in range(len(content)):
        content[i]=content[i].text
    #writting to database
    item_object = {
        'title':title,
        'url':link,
        'username':user,
        'created_at':postDate,
        "additional_info":{
            "reputation":reputation
            },
        "more_details":{
            "body_text": content[0],
            "currency":currency,
            "stars":stars,
            "posts_count":numberOfPosts,
            "threads_count":numberOfThreads
            }    
        }
    collection.insert_one(item_object)



#Defining the cluster and the collection for saving the data to the database
cluster=MongoClient('AddYourClusterLink')
db=cluster["AddClusterName"]
collection=db["AddCollectionName"]

# Credentials for hacker forum
username = 'AddYourAccount' 
password = 'AddYourPassword' 

driver = uc.Chrome(use_subprocess=True)


try:
    
    url='https://sinister.ly'
    driver.get(url)
    
except:
    
    Print("Page not reachable")

    
# login
login(username,password,driver)

# Execute search for a keyword
search("canada",driver)

# Find the links
links=[]
findLinks(collection,links,driver)

time.sleep(10)
