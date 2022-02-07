from flask import Flask, jsonify
from Posts_Class import Posts

app = Flask(__name__)

class MyServer:
    def __init__(self, sites):
        self.sites = None
        self.Posts = Posts(sites)

global my_server
global my_server2
my_server = None
my_server2 = None

@app.route('/s/<query>&<priceRange>&<valueDiff>&<sites>&<condition>&<sortBy>')
#/s/searchterm&price,range&valuediff&site,site&condition&ageofpost&sortby
def index(query, priceRange, valueDiff, sites, condition, sortBy): 
    global my_server
    global my_server2
    sites_list = list(sites.split(','))
    filters = [priceRange, valueDiff, condition, sortBy, sites_list]
    if my_server is not None and my_server2 is None:
        my_server = None
        my_server2 = MyServer(filters[4])
        sitePosts = my_server2.Posts.posts(query, filters)  #Initial scrape for all sites
    else:
        my_server = MyServer(filters[4])
        sitePosts = my_server.Posts.posts(query, filters)  #Initial scrape for all sites
    resp = jsonify(sitePosts)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
    
@app.route('/l/<ids>')
def individual(ids):
    if my_server is not None:
        itemListing = my_server.Posts.ind_posts(ids)     #Scrape for single product
    else:
        itemListing = my_server2.Posts.ind_posts(ids)     #Scrape for single product
    resp = jsonify(itemListing)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == '__main__':  
    app.run()
