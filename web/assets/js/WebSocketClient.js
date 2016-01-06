// assets/js/WebSocketClient.js

function WebSocketClient (serverURI, handler) {
    this.STATE_DISCONNECTED = 0;
    this.STATE_CONNECTED = 1;
    this.STATE_CONNECTING = 2;
    this.STATE_CLOSED = 3;
    
    this.serverURI = serverURI;
    this.handler = handler;
    this.ws = new WebSocket(serverURI);
    
    this.ws.onopen = function() {
	handler.onOpen();
    };
    this.ws.onmessage = function(e) {
	handler.onMessage(e);
    };
    this.ws.onclose = function() {
	handler.onClose();
    };
    this.ws.onerror = function(e) {
	handler.onError(e);
	
    };
}
 
/**
 * Send a message to the WebSocket Server
 */
WebSocketClient.prototype.send = function(message) {
    if (this.ws.readyState == this.STATE_CONNECTED) {
	this.handler.send(message);
	this.ws.send(message);
    } else {
	this.handler.onError("Not Connected");
    }
};
/**
 * close the connection
 */
WebSocketClient.prototype.disconnect = function() {
    this.ws.close();
}

