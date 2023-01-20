from multiprocessing import Process
import schedule
import time


# A function to run twitter crawling module in a process
def runTwitterCrawler():
    schedule.every(10).seconds.do(exec(open("./Twitter module/twitter.py").read()))
    while True:
        schedule.run_pending()
        time.sleep(1)
 


# A function to run hacker forum crawling module in a process
def runHackerForumCrawler():
    schedule.every(5).to(15).seconds.do(exec(open("./Hacker forum module/HackerForum Crawler.py").read()))
    while True:
        schedule.run_pending()
        time.sleep(1)



# A function to run github crawling module in a process
def runGithubCrawler():
    schedule.every(10).seconds.do(exec(open("./GitHub module/Github_Crawler.py").read()))
    while True:
        schedule.run_pending()
        time.sleep(1)


 
# A function to run the GUI in a process
def runGUI():
    exec(open("./Web Application/routes.py").read())




# Running the crawlers and GUI in a scheduled manner
Process(target = runTwitterCrawler,args=()).start()
Process(target = runHackerForumCrawler,args=()).start()
Process(target = runGithubCrawler,args=()).start()
exec(open("./routes.py").read())
