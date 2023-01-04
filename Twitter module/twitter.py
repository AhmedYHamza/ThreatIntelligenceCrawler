# -*- coding: utf-8 -*-

# !pip install tweepy==4.0
# !pip install pymongo==3.7.2
# !pip install pymongo[srv]

import re
import io
import csv
import json
import tweepy
import pymongo
from pymongo import MongoClient
import time

# API keyws that yous saved earlier
api_key = "Input Twitter API key here"
api_secrets = "Input Twitter API secret here"
access_token = "Input access token here"
access_secret = "Input access secret here"

# Authenticate to Twitter
auth = tweepy.OAuthHandler(api_key, api_secrets)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

try:
    api.verify_credentials()
    print('Successful Authentication')
except:
    print('Failed authentication')

keywords = []
egWords = ["egypt", "egy", "مصر"]

# Open mongodb client
cluster = MongoClient(
    'Input the database client here')
db = cluster["Input the name of the cluster "]
collection = db["Input the name of the posts collection"]
stopping_collection = db["Input the name of the collection containing the Max ID"]
keyword_collection = db["Input the name of the keyword collection"]

# empty list to store parsed tweets
tweets = []

# call twitter api to fetch tweets
keyword_archive = []
fetched_tweets = []

for i in keyword_collection.find():
    keywords.append(i['Keyword'])

since_id = int(stopping_collection.find_one({"_id": "0001"})['since_id'])
maxid = since_id

for i in keywords:
    for j in egWords:
        tmp = j+" "+i
        tweets_temp = api.search_tweets(tmp, lang=(
            'en' or 'ar'), count=10, since_id=since_id, tweet_mode="extended")
        for k in range(len(tweets_temp)):
            if (int(tweets_temp[k].id) > maxid):
                maxid = int(tweets_temp[k].id)
            fetched_tweets.append(tweets_temp[k])
            urls_temp = []
            user_mentions_temp = []
            retweet_info = []
            if (hasattr(tweets_temp[k], 'retweeted_status')):
                flg = 0
                tweet_temp = collection.find_one(
                    {"_id": tweets_temp[k].retweeted_status.id})
                retweet_url = "https://twitter.com/" + \
                    str(tweets_temp[k].user.screen_name) + \
                    "/status/"+str(tweets_temp[k].id)
                retweet_info = [
                    {'id': tweets_temp[k].id, 'user_screen_name':tweets_temp[k].user.screen_name, 'url':retweet_url}]
                if (tweet_temp):
                    for m in range(len(tweet_temp['retweet_info'])):
                        if (tweet_temp['retweet_info'][m]['id'] == tweets_temp[k].id):
                            flg = 1
                    if (flg == 0):
                        tweet_temp['retweet_info'].append(retweet_info[0])
                        collection.update_one({"_id": tweet_temp['_id']}, {
                                              "$set": {'retweet_info': tweet_temp['retweet_info']}})
                    continue
                else:
                    tweet_temp = tweets_temp[k].retweeted_status
            else:
                tweet_temp = tweets_temp[k]
            if (collection.find_one({"_id": tweets_temp[k].id})):
                continue
            else:
                if (hasattr(tweet_temp, 'entities')):
                    if (tweet_temp.entities['urls']):
                        for l in tweet_temp.entities['urls']:
                            urls_temp.append(l['expanded_url'])
                    if (tweet_temp.entities['user_mentions']):
                        for l in tweet_temp.entities['user_mentions']:
                            user_mentions_temp.append(
                                {"id": l['id'], "screen_name": l['screen_name']})
                url = "https://twitter.com/" + \
                    str(tweet_temp.user.screen_name) + \
                    "/status/"+str(tweet_temp.id)
                post_temp = {"_id": tweet_temp.id, "url": url, "payload_urls": urls_temp, "user_id": tweet_temp.user.id, "user_screen_name": tweet_temp.user.screen_name, "user_location": tweet_temp.user.location, "created_at": tweet_temp.created_at, "Keywords": [
                    i, j], "TweetText": tweet_temp.full_text, "hashtags": tweet_temp.entities['hashtags'], "mentions": user_mentions_temp, "Metadata": tweet_temp.metadata, 'retweet_info': retweet_info}
                collection.insert_one(post_temp)

if (maxid > since_id):
    stopping_collection.update_one(
        {"_id": "0001"}, {"$set": {'since_id': str(maxid)}})
