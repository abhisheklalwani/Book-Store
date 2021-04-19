from flask import Flask,session
from flask_session import Session
import requests 
from flask import request
from flask import jsonify
from response_util import get_failed_response,get_success_response 
import sys
from flask_caching import Cache
sys.path.insert(1, '../')
import logging

logging.basicConfig(filename="frontend.log", level=logging.DEBUG, format='%(asctime)s %(message)s', filemode='w')

config = {          
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 0
}

app = Flask(__name__)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

app.config.from_mapping(config)
cache = Cache(app)

CATALOG_SERVER_1 = {"type": "catalog", "IP": "http://localhost", "PORT": 8011}
ORDER_SERVER_1 = {"type": "order", "IP": "http://localhost", "PORT": 8012}
CATALOG_SERVER_2 = {"type": "catalog", "IP": "http://localhost", "PORT": 8013}
ORDER_SERVER_2 = {"type": "order", "IP": "http://localhost", "PORT": 8014}

# defining the default page
@app.route('/', methods=['GET'])
def hello_world():
    return "Welcome to Book Store!"

# the buy method which makes calls to the order server to buy an item based on provided item id
@app.route('/buy', methods=['GET'])
def buy():
    try:
        data = request.args
        id=data["id"]
        app.logger.info("Buy method called with the item with id '%s' in catalog server." % (id))
        if session['load_balancer_order'] == 0:
            session['load_balancer_order'] = 1
            results=requests.get("%s:%s/buy/%s"%(ORDER_SERVER_1["IP"],ORDER_SERVER_1["PORT"],id))
            results=results.json()
        else:
            session['load_balancer_order'] = 0
            results=requests.get("%s:%s/buy/%s"%(ORDER_SERVER_2["IP"],ORDER_SERVER_2["PORT"],id))
            results=results.json()
        cache.clear()
        app.logger.info("Purchase of item '%s' successfull."%(id))
        return results
    except Exception as e:
        app.logger.info("Failed to connect to order server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))


#the search method makes calls to the catalog server and searches for items based on topic name 
@app.route('/search',methods=['GET'])
@cache.cached(key_prefix='topic_lookup')
def search():
    try:
        if 'topic' in request.args:
            topic=request.args['topic']
        else:
            return "Error: No topic field provided. Please specify a topic."
        app.logger.info("Search method called with the topic name '%s' in catalog server." % (topic))
        if session['load_balancer_catalog'] == 0:
            session['load_balancer_catalog'] = 1
            results=requests.get("%s:%s/item?topic=%s"%(CATALOG_SERVER_1["IP"],CATALOG_SERVER_1["PORT"],topic))
            app.logger.info("Searching of items with topic '%s' successful."%(topic))
        else:
            session['load_balancer_catalog'] = 0
            results=requests.get("%s:%s/item?topic=%s"%(CATALOG_SERVER_2["IP"],CATALOG_SERVER_2["PORT"],topic))
            app.logger.info("Searching of items with topic '%s' successful."%(topic))
        results=results.json()
        return results
    except Exception as e:
        app.logger.info("Failed to connect to catalog server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))


# the lookup method makes calls to the catalog server and searches for the item corresponding to item id
@app.route('/lookup',methods=['GET'])
@cache.cached(key_prefix='id_lookup')
def lookup():
    try:
        if 'id' in request.args:
            id=request.args['id']
        else:
            return "Error: No id field provided. Please specify an id."
        app.logger.info("Lookup method called with the id '%s' in catalog server." % (id))
        if session['load_balancer_catalog'] == 0:
            session['load_balancer_catalog'] = 1
            results=requests.get("%s:%s/item/%s"%(CATALOG_SERVER_1["IP"],CATALOG_SERVER_1["PORT"],id))
            results=results.json()
        else:
            session['load_balancer_catalog'] = 0
            results=requests.get("%s:%s/item/%s"%(CATALOG_SERVER_2["IP"],CATALOG_SERVER_2["PORT"],id))
            results=results.json()
        app.logger.info("Looking Up of item with id '%s' successful."%(id))
        return results
        
    except Exception as e:
        app.logger.info("Failed to connect to catalog server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))