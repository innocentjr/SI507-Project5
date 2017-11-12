## import statements
import tornado.ioloop
import time
import tornado.web
import requests_oauthlib
from secret_data import *
import csv
import webbrowser
import json
import os
from datetime import datetime

## Variables
APP_ID = app_id
APP_SECRET = app_secret
AUTHORIZATION_BASE_URL = 'https://www.eventbrite.com/oauth/authorize'
TOKEN_URL = 'https://www.eventbrite.com/oauth/token'
REDIRECT_URI = 'http://localhost:8000'
port = 8000
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
eventbrite_session = False
DAYS = 1
timecache = True
endpoints = ['subcategories', 'events']
filenames = ['eventbrite.json', 'events.json']
token_names = 'super_token.json'
events_params = ['/search/?q=chicago']


## Tornado setUp
class CodeListener(tornado.web.RequestHandler):
	'''
	This handler listens for a GET request and then shuts down the server the first time one is recieved.
	'''
	def get(self):
		# print('Received a hit on port! Stopping the server.')
		token = self.get_argument("code", None, True)
		self.write("Access token received. Please return to the Python application")
		self.application.code = token
		tornado.ioloop.IOLoop.current().stop()

def listen_on_port(port):
    application = tornado.web.Application([(r"/", CodeListener),])
    application.code = None
    application.listen(port)
    print('Starting to listen on port',port)
    tornado.ioloop.IOLoop.current().start()
    print('Stopped listening on port. Returning code.')
    return application.code

## CACHING SETUP
def has_cache_expired(timestamp_str, expire_in_days):
    """Check if cache timestamp is over expire_in_days old"""
    #gives current datetime
    try:
        now = datetime.now()

        #Converts a formatted string into datetime object
        cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

        #subtracting two datetime objects gives you a timedelta objects
        delta = now - cache_timestamp
        delta_in_days = delta.days

        # now that we have days as integers, we can just use comparison
        # and decide if cache has expired or not
        if delta_in_days > expire_in_days:
            return True #it's been longer than expiry time
        else:
            return False
    except:
        return False

def get_saved_token(tokens):
    with open(tokens, 'r') as f:
        token_json = f.read()
        token_dict = json.loads(token_json)
        return token_dict

def save_token(token_dict, tokens):
    with open(tokens, 'w') as f:
        token_json = json.dumps(token_dict)
        f.write(token_json)

def addtimeStamp_token(timecache, tokens):
    with open(tokens, 'r') as f:
        token = json.loads(f.read())
        token['timestamp'] = timecache
        save_token(token, tokens)
        f.close()

## ADDITIONAL CODE for program should go here...
## Perhaps authentication setup, functions to get and process data, a class definition... etc.
def make_eventbrite_request(url=None, params=None, tokens = None):
    # we use 'global' to tell python that we will be modifying this global variable
    global eventbrite_session

    if not eventbrite_session:
        start_eventbrite_session(tokens)

    if not params:
        params = {}

    return eventbrite_session.get(url, params=params)

def start_eventbrite_session(tokens):
    global eventbrite_session

    # 0 - get token from cache
    try:
        token = get_saved_token(tokens)
    except FileNotFoundError:
        token = None

    if token:
        eventbrite_initial_session = requests_oauthlib.OAuth2Session(APP_ID, token=token)
        eventbrite_session = eventbrite_initial_session

    else:
        # 1 - session
        eventbrite_initial_session = requests_oauthlib.OAuth2Session(APP_ID, redirect_uri=REDIRECT_URI)
        eventbrite_session = eventbrite_initial_session

        # 2 - authorization
        authorization_url, state = eventbrite_session.authorization_url(AUTHORIZATION_BASE_URL)
        print('Opening browser to {} for authorization'.format(authorization_url))
        webbrowser.open(authorization_url)

        # 3 - token
        code = listen_on_port(port)
        token_response = eventbrite_session.fetch_token(TOKEN_URL, code=code, client_secret=APP_SECRET)
        timecache = datetime.now()

        # 4 - save token
        save_token(token_response, tokens)
        addtimeStamp_token(str(timecache), tokens)

