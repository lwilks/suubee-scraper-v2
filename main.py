#!/usr/bin/env python
# coding: utf-8
from dotenv import load_dotenv
from flask import Flask
import requests
import json
import time
import csv
import os
import re
from collections import OrderedDict

load_dotenv()

app = Flask(__name__)

#Try request. If we recieve a 403 response, wait 60 seconds and try again.
def tryreq(param, d, headers, method):
    global timeout
    global igurl
    try:
        data = None
        if d:
            data = json.dumps(d)
        r = session.request(method=method, url=igurl+param, data=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if (err.response.status_code == 403):
            print("API calls exceeded, waiting 65 seconds")
            time.sleep(timeout)
            print("Wait over, resuming")
            r = session.request(method=method, url=igurl+param, data=data, headers=headers)
        else:
            print(err)
            return err
    return r

# Main function - log's into Suubee, scrapes list data from Trade Desk and US Page, provides list of ticker symbols to createlist function for creation of lists in IG (and ProRealtime)
@app.route("/")
def run(event=None,context=None):
    #IG numerical username (same as what you log into IG with)
    igusername = os.environ['IG_USER']
    #IG Password
    igpassword = os.environ['IG_PASS']
    #Base IG API URL
    global igurl
    igurl = 'https://api.ig.com/gateway/deal/'
    #IG API Key (genereted under "account settings" in IG Portal)
    global igapikey
    igapikey = os.environ['IG_API_KEY']

    #Set to true to print list of "epics" instead of creating lists
    printonly = False

    #Start requests "session"
    global session
    session = requests.Session()

    #Load lists from google sheets
    r = session.get('https://docs.google.com/spreadsheets/d/e/2PACX-1vQHISABW77-Qsg6EM5aHOI3wGTPi_tzECzRU5hrrQEyQLnxFnPVsgRE50uuadvHIB4-jRIR0snlSReM/pub?gid=0&single=true&output=csv')
    rows = r.text.split("\n")
    reader = csv.DictReader(rows)

    global lists
    lists = {}
    for row in reader:
        lists[row['LIST']] = row['URL']

    #Create header to authenticate with IG API
    headers = {'Version': '2', 'X-IG-API-KEY': igapikey}
    data = {"identifier": igusername, "password": igpassword, "encryptedPassword": '' }

    #How long should be wait between calls to IG API if we have exceeded max hits (default 65 seconds)
    global timeout
    timeout = 65

    #Authenticate with IG API. If max hits exceeded (code 403) than wait (for duration specified in timeout variable) then try again
    try:
        print("Authenticating with ID")
        r = session.post(igurl+'session', json=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if (err.response.status_code == 403):
            time.sleep(timeout)
            try:
                r = session.post(igurl+'session', json=data, headers=headers)
                r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                if (err.response.status_code == 403):
                    print("Invalid API key for IG")
                    print("Raw Exception: "+str(err))
                    return "<p>Invalid API key for IG</p>"
                else:
                    print(err)
                    return "<p>"+str(err)+"</p>"
        elif (err.response.status_code == 401):
            print("Invalid username and password combination for IG")
            print("Raw Exception: "+str(err))
            return "<p>Invalid username and password combination for IG</p>"
        else:
            print(err)
            return "<p>"+str(err)+"</p>"

    #Get security token from IG
    global igsectoken
    igsectoken = r.headers.get('X-SECURITY-TOKEN')
    global igcst
    igcst = r.headers.get('CST')

    #Construct new header for IG with the security token obtained above
    headers = {'Version': '1', 'X-IG-API-KEY': igapikey, 'X-SECURITY-TOKEN': igsectoken, 'CST': igcst}

    results = []

    print("Retreiving Watchlists")
    r = tryreq('watchlists', None, headers, 'GET')

    watchlists = json.loads(r.text)

    #If we are not simply printing the epics then delete the existing lists we have created
    if not printonly:
        for x in watchlists['watchlists']:
            valid = re.search("^Suubee *", x['name'])
            if valid:
                print("Deleting watchlists")
                r = tryreq('watchlists/'+x['id'], None, headers, 'DELETE')

    for iglist in lists:
        r = session.get(lists[iglist])
        rows = r.text.split("\n")

        stripped_rows = []
        for row in rows:
            if (len(row)):
                stripped_rows.append(row.rstrip())

        if len(stripped_rows):
            d = {}
            d['name'] = iglist
            d['epics'] = stripped_rows

            print("Adding list "+iglist)
            try:
                r = tryreq('watchlists', d, headers, 'POST')
                r.raise_for_status()

                print ("Added list "+iglist)
                results.append("Added list "+iglist)
            except requests.exceptions.HTTPError as err:
                print ("Bad header for list "+iglist)
                results.append("Bad header for list "+iglist)
            
        
        # wl = json.loads(r.content)
        # wlID = wl['watchlistId']        

        # d = {}
        # for row in rows:
        #     d['epic'] = row.rstrip()
        #     r = tryreq('watchlists/'+wlID, d, headers, 'PUT')

    # This part for generate HTML for return
    html = ''
    for i in results:
        html += '<h2>' + str(i) + '</br>'

    return html
    #print(results)

#run()
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
