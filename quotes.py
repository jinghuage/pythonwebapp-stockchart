'''
apis: 

1. yahoo intraday range='1d': 1min (delayed 15min I think) 
    YAHOO_INTRADAY = "http://chartapi.finance.yahoo.com/instrument/1.0/%s/chartdata;type=quote;range=%s/csv"
    
1. yahoo intraday range='2-30d': 5min
1. yahoo intraday range='>30d': daily
1. yahoo realtime: 1min. YAHOO_WEBSERVICE="http://finance.yahoo.com/webservice/v1/symbols/%s/quote?format=json"

1. pandas data api: daily until yesterday 
    pandas.io.data.DataReader(symbol, "yahoo", start="2015/3/1")
    
1. yahoo today daily: YAHOO_TODAY="http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=sd1ohgl1vl1"

database tables: 

1. daily table: useful when plot multiple month or years data 
1. realtime 1min table: yahoo realtime, only hold up to one day's data
1. 5min table: useful when plot data 2day to 2month for example -- hold up to 2 month's data

user interaction buttons: 

1. today : start up to time when the app is launched. afterwards click to update to current time(minute)
1. one week: up to one week 5min data
1. one month: up to one month 5min data
1. three month : up to 3 month 5min data
1. six month: up to 6 month daily data
1. one year : up to 1 year daily data

data collecting schedule: 

1. get_today_1min() : when called, use yahoo intraday 1d range to get 1min data, save new timestamps into today 1min table
1. get_realtime_1min(): call every minute since app started, use yahoo realtime to get 1min data, insert into realtime 1min table
1. get_30day_5min(): when called, use yahoo intraday 30d range to get 5min data, save new timestamps into 5min table
1. get_1day_5min(): called daily at end of day, add to 5min table
1. get_1year_daily(): when called, get 1year daily data, insert into daily table
1. get_today_daily(): called daily at end of day, add to daily table
'''

import datetime
import urllib2
import csv
import re
import matplotlib.dates as mdates
import pandas as pd
import pandas.io.data as web

import matplotlib.finance as finance
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.mlab as mlab


YAHOO_INTRADAY = "http://chartapi.finance.yahoo.com/instrument/1.0/%s/chartdata;type=quote;range=%s/csv"


def get_quote_intraday(symbol, timerange):
    columnarr = []
    filename = ''
    f=None
    
    st1str = ''
    st2str = ''
    datalist = []
    daily = False
    
    url = YAHOO_INTRADAY % (symbol, timerange)
    print url
    
    response = urllib2.urlopen(url)
    reader = csv.reader(response, delimiter=",", quotechar='"')
    for row in reader:
        #print row
        if 'Timestamp:' in row[0]:
            daily = False
            st1 = map(int, re.findall(r'\d+', row[0]))[0]
            st2 = map(int, re.findall(r'\d+', row[1]))[0]
            #print st1, st2
            #print pd.to_datetime([st1, st2], unit='s')
            st1str = datetime.datetime.fromtimestamp(st1).strftime('%Y-%m-%d')#-%H:%M:%S')
            st2str = datetime.datetime.fromtimestamp(st2).strftime('%Y-%m-%d')#-%H:%M:%S')
        elif 'last-trade' in row[0]:
            daily = True
            st2str = re.findall(r'\d+', row[0])[0]
            #print mdates.date2num(pd.to_datetime(st2str, format='%Y%m%d'))
            #print st2str
        elif daily and ('labels' in row[0]):
            st1str = re.findall(r'\d+', row[0])[0]
            #print mdates.date2num(pd.to_datetime(st1str, format='%Y%m%d'))
            #print st1str
        elif 'values:' in row[0]:
            row[0] = row[0].replace('values:','')
            columnarr = row
            #row[0] = re.sub('\s+', ' ', row[0])
            if st1str == st2str:
                filename = symbol+'--'+st1str+'.csv'
            else:
                filename = symbol+'--'+st1str+'--'+st2str+'.csv'
            f=open(filename,'w')
            print filename+' opened for write'
            f.write(','.join(row) + '\n')
        elif row[0].isdigit():
            f.write(','.join(row) + '\n')
            #od = 0.0
            if daily:
                row[0] = mdates.date2num(pd.to_datetime(row[0], format='%Y%m%d'))
            else:
                #od = mdates.date2num(datetime.datetime.utcfromtimestamp(int(row[0])))
                row[0] = mdates.date2num(pd.to_datetime(int(row[0]), unit='s'))
            #print od
            row = map(float, row)   
            #print row
            datalist.append(row)
    f.close()
    print filename+' closed'
    #return columnarr
    return columnarr, datalist


