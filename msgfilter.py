import time
import json
import sys
from collections import defaultdict
import re
import logging
logger = logging.getLogger('filter')
logger.setLevel(logging.DEBUG)

import graph

from datetime import datetime,date,tzinfo,timedelta


class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

GMT = Zone(0,False,'GMT')
EST = Zone(-5,False,'EST')
CST = Zone(-6, True, 'CST')

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


import operator

def get_operator_fn(op):
    return {
        '+' : operator.add,
        '-' : operator.sub,
        '*' : operator.mul,
        '/' : operator.div,
        '%' : operator.mod,
        '^' : operator.xor,
        '>' : operator.gt,
        '<' : operator.lt,
        '>=' : operator.ge,
        '<=' : operator.lt
        }[op]


def visitop(op, left, right):
    return get_operator_fn(op)(left, right)
    



class MSGFilter:
    def __init__(self):
        self.filters = defaultdict(list)
        

    def process_cmd(self, cmd):
        msg = cmd
        if cmd.startswith('sub:'):
            items = re.findall(r'sub:(.*?):\s*(.*?)\s*([<>=]+)\s*(\d+\.*\d+)', cmd)
            #logger.log(logging.DEBUG, ' '.join(items[0]))
            symbol = items[0][0]
            self.add_filter(symbol, items[0][1:])
        elif cmd.startswith('desub:'):
            items = re.findall(r'desub:(.*)', cmd)
            symbol = items[0].strip()
            self.delete_filter(symbol)
        elif cmd.startswith('desub all'):
            self.delete_all_filters()
        elif cmd.startswith('listsub:'):
            items = re.findall(r'listsub:(.*)', cmd)
            symbol = items[0].strip()
            msg = self.print_filter(symbol)  
        elif cmd.startswith('listsub all'):
            msg = self.print_all_filters()
        elif cmd.startswith('graph:'):
            items = re.findall(r'graph:(.*)', cmd)
            args = items[0].strip().split(' ')
            print args
            graph.update(args)
            plotid, fightml = graph.plot_to_html()

            msg = 'plotid:'+ plotid
            msg += ('fightml:' + fightml)
            #msg += ('fightml:<p>' +symbol+ ' '+datetime.strftime(date1,'%Y-%m-%d')+' -- '+datetime.strftime(date2,'%Y-%m-%d')+'</p>\n'+ fightml)

        return msg


    def add_filter(self, symbol, f):
        self.filters[symbol].append(f)
        funcname = sys._getframe().f_code.co_name
        logger.log(logging.DEBUG, funcname + ':' + self.print_filter(symbol))

    def apply_filter(self, quote):
        quoteobj = byteify(json.loads(quote))
        msg = ''
        funcname = sys._getframe().f_code.co_name
        resources = quoteobj['list']['resources']
        for r in resources:
            fields = r['resource']['fields']
            symbol = fields['symbol']

            timestamp = fields['utctime']
            t = datetime.strptime(timestamp,'%Y-%m-%dT%H:%M:%S+0000')
            t = t.replace(tzinfo=GMT)
            tscst = t.astimezone(CST).strftime('%m/%d/%Y %H:%M:%S %Z')
            logger.log(logging.DEBUG, funcname+':'+symbol+'--'+tscst)
            
            if symbol in self.filters:
                conditions = self.filters[symbol]
                for c in conditions:
                    left = c[0]
                    op = c[1]
                    right = c[2]
                    logger.log(logging.DEBUG, ' '.join(c))

                    if left in fields:
                        value = float(fields[left])
                        if visitop(op, value, float(right)):
                            msg += symbol + ':Condition met at ' + tscst + ':' + str(value) + '\n'
                    else:
                        msg += 'attribute ' + left + ' is not in filter list for ' + symbol + '\n'
            else:
                msg += symbol + ' does not have filter\n'

        logger.log(logging.DEBUG, msg)    
        return msg


    def print_filter(self, symbol):
        msg = ''
        if symbol in self.filters:
            msg = symbol+':'
            filter = self.filters[symbol]
            for f in filter:
                msg += ' '.join(f)
        else:
            msg='no filter for symbol ' + symbol + ' found'
        return msg

    def print_all_filters(self):
        msg = ''
        for symbol in self.filters:
            msg += self.print_filter(symbol)

        return msg
            

    def delete_filter(self, symbol):
       if symbol in self.filters:
           del self.filters[symbol]

    def delete_all_filters(self):
        for symbol in self.filters:
            self.delete_filter(symbol)
