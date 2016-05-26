

A Websocket viz application : Stockchart
========================================

User interface: 
----------------

* A stock technical analysis chart runs on web browser, powered by python backend server
* Allows user to create up to three charts, to enable chart comparision. 
* Allows user to choose timerange, and add/remove available technical indicators (up to three addons, and three inchart indicators)


Run the app
-------------

To start the server, from terminal::

  python server.py

To start the webapp, go to your browser::

  localhost:9999
  

play with code
---------------

each file should have a test unit (if __name__ == '__main__') if you run it standalone. 

For example, edit quotes.py, change symbol and start date, then run::

  python quotes.py 

This will download the daily data for this symbol from start date to today, then save to a csv file


To test the graph in standalone mode, edit the test unit code in graph.py, then run::

  python graph.py

at function graph.init_data(), line 179. If you comment/uncomment lines to use local data from csv file
at function graph.plot_to_html(), line 344. If you uncomment mpld3.show(), you can see graph served at localhost

Or if you don't want to save to html yet, call graph.plotdata() instead. uncomment plt.show() to show in matplotlib rendering backend. 


jinja2 are used for testing template html file serving, ignore it if you are not interested in template yet


To add another indicator, things you need to do:

* give it a chart name, a label, and a data attribute. For example, the ``Acumulation Distribution Line'' indicator has a chart name 'ADL', a label 'Accum/Dist', and a data attribute 'adl'

* add chart name in websocketwiget_stockchart.js, it will be sent to server as chart update argument

* in stock_graph.py, add : 

  - adl() function to compute the indicator
  - in compute_indicator() function, add an *elif* clause for adl attribute
  - depends on this indicator will be drawn as inchart or addon chart, add an *elif* clause in graph_incharts() or graph_addons() function
  - graph_adl() function to draw the chart




Technical Features: 
--------------------

* The web user interface is dynamically created by javascript. So technically can create arbitrary number of charts. But the user interface set a limit to three to avoid cluttering. 

* Tornado web server (python) and websocket data communication
 
* The plots are created at server side using python libraries, e.g numpy, pandas, matplotlib. Then plots are exported into javascript and D3 scripts using mpld3 library. The scripts are send to the web to reproduce the plot




Code structure: 
----------------

Client side javascript code: 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

index html:  ./web/index_stockchart.html
javascript files: ./web/assets/js/
css files: ./web/assets/css/

scripts:

* websocketclient.js, wshandler.js  -- web socket connection and event handling

* Console.js -- bind to html div container to display messages send to and receive from server

* Figure.js -- bind to html div container to display D3 script received from server

* stockchart-multicolumn.js: Let user select number of charts, and create stockchart widgets accordingly

* websocketwidget_stockchart.js: A stockchart widget generator, implemented as Javascript Module pattern. The generator itself is a function, which take a 'table > tr' as input. This tr should contaion two 'td', one td is used to hold controls, the other to hold the figure (actually D3 script which will create svg graph) received from server. The generator's implementation include:
 
  - create all user input widgets and register their event handler to collect configurations for the stockchart and send them to server 
  - create a console div holder which display controlling message communication between websocket server and client
  - create a figure div holder to receive plot from websocket server 
  - create websocket client attached to the current chart widget, when the chart is deleted, the websocket client will disconnect from server and delete itself. 


**Note: each stockchart widget bind a websocket client to its html container. So when multiple stockchart widgets are created, their will be same number of websocket clients created.**


Server side python code: 
~~~~~~~~~~~~~~~~~~~~~~~~~

* server.py: the tornado web server 

  - open connection, create a websocket client and a graph object for each connection, 
  - receive message from clients
  - forward client request to a python graph module 
  - send output from graph module back to client as response

* graph.py : the graph module, create matplotlib figure by request. its functions are:

  - upon figure configuration request, update figure layout, e.g. change figure size, position and size subplots, etc
  - upon data request, call python data collector module
  - upon indicator request, call python indicator calculation module
  - upon plot request, call stock graph functions to plot stocks data and indicators


* stock_graph.py -- stock and indicator calculation and plotting functions

* quotes.py -- data collector from yahoo finance, or from csv datasets

**Note: All data will be stored as pandas DataFrame object.**