YAHOO_TODAY="http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=sd1ohgl1vl1"

'''
"Date","Open", "High", "Low", "Close", "Volume", "Adj Close"
"Timestamp","close', 'high', 'low', 'open', 'volume'
'''

def get_quote_today(symbol):
    response = urllib2.urlopen(YAHOO_TODAY % symbol)
    reader = csv.reader(response, delimiter=",", quotechar='"')
    for row in reader:
        print row
        if row[0] == symbol:
            date = row[1]
            od = mdates.date2num(pd.to_datetime(date, format='%m/%d/%Y'))
            o = float(row[2])
            h = float(row[3])
            l = float(row[4])
            c = float(row[5])
            v = float(row[6])
            return [od, c, h, l, o, v]


import datetime
def get_quote_daily_pandas(symbol, timerange, save_csv=False):
    print "get_quote_daily_pandas()"

    if len(timerange) == 2:
        start = timerange[0]
        end = timerange[1]
    else:
        start = datetime.datetime(2006, 1, 1)
        end = datetime.datetime.today()

    print "reading data range:", start, end
    history = web.DataReader(symbol, "yahoo", start, end)

    # append today's quote
    # today = datetime.date.today()
    # df = pandas.DataFrame(index=pandas.DatetimeIndex(start=today, end=today, freq="D"),
    #                   columns=["Open", "High", "Low", "Close", "Volume", "Adj Close"],
    #                   dtype=float)

    # row = get_quote_today(symbol)
    # df.ix[0] = map(float, row[2:])

    # history = history.append(df)

    # print "today is %s" % today
    # print history.tail(2)

    if save_csv:
        st1str = timerange[0].strftime('%Y-%m-%d')
        st2str = timerange[1].strftime('%Y-%m-%d')
        filename = symbol+'--'+st1str+'--'+st2str+'.csv'
        history.to_csv(filename, 
                       sep=',', #'\t', 
                       encoding='utf-8')

        print filename, 'saved'

    print history.tail(2)
    return history


def get_quote_daily_matplotlib(ticker):

    startdate = datetime.date(2006, 1, 1)
    today = enddate = datetime.date.today()
    #ticker = 'SPY'


    fh = finance.fetch_historical_yahoo(ticker, startdate, enddate)
    # a numpy record array with fields: date, open, high, low, close, volume, adj_close

    r = mlab.csv2rec(fh)
    fh.close()
    r.sort()
    return r




YAHOO_WEBSERVICE="http://finance.yahoo.com/webservice/v1/symbols/%s/quote?format=json"

def get_quote_now(symbol):
    response = urllib2.urlopen(YAHOO_WEBSERVICE % symbol)
    quote = response.read()

    quoteobj = byteify(json.loads(quote))


    resources = quoteobj['list']['resources']
    for r in resources:
        fields = r['resource']['fields']
        symbol = fields['symbol']

        timestamp = fields['utctime']
        t = datetime.strptime(timestamp,'%Y-%m-%dT%H:%M:%S+0000')
        t = t.replace(tzinfo=GMT)
        tscst = t.astimezone(CST).strftime('%m/%d/%Y %H:%M:%S %Z')
        print tscst

        od = mdates.date2num(t)
        c = fields['price']
        return [od, c]


import os

