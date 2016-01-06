// Console.js

console.log("hello from Console.js");

/**
 * The console outputs data to the screen
 */
function Console(consoleElement) {
    console.log("function Console");
    this.con = consoleElement;
}
Console.prototype.appendFromClient = function(data) {	
	this.append('<div class="msg"><i class="icon-laptop">You said:</i><pre>'+this.encodeHTML(data)+"</pre></div>");
}
Console.prototype.appendFromServer = function(data) {
	this.append('<div class="msg"><i class="icon-white icon-cloud">Server said:</i><pre>'+this.encodeHTML(data)+"</pre></div>");
}
Console.prototype.appendError = function(data) {
	this.append('<div class="msg"><i class="icon-white icon-warning-sign">Error:</i><pre>'+this.encodeHTML(data)+"</pre></div>");
}
/**
 * append text to the console
 */
Console.prototype.append = function(data) {
    // only scroll to bottom if we are currently 
    // scrolled down
	// if the user is browsing earlier content, 
    // don't force them down
	// the page when the console updates
	scrollToBottom = true
	// if (this.isAtBottom()) {
	// 	scrollToBottom = true;
	// }
	this.con.html(this.con.html()+data);
	if (scrollToBottom) this.scrollToBottom();
};
/**
 * scroll the console to the bottom
 */
Console.prototype.scrollToBottom = function() {
    //console.log("Console.prototype.scrollToBottom");
    this.con.scrollTop(this.con[0].scrollHeight);
};
/**
 * determine if the console is currently 
 * scrolled to the bottom
 */
Console.prototype.isAtBottom = function() {
    return (this.con[0].scrollHeight - this.con[0].clientHeight <= this.con.scrollTop());
}
/**
 * encode HTML so it's safe for printing
 */
Console.prototype.encodeHTML = function(message) {
	// this method taken from:
	// http://stackoverflow.com/questions/1219860/html-encoding-in-javascript-jquery
	return $('<div/>').text(message).html();
}
