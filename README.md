# Threat Intelligence Crawler
A crawler that gathers data needed by threat intelligence specialists.

## Overview
Our project is consists of 3 main parts which are 
1. Implement a threat intelligence crawler that crawls 3 different categories of platforms which are social media, hacker forums and code hosting and collaboration platforms, to collect digital threats about Egypt as a country.  
2. Implement a searchable database.
3. Develop a user-friendly Admin panel which threat intelligence specialists can used to investigate the founded threats.

## Project Diagram and Methodology
![image](https://user-images.githubusercontent.com/36446976/210483219-96b29201-d03f-4c33-b81c-df379127d951.png)

## Installation guide
### Setting up the environment
We used Ubuntu 20.04.5 LTS in the development
1. Install Python (we recommend version 3.8.10)
2. Install Pip (we recommend version 20.0.2)
3. Install chrome 

### Set up environment variables
You need to setup environment variables as follows 
Name: description
GITHUB_USERNAME: Your github crawling account username
GITHUB_PASSWORD: Your github crawling account password

FORUM_USERNAME: Your hacker forum crawling account username
FORUM_PASSWORD: Your hacker forum crawling account password

MONGO_CLIENT: Your mongdb client link
MONGO_DB_NAME: Your mongdb database name
MONGO_POSTS_COLLECTION: Your mongdb posts collection name(for twitter and the hacker forum)
MONGO_GITHUB_COLLECTION: Your mongdb github collection name
MONGO_KEYWORD_COLLECTION: Your mongdb keyword collection name
MONGO_DOMAINS_COLLECTION: Your mongdb domains collection name
MONGO_STOPPING_COLLECTION: Your mongdb MaxID collection name that has the max id for twitter in id 0001

TWITTER_API_KEY: The Twitter API key
TWITTER_API_SECRET: The Twitter API secret
TWITTER_ACCESS_TOKEN: The Twitter access token
TWITTER_ACCESS_SECRET: The Twitter access secret

### Run the code
1. Install requirements (pip3 install -r requirements.txt)
2. Run main.py

## Used Tools and Libraries
1. Language used: Python (https://www.python.org/)
2. Database used: MongoDB (https://www.mongodb.com/)
3. Main tools and libraries used in crawling: 
     - Selenium (https://www.selenium.dev/)
      - requests (https://pypi.org/project/requests/)
    - Flask framework (https://flask.palletsprojects.com/en/2.2.x/)
    - pymongo (https://pymongo.readthedocs.io/en/stable/)
    - PyCharm (https://www.jetbrains.com/pycharm/)
    - VS Code (https://code.visualstudio.com/)
