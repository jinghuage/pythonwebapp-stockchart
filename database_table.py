import sqlite3
import pandas as pd
import sys

class table:
    def __init__(self, name, conn):
        self.name = name
        self.conn = conn

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError('name must be a string')
        self._name = value

    @property
    def conn(self):
        return self._conn

    @conn.setter
    def conn(self, value):
        if not isinstance(value, sqlite3.Connection):
            raise TypeError('conn must be a database connection')
        self._conn = value


    def create(self, schema):
        c = self.conn.cursor()
        #create_syntax = 'CREATE TABLE if not exists %s (id INTEGER PRIMARY KEY,%s)' % (self.name, schema)
        create_syntax = 'CREATE TABLE if not exists %s (%s)' % (self.name, schema)
        print create_syntax
        c.execute(create_syntax)
        #c.execute('''CREATE TABLE my_db1 (Timestamp INT, close FLOAT, high FLOAT, low FLOAT, open FLOAT, volume FLOAT)''')

    def add_column(new_column, column_type, default_val):
        '''
        new_column = 'my_3nd_column'  # name of the new column
        column_type = 'TEXT' # E.g., INTEGER, TEXT, NULL, REAL, BLOB
        default_val = 'Hello World' # a default value for the new column rows
        '''

        c = self.conn.cursor()
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct} DEFAULT '{df}'"\
                        .format(tn=self.name, cn=new_column, ct=column_type, df=default_val))

        # Committing changes and closing the connection to the database file
        self.conn.commit()


    def destroy(self):
        c = self.conn.cursor()
        drop_syntax = 'drop table if exists %s' % self.name
        c.execute(drop_syntax)
        
    def clear(self):
        c = self.conn.cursor()
        delete_syntax = 'DELETE FROM %s' % self.name
        c.execute(delete_syntax)
        self.conn.commit()
        
    def clampto(self, timestamp):
        c = self.conn.cursor()
        funcname = sys._getframe().f_code.co_name
        print ','.join(map(str, [funcname, self.name, timestamp]))

        clamp_syntax = 'DELETE FROM %s WHERE Timestamp<?' % self.name
        print clamp_syntax
        c.execute(clamp_syntax, (timestamp,))
        self.conn.commit()
        print "Total number of rows deleted: ", self.conn.total_changes

        
    def get_first_ts(self):
        c = self.conn.cursor()
        first_syntax = 'SELECT * FROM %s ORDER BY Timestamp LIMIT 1' % self.name
        c.execute(first_syntax)
        first = c.fetchone()
        if first:
            return first[0]
        else:
            return None

    def get_last_ts(self):
        c = self.conn.cursor()
        last_syntax = 'SELECT * FROM %s ORDER BY Timestamp DESC LIMIT 1' % self.name
        #last_syntax = 'SELECT * FROM %s WHERE Timestamp = (SELECT MAX(Timestamp) FROM %d)' % (self.name, self.name)        
        c.execute(last_syntax)
        last = c.fetchone()
        if last:
            return last[0]
        else:
            return None


    def get_timestamp_range(self):
        ts1 = None
        ts2 = None

        firstts = self.get_first_ts()
        lastts = self.get_last_ts()
        return firstts, lastts

        # if firstts:
        #     ts1 = firstts[0]
        # if lastts:
        #     ts2 = lastts[0]
        # return ts1, ts2
        

    def get_columns(self):
        c = self.conn.cursor()
        columnsQuery = "PRAGMA table_info(%s)" % self.name
        c.execute(columnsQuery)
        #numberOfColumns = len(self._c.fetchall())
        columns = map(lambda t: t[1], c.fetchall())  
        #print columns
        return columns
        
    def get_num_rows(self):
        c = self.conn.cursor()
        rowsQuery = "SELECT Count() FROM %s" % self.name
        c.execute(rowsQuery)
        numberOfRows = c.fetchone()[0]
        return numberOfRows
    
    def isempty(self):
        #print 'table', self.name, 'isempty?'        
        if self.get_num_rows() == 0: 
            return True
        else:
            return False
        
    def fill(self, lst, datacolumns=None):
        print '--'
        funcname = sys._getframe().f_code.co_name
        print ','.join(map(str, ['--', funcname, self.name, len(lst)]))

        c = self.conn.cursor()

        columns = datacolumns
        if columns is None:
            columns = self.get_columns()
        tsid = columns.index('Timestamp') # make sure Timestamp exists
        if tsid == -1: 
            print 'can not fill in data without Timestamp (as primary key)'
            return
          
        columnstr = ','.join(columns)
        wildcards = ','.join(['?'] * (len(columns)))
        insert_syntax = 'INSERT OR IGNORE INTO %s (%s) VALUES (%s)' % (self.name, columnstr, wildcards)
        print insert_syntax
        #c.executemany("INSERT INTO my_db1 VALUES (?,?,?,?,?,?)", lst)
        c.executemany(insert_syntax, lst)
        self.conn.commit()    
        #print "Total number of rows inserted: ", self.conn.total_changes



    def from_dataframe(self, df, datacolumns):
        #df.to_sql(self.name)
        # get output ready for database export
        output = df.itertuples()
        data = list(output)
        data = [d[1:] for d in data]  #drop the index column from pandas dataframe
        # print data[0]
        self.fill(data, datacolumns)
        


    def to_dataframe(self, timerange=None):
        c = self.conn.cursor()

        select_byrange = True
        select_syntax = None
        df = None


        if timerange is None:
            print 'select all'
            select_byrange = False
        elif len(timerange) == 1:
            timestamp1 = int(timerange[0])
            timestamp2 = timestamp1 + 1
        elif len(timerange) == 2:
            timestamp1 = timerange[0]
            timestamp2 = timerange[1]

        if select_byrange:
            select_syntax = 'SELECT * FROM %s WHERE Timestamp>=? AND Timestamp<? ORDER BY Timestamp' % self.name
            print 'params=', timestamp1, timestamp2
            df = pd.read_sql_query(select_syntax, self.conn, params=[timestamp1, timestamp2])
        else:
            select_syntax = 'SELECT * from %s ORDER BY Timestamp' % self.name
            df = pd.read_sql_query(select_syntax, self.conn, index_col=['Timestamp'])


        print select_syntax

        #c.execute(select_syntax, (timestamp1, timestamp2))
        #df = pd.DataFrame(self._c.fetchall())
        #df.columns = c.keys()
        #df.set_index(['Timestamp'])

        #df = pd.read_sql_query(select_syntax, self.conn, params=[timestamp1, timestamp2], index_col=['Timestamp'])


        return df
        
