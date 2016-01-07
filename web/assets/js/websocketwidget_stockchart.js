//namespace
if(typeof websocketwidget == 'undefined'){
    websocketwidget = {};
};


console.log("name space websocketwidget is :", websocketwidget);




websocketwidget.stockchart = function(){

    //private variables -- accessable only to stockchart because of closure
    //for outside, expose them using a stockchart.publicmethod

    var _server = "ws://localhost:9999/ws";
    var _width = 1200;
    var _height = 600;


    //var t = new Console();


    //selection: jquery selection
    var stockchart = function(selection) {
        var id = 'panel';

        //console.log(selection);
        id = selection.id;

        selection.addClass("stockvis");
        selection.attr('id', id);

        var tds = selection.children();
        var td1 = $(tds[0]);
        var td2 = $(tds[1]);



        //console: communication message with websocket server
        var $console = $('<div></div>').appendTo(td1);
        $console.attr('id', id+'-console');
        $console.addClass("text_io"); //.attr("class", "console");
        //$console.width(_width);


        //figure : reuturned figure html from websocket server
        var $figure = $('<div></div>').appendTo(td2);
        $figure.attr('id', id+'-figure');
        $figure.addClass("fig"); //.attr("class", "console");
        //$figure.width(_width);


        //the control td -- left side
        //create DOM and setup id and class attributes
        td1.append('<label>Ticker: </label>');
        var $ticker = $('<select></select>').appendTo(td1);
        $ticker.attr("id", id+"-ticker");

        var tickers = ['SPY', 'QQQ', 'IWM', 'IBB', 'GLD', 'GDX'];

        $.each(tickers, function(i,s){
            var optionString = '<option value=' + i + '>' + s + '</option>';
            $('#'+ id +'-ticker').append(optionString);
        });

        td1.append("<label>Date Range:</label>");
        var $dailymin = $('<input type="date" min="2006-01-01" value="2014-09-01">').appendTo(td1);
        $dailymin.attr("id", id+"-dailymin");

        var $dailymax = $('<input type="date" max="2016-01-01" value="2015-12-01">').appendTo(td1);
        $dailymax.attr("id", id+"-dailymax");

        td1.append("<br>");
        var $update = $('<button>Update</button>').appendTo(td1);
        $update.attr("id", id+"-update");
        td1.append("<br>");


        var mainchart = ['ClosePrice', 'OCHL_Candlestick', 'OCHL_Candlestick(5)'];
        var addons = ['None', 'DollarVolume', 'ADL', 'MACD(12,26,9)', 'RSI(14)', 'ATR(14)'];
        var incharts = ['None', 'MA(13)', 'MA(20)', 'MA(50)', 'MA(200)', 'BollingerBands'];

        // One main chart
        td1.append("<label>Main Chart type:</label>");
        var $mainchartype = $('<select></select>').appendTo(td1);
        $mainchartype.attr("id", id+"-mainchartype");
        $.each(mainchart, function(i,s){
            var optionString = '<option value=' + i + '>' + s + '</option>';
            $mainchartype.append(optionString);
        });
        $mainchartype.val(0);
        $mainchartype.on('change', function(e){
            var value = mainchart[this.value]
            message = ['graph:', 'main', value].join(' ');
            console.log(message);
            selection.Socket.send(message);
        });

        // Maximum three addon subcharts
        td1.append("<label>Add-on Indicators:</label>");
        [1,2,3].map(function(d,i){
            
            var $addon = $('<select></select>').appendTo(td1);
            $addon.attr("id", id+"-addon"+d);
            $.each(addons, function(i,s){
                var optionString = '<option value=' + i + '>' + s + '</option>';
                $addon.append(optionString);
            });
            $addon.val(d);           

            $addon.on('change', function(e){
                var value = addons[this.value]
                message = ['graph:', 'addon_id', i, value].join(' ');
                console.log(message);
                selection.Socket.send(message);
            });
        });


        // Maximum Three inchart subcharts
        td1.append("<label>In-chart Indicators:</label>");
        [1,2,3].map(function(d,i){

            var $inchart = $('<select></select>').appendTo(td1);
            $inchart.attr("id", id+"-inchart"+d);
            $.each(incharts, function(i,s){
                var optionString = '<option value=' + i + '>' + s + '</option>';
                $inchart.append(optionString);
            });
            $inchart.val(d);

            $inchart.on('change', function(e){
                var value = incharts[this.value]
                message = ['graph:', 'inchart_id', i, value].join(' ');
                console.log(message);
                selection.Socket.send(message);
            });
        });




        //var $console = $("#" + _id + "-console");
        //var $figure = $("#" + _id + "-figure");
        //console.log("this is:", this);

        selection.C = new Console($console);
        selection.F = new Figure($figure);
        selection.Handler = new WebSocketHandler(id, selection.C, selection.F);
        selection.Socket = new WebSocketClient(_server, selection.Handler);


        function send(style){
            //console.log("send called on: ", selection, style);
            var message = 'graph:';

            var ticker = tickers[$("#"+ id + "-ticker").val()],
                main = mainchart[$("#"+id+"-mainchartype").val()],
                in1 = incharts[$("#"+ id + "-inchart1").val()],
                in2 = incharts[$("#"+ id + "-inchart2").val()],
                in3 = incharts[$("#"+ id + "-inchart3").val()],

                a1 = addons[$("#"+ id + "-addon1").val()],
                a2 = addons[$("#"+ id + "-addon2").val()],
                a3 = addons[$("#"+ id + "-addon3").val()];

            var date1 = '2006-01-01',
                date2 = 'today';

            if(style == 'range'){
                date1 = $('#'+ id + '-dailymin').val();
                date2 = $('#'+ id + '-dailymax').val();
            }
            //console.log(ticker, date1, date2);

            if(style == 'init'){
                message = ['graph:', style, ticker, date1, date2,
                          main,
                          a1, a2, a3,
                          in1, in2, in3].join(' ');
            }
            else if(style=='range'){
                message = ['graph:', style, date1, date2].join(' ');
            }
            
            console.log(message)
            selection.Socket.send(message);
        }


        selection.bind("connected", function(){
            send('init');
        });

        selection.bind("remove", function(){
            //console.log("remove event triggered on: ", selection);
            selection.Socket.disconnect();

            delete selection.C;
            delete selection.F;
            delete selection.Handler;
            delete selection.Socket;
        });

        $("#"+ id + "-update").click(function(){
            send('range');
        });
        $("#"+ id + "-ticker").on("change", function(){
            send('init');
        });
    };




    stockchart.server = function(_) {
        if(!arguments.length) return _server;
        _server = _;
        return stockchart;
    };


    stockchart.width = function(_) {
        if (!arguments.length) return _width;
        _width = _;

        return stockchart;
    };

    stockchart.height = function(_) {
        if (!arguments.length) return _height;
        _height = _;

        return stockchart;
    };


    return stockchart;
};
