
import datetime
import urllib2
import csv
import re
import pandas as pd
import pandas.io.data
from pandas.stats.moments import rolling_mean
import matplotlib.dates as mdates
import numpy as np
import matplotlib.pyplot as plt
import datetime

from pytz import timezone
import pytz
import mpld3
from matplotlib.finance import candlestick
import os.path
import mpld3plugins

import sqlite3
import database_table 
import quotes

import stock_graph


# helper functions

def get_all_days(dd):
    ndays = np.unique(np.trunc(dd), return_index=True)
    return ndays


def get_xdays(dates, ndays):
    xdays =  []
    xvalues = []
    dnum = len(ndays[0])

    step = 1
    xnum = dnum-1

    if dnum > 21:
        step = dnum / 21
        xnum = (dnum-1) / step

    #xnum = dnum / step

    for n in np.arange(xnum+1):
        dt = dates[ndays[1]][n*step]
        #dt = mdates.num2date(date_od) #tz=tz
        dtid = ndays[1][n*step]
        xdays.append(datetime.date.isoformat(dt))
        xvalues.append(dtid)

    # if n*step < dnum:
    #     dt = dates[ndays[1]][dnum-1]
    #     dtid = ndays[1][dnum-1]
    #     xdays.append(datetime.date.isoformat(dt))
    #     xvalues.append(dtid)

    return xdays, xvalues



