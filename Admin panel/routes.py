from flask import Flask, render_template, abort
from dbpass import mongopass 
from pymongo import MongoClient
from flask import request
from flask import jsonify
from datetime import datetime
from bson.objectid import ObjectId
import math 
import re

app = Flask(__name__, template_folder='template')

# Database Connection 
cluster = MongoClient(mongopass)
db = cluster["EgycertCrawler"]
collection = db["Twitter"]
githubcollection = db["Github2"]
forumcollection = db["HackerForum"]
keywordCollection = db["Keywords"]
domainsCollection = db["SensitiveDomains"]


@app.route('/home')
def home():    
    return render_template("home.html")

@app.route('/')
@app.route('/dashboard',  methods=["GET", "POST"])
def dashboard():
    #Paging Parameters
    page_size = 10
    page_num = request.args.get('page_num')
    if not page_num: 
        page_num = 1
    else:
        page_num = int(page_num)
    skips = page_size * (page_num - 1)

    #If the user searching
    search = request.args.get("search")
    searchuser = request.args.get("searchuser")
    if request.method == "POST" or search or searchuser:  
        if request.method == "POST":
            search = request.form.get("searchbody").strip()
            if not search: 
                searchuser = request.form.get("searchuser").strip()
        if search or searchuser:
            if search: 
                searchKeywords = convertStringToList(search)
                searchString = '|'.join(searchKeywords)
                pat = re.compile(searchString, re.I)
                query = {"TweetText": {'$regex': pat}} 
            else:
                searchKeywords = convertStringToList(searchuser)
                searchString = '|'.join(searchKeywords)
                pat = re.compile(searchString, re.I)
                query = {"user_screen_name": {'$regex': pat}}
            
            results = collection.find(query, {'url':1, 'created_at':1, 'TweetText':1, 'Keywords':1, 'user_screen_name':1, 'user_id':1}).sort("created_at", -1).skip(skips).limit(page_size)
            count = collection.count_documents(query)
            total_pages = math.ceil(count/page_size)

            return render_template("dashboard.html", title="Dashboard", results = results, count=count, search=search, searchuser=searchuser, page_num=page_num, total_pages=total_pages)
    
    #If the user not searching display the dashboard by default crawling settings
    results = collection.find({}, {'url':1, 'created_at':1, 'TweetText':1, 'Keywords':1, 'user_screen_name':1, 'user_id':1}).sort("created_at", -1).skip(skips).limit(page_size)
    count = collection.count_documents({})
    total_pages = math.ceil(count/page_size)
    return render_template("dashboard.html", title="Dashboard", results = results, count=count, page_num=page_num, total_pages=total_pages)

@app.route('/credentials-dashboard', methods=["GET", "POST"])
def credentialsDashboard():
    #Paging Parameters
    page_size = 10
    page_num = request.args.get('page_num')
    if not page_num: 
        page_num = 1
    else:
        page_num = int(page_num)
    skips = page_size * (page_num - 1)
    
    #If the user searching
    search = request.args.get("search")
    searchrepo = request.args.get("searchrepo")
    if request.method == "POST" or search or searchrepo:  
        if request.method == "POST":
            search = request.form.get("search").strip()
            if not search: 
                searchrepo = request.form.get("searchrepo").strip()
        if search or searchrepo:
            if search: 
                searchKeywords = convertStringToList(search)
                searchString = '|'.join(searchKeywords)
                pat = re.compile(searchString, re.I)
                query = {"domain": {'$regex': pat}} 
            else:
                searchKeywords = convertStringToList(searchrepo) 
                searchString = '|'.join(searchKeywords)
                pat = re.compile(searchString, re.I)
                query = {"RepoFullName": {'$regex': pat}}
            
            results = githubcollection.find(query).sort("UpdatedDate", -1).skip(skips).limit(page_size)
            count = githubcollection.count_documents(query)
            total_pages = math.ceil(count/page_size)

            return render_template("github-dashboard.html", title="Credentials Dashboard", results = results, count=count, search=search, searchuser=searchrepo, page_num=page_num, total_pages=total_pages)
    
    #If the user not searching display the dashboard by default crawling settings
    results = githubcollection.find({}).sort("UpdatedDate", -1).skip(skips).limit(page_size)
    count = githubcollection.count_documents({})
    total_pages = math.ceil(count/page_size)
    return render_template("github-dashboard.html", title="Credentials Dashboard", results = results, count=count, page_num=page_num, total_pages=total_pages)

