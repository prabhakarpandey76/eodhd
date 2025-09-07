from eodhd import APIClient
import urllib, json
import ohlc
from datetime import datetime
from datetime import date
import time

import pandas as pd
import plotly.graph_objects as go 
import plotly.io as io
import numpy as np

import os

from bs4 import BeautifulSoup as bs 
import requests 

import threading

import db

#IMPORTANT NOTE : run from command prompt as python3.8 eodhd_driver.py

signal_symbols = {}
pathname = ""

api_token =  "64dc8ae61f9610.58218286"
US_exchange = "US"
India_exchange = "NSE"
cryptos = "CC"
exchange = India_exchange
#exchange = US_exchange
#exchange = US_exchange
sub_exchange = "NASDAQ"
frequency = "m"

num_of_threads = 5 

all_sym_alert =[]

def get_symbol_data(symbol):
    global api_token
    #url = "https://eodhistoricaldata.com/api/eod/"+symbol+"?api_token="+api_token+"&order=d&fmt=json&period=w&from=1995-01-01&function=splitadjusted"
    url = "https://eodhd.com/api/technical/"+symbol+"?fmt=json&order=d&function=splitadjusted&from=1995-01-01&agg_period="+frequency+"&api_token=64dc8ae61f9610.58218286"
    #print(url)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    #print(data)
    #print(data[0])
    #print(data[0]['date'])
    return(data)


def print_exchanges():
    global api_token
    print("Printing the exchanges list....")
    url = "https://eodhistoricaldata.com/api/exchanges-list/?api_token="+api_token
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    print(data)

def get_X_tickers(X):
    global api_token, US_exchange
    
    #print("Printing the exchanges list....")
    url = "https://eodhistoricaldata.com/api/exchange-symbol-list/"+X+"?api_token="+api_token+"&fmt=json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    #print(data)
    return data


def funda_screener():
    #global signal_symbols
    global pathname
    global exchange
    global num_of_threads
    
    thread_count=0

    sym_names = get_X_tickers(exchange)
    print("total number of stocks to process: ", len(sym_names))
    count = 0
    
    t = []
    
    for symbol in sym_names:
        
        #if count==10:
        #    break
        
        if exchange == "US" :
            if symbol['Exchange'] != sub_exchange:
                continue
        count = count+1
        if count%500 == 0:
            print("--------Processed: ", count, " out of total ",len(sym_names), "----------")
            time.sleep(30)
        #print("processing:  "+symbol['Code'])
        ticker_name = symbol['Code']+"."+exchange
        
        if (thread_count < num_of_threads):
            #print("creating new thread: ", thread_count)
            xxx = threading.Thread(target=process_symbol, args=(symbol, ticker_name,))
            xxx.start()
            t.append(xxx)

            #process_symbol(symbol, ticker_name)
            
            thread_count += 1    
            
            if thread_count == 5:
                thread_count = 0
                #join the threads below 
                for i in range(num_of_threads):
                    #print('joining the thread: ', i)
                    t[i].join()
                
                
    for i in range(thread_count):
        #print('joining the thread: ', i)
        t[i].join()
    
    #print_funda_report()
    

