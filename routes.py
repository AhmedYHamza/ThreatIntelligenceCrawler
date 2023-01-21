from flask import Flask, render_template, abort, redirect, url_for
from pymongo import MongoClient
from flask import request
from flask import jsonify
from datetime import datetime
from bson.objectid import ObjectId
import math 
import re
import gladiator as gl
import os

app = Flask(__name__, template_folder='template')

# Database Connection 
cluster = MongoClient(os.environ['MONGO_CLIENT'])
db = cluster[os.environ['MONGO_DB_NAME']]
collection = db[os.environ['MONGO_POSTS_COLLECTION']]
githubcollection = db[os.environ['MONGO_GITHUB_COLLECTION']]
keywordCollection = db[os.environ['MONGO_KEYWORD_COLLECTION']]
domainsCollection = db[os.environ['MONGO_DOMAINS_COLLECTION']]


@app.route('/home')
def home():    
    return render_template("home.html")

@app.route('/')
def home2():    
    return redirect(url_for('dashboard')) 

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

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
    error_flag = False
    if request.method == "POST" or search or searchuser:  
        if request.method == "POST":
            search = request.form.get("searchbody")
            if search and not validate_search(search): 
                error_flag = True
            elif not search: 
                searchuser = request.form.get("searchuser")
                if searchuser and not validate_search(searchuser): 
                    error_flag = True
        if (search or searchuser) and not error_flag:
            if search: 
                searchKeywords = convertStringToList(search)
                searchString = '|'.join(searchKeywords)
                pat = re.compile(searchString, re.I)
                query = { "title": {'$regex': pat}}
            elif searchuser and validate_search(searchuser):
                searchKeywords = convertStringToList(searchuser)
                searchString = '|'.join(searchKeywords)
                pat = re.compile(searchString, re.I)
                query = {"username": {'$regex': pat}}
            
            results = collection.find(query).sort("created_at", -1).skip(skips).limit(page_size)
            count = collection.count_documents(query)
            total_pages = math.ceil(count/page_size)

            return render_template("dashboard.html", title="Dashboard", results = results, count=count, search=search, searchuser=searchuser, page_num=page_num, total_pages=total_pages, errorFlag = error_flag)
    
    #If the user not searching display the dashboard by default crawling settings
    results = collection.find().sort("created_at", -1).skip(skips).limit(page_size)
    count = collection.count_documents({})
    total_pages = math.ceil(count/page_size)
    print(error_flag)
    return render_template("dashboard.html", title="Dashboard", results = results, count=count, page_num=page_num, total_pages=total_pages, errorFlag = error_flag)

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
    error_flag = False
    if request.method == "POST" or search or searchrepo:  
        if request.method == "POST":
            search = request.form.get("search")
            if search and not validate_search(search): 
                error_flag = True
            elif not search: 
                searchrepo = request.form.get("searchrepo")
                if searchrepo and not validate_search(searchrepo): 
                    error_flag = True
        if (search or searchrepo) and not error_flag:
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

            return render_template("github-dashboard.html", title="Credentials Dashboard", results = results, count=count, search=search, searchuser=searchrepo, page_num=page_num, total_pages=total_pages, errorFlag = error_flag)
    
    #If the user not searching display the dashboard by default crawling settings
    results = githubcollection.find({}).sort("UpdatedDate", -1).skip(skips).limit(page_size)
    count = githubcollection.count_documents({})
    total_pages = math.ceil(count/page_size)
    return render_template("github-dashboard.html", title="Credentials Dashboard", results = results, count=count, page_num=page_num, total_pages=total_pages, errorFlag = error_flag)

@app.route('/details')
def details():
    id = request.args.get('id')
    try: 
        result = collection.find_one({'_id': ObjectId(id)})
        return render_template("item-details.html", title="Details", item=result)
    except: 
        return redirect(url_for('dashboard'))


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

def convertStringToList(searchText):
    searchList = searchText.split()
    searchConverted= [s.strip() for s in searchList]
    return searchConverted

def validate_search(searchtext): 
    return gl.validate((gl.required, gl.type_(str), gl.regex_('[a-zA-Z][0-9a-zA-Z\-\. ]+')), searchtext).success
    
if __name__ == "__main__":
    app.run(debug=False)
