from threading import Thread
import schedule
import time


# A function to run twitter crawling module in a thread
def runTwitterCrawler():

    twitter_thread = Thread(target = exec(open("./Twitter module/twitter.py").read()))
    twitter_thread.start()
 


# A function to run hacker forum crawling module in a thread
def runHackerForumCrawler():

    hacker_forum_thread = Thread(target = exec(open("./Hacker forum module/HackerForum Crawler.py").read()))
    hacker_forum_thread.start()



# A function to run github crawling module in a thread
def runGithubCrawler():

    github_thread = Thread(target = exec(open("./GitHub module/Github_Crawler.py").read()))
    github_thread.start()


 
# A function to run the GUI in a thread
def runGUI():

    gui_thread = Thread(target = exec(open("./Web Application/routes.py").read()))
    gui_thread.start()




# Running the crawlers and GUI in a scheduled manner
schedule.every(60).minutes.do(runTwitterCrawler)
schedule.every(30).to(90).minutes.do(runHackerForumCrawler)
schedule.every(60).minutes.do(runGithubCrawler)
runGUI()


# A loop to keep the code running and searching for pending runs
while True:
    schedule.run_pending()
    time.sleep(1)

