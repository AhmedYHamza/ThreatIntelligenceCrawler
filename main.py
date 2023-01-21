from multiprocessing import Process
import HackerForumCrawler
import schedule
import time


# A function to run twitter crawling module in a process
def runTwitterCrawler():
    schedule.every(60).minutes.do(exec,(open("./twitter.py").read()))
    while True:
        schedule.run_pending()
        time.sleep(1)
 


# A function to run hacker forum crawling module in a process
def runHackerForumCrawler():
    schedule.every(30).to(90).minutes.do(HackerForumCrawler.main)
    while True:
        schedule.run_pending()
        time.sleep(1)



# A function to run github crawling module in a process
def runGithubCrawler():
    schedule.every(60).minutes.do(exec,(open("./Github_Crawler.py").read()))
    while True:
        schedule.run_pending()
        time.sleep(1)




# Running the crawlers and GUI in a scheduled manner
Process(target = runTwitterCrawler,args=()).start()
Process(target = runHackerForumCrawler,args=()).start()
Process(target = runGithubCrawler,args=()).start()
exec(open("./routes.py").read())
