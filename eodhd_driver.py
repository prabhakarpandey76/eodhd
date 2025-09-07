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
sub_exchange = "NASDAQ"
frequency = "m"

PARTIAL_BREAKOUT = 100
ALL_TIME_BREAKOUT = 200

num_of_threads = 3

all_sym_alert =[]

def get_symbol_data(symbol):
    global api_token
    #url = "https://eodhistoricaldata.com/api/eod/"+symbol+"?api_token="+api_token+"&order=d&fmt=json&period=w&from=1995-01-01&function=splitadjusted"
    url = "https://eodhd.com/api/technical/"+symbol+"?fmt=json&order=d&function=splitadjusted&from=1995-01-01&agg_period="+frequency+"&api_token=64dc8ae61f9610.58218286"
    #print(url)
    response = urllib.request.urlopen(url)
    status_code = response.getcode()
    if status_code == 402:
        print("######################################## payment needed :     exit")
        exit(1)
    data = json.loads(response.read())
    #print("data = ", data)
    return data

    #print(data)
    #print(data[0])
    #print(data[0]['date'])
    

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


def detect_breakout_symbol(ohlc1):
    global PARTIAL_BREAKOUT, ALL_TIME_BREAKOUT
    
    i = 1
    prev_high_close = 0
    prev_high_bar = 0
    while (i < len(ohlc1)):
        if(ohlc1[0].CLOSE > ohlc1[i].CLOSE):
            
            if (ohlc1[i].CLOSE > prev_high_close):
                prev_high_close = ohlc1[i].CLOSE
                prev_high_bar = i
            i += 1
        else:
            break
        
    if (i>104):
        if (i<len(ohlc1)):
            #print(ohlc1[0].SYMBOL, " breakout after bars : ", i, " DATE: ", ohlc1[i].PRICE_DATE)
            return PARTIAL_BREAKOUT
        else:
            if(prev_high_bar > 104):
                print(ohlc1[0].SYMBOL, " All time breakout after ", prev_high_bar)
                return ALL_TIME_BREAKOUT
                
    return False


def detect_fibs_symbol(ohlc1):
    
    i = 1

    #print("symbol =",ohlc1[0].SYMBOL, ohlc1[0].PRICE_DATE)
    highest = 0
    lowest = 0
    
    while (i < len(ohlc1)):
        if(ohlc1[i].HIGH > ohlc1[highest].HIGH):
            highest = i
        if(ohlc1[i].LOW <= ohlc1[lowest].LOW):
            lowest = i

        i += 1
    if (highest < lowest):
        level_618 = ohlc1[highest].HIGH - ((ohlc1[highest].HIGH-ohlc1[lowest].LOW) * 0.618)
        #print("highest=", ohlc1[highest].HIGH, "   lowest=",ohlc1[lowest].LOW)
        #print( "61.8 level = ", level_618)
        count_618 = 0
        if (ohlc1[0].LOW <= level_618):
            for i in range(highest):
                if ohlc1[i].LOW <= level_618:
                    count_618 += 1
            if (count_618 < 5):
                #print(ohlc1[0].SYMBOL, " --- hit 61.8 fib level ", "Current bar Low=",ohlc1[0].LOW, " 61.8 level=", level_618, " high swing=", ohlc1[highest].HIGH, " low swing=",ohlc1[lowest].LOW)
                return True

    return False


def breakouts_and_fibs_all():
    #global signal_symbols
    global pathname
    global exchange
    global num_of_threads
    
    thread_count=0

    sym_names = get_X_tickers(exchange)
    print("total number of stocks to process: ", len(sym_names))
    count = 0
    
    pathname = exchange +"/"+str(date.today())+"-"+frequency
    os.makedirs(pathname)
    t = []
    
    for symbol in sym_names:
        
        #if count==500:
        #    break
        time.sleep(0.1)
        
        """
        if exchange == "US" :
            if symbol['Exchange'] != sub_exchange:
                continue
        
        """
        
        count = count+1
        if count%500 == 0:
            print("--------Processed: ", count, " out of total ",len(sym_names), "----------")
            time.sleep(100)
        #print("processing:  "+symbol['Code'])
        ticker_name = symbol['Code']+"."+exchange
        
        if (thread_count < num_of_threads):
            #print("creating new thread: ", thread_count)
            try:
                xxx = threading.Thread(target=process_symbol, args=(symbol, ticker_name,))
                xxx.start()
                t.append(xxx)
            except Exception as e:
                print(e)
                exit(1)

            #process_symbol(symbol, ticker_name)
            
            thread_count += 1    
            
            if thread_count == num_of_threads:
                thread_count = 0
                #join the threads below 
                for i in range(num_of_threads):
                    #print('joining the thread: ', i)
                    t[i].join()
                
                
    for i in range(thread_count):
        #print('joining the thread: ', i)
        t[i].join()
            
    
    create_final_page()


