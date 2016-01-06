// assets/js/wshandler.js

/**
 *  This event handler responds to the WebSocketClient, customizing the actions we take 
 *  when it issues events such as onOpen or onMessage.
 *
 *  We implement this separately so that we can perform layout-specific changes while
 *  keeping the WebSocketClient abstracted from UI
 */
function WebSocketHandler(pid, console, figure) {
        this.owner = $("#"+pid);
	this.con = console;
        this.fig = figure;
}

/**
 *  when the user tries to send a message,
 *  publish your message into the console
 */
WebSocketHandler.prototype.send = function(message) {
	this.con.appendFromClient(message + ', waiting for server response......');
}

/**
 * upon connection, 
 *   - exchange the Connect button for a Disconnect button, 
 *   - allow user to send messages to the server,
 *   - notify user of the connection
 */
WebSocketHandler.prototype.onOpen = function() {
    //$(window).trigger("connected");
    this.owner.trigger("connected");
 };
/**
 *  when a message is recieved from the server,
 *  publish the server's message into the console
 */
WebSocketHandler.prototype.onMessage = function(e) {
    var message = e.data;

    var ind1 = message.indexOf('plotid:');
    var ind2 = message.indexOf('fightml:');
    //console.log(ind1, ind2);

    var conmsg = '';
    var figmsg = '';

    if(ind1>-1 && ind2>-1){
        conmsg = message.substring(ind1, ind2);
        figmsg = message.substring(ind2+8);
    }
    else conmsg = message;

    if(conmsg.length>0) this.con.appendFromServer(conmsg);
    if(figmsg.length>0) this.fig.appendFromServer(figmsg);
  
};

/**
 * upon connection, 
 *   - exchange the Connect button for a Disconnect button, 
 *   - allow user to send messages to the server,
 *   - notify user of the connection
 */
WebSocketHandler.prototype.onClose = function() {

};

/**
 * if there was an error,
 * print the error into the console
 */
WebSocketHandler.prototype.onError = function(e) {
	var message = e.data;
	this.con.appendError(message);
};