def print_funda_report():
    global signal_symbols, exchange
    #print(signal_symbols)
    filename = "funda_screener_"+exchange+"-"+str(date.today())+"-"+datetime.now().strftime("%H-%M-%S")+".csv"
    
    try:
        file1 = open(filename, 'w')
        
        file1.write("SECTOR, INDUSTRY, SYMBOL, MARKETCAP, EBITDA,PE, PEG, MARGIN, DIVIDEND, ROE")
        file1.write("\n")
        
        copy_symbols = dict(signal_symbols)
        
        symkeys = copy_symbols.keys()

        for sym in symkeys:
            print("came in: ", sym)
            #print(sym, copy_symbols[sym])
            tempdata = copy_symbols[sym]
            
            s_sector = "None"
            if tempdata['sector'] is not None:
                s_sector = tempdata['sector']

            s_industry = "None"            
            if tempdata['industry'] is not None:
                s_industry = tempdata['industry']
                
            s_marketcap = "None"
            if tempdata['marketcap'] is not None:
                s_marketcap = str(tempdata['marketcap'])
                
            s_ebitda = "None"
            if tempdata['ebitda'] is not None:
                s_ebitda = str(tempdata['ebitda'])
            
            s_pe = "None"
            if tempdata['pe'] is not None:
                s_pe = str(tempdata['pe'])

            s_peg = "None"
            if tempdata['peg'] is not None:
                s_peg = str(tempdata['peg'])

            s_margin = "margin"
            if tempdata['margin'] is not None:
                s_margin = str(tempdata['margin'])

            s_dividend = "None"
            if tempdata['dividend'] is not None:
                s_dividend = str(tempdata['dividend'])

            s_roe = "None"
            if tempdata['roe'] is not None:
                s_roe = str(tempdata['roe'])
            
            
            file1.write(s_sector+","+s_industry+","+sym+","+s_marketcap+","+s_ebitda+","+s_pe+","
            +s_peg+","+s_margin+","+s_dividend+","+s_roe)
            
            file1.write("\n")
            
    except Exception as e:
        print(e)
        print("Error in creating the report")
            
    file1.close()
    
def process_symbol(symbol, ticker_name):
    global funda_data
    #print("process symbol: ", ticker_name)
    data = get_fundamental_data(symbol['Code'])
    
    market_cap = 0
    ebitda = 0
    pe = 0
    peg = 0
    dividend = 0
    margin = 0
    roe = 0
    sector = "N/A"
    industry = "N/A"
    description = "N/A"
    
    try:
        market_cap = int(int(data['Highlights']['MarketCapitalization']))
    except:
        market_cap = "Not Available"
    
    try:
        ebitda = int(int(data['Highlights']['EBITDA']))
    except:
        ebitda = "Not Available"
    
    try:
        pe = int(data['Highlights']['PERatio'])
    except:
        pe = "Not Available"
    
    try:
        peg = float(data['Highlights']['PEGRatio'])
    except:
        peg = "Not Available"
    
    try:
        dividend = float(data['Highlights']['DividendYield'])
    except:
        dividend = "Not Available"
    
    try:
        margin = float(data['Highlights']['ProfitMargin'])
    except:
        margin = "Not Available"
    
    try:
        roe = int(int(data['Highlights']['ReturnOnEquityTTM']))
    except:
        roe = "Not Available"
        
    try:
        sector = data['General']['Sector']
    except:
        sector = "Not Available"

    try:
        industry = data['General']['Industry']
    except:
        industry = "Not Available"

    try:
        description = data['General']['Description']
    except:
        description = "Not Available"

    funda_data = {'marketcap': market_cap, 'ebitda': ebitda, 'pe': pe,
                'peg': peg, 'dividend': dividend, 'margin': margin, 'roe': roe, 'sector': sector, 
                'industry':industry, 'description': description }
    
    #print(symbol['Code'], data['Highlights']['PEGRatio'])
    if (run_screener(funda_data)):
        #print(signal_symbols)
        signal_symbols[symbol['Code']] = funda_data
        #print(symbol['Code'], funda_data)


def run_screener(funda_data):
    
    return True
    
    try:
        if funda_data['peg'] < 1:
            return True
    except:
        return False
            
    return False

def get_fundamental_data(symbol):
    global api_token
    ticker = symbol+"."+exchange
    
    url = "https://eodhd.com/api/fundamentals/"+ticker+"?api_token="+api_token
    
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data

def init_prog():
    global all_sym_alert
    db.connectDB()
    all_sym_alert = db.get_all_alerts()
    #print(all_sym_alert)
    
def end_prog():
    print("disconnecting DB...")
    db.terminate_db()

def symbol_in_alerts(symbol):
    global all_sym_alert
    
    for item in all_sym_alert:
        if item == symbol:
            return True
    
    return False

if __name__ == "__main__":
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("program starting: ", current_time)
    
    init_prog()

    funda_screener()
    
    print_funda_report()

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    end_prog()
    
    print("program ended: ",current_time)