class graph:

    def __init__(self):
        self.alldata = None
        self.slicedata = None
        self.info = {}
        self.info['symbol'] = None
        self.info['timerange'] = []
        self.figlayout = {}
        self.figlayout['main'] = {}
        self.figlayout['addon'] = {}
        self.figlayout['inchart'] = {}
        self.figlayout['size'] = ()
        self.fig = None
        self.axes = []
        self.axtop = 0


    #-----------------------------------------------------------------------------
    # config
    #-----------------------------------------------------------------------------

    def update_config_info(self, **kargs):
        print '***'
        print 'graph.update_config_info()', kargs
        print '***'

        for key, value in kargs.items():
            if key == 'timerange':
                value = map(lambda x: datetime.datetime.today() if x =='today' else pd.to_datetime(x, '%Y-%m-%d'), value)

            self.info[key] = value                
                    

    def update_config_fig(self, **kargs):
        print '***'
        print 'graph.update_config_fig()', kargs
        print '***'

        for key, value in kargs.items():
            if key == 'inchart_id':
                id = int(value[0])
                self.figlayout['inchart']['name'][id] = value[1]
            elif key == 'addon_id':
                id = int(value[0])
                self.figlayout['addon']['name'][id] = value[1]
            else:
                self.figlayout[key]['name'] = value

            if 'addon' in key:
                #print self.figlayout['addon']
                self.update_figlayout()


    def update_figlayout(self):
        print '--'
        print 'graph.update_figlayout()'

        addons = self.figlayout['addon']['name']

        left,width=0.1, 0.8
        h, h1, h2, h3 = 0, 0, 0, 0
        b = 0.1
        figw, figh = 11, 8

        if addons[1] == 'None' and addons[2] == 'None': 
            h = 0.8
            h1 = 0.15
            b = 0.12
            figh = 8
        elif addons[1] == 'None' or addons[2] == 'None': 
            h = 0.62
            h1 = 0.1
            h2 = 0.2
            b = 0.11
            figh = 9
        else: 
            h = 0.55
            h1 = 0.07
            h2 = 0.15
            h3 = 0.15
            b = 0.1
            figh = 10

        rect = [left, b, width, h]
        rect1 = [left, b, width, h1]
        rect2 = [left, b+h, width, h2]
        rect3 = [left, b+h+h2, width, h3]

        self.figlayout['main']['rect'] = rect
 
        addonrect= [[],[],[]]
        if addons[0] != 'None':
            addonrect[0] = rect1

        if addons[1] != 'None':
            addonrect[1] = rect2
                
        if addons[2] != 'None':
            if addons[1] == 'None':
                addonrect[2] = rect2
            else:
                addonrect[2] = rect3
            
        self.figlayout['addon']['rect'] = addonrect
        self.figlayout['size'] = (figw, figh)
        print "graph.figlayout=", self.figlayout


    #-----------------------------------------------------------------------------
    # data
    #-----------------------------------------------------------------------------

    def init_data(self):
        print '--'
        print 'graph.init_data()'

        self.alldata = quotes.get_quote_daily_pandas(self.info['symbol'], self.info['timerange'])

        #for local testing
        #self.alldata = quotes.get_quote_csv(self.info['symbol'], self.info['timerange'])

        stock_graph.pre_compute_indicators(self.alldata)



    def slice_data(self):
        print '--'
        print 'graph.slice_data()', self.info['timerange']


        one_day = datetime.timedelta(days=1)
        st1 = self.info['timerange'][0] - one_day
        st2 = self.info['timerange'][1] + one_day


        self.slicedata = self.alldata[st1:st2]


    def update_indicators(self):
        print '--'
        print 'graph.update_indicators()'
        
        incharts = self.figlayout['inchart']['name']
        for inc in incharts:
            stock_graph.compute_indicator(self.alldata, inc)

        addons = self.figlayout['addon']['name']
        for ado in addons:
            stock_graph.compute_indicator(self.alldata, ado)


        print self.alldata.columns


    #-----------------------------------------------------------------------------
    # plotting
    #-----------------------------------------------------------------------------

    def create_fig_axes(self):
        print '--'
        print 'graph.create_fig_axes()'


        if self.fig: 
            plt.close()
        self.fig = plt.figure(figsize=self.figlayout['size'])
        self.axes = []

        axescolor = '#f6f6f6'  # the axes background color

        ax = self.fig.add_axes(self.figlayout['main']['rect'], axisbg=axescolor)  # left, bottom, width, height
        self.axes.append(ax)
        self.axtop = 0

        addonrect = self.figlayout['addon']['rect']
        addonname = self.figlayout['addon']['name']
        addonlen = len(addonrect)
        for i in range(addonlen):
            arect = addonrect[i]
            aname = addonname[i]
            if aname != 'None':
                #print "create fig axes for ", arect, aname
                self.axes.append(self.fig.add_axes(arect, axisbg=axescolor, sharex=ax))
            else:
                self.axes.append(None)

        if self.axes[3] != None:
            self.axtop = 3
        elif self.axes[2] != None:
            self.axtop = 2


        # customization of the axis
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.spines['left'].set_linewidth(2)
        ax.spines['bottom'].set_linewidth(2)

        ax.set_ylabel('Quote ($)', size=20)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        ax.tick_params(axis='both', direction='out', width=2, length=8,
                   labelsize=12, pad=8)


    def reset_xticks_date(self):
        '''
        Use mpld3 plugins to fix the chart artifacts introduced by mplexportor
        '''

        print '--'
        print 'graph.reset_xticks_date()'


        data = self.slicedata

        # set the ticks of the x axis only when starting a new day
        # use the helper functions to get new days and generate x tick labels
        dd = mdates.date2num(data.index.to_pydatetime())
        ndays = get_all_days(dd)
        xdays,xvalues = get_xdays(data.index.to_pydatetime(), ndays) #, est)
        #print xdays, xvalues

        ax = self.axes[0]
        ax.set_xticks(xvalues)#Date[ndays[1]])
        ax.set_xticklabels(xdays, rotation=45, horizontalalignment='right')


        ax_ori = mpld3plugins.RotateTick(0, xdays)
        mpld3.plugins.connect(self.fig, ax_ori)



    def set_title(self):

        addonlen = len(self.figlayout['addon']['name'])

        timerange = self.info['timerange']
        str1 = datetime.datetime.strftime(timerange[0], '%Y/%m/%d')
        str2 = datetime.datetime.strftime(timerange[1], '%Y/%m/%d')
        #print str1, str2
        self.axes[self.axtop].set_title(self.info['symbol'] + ' Daily Chart ' + ' to '.join([str1, str2]))

    

    def plotdata(self):
        # 'Date': a data column created to plot x axis
        # for intraday: matplotlib date object -- computed from data.Timestamp and adjust to current timezone
        # for daily: length of data tuples -- get rid of non-trading date gaps

        print '--'
        print "graph.plotdata()"

        self.update_indicators()
        self.slice_data()

        data = self.slicedata
        Date = np.arange(data.shape[0])
        print 'slicedata xrange:', data.shape[0]


        self.create_fig_axes()

        ax = self.axes[0]
        aax = self.axes[1:]

        stock_graph.graph_main(ax, Date, data, self.figlayout['main']['name'])
        stock_graph.graph_incharts(ax, Date, data, self.figlayout['inchart']['name'])
        stock_graph.graph_addons(aax, Date, data, self.figlayout['addon']['name'])
        self.set_title()
        self.reset_xticks_date()


        #plt.show()



    #-----------------------------------------------------------------------------
    # input-output to graph requests from web interface
    #-----------------------------------------------------------------------------

    def plot_to_html(self, serve_html=False):

        self.plotdata()
        #mpld3.show()

        mainplotid = mpld3.utils.get_id(self.axes[0])
        fightml = mpld3.fig_to_html(self.fig)

        # to save the results
        with open("fig.html", "wb") as fh:
            fh.write(fightml)

        if serve_html: 
            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template('template.html')
            #template

            jinja_html = template.render(my_fig_html=fightml)

            serve(jinja_html)

        else:
            return mainplotid, fightml




    def update(self, args):
        '''
        '''

        style = args[0]


        if style=='init':
            self.update_config_info(symbol = args[1], timerange = [args[2], args[3]])
            self.init_data()        

            self.update_config_fig(main = args[4], 
                                  addon = [args[5], args[6], args[7]], 
                                  inchart = [args[8], args[9], args[10]]) 

        elif style=='range':
            self.update_config_info(timerange = [args[1], args[2]])
        elif style== 'main':
            self.update_config_fig(main = args[1])
        elif style=='inchart_id':
            self.update_config_fig(inchart_id=[args[1], args[2]])
        elif style=='addon_id':
            self.update_config_fig(addon_id = [args[1], args[2]])