def process_symbol(symbol, ticker_name):
    global pathname, ALL_TIME_BREAKOUT, PARTIAL_BREAKOUT
    
    symbol_data = get_symbol_data(ticker_name)
    #print("symbol data  = ", symbol_data)
    ohlc1 = []
    for each_date in symbol_data:
        od = ohlc.ohlcdata(exchange, symbol['Code'], each_date['date'], "", each_date['open'], each_date['high'], 
        each_date['low'], each_date['close'], "","", each_date['volume'], "", ""  )
            
        #print(od)
        ohlc1.append(od)
        
        if each_date['date'][0:4] == '2005':
            #print("broken out")
            break;


    found_break = detect_breakout_symbol(ohlc1)
    #found_fib = detect_fibs_symbol(ohlc1)
    found_fib = False
    
    if ( (found_break == ALL_TIME_BREAKOUT) or found_fib):
       #signal_symbols.append(ohlc1[0].SYMBOL)
       
       if  symbol_in_alerts(ohlc1[0].SYMBOL) == False:
        create_web_page(ohlc1, pathname, found_break)


def create_web_page(ohlc1, pathname="", found_break=False):
    global signal_symbols
    
    crore = 10000000
    #data = get_fundamental_data(ohlc1[0].SYMBOL)
    data = None
    #print(data)
    
    #market cap
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
        if(exchange == "NSE"):
            market_cap = market_cap/crore
        else:
            market_cap = market_cap/1000000
    except:
        market_cap = 0
    
    try:
        ebitda = int(int(data['Highlights']['EBITDA']))
        if(exchange == "NSE"):
            ebitda = ebitda/crore
        else:
            ebitda = ebitda/1000000
        
    except:
        ebitda = 0
    
    try:
        pe = int(data['Highlights']['PERatio'])
    except:
        pe = 0
    
    try:
        peg = int(data['Highlights']['PEGRatio'])
    except:
        peg = 0
    
    try:
        dividend = int(data['Highlights']['DividendYield'])
    except:
        dividend = 0
    
    try:
        margin = int(data['Highlights']['ProfitMargin'])
    except:
        margin = 0
    
    try:
        roe = int(int(data['Highlights']['ReturnOnEquityTTM']))
    except:
        roe = 0
        
    try:
        sector = data['General']['Sector']
    except:
        sector = "N/A"

    try:
        industry = data['General']['Industry']
    except:
        industry = "N/A"

    try:
        description = data['General']['Description']
    except:
        description = "N/A"

        
    funda_data = {'found_break': found_break, 'marketcap': market_cap, 'ebitda': ebitda, 'pe': pe,
                'peg': peg, 'dividend': dividend, 'margin': margin, 'roe': roe, 'sector': sector, 
                'industry':industry, 'description': description, 'price': ohlc1[0].CLOSE
    }
    
    signal_symbols[ohlc1[0].SYMBOL] = funda_data
    plot_graph(ohlc1, pathname, found_break)
    
    #scrap_screener(ohlc1[0].SYMBOL, pathname)
    

