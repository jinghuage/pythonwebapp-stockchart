

Description: 

Plotting the stock data and its indicators is the first step of a financial viz system, so I made it a demo infoviz project. This is my version of many possible implemenations of this project. 


User interface: 

* runs on web browser
* Allows user to create up to three charts, to enable chart comparision. 
* Allows user to choose timerange, and add/remove available technical indicators


Technical Features: 

* The web user interface is dynamically created by javascript. So technically can create arbitrary number of charts. But the user interface set a limit to three to avoid cluttering. 

* Tornado web server (python) and websocket data communication
 
* The plots are created at server side using python libraries, e.g numpy, pandas, matplotlib. Then plots are exported into javascript and D3 scripts using mpld3 library. The scripts are send to the web to reproduce the plot

* data collection: many options, including:  

  Using libraries: 
  - pandas.io.data for daily data
  - matplotlib.finance for data data

  Using web api: 
  - Yahoo finance chartapi for intra-day 5min data (up to 21 days for most current query)
  - Yahoo finance webservice for realtime 1min data (15min delay for most current query)

  Using locally saved data: 
  - local sqlite3 database to save intra-day 5min data and realtime 1min data
  - local csv files


Future work: 

   - many other indicators can be calculated and plotted 
   - strategies and signals can be generated based on technical calculations
   - backtesting 





Code structure: 
Client side javascript code: 

websocketclient.js, websockethandler.js  -- web socket connection and event handling
Console.js -- bind to html div container to display messages send to and receive from server
Figure.js -- bind to html div container to display D3 script received from server


app.js: -- stockchart-multicolumn.js:

     Let user select number of charts, and create stockchart widgets accordingly

Javascript module websocketwidget_stockchart.js:

     A stockchart widget generator, implemented as Javascript Module pattern. The generator itself is a function, which take a 'table > tr' as input. This tr should contaion two 'td', one td is used to hold controls, the other to hold the figure (actually D3 script which will create svg graph) received from server. The generator's implementation include:
 
     -- create all user input widgets and register their event handler to collect configurations for the stockchart and send them to server 
     -- create a console div holder which display controlling message communication between websocket server and client
     -- create a figure div holder to receive plot from websocket server 
     -- create websocket client attached to the current chart widget, when the chart is deleted, the websocket client will disconnect from server and delete itself

Note: each stockchart widget bind a websocket client to its html container. So when multiple stockchart widgets are created, their will be same number of websocket clients created.

Server side python code: 

       tornado server.py: the tornado web server 
         -- open connection, create a websocket client and a graph object for each connection, 
         -- receive message from clients
         -- forward client request to a python graph module 
         -- send output from graph module back to client as response

       graph.py : the graph module, create matplotlib figure by request. its functions are:
        -- upon figure configuration request, update figure layout, e.g. change figure size, position and size subplots, etc
        -- upon data request, call python data collector module
        -- upon indicator request, call python indicator calculation module
        -- upon plot request, call stock graph functions to plot stocks data and indicators


       stock_graph.py -- stock and indicator calculation and plotting functions

       quotes.py -- data collector from yahoo finance, or from csv datasets

Note: All data will be stored as pandas DataFrame object. 