if __name__ == '__main__':

    from _server import serve
    from jinja2 import Environment, FileSystemLoader



    symbol = 'IWM'#'SPY'
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

    # # maybe the tables should be spy, nasdaq, russel, and daily only -- how about start another database file
    # # my_db2.db ??
    # tablename = 'daily' #'daily' #'fivemin' 'onemin'
    # #conn = sqlite3.connect('/Users/jinghuage/Documents/webvisgenerator/my_db1.db')
    # conn = sqlite3.connect('my_db1.db')
    # table = database_table.table(tablename, conn)
    # # retrieve all data from database, use select *
    # data = from_database(table, symbol, fill_to_today=False)

    #retrieve data using pandas io
    # data from pandas: index:pandas.DatetimeIndex, 
    # columns: "Open", "High", "Low", "Close", "Volume", "Adj Close"
    # convert from pandas.DatetimeIndex to numpy.datetime64, to datetime
    # http://stackoverflow.com/questions/13703720/converting-between-datetime-timestamp-and-datetime64
    # data = quotes.get_quote_daily_pandas(symbol)
    # compute_indicators(data)
    #print data.head(2)
   
    mygraph = graph()

    vargs = ['init', 
             'AAPL', 
             '2006-01-01', 'today', 
             'ClosePrice',
             'DollarVolume', 'ADL', 'RSI(14)', 
             'MA(20)', 'MA(200)', 'BollingerBands']
    mygraph.update(vargs)

    #    var mainchart = ['ClosePrice', 'OCHL_Candlestick', 'OCHL_Candlestick(5)'];
    #    var addons = ['None', 'DollarVolume', 'ADL', 'MACD(12,26,9)', 'RSI(14)', 'ATR(14)'];
    #    var incharts = ['None', 'MA(20)', 'MA(50)', 'MA(200)', 'BollingerBands'];

    # all test cases
    vargs = ['range', '2015-01-11', '2016-1-10']
    mygraph.update(vargs)


    # # vargs = ['main', 'ClosePrice']
    # # vargs = ['inchart_id', '0', 'MA(13)']
    # vargs = ['addon_id', '0', 'None']
    # mygraph.update(vargs)
    # vargs = ['addon_id', '1', 'None']
    # mygraph.update(vargs)
    # vargs = ['addon_id', '2', 'None']
    # # vargs = ['addon_id', '1', 'ATR(14)']
    # # vargs = ['addon_id', '2', 'RSI(14)']

    # mygraph.update(vargs)


    #mygraph.plotdata()
    mygraph.plot_to_html()