def get_quote_csv(symbol, timerange):
    '''
    symbol: ticker
    timerange: array of datetime.date objects
    return: pandas dataframe 
    '''

    today_str = datetime.date.today().strftime('%Y-%m-%d')
    st1str = ''
    st2str = ''
    filename = ''
    #columns = ['Timestamp', 'close', 'high', 'low', 'open', 'volume']
    columns=["Timestamp", "Open", "High", "Low", "Close", "Volume", "Adj Close"]

    if len(timerange) == 1: 
        st1str = timerange[0].strftime('%Y-%m-%d')
        filename = symbol + '--' + st1str + '.csv'
    else:
        st1str = timerange[0].strftime('%Y-%m-%d')
        st2str = timerange[1].strftime('%Y-%m-%d')
        filename = symbol+'--'+st1str+'--'+st2str+'.csv'


    print filename

    # if file doesn't already exist
    if not os.path.isfile(filename):
        print filename + ' does not exist'
        return None

    #read from file -- maybe read from a database is better later......
    data = pd.read_csv(filename,
                       skiprows=1, names=columns,
                       index_col='Timestamp', 
                       parse_dates = ["Timestamp"]
                      )

    #data.head()
    #data.index = pd.to_datetime(data.index, unit='s')
    #data.index = data.index.tz_localize('UTC').tz_convert('US/Eastern')

    #data['Timestamp'] = pd.to_datetime(data.Timestamp, unit='s')#.tz_localize('UTC').tz_convert('US/Eastern')
    #data['Timestamp'] = map(mdates.date2num, data.Timestamp)

    #data = data.asfreq('15Min', method='pad')
    #data = df.resample('1min', how='ohlc')
    #data = data.asfreq('BH', method='pad')

    # convert the datetime64 column in the dataframe to 'float days'
    #data['Date'] = mdates.date2num(data.index) #pyformat
    #data['Timestamp'] = mdates.date2num(data.index.to_pydatetime()) #pandas datetime64 format

    print data.tail(2)
    return data



def get_quote_database(table, symbol, timerange):
    '''
    table: sqlite3 database table object
    database primary key: date in mdates ordinal format
    return: pandas dataframe
    '''

    selection = True

    if len(timerange) == 1:
        od1 = int(mdates.date2num(timerange[0]))
        od2 = od1+1
    elif len(timerange) == 2:
        od1 = int(mdates.date2num(timerange[0]))
        od2 = int(mdates.date2num(timerange[1])) + 1


    print 'request range:', [od1, od2]

    ts1, ts2 = table.get_timestamp_range()
    print 'available data range: ', [ts1, ts2]


    if ts1 and ts2:
        if (od2<ts1) or (od1>ts2):
            selection = False

    if selection is True:
        data = table.to_dataframe([od1, od2])
        print data.head()
        return data
    else:
        print "no selection available"
        return pd.DataFrame({})



# play with datetime: https://pymotw.com/2/datetime/
def play_with_datetime():

    today = datetime.date.today()
    print 'ctime:', today.ctime()
    print 'tuple:', today.timetuple()
    print 'ordinal:', today.toordinal()
    print 'Year:', today.year
    print 'Mon :', today.month
    print 'Day :', today.day

    one_day = datetime.timedelta(days=1)
    print 'One day  :', one_day
    one_week = datetime.timedelta(weeks=1)

    yesterday = today - one_day
    print 'Yesterday:', yesterday

    tomorrow = today + one_day
    print 'Tomorrow :', tomorrow
    print 'tomorrow - yesterday:', tomorrow - yesterday
    print 'yesterday - tomorrow:', yesterday - tomorrow

    today_o = today.toordinal()
    
    datetime.date.fromordinal(o)


if __name__ == '__main__':
    symbol = 'AAPL'
    startstr = '20060101'
    st1str = '20150801'
    st2str = '20151202'
    singledaystr = '20151007'
    format = '%Y%m%d'

    start = pd.to_datetime(startstr, format)
    st1 = pd.to_datetime(st1str, format)
    st2 = datetime.datetime.strptime(st2str, format) #both works
    sd = datetime.datetime.strptime(singledaystr, format)
    today = datetime.datetime.today()
    print st1, st2, sd

    timerange = [start, today]
    get_quote_daily_pandas(symbol, timerange, save_csv=True)
    alldata = get_quote_csv(symbol, timerange)

    slicedata = alldata[st1:st2]
    print slicedata.head(2)
