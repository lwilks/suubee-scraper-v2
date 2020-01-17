#!/usr/bin/env python
# coding: utf-8
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from flask import Flask
import requests
import json
import csv
import time
import os

load_dotenv()

app = Flask(__name__)

# Function to read ticker symbol lists, translate symbol lists into IG API "epics" lists and create list in IG
def createlist(syms, country, listname, checknewscode=False, overrides=None, printonly=True):
    global timeout
    global igurl
    if overrides == None:
        overrides = {}
    epics = []
    #Loop through ticker list and resolve ticker symbols into epics
    for sym in syms:
        #Search for symbol in IG API. If max hits exceeded (code 403) than wait (for duration specified in timeout variable) then try again
        try:
            r = session.get(igurl+'markets?searchTerm='+sym, headers=headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if (err.response.status_code == 403):
                time.sleep(timeout)
                r = session.get(igurl+'markets?searchTerm='+sym, headers=headers)
            else:
                print(err)
                return                
        json_data = json.loads(r.text)
        #If an override exists, use that instead
        if overrides.get(sym):
            epics.append(overrides.get(sym))
            break

        for market in json_data['markets']:
            epic = market['epic']
            headers2 = {'Version': '3', 'X-IG-API-KEY': igapikey, 'X-SECURITY-TOKEN': igsectoken, 'CST': igcst}   
            try:
                r2 = session.get(igurl+'markets/'+epic, headers=headers2)
                r2.raise_for_status()
            except requests.exceptions.HTTPError as err:
                if (err.response.status_code == 403):
                    time.sleep(timeout)
                    r2 = session.get(igurl+'markets/'+epic, headers=headers2)
                else:
                    print(err)
                    return               
            json_data2 = json.loads(r2.text)
            newscode = json_data2['instrument']['newsCode']
            if (json_data2['instrument']['type'] == 'SHARES' and json_data2['instrument']['country'] == country):
                if (newscode[:newscode.find('.')] == sym or checknewscode == False):
                    epics.append(market['epic'])
                    break
            
    d = {}
    d['name'] = 'SB-'+listname
    d['epics'] = epics

    if printonly:
        print(json.dumps(d, indent = 4))
    else:
        try:
            r = session.post(igurl+'watchlists', data=json.dumps(d), headers=headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if (err.response.status_code == 403):
                time.sleep(timeout)
                r = session.post(igurl+'watchlists', data=json.dumps(d), headers=headers)
            else:
                return err    
        return r.text

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

    #Suubee Premium username
    username = os.environ['SUUBEE_USER']
    #Suubee Premium password
    password = os.environ['SUUBEE_PASS']
    #Suubee Premium url
    url = 'https://suubeepremium.com/login/'
    
    #Set to true to print list of "epics" instead of creating lists
    printonly = False

    #Start requests "session"
    global session
    session = requests.Session()
    
    #Create headers - Need to make script look like desktop browsewr so we get the full site from Suubee
    global headers
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # This is chrome, you can set whatever browser you like
    r = session.get(url, headers=headers)

    #Login to suubee premium
    values = {'log' : username, 'pwd' : password, 'rememberme' : 'forever', 'wp-submit' : 'Log In', 'redirect_to' : 'https://suubeepremium.com/trading-desk/', 'mepr_process_login_form' : 'true', 'mepr_is_login_page' : 'true'}
    r = session.post(url, data=values, headers=headers)

    #Use Beautiful Soup library to scrape and parse Suubee website data
    soup = BeautifulSoup(r.text, 'lxml')

    #Find "Leaders" table
    leaders = soup.find('tbody', id='leaders_content')  

    #Get list of symbols and full company names from ASX website
    r = session.get('https://www.asx.com.au/asx/research/ASXListedCompanies.csv')

    rows = r.text.split("\n")

    reader = csv.DictReader(rows[2:])

    #Make sure we only filter in valid company types
    asxcodes = {}
    for row in reader:    
        key = row.pop('ASX code')
        if row['Company name'].endswith(' LIMITED'):
            row['Company name'] = row['Company name'][:-8]
        if row['Company name'].endswith(' LIMITED.'):
            row['Company name'] = row['Company name'][:-9]        
        if row['Company name'].endswith(' LTD'):
            row['Company name'] = row['Company name'][:-4]
        if row['Company name'].endswith(' TRUST'):
            row['Company name'] = row['Company name'][:-6]
        if row['Company name'].endswith(' REIT'):
            row['Company name'] = row['Company name'][:-6]         
        asxcodes[key] = row['Company name']

    #Create header to authenticate with IG API
    headers = {'Version': '2', 'X-IG-API-KEY': igapikey}
    data = {"identifier": igusername, "password": igpassword, "encryptedPassword": '' } 

    #How long should be wait between calls to IG API if we have exceeded max hits (default 65 seconds)
    global timeout
    timeout = 65
    
    #Authenticate with IG API. If max hits exceeded (code 403) than wait (for duration specified in timeout variable) then try again
    try:
        r = session.post(igurl+'session', json=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if (err.response.status_code == 403):
            time.sleep(timeout)
            r = session.post(igurl+'session', json=data, headers=headers)
        else:
            print(err)
            return

    #Get security token from IG
    global igsectoken
    igsectoken = r.headers.get('X-SECURITY-TOKEN')
    global igcst
    igcst = r.headers.get('CST')

    #Construct new header for IG with the security token obtained above
    headers = {'Version': '1', 'X-IG-API-KEY': igapikey, 'X-SECURITY-TOKEN': igsectoken, 'CST': igcst}
	
    results = []
	
    #If we are not simply printing the epics then delete the existing lists we have created
    if not printonly:
        try:
            r = session.get(igurl+'watchlists', headers=headers)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if (err.response.status_code == 403):
                time.sleep(timeout)
                r = session.get(igurl+'watchlists', headers=headers)
            else:
                print(err)
                return

        json_data = json.loads(r.text)

        for x in json_data['watchlists']:
            if x['name'][0:3] == 'SB-':
                try:
                    r = session.delete(igurl+'watchlists/'+x['id'], headers=headers)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    if (err.response.status_code == 403):
                        time.sleep(timeout)
                        r = session.delete(igurl+'watchlists/'+x['id'], headers=headers)
                    else:
                        print(err)
                        return

    #Build list of ticker codes from leaders table
    syms = []
    for leader in leaders.find_all('tr'):
        syms.append(asxcodes[leader.find('td').text.strip()])
    #Submit list to createlist function for tranlation into "epics" and list creation
    results.append(createlist(syms, 'AU', 'Leaders', printonly=printonly))
    
    #Build list of ticker codes from emerging table
    syms = []
    leaders = soup.find('tbody', id='juniors_content')
    for leader in leaders.find_all('tr'):
        try:
            syms.append(asxcodes[leader.find('td').text.strip()])
        except KeyError:
            continue
    #Submit list to createlist function for tranlation into "epics" and list creation
    results.append(createlist(syms, 'AU', 'Emerging', printonly=printonly))

    #Build list of ticker codes from shorts table
    syms = []
    leaders = soup.find('tbody', id='top20content')
    for leader in leaders.find_all('tr'):
        try:
            syms.append(asxcodes[leader.find('td').text.strip()])
        except KeyError:
            continue
    #Submit list to createlist function for tranlation into "epics" and list creation
    results.append(createlist(syms, 'AU', 'Shorts', printonly=printonly))

    #Cycle through various sector lists
    leadercount = 0    
    leaders = soup.find('table', class_='strongsectors_table')
    titles = leaders.find_all('div', class_='subtitle_widget')
    for leader in leaders.find_all('table', class_='subtable'):
        syms = []
        #Build list of ticker codes from sector table
        for ticker in leader.find_all('tr'):
            try:
                syms.append(asxcodes[leader.find('td').text.strip()])
            except KeyError:
                continue
        #Submit list to createlist function for tranlation into "epics" and list creation
        results.append(createlist(syms, 'AU', titles[leadercount].text, printonly=printonly))
        leadercount += 1

    # #Get Suubee google sheets spreadsheet for US Data
    # r = session.get('https://docs.google.com/spreadsheets/d/e/2PACX-1vRLi_7mUvV_EJ3NajuyoaZvOFOQ5Q5jelch39gRm9AFgi-iwGaez_aGHOSLmanU429GKKbB4wm2JelE/pubhtml', headers=headers)

    # #Parse google sheets spreadsheet using Beautiful Soup
    # soup = BeautifulSoup(r.text, 'lxml')

    # leaders = []

    # #Skip first 6 rows then read first column for US Leaders
    # for row in soup.find('table').find('tbody').find_all('tr')[5:]:
        # sym = row.find_all('td')[0].text
        # if (sym[:1] != '*'):
            # leaders.append(sym)

    # shortsyms = []
    # goldsyms = []
    # stage1syms = []
    # shorts = True
    # golds = True
    # goldsblankcount = 0
    # #Skip first 6 rows then read sixth column for US Shorts, US Golds & US Stage One
    # for row in soup.find('table').find('tbody').find_all('tr')[5:]:
        # sym = row.find_all('td')[5].text.strip()
        # if shorts:
            # if sym == '':
                # shorts = False
            # else:
                # shortsyms.append(sym)
        # elif golds:
            # if sym == '':
                # if goldsblankcount > 0:
                    # golds = False
                # goldsblankcount = goldsblankcount + 1
            # elif sym != 'US Gold' and sym != 'Ticker':
                # goldsyms.append(sym)
        # else:
            # if sym != '' and sym != 'Stage One' and sym != 'Ticker':
                # stage1syms.append(sym)

    # #Submit list to createlist function for tranlation into "epics" and list creation
    # results.append(createlist(leaders, 'US', 'US-Leaders', True, printonly=printonly))
    # #Submit list to createlist function for tranlation into "epics" and list creation
    # results.append(createlist(shortsyms, 'US', 'US-Shorts', True, printonly=printonly))

    # #Override Ticker and provide "epic" manually
    # overrides={}
    # overrides['FR'] = 'SA.D.AGSUS.CASH.IP'
    # #Submit list to createlist function for tranlation into "epics" and list creation
    # results.append(createlist(goldsyms, 'US', 'US-Gold', True, overrides, printonly=printonly))
    # #Submit list to createlist function for tranlation into "epics" and list creation
    # results.append(createlist(stage1syms, 'US', 'US-Stage-One', True, printonly=printonly))
	
    # This part for generate HTML for return
    html = ''
    for i in results:
        html += '<h2>' + i + '</br>'

    return html	
    #print(results)

#run()
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)