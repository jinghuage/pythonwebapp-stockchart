// assets/js/websockettester.js

// initialize global variables

var KEY_SERVER_URI = "websockettest.serveruri";

var tickers = ['SPY', 'QQQ', 'IWM', 'IBB', 'GLD', 'GDX'];

$.each(tickers, function(i,s){
    var optionString = '<option value=' + i + '>' + s + '</option>';
    //console.log(optionString);
    $('#ticker').append(optionString);
});

/**
 * set up the actions and global variables on the page
 */
$( document ).ready(function() {
    // initialize the console and the Handler
    Console = new Console($("#console"));
    Figure = new Figure($("#figs"));
    Handler = new WebSocketHandler(Console, Figure);
    
    // load the saved serverURI into the serveruri input
    var server = localStorage.getItem(KEY_SERVER_URI);

    if(server){
        $("#serveruri").val(server);
    }
    else{
        server = "ws://localhost:9999/ws";
	localStorage.setItem(KEY_SERVER_URI, server);
    }

    console.log(server);

    window.WebSocketClient = new WebSocketClient(server, window.Handler);


    $(window).bind("connected", function(e){
        ticker = tickers[$("#ticker").val()];
        style = 'init';
        date1 = '2006-01-01';
        date2 = 'today';
        var message = ['graph:', ticker, style, date1, date2].join(' ');
        window.WebSocketClient.send(message);
    });

    $("#ticker").on("change", function(e){
        var value = this.value;
        ticker = tickers[value];


        // send an initialization message, to receive the start-up graph:)
        //ticker = 'SPY';
        style = 'init';
        date1 = '2006-01-01';
        date2 = 'today';
        var message = ['graph:', ticker, style, date1, date2].join(' ');
        window.WebSocketClient.send(message);
    });


    $("#update").click(function(e) {
        ticker = tickers[$("#ticker").val()];
        style = 'range';
        date1 = $('#dailymin').val()
        date2 = $('#dailymax').val()
        //var message = 'AAPL, daily, 2015-09-01,2015-10-10';
        var message = ['graph:', ticker, style, date1, date2].join(' ');
        window.WebSocketClient.send(message);
        e.preventDefault();
    });


});
