#stock related graphs


import re
import numpy as np


def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    x = np.asarray(x)
    if type == 'simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()

    a = np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a


def moving_average_convergence(x, nslow=26, nfast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = moving_average(x, nslow, type='exponential')
    emafast = moving_average(x, nfast, type='exponential')
    return emaslow, emafast, emafast - emaslow



def relative_strength(prices, n=14):
    """
    compute the n period relative strength indicator
    http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
    http://www.investopedia.com/terms/r/rsi.asp
    """

    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n - 1) + upval)/n
        down = (down*(n - 1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)

    return rsi



def average_true_range(high, low, close, N=14):
    '''
    The ATR is the 14 day moving average of the "True Range".  
    Wilder defined the TR as the greatest of three measurements:
    1.  The distance from today's high to today's low.
    2.  The distance from yesterday's close to today's high.
    3.  The distance from yesterday's close to today's low.
    ATR=((N-1)PATR+TR)/N
    '''
    atr = np.zeros_like(high)
    #print 'lenght of atr:', len(atr)

    hi = np.asarray(high)[1:] #note: hi is one item forward in this computation
    lo = np.asarray(low)[1:]  #note: low is one item forward in this computation
    pclo = np.asarray(close)[:-1] 


    hilo = hi-lo;
    hiclo = abs(hi - pclo)
    loclo = abs(lo - pclo)
    
    tr = np.maximum(hilo, hiclo, loclo) #note: tr is one item forward in this computation
    #atr = rolling_mean(tr, 14)

    atr[0] = np.mean(tr[0:N])
    for i in range(1, len(atr)):
        atr[i] = (N - 1) * atr[i - 1] + tr[i-1]
        atr[i] /= N

    #print 'lenght of atr:', len(atr)
    #print np.amin(atr), np.amax(atr)

    return atr

def dolloar_volume(c, v):
    return (v * c)/1e6  # dollar volume in millions


# Accumulation Distribution Line (ADL)
def adl(high, low, close, volume):
    '''
    Formular:
      1. Money Flow Multiplier = [(Close  -  Low) - (High - Close)] /(High - Low) 

      2. Money Flow Volume = Money Flow Multiplier x Volume for the Period

      3. ADL = Previous ADL + Current Period's Money Flow Volume
    '''
    adl = np.zeros_like(high)

    hi = np.asarray(high)
    lo = np.asarray(low)
    cl = np.asarray(close)
    vo = np.asarray(volume)

    mfm = ((cl - lo) - (hi - cl)) / (hi - lo)
    mfv = mfm * vo

    adl = np.cumsum(mfv)

    return adl


# http://pandas.pydata.org/pandas-docs/stable/computation.html#moving-rolling-statistics-moments


# temp_data_set['20d_ma'] = pandas.rolling_mean(temp_data_set['Adj Close'], window=20)
# temp_data_set['50d_ma'] = pandas.rolling_mean(temp_data_set['Adj Close'], window=50)
# temp_data_set['Bol_upper'] = pandas.rolling_mean(temp_data_set['Adj Close'], window=20) + 2* pandas.rolling_std(temp_data_set['Adj Close'], 20, min_periods=20)
# temp_data_set['Bol_lower'] = pandas.rolling_mean(temp_data_set['Adj Close'], window=20) - 2* pandas.rolling_std(temp_data_set['Adj Close'], 20, min_periods=20)
# temp_data_set['Bol_BW'] = ((temp_data_set['Bol_upper'] - temp_data_set['Bol_lower'])/temp_data_set['20d_ma'])*100
# temp_data_set['Bol_BW_200MA'] = pandas.rolling_mean(temp_data_set['Bol_BW'], window=50)#cant get the 200 daa
# temp_data_set['Bol_BW_200MA'] = temp_data_set['Bol_BW_200MA'].fillna(method='backfill')##?? ,may not be good
# temp_data_set['20d_exma'] = pandas.ewma(temp_data_set['Adj Close'], span=20)
# temp_data_set['50d_exma'] = pandas.ewma(temp_data_set['Adj Close'], span=50)

         

def bollinger_bands(close):
    '''
    * Middle Band = 20-day simple moving average (SMA)
    * Upper Band = 20-day SMA + (20-day standard deviation of price x 2) 
    * Lower Band = 20-day SMA - (20-day standard deviation of price x 2)
    '''
    cl = np.asarray(close)
    mb = pd.rolling_mean(cl, window=20)
    st = 2 * pd.rolling_std(cl, 20, min_periods=20)

    return mb-st, mb+st


def compute_indicator(df, label):
    '''
    when label is an indicator with parameter, e.g. RSI(14), MA(200)
    pre-computation can't easily enumerate them
    so only calculate when requested 
    '''
    #print '--'
    #print 'stock_graph.compute_indicator()', label


    items = re.findall(r'\w+', label.lower())
    itype = items[0]

    if itype == 'rsi':
        n = int(items[1])
        attr = itype + items[1]
        if not attr in df:
            #print 'compute indicator:', attr 
            df[attr] = relative_strength(df.Close, n)        
    elif itype == 'ma':
        n = int(items[1])
        attr = itype + items[1]
        if not attr in df:
            #print 'compute indicator:', attr
            df[attr] = moving_average(df.Close, n, type='simple')     
            #print df.columns
    elif itype == 'bb':
        attr = ['bbl', 'bbu']
        if not attr in df:
            df[attr] = bollinger_bands(df.Close)
    elif itype == 'atr':
        n = int(items[1])
        attr = itype + items[1]
        if not attr in df:
            #print 'compute indicator:', attr
            df[attr] = average_true_range(df.High, df.Low, df.Close)        
    elif itype == 'macd':
        nslow = int(items[1])
        nfast = int(items[2])
        nema = int(items[3])
        attr = itype + items[1]+'-'+items[2]
        if not attr in df:
            #print 'compute indicator:', attr
            emaslow, emafast, macd = moving_average_convergence(df.Close, nslow=nslow, nfast=nfast)
            data[attr] = macd

        attr='ema'+items[3]
        if not attr in df:
            #print 'compute indicator:', attr
            df[attr] = moving_average(macd, nema, type='exponential')



        



def pre_compute_indicators(df):

    prices = df.Close

    ma20 = moving_average(prices, 20, type='simple')
    ma200 = moving_average(prices, 200, type='simple')
    volume = (prices * df.Volume)/1e6  # dollar volume in millions
    rsi = relative_strength(prices)
    nslow = 26
    nfast = 12
    nema = 9
    emaslow, emafast, macd = moving_average_convergence(prices, nslow=nslow, nfast=nfast)
    ema9 = moving_average(macd, nema, type='exponential')
    atr = average_true_range(df.High, df.Low, df.Close)

    df['rsi14'] = rsi
    df['ma20'] = ma20
    df['ma200'] = ma200
    df['dollarvolume'] = volume
    df['macd12-26'] = macd
    df['ema9'] = ema9
    df['atr14'] = atr




#graph names, copy from wesocketwidget_stockchart.js
#var mainchart = ['ClosePrice', 'OCHL_Candlestick', 'OCHL_Candlestick(5)'];
#var addons = ['None', 'DollarVolume', 'MACD(12,26,9)', 'RSI(14)', 'ATR(14)'];
#var incharts = ['None', 'MA20', 'MA200', 'BollingerBands', 'TrendLines'];

def graph_main(ax, Date, data, name):
    print "stock_graph.graph_main()", name


    if name=='ClosePrice':
        graph_closeprice(ax, Date, data, 'Close')
    elif name == 'OCHL_Candlestick':
        graph_candlestick(ax, Date, data, 'ochl')
    elif name == 'OCHL_Candlestick(5)':
        graph_candlestick(ax, Date, data, 'ochl5', 5)


def graph_incharts(ax, Date, data, names):
    print '--'
    print "stock_graph.graph_incharts()", names


    for name in names:
        items = re.findall(r'\w+', name.lower())
        itype = items[0]
        attr = ''.join(items)
        
        if itype == 'ma':
            graph_ma(ax, Date, data, name, attr)
        elif itype == 'bollingerbands':
            graph_bb(ax, Date, data, name, attr)
        elif itype == 'trendlines':
            graph_trendlines(ax, Date, data, name, attr)


def graph_addons(axs, Date, data, names):
    print '--'
    print "stock_graph.graph_addons()", names

    alen = len(axs)

    for i in range(alen):
        #print "addon:", i, names[i], axs[i]
        ax = axs[i]
        name = names[i]

        items = re.findall(r'\w+', name.lower())
        itype = items[0]
        if itype == 'macd':
            attr = [itype+items[1]+'-'+items[2], 'ema'+items[3]]
        else:
            attr = ''.join(items)

        if itype == 'dollarvolume':
            graph_volume(ax, Date, data, name, attr)
        elif itype == 'macd':
            graph_macd(ax, Date, data, name, attr)
        elif itype == 'rsi':
            graph_rsi(ax, Date, data, name, attr)
        elif itype == 'atr':
            graph_atr(ax, Date, data, name, attr)
    

def graph_ma(ax, Date, data, label, attr):
    '''
    Date: x axis data value, don't need to be date exactly, but when ax x label is created, date will be used
    to translate as datetime.date objects -- extra handling
    data: data includes mas
    mas: array of ma names, e.g. ['ma20', 'ma200']
    '''

    #print '--'
    #print 'stock_graph.graph_ma()', label, attr

    # color = ['blue', 'red']
    # for ma in mas:        
    #     items = re.findall(r'(\d+)', ma)
    #     print items
    #     ax.plot(Date, data[ma], color=color.pop(), lw=2, label=label)

    #print data.columns

    mydata = data[attr]
    

    import random
    colors = "bgrcmykw"
    #color_index = 0
    #rcolor = np.random.rand(3,1)
    #r = random.randint(0,8)
    ax.plot(Date, mydata, color=(random.random(), random.random(), random.random()), lw=2, label=label)


    # Now add the legend with some customizations.
    legend = ax.legend(loc='upper left', shadow=False, title='')

    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')
    
    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('small')

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width


def graph_bb(ax, Date, data, label, attr):

    fillcolor = (1, 1, 0, 0.5)
    ax.fill_between(Date, data['bbl'], data['bbu'], facecolor=fillcolor, edgecolor=fillcolor)



def graph_volume(ax, Date, data, label, attr):
    '''
    Date: x axis data values
    data.dollarvolume is the plotting data value for y axis
    '''
    #print '--'
    #print "stock_graph.graph_volume()", label, attr

    mydata = data[attr]



    fillcolor = 'darkgoldenrod'
    vmax = mydata.max()
    poly = ax.fill_between(Date, mydata, 0, label='Volume', facecolor=fillcolor, edgecolor=fillcolor)
    ax.set_ylim(0, vmax)
    ax.set_yticks([])
    for label in ax.get_xticklabels():
        label.set_visible(False)


def graph_rsi(ax, Date, data, label, attr):
    '''
    '''
    #print '--'
    #print "stock_graph.graph_rsi()", label, attr

    fillcolor = 'darkgoldenrod'
    textsize = 9
    


    mydata = data[attr]


    
    ax.plot(Date, mydata, color=fillcolor)
    ax.hlines(70, 0, len(mydata), color=fillcolor)
    ax.hlines(30, 0, len(mydata), color=fillcolor)
    #ax.fill_between(Date, data[rsi], 70, where=(data[rsi] >= 70), facecolor=fillcolor, edgecolor=fillcolor)
    #ax.fill_between(Date, data[rsi], 30, where=(data[rsi] <= 30), facecolor=fillcolor, edgecolor=fillcolor)
    ax.text(0.6, 0.9, '>70 = overbought', va='top', transform=ax.transAxes, fontsize=textsize)
    ax.text(0.6, 0.1, '<30 = oversold', transform=ax.transAxes, fontsize=textsize)
    ax.set_ylim(0, 100)
    ax.set_yticks([30, 70])
    ax.text(0.025, 0.95, label, va='top', transform=ax.transAxes, fontsize=textsize)

    for label in ax.get_xticklabels():
        label.set_visible(False)


def graph_atr(ax, Date, data, label, attr):
    '''
    '''
    #print '--'
    #print "stock_graph.graph_atr()", label, attr

    fillcolor = 'darkgoldenrod'
    textsize = 10


    mydata = data[attr]



    ax.plot(Date, mydata, color=fillcolor)
    ax.set_ylim(0, 8)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.hlines(5.0, 0, data.shape[0], color=fillcolor)
    ax.hlines(2.0, 0, data.shape[0], color=fillcolor)
    ax.text(0.025, 0.9, label, va='top', transform=ax.transAxes, fontsize=textsize)

    for label in ax.get_xticklabels():
        label.set_visible(False)



def graph_macd(ax, Date, data, label, attr):
    '''
    '''
    #print '--'
    #print "stock_graph.graph_macd()", label, attr

    fillcolor = 'darkslategrey'
    textsize=9

    macd = attr[0]
    ema = attr[1]


    mymacd = data[macd]
    myema = data[ema]



    ax.plot(Date, mymacd, color='black', lw=2)
    ax.plot(Date, myema, color='blue', lw=1)
    ax.fill_between(Date, mymacd - myema, 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)

    nslow = 26
    nfast = 12
    nema = 9
    ax.text(0.025, 0.95, label, #'MACD (%d, %d, %d)' % (nfast, nslow, nema), 
            va='top', transform=ax.transAxes, fontsize=textsize)

    for label in ax.get_xticklabels():
        label.set_visible(False)


def graph_closeprice(ax, Date, data, close='Close'):
    '''
    '''
    #print '--'
    #print 'stock_graph.graph_closeprice()', close


    mydata = data[close]
    ax.plot(Date, mydata, color='black', lw=1)


    pmin = np.amin(mydata)
    pmax = np.amax(mydata)
    ax.set_ylim([pmin-(pmax-pmin)/6, pmax])
    ax.set_xlim([0, len(Date)])


def graph_candlestick(ax, Date, data, ochl=""):
    '''
    '''
    print '--'
    print 'stock_graph.graph_candlestick()', ochl


    DOCHL = zip(Date , data.open, data.close, data.high, data.low)
    candlestick(ax, DOCHL, width=0.5, colorup='g', colordown='r')
