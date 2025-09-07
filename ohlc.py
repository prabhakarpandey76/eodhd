
class ohlcdata:
    EXCHANGE = ""
    SYMBOL = ""
    PRICE_DATE = ""
    ISIN = ""
    OPEN = 0.0
    HIGH = 0.0
    LOW = 0.0
    CLOSE = 0.0
    LAST = 0.0
    PREVCLOSE = 0.0 
    TRADED_QUANTITY = 0
    TRADED_VALUE = 0.0 
    TOTAL_TRADES = 0
    
    def __init__(self, exc, sym, dt, isin, op, hi, lo, cl, la, pr, tq, tv, tt):
        self.EXCHANGE = exc
        self.SYMBOL = sym
        self.PRICE_DATE = dt
        self.ISIN = isin
        self.OPEN = op
        self.HIGH = hi
        self.LOW = lo
        self.CLOSE = cl
        self.LAST = la
        self.PREVCLOSE = pr 
        self.TRADED_QUANTITY = tq
        self.TRADED_VALUE = tv
        self.TOTAL_TRADES = tt
        
    def __str__(self):
        str1 = "EXCHANGE = "+ self.EXCHANGE
        str1 += " SYMBOL = "+self.SYMBOL
        str1 += " PRICE_DATE = "+ str(self.PRICE_DATE)
        str1 += " ISIN = "+ self.ISIN
        str1 += " OPEN = "+ str(self.OPEN)
        str1 += " HIGH = "+ str(self.HIGH)
        str1 += " LOW = "+str(self.LOW)
        str1 += " CLOSE = "+str(self.CLOSE)
        str1 += " LAST = "+str(self.LAST)
        str1 += " PREVCLOSE = "+str(self.PREVCLOSE)
        str1 += " TRADED_QUANTITY = "+str(self.TRADED_QUANTITY)
        str1 += " TRADED_VALUE = "+str(self.TRADED_VALUE)
        str1 += " TOTAL_TRADES = "+str(self.TOTAL_TRADES)
        return str1
    
