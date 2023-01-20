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
import os

# API keyws that yous saved earlier
api_key = os.environ['TWITTER_API_KEY']
api_secret = os.environ['TWITTER_API_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_secret = os.environ['TWITTER_ACCESS_SECRET']

# Authenticate to Twitter
auth = tweepy.OAuthHandler(api_key, api_secret)
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
cluster = MongoClient(os.environ['MONGO_CLIENT'])
db = cluster[os.environ['MONGO_DB_NAME']]
collection = db[os.environ['MONGO_POSTS_COLLECTION']]
stopping_collection = db[os.environ['MONGO_STOPPING_COLLECTION']]
keyword_collection = db[os.environ['MONGO_KEYWORD_COLLECTION']]


# Reading keywords from database
for i in keyword_collection.find():
  keywords.append(i['Keyword'])

# Getting the id of the latest tweet that was found in the previous crawling round
if(stopping_collection.find_one({"_id": "0001"})['since_id']):
  since_id=int(stopping_collection.find_one({"_id": "0001"})['since_id'])
else:
  since_id=0

# Empty list to store parsed tweets
tweets = []

# Set current max id 
maxid=since_id

for i in keywords:

    for j in egWords:
      tmp=j+" "+i

      # Call twitter api to fetch tweets
      try:
        tweets_temp=api.search_tweets(tmp,lang=('en' or 'ar'), count = 10, since_id=since_id, tweet_mode="extended")
      except:
        time.sleep(15*60)
        tweets_temp=api.search_tweets(tmp,lang=('en' or 'ar'), count = 10, since_id=since_id, tweet_mode="extended")

      # For each tweet
      for k in range(len(tweets_temp)):

        # Update the max id
        if(int(tweets_temp[k].id)>maxid):
          maxid=int(tweets_temp[k].id)

        urls_temp=[]
        user_mentions_temp=[]
        retweet_info=[]

        # If the tweet has retweet status
        if(hasattr(tweets_temp[k], 'retweeted_status')):

          flg=0

          # Find the retweet id
          tweet_temp=collection.find_one({"additional_info.tweet_id": tweets_temp[k].retweeted_status.id})

          # Form retweet info
          retweet_url="https://twitter.com/"+str(tweets_temp[k].user.screen_name)+"/status/"+str(tweets_temp[k].id)
          retweet_info=[{
              'id':tweets_temp[k].id,
               'user_screen_name':tweets_temp[k].user.screen_name,
               'url':retweet_url
               }]

          # If this tweet is indeed a retweet
          if(tweet_temp):

            # Check if the retweet is already recorded in the database
            for m in range(len(tweet_temp["more_details"]["retweet_info"])):

              if(tweet_temp["more_details"]["retweet_info"][m]['id']==tweets_temp[k].id):
                flg=1

            # If it wasn't already recorded in the database
            if(flg==0):

              # Append the retweet to the retweet list collected from the database
              tweet_temp["more_details"]["retweet_info"].append(retweet_info[0])

              # Push the updated version of the retweet list to the database
              collection.update_one(
                  {
                      "additional_info.tweet_id": tweet_temp['_id']
                   }, 
                   { 
                       "$set":{ "more_details.retweet_info": tweet_temp["more_details"]["retweet_info"]}
                    })
              
            # Continue to the next tweet
            continue
            
          # If it is the original tweet that was retweeted 
          # Use the retweeted status as the main info of the tweet
          else:

            tweet_temp=tweets_temp[k].retweeted_status

        # If it doesn't have retweet status return the tweets info as is
        else:

          tweet_temp=tweets_temp[k]

        # If the tweet is already in the database skip it
        if(collection.find_one({"additional_info.tweet_id": tweets_temp[k].id})):

          continue

        # Else parse it and push it to the database
        else:

          if(hasattr(tweet_temp, 'entities')):

            if (tweet_temp.entities['urls']):

                for l in tweet_temp.entities['urls']:

                    urls_temp.append(l['expanded_url'])

            if(tweet_temp.entities['user_mentions']):

                for l in tweet_temp.entities['user_mentions']:

                    user_mentions_temp.append({
                        "id":l['id'] ,
                        "screen_name":l['screen_name']
                        })
                    
          url="https://twitter.com/"+str(tweet_temp.user.screen_name)+"/status/"+str(tweet_temp.id)

          post_temp={
                     "title":tweet_temp.full_text,
                     "url":url,
                     "username":tweet_temp.user.screen_name,
                     "created_at":tweet_temp.created_at,
                     "additional_info":{
                                        "tweet_id":tweet_temp.id,
                                        "user_id": tweet_temp.user.id,
                                        },
                     "more_details":{
                                     "body_text": tweet_temp.full_text,
                                     "payload_urls": urls_temp,
                                     "user_location":tweet_temp.user.location,
                                     "Keywords":[i,j],
                                     "hashtags":tweet_temp.entities['hashtags'],
                                     "mentions":user_mentions_temp,
                                     "Metadata":tweet_temp.metadata,
                                     'retweet_info':retweet_info
                                     }
                     }

          collection.insert_one(post_temp)


# If there is a new max id push it to the database
if(maxid>since_id):

  stopping_collection.update_one({"_id": "0001"}, { "$set":{ 'since_id': str(maxid)}}, upsert=True)