def create_final_page():
    global pathname
    global signal_symbols
    finalfilename = pathname+"/allsym"+".html"
    file1 = open(finalfilename, 'w')
    file1.write("<html><body>")
    uom = "Million"
    if exchange == "NSE":
        uom = "Crores"
    
    i=0;
    
    while (i<2):
        for symbol in signal_symbols.keys():
            funda_data = signal_symbols[symbol]
            
            if (i==0 and funda_data['found_break']== False):
                continue
            elif (i==1 and funda_data['found_break'] == True):
                continue
            filenameimg = symbol+".png"

            file1.write("<div>")
            funda_data = signal_symbols[symbol]
        
            mcap = funda_data['marketcap']
            ebitda = funda_data['ebitda']
            pe = funda_data['pe']
            peg = funda_data['peg']
            dividend = funda_data['dividend']
            margin = funda_data['margin']
            roe = funda_data['roe']
            sector = funda_data['sector']
            industry = funda_data['industry']
            description = funda_data['description']
        
            file1.write("<p><b>"+symbol+" (figures in "+uom+")</b></p>")
        
            file1.write("<table border=\"1\"><tr><td>")
            file1.write("<b>market cap:</b> "+format(mcap, '0.0f')+"</td><td>")
            file1.write("<b>ebitda: </b>"+format(ebitda, '0.0f')+"</td><td>")
            file1.write("<b>pe: </b>"+format(pe, '.1f')+"</td></tr><tr><td>")
            file1.write("<b>peg: </b>"+format(peg, '.2f')+"</td><td>")
            file1.write("<b>dividend: </b>"+format(dividend, '.2f')+" %</td><td>")
            file1.write("<b>margin: </b>"+format(margin, '.2f')+"</td></tr><tr><td>")
            file1.write("<b>roe: </b>"+str(roe)+"</td><td><b>Sector: </b>")
            file1.write(str(sector)+"</td><td><b>Industry:</b> "+str(industry)+"</td></tr><tr><td colspan = \"3\"><b>Description: </b>"+str(description)+"</td></tr></table>")
        
        
            file1.write("<img src=\""+filenameimg+"\"> </img>")

            file1.write("</div>")
            
            alert = "Fib618"
            if funda_data['found_break']:
                alert = "breakout"
            
            db.insert_alert(symbol, exchange, date.today(), frequency, sector, industry, alert, funda_data['price'])
            
        i += 1
        
    file1.write("</body></html>")
    
def scrap_screener(symbol, pathname=""):
    URL = "https://www.screener.in/company/"+symbol+"/" 
 
    page = requests.get(URL)
    
    filename = ""
    if pathname == "":
        filename = symbol+".html"
    else:
        filename = pathname+"/"+symbol+".html"

    #print(page.text)
    file1 = open(filename, 'w')
    file1.write(page.text)
    file1.close()
 

def plot_graph(ohlc1, pathname="", found_break=False):
    arr1 = ohlc_to_col(ohlc1)
    
    df = pd.DataFrame(arr1)
    
    #print(df.to_string())
    
    fig = go.Figure(data=go.Ohlc(x=df['date'], 
                             open=df['open'], 
                             high=df['high'], 
                             low=df['low'], 
                             close=df['close'])) 
    update_text = ": Fibonacci \n"
    if found_break:
        update_text = ": Breakout \n"
    fig.update_layout(title_text=ohlc1[0].SYMBOL+update_text)    
    fig.update_layout(width=1500, height=700)
    fig.update(layout_xaxis_rangeslider_visible=False)
    
    if (pathname != ""):
        io.write_image(fig, pathname+"/"+ohlc1[0].SYMBOL+".png", "png")
    else:
        io.write_image(fig, ohlc1[0].SYMBOL+".png", "png")
    #print(fig)


def get_fundamental_data(symbol):
    global api_token
    ticker = symbol+"."+exchange
    
    url = "https://eodhd.com/api/fundamentals/"+ticker+"?api_token="+api_token
    
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data

def breakouts_and_fibs_specificstock(stock_code):
    
    global exchange
    
    ticker_name = stock_code+"."+exchange
    symbol_data = get_symbol_data(ticker_name)
    #print(symbol_data)
    ohlc1 = []
    
    for each_date in symbol_data:
        od = ohlc.ohlcdata(exchange, stock_code, each_date['date'], "", each_date['open'], each_date['high'], 
        each_date['low'], each_date['close'], "", "", each_date['volume'], "", ""  )
            
        #print(od)
            
        ohlc1.append(od)
        #print(each_date['date'])
            
    detect_breakout_symbol(ohlc1)
    detect_fibs_symbol(ohlc1)
    create_web_page(ohlc1)

    
    
def ohlc_to_col(ohlc1):
    price_date = []
    price_open = []
    price_high = []
    price_low = []
    price_close = []
    price_vol = []
    
    for i in range(len(ohlc1)):
        price_date.append(ohlc1[i].PRICE_DATE)
        price_open.append(ohlc1[i].OPEN)
        price_high.append(ohlc1[i].HIGH)
        price_low.append(ohlc1[i].LOW)
        price_close.append(ohlc1[i].CLOSE)
        price_vol.append(ohlc1[i].TRADED_QUANTITY)
                
    
    dict1 = {'date': price_date, 'open': price_open, 'high': price_high, 'low': price_low, 'close': price_close, 'volume': price_vol}
    return dict1

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

    breakouts_and_fibs_all()
    #breakouts_and_fibs_specificstock("INDIAMART")
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    end_prog()
    
    print("program ended: ",current_time)


