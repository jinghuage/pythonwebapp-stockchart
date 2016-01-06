import datetime
import sqlite3
import matplotlib.dates as mdates
import sys


# internal packages
import database_table
import quotes



def create_tables():
    conn = sqlite3.connect('my_db1.db')
    cursor = conn.cursor()

    # Timestamp is epoch integer
    #table_fields = {'Timestamp':'FLOAT',  #epoch timestamp and string date merged into matplotlib date in float ordinal format
    #                 'close': 'FLOAT', 
    #                 'high':'FLOAT', 
    #                 'low': 'FLOAT', 
    #                 'open': 'FLOAT', 
    #                 'volume': 'FLOAT'}
    #columns = ','.join(key for key in table_fields)
    #print columns
    #schema = ','.join([' '.join([key,dtype]) for key,dtype in table_fields.iteritems()])
    #print schema

    
    schema = 'Timestamp FLOAT PRIMARY KEY,close FLOAT,high FLOAT,low FLOAT,open FLOAT,volume FLOAT'
    
    Tdaily = database_table.table('daily', conn)
    Tdaily.create(schema)
    T1min = database_table.table('onemin', conn)
    T1min.create(schema)
    T5min = database_table.table('fivemin', conn)
    T5min.create(schema)


    # Get List of Tables:      
    tableListQuery = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY Name"
    cursor.execute(tableListQuery)
    tables = map(lambda t: t[0], cursor.fetchall())
    print tables
    
    return Tdaily, T1min, T5min




def init_table(ticker, table, timespan):
    print '--'
    funcname = sys._getframe().f_code.co_name
    print ','.join(['--', funcname, ticker, table.name, timespan])

    #timespan = '1y' #'6m' #'1d', '1y'
    if table.name != 'daily':
        columns, data = quotes.get_quote_intraday(ticker, timespan)
        table.fill(data)
    else:
        #data = quotes.get_quote_daily_matplotlib(ticker)
        data = quotes.get_quote_daily_pandas(ticker)

        #
        # data from matplotlib: a numpy record array with fields: date, open, high, low, close, volume, adj_close
        # schema = 'Timestamp FLOAT PRIMARY KEY,close FLOAT,high FLOAT,low FLOAT,open FLOAT,volume FLOAT'
        #DCHLOV = zip(mdates.date2num(data.date), 
        #        data.close, data.high, data.low, data.open, data.volume)

        #print DCHLOV[:5]


        # data from pandas: index:pandas.DatetimeIndex, 
        # columns: "Open", "High", "Low", "Close", "Volume", "Adj Close"
        # convert from pandas.DatetimeIndex to numpy.datetime64, to datetime
        # http://stackoverflow.com/questions/13703720/converting-between-datetime-timestamp-and-datetime64
        DCHLOV = zip(mdates.date2num(data.index.to_pydatetime()), 
               data.Close, data.High, data.Low, data.Open, data.Volume)
        table.fill(DCHLOV)
    
    print 'first and last timestamp of table:'
    print table.get_first_ts()
    print table.get_last_ts()


def update_table(ticker, table, od_today, limitdays):
    print '--'
    funcname = sys._getframe().f_code.co_name
    print ','.join(map(str, ['--', funcname, ticker, table.name]))



    od_first, od_last = table.get_timestamp_range()        
    od_limit = int(od_today - limitdays)
    print ','.join(map(str,['f-l-to-li',od_first, od_last, od_today, od_limit]))


    # fill until today
    days = int(od_today - od_last) + 2 # explain why +2 here
    months = days / 30 + 1
    #print ','.join(map(str, ['days', days, 'months', months]));

    timespan = None

    if table.name == 'daily':
        timespan = str(months)+'m'
    elif table.name == 'fivemin':
        timespan = str(days)+'d'
    elif table.name == 'onemin':
        timespan = '1d'

    if timespan:
        #print timespan
        columns, data = quotes.get_quote_intraday(ticker, timespan)
        table.fill(data)


    # clamp up to limits
    if od_first < od_limit:
        table.clampto(od_limit)


def check_status(tables):
    import pytz
    est=pytz.timezone('US/Eastern')

    for table in tables:
        print '--'
        print '--', table.name, ' status:'
        st1_od = table.get_first_ts()
        st2_od = table.get_last_ts()
        if st1_od:
            print '--', st1_od, mdates.num2date(st1_od, tz=est)
            print '--', st2_od, mdates.num2date(st2_od, tz=est)
        print '-- num of rows: ',table.get_num_rows()
        print '--'




def collect_data(tables, ticker, od_today, init=False):
    
    init_timespan = {'daily': '5y', 
                     'onemin': '1d',
                     'fivemin': '21d'}

    limit_days = {'daily': 1800,
                  'onemin': 5,
                  'fivemin': 180}


    for table in tables: 
        if init:
            if not table.isempty():
                table.clear()
            init_table(ticker, table, init_timespan[table.name])
        else: 
            update_table(ticker, table, od_today, limit_days[table.name])
    

    
    
            

if __name__ == '__main__':
    ticker = 'SPY'

    format = "%a %b %d %H:%M:%S %Y"
    today = datetime.datetime.today()
    s = today.strftime(format)
    print 'strftime:', s

    #d = datetime.datetime.strptime(s, format)
    #print 'strptime:', d.strftime(format)

    od_today = mdates.date2num(today)
    print od_today

    #Tdaily, T1min, T5min = create_tables()
    #print Tdaily.get_columns()
    #print T1min.get_columns()
    #print T5min.get_columns()

    tables = create_tables()
    check_status(tables)
    collect_data(tables, ticker, od_today, init=True)#, init=True)
    check_status(tables)

    #update_table(ticker, T5min, od_today, 180)
    #check_status((T5min,))
