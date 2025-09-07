import pymysql.cursors
import appsconfig

dba = None

def connectDB():
    global dba
    print("connecting...")
    dba = pymysql.connect(host=appsconfig.DB_SERVER,user=appsconfig.DB_USER,password=appsconfig.DB_PASS,database=appsconfig.DB_INSTANCE )
    return 0
    
    
def disconnectDB():
    global dba
    dba.close()

def getDB():
    connectDB()
    return dba
    
def initialize_db():
    connectDB()
    
def terminate_db():
    dba.close()
    
    

def insert_alert(symbol, exchange, alert_date, freq, sector, industry, alert, alert_price):
    global dba
    
    cursor = dba.cursor()
    if sector is None:
        sector = "N/A"
    if industry is None:
        industry = "N/A"

    try:        
        sqlstmt = "INSERT IGNORE INTO EODALERTS (SYMBOL, EXCHANGE, DATE, FREQ, SECTOR, INDUSTRY, ALERT, STATUS, ALERTPRICE) VALUES ("
            
        sqlstmt += "'"+symbol+"', '"+exchange+"', '"+alert_date.strftime('%Y-%m-%d %H:%M:%S')+"','"+freq+"', '"+sector+"', '"+industry+"', '"+alert+"', 'observe', "+str(alert_price)+")"

        cursor.execute(sqlstmt)     
        
        dba.commit() #commit at end for performance ??
    
    except (pymysql.Error, pymysql.Warning) as e:
        print(e)

    finally:
        cursor.close()
    

def get_all_alerts():
    global dba
    cursor = dba.cursor()

    try:
        
        sqlstmt = "select distinct SYMBOL, ALERT from EODALERTS" 
                
        cursor.execute(sqlstmt)     
        
        results = cursor.fetchall()
        isin_arr = []
        for row in results:
            isin_arr.append(row[0])
            
    except (pymysql.Error, pymysql.Warning) as e:
        print(e)
  
    finally:
        cursor.close() 
    
    return isin_arr
    
