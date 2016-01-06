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
        td1.append("<br><br>");


        var indicators = ['None', 'MACD(12,26,9)', 'RSI(14)'];
        var mas = ['None', 'MA20', 'MA200'];

        td1.append("<label>Add-on Indicators:</label>");
        var $ind1 = $('<select></select>').appendTo(td1);
        $ind1.attr("id", id+"-ind1");
        $.each(indicators, function(i,s){
            var optionString = '<option value=' + i + '>' + s + '</option>';
            $('#'+ id +'-ind1').append(optionString);
        });
        $ind1.val(1);


        var $ind2 = $('<select></select>').appendTo(td1);
        $ind2.attr("id", id+"-ind2");
        $.each(indicators, function(i,s){
            var optionString = '<option value=' + i + '>' + s + '</option>';
            $('#'+ id +'-ind2').append(optionString);
        });
        $ind2.val(2);

        td1.append("<label>In-chart Indicators:</label>");
        var $ma1 = $('<select></select>').appendTo(td1);
        $ma1.attr("id", id+"-ma1");
        $.each(mas, function(i,s){
            var optionString = '<option value=' + i + '>' + s + '</option>';
            $('#'+ id +'-ma1').append(optionString);
        });
        $ma1.val(1);

        var $ma2 = $('<select></select>').appendTo(td1);
        $ma2.attr("id", id+"-ma2");
        $.each(mas, function(i,s){
            var optionString = '<option value=' + i + '>' + s + '</option>';
            $('#'+ id +'-ma2').append(optionString);
        });
        $ma2.val(2);

        var $console = $('<div></div>').appendTo(td1);
        $console.attr('id', id+'-console');
        $console.addClass("text_io"); //.attr("class", "console");
        //$console.width(_width);


        var $figure = $('<div></div>').appendTo(td2);
        $figure.attr('id', id+'-figure');
        $figure.addClass("fig"); //.attr("class", "console");
        //$figure.width(_width);




        //var $console = $("#" + _id + "-console");
        //var $figure = $("#" + _id + "-figure");
        //console.log("this is:", this);

        selection.C = new Console($console);
        selection.F = new Figure($figure);
        selection.Handler = new WebSocketHandler(id, selection.C, selection.F);
        selection.Socket = new WebSocketClient(_server, selection.Handler);


        function send(style){
            //console.log("send called on: ", selection, style);

            var ticker = tickers[$("#"+ id + "-ticker").val()];
            var date1 = '2006-01-01';
            var date2 = 'today';
            if(style == 'range'){
                date1 = $('#'+ id + '-dailymin').val();
                date2 = $('#'+ id + '-dailymax').val();
            }
            console.log(ticker, date1, date2);
            var message = ['graph:', ticker, style, date1, date2].join(' ');
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