def grab_subcatergories(var, file_name, tokens):
    if var != endpoints[0]:
        my_response = make_eventbrite_request('https://www.eventbriteapi.com/v3/'+ str(var) + events_params[0],'' , tokens)
    else:
        my_response = make_eventbrite_request('https://www.eventbriteapi.com/v3/'+ str(var),'' , tokens)

    CACHE_DICTION = json.loads(my_response.text)
    print(CACHE_DICTION)
    final = True
    while final == True:
        try:
            with open(file_name,"r") as f:
                json_dic = json.loads(f.read())
                f.close()
                for entry in CACHE_DICTION[var]:
                    json_dic.append(entry)

            with open(file_name,"w") as f:
                json_dic = json.dumps(json_dic, indent=4, sort_keys=True, separators=(',', ': '))
                f.write(json_dic)
                f.close

        except:
            with open(file_name,"w") as f:
                print(type(CACHE_DICTION))
                print(CACHE_DICTION.keys())
                json_dic = json.dumps(CACHE_DICTION[var], indent=4, sort_keys=True, separators=(',', ': '))
                f.write(json_dic)
                f.close

        if CACHE_DICTION['pagination']['has_more_items'] == True:
            if tokens == "events_token.json":
                break
            else:
                my_response = make_eventbrite_request('https://www.eventbriteapi.com/v3/'+var+'/?'+'continuation='+str(CACHE_DICTION['pagination']['continuation']))
            CACHE_DICTION = json.loads(my_response.text)
        elif CACHE_DICTION['pagination']['has_more_items'] ==  False:
            final = False
        else:
            pass

    json_dic = json.loads(json_dic)
    print(type(json_dic))
    return json_dic

# TODO use make_eventbrite_request
def run(file_name, tokens, endpoint):
    try:
        with open(file_name,"r") as f:
            subcat = json.loads(f.read())
            f.close()
            with open(tokens, 'r') as f:
                token = json.loads(f.read())
                f.close()
                print(has_cache_expired(token['timestamp'], 1))
                if has_cache_expired(token['timestamp'], DAYS) == True:
                    os.remove(tokens)
                    os.remove(file_name)
                    raise Exception
    except:
        # Grab the subcatergories and save thme to a json file
        subcat = grab_subcatergories(endpoint, file_name, tokens)
    return subcat



## Make sure to run your code and write CSV files by the end of the program.
def collectObjects(masterlist, somelist):
    headers = ["Subcategory ID", "Name", "Parent Category ID", "Parent Category Name", "Parent Category Localized Name", "Resource URI"]
    masterlist.append(headers)
    for obj in somelist:
        mono = []
        mono.append(obj.get('id'))
        mono.append(obj.get('name'))
        mono.append(obj.get('parent_category').get('id'))
        mono.append(obj.get('parent_category').get('name'))
        mono.append(obj.get('parent_category').get('name_localized'))
        mono.append(obj.get('parent_category').get('resource_uri'))
        masterlist.append(mono)

def collectEvents(masterlist, somelist):
    headers = ["Name", "Description", "Capacity", "Event Id", "Subcategory ID", "Venue ID", "URL"]
    masterlist.append(headers)
    for obj in somelist:
        mono = []
        mono.append(obj.get('name').get('text'))
        mono.append(obj.get('description').get('text'))
        mono.append(obj.get('capacity'))
        mono.append(obj.get('id'))
        mono.append(obj.get('subcategory_id'))
        mono.append(obj.get('venue_id'))
        mono.append(obj.get('url'))
        masterlist.append(mono)

def writeLists(filelist, entry):
    with open(entry, "w", encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        writer.writerows(filelist)
        f.close()

if __name__ == "__main__":
    # Invoke
	subcat = run(filenames[0], token_names, endpoints[0])
	subcategory_objects = []

	masterlist = []
	collectObjects(masterlist, subcat)
	writeLists(masterlist, "EventbriteSubcategories.csv")

	masterlist = []
	subcatTwo = run(filenames[1], token_names, endpoints[1])
	collectEvents(masterlist, subcatTwo)
	writeLists(masterlist, "SomeEventsinChicago.csv")