def convertStringToList(searchText):
    searchList = searchText.split()
    searchConverted= [s.strip() for s in searchList]
    return searchConverted

@app.route('/details')
def details():
    tweet_id = request.args.get('tweet_id')
    result = collection.find_one({'_id': int(tweet_id)})
    
    return render_template("item-details.html", title="Details", item=result)


@app.route('/keywords', methods=["GET", "PUT", "POST", "DELETE"])
def keywords():
    # If user is adding new Keyword
    if request.method == "POST":
        text = request.json['text']
        result = keywordCollection.find_one({'Keyword': text.strip().lower()})
        if result : 
            abort(400)
        
        keyword = {
            'Keyword': text.strip().lower(),
            'Created': datetime.now(), 
            'Modified': datetime.now(), 
        }
        x = keywordCollection.insert_one(keyword)
        return jsonify({'keyword': str(text)})

    # If user is editing an existing Keyword
    elif request.method == "PUT":
        text = request.json['text']
        tid = request.json['id']
        result = keywordCollection.find_one({'Keyword': text.strip().lower()})
        if result : 
            abort(400)
        
        keywordCollection.update_one({"_id": ObjectId(tid)}, {"$set": { "Keyword": text.strip().lower(), "Modified": datetime.now()}})
        return jsonify({'keyword': str(text)})
    
    # If user is deleting an existing Keyword
    elif request.method == "DELETE":
        tid = request.json['id']
        result = keywordCollection.find_one({'_id': ObjectId(tid)})
        if not result: 
            abort(400)
        
        keywordCollection.delete_one({"_id": ObjectId(tid)})
        return jsonify({'deleted': True})
    
    # listing the keywords
    results = keywordCollection.find().sort("Created", -1)
    count = keywordCollection.count_documents({})
    
    return render_template("keyword-list.html", title="Keywords", results= results, count=count)

@app.route('/sensitive-domains', methods=["GET", "PUT", "POST", "DELETE"])
def sensitiveDomains():
    # If user is adding new domain
    if request.method == "POST":
        print(request.json)
        domain = request.json['Domain']
        entity = request.json['Entity']
        result = domainsCollection.find_one({'Domain': domain.strip().lower()})
        if result : 
            abort(400)
        
        keyword = {
            'Domain': domain.strip().lower(),
            'Entity': entity.strip().lower(),
            'Created': datetime.now(), 
            'Modified': datetime.now(), 
        }
        domainsCollection.insert_one(keyword)
        return jsonify({'domain': str(domain)})

    # If user is editing an existing Keyword
    elif request.method == "PUT":
        domain = request.json['Domain']
        entity = request.json['Entity']
        tid = request.json['id']
        result = domainsCollection.find_one({'Domain': domain.strip().lower()})
        if result : 
            abort(400)
        
        domainsCollection.update_one({"_id": ObjectId(tid)}, {"$set": { "Entity": entity.strip().lower(), "Domain": domain.strip().lower(),  "Modified": datetime.now()}})
        return jsonify({'domain': str(domain)})
    
    # If user is deleting an existing Keyword
    elif request.method == "DELETE":
        tid = request.json['id']
        result = domainsCollection.find_one({'_id': ObjectId(tid)})
        if not result: 
            abort(400)
        
        domainsCollection.delete_one({"_id": ObjectId(tid)})
        return jsonify({'deleted': True})
    
    # listing the keywords
    results = domainsCollection.find().sort("Created", -1)
    count = domainsCollection.count_documents({})
    return render_template("github-keyword-list.html", title="Sensitive Domains", results=results, count=count)

if __name__ == "__main__":
    app.run(debug=True)