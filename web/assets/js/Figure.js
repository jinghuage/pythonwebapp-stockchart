// Figure.js


/**
 * The console outputs data to the screen
 */
function Figure(figureElement) {
    this.fig = figureElement;
}
Figure.prototype.appendFromServer = function(data) {	
	this.append('<div class="fig">'+data+'</div>');
}


/**
 * append html to the figure
 */
Figure.prototype.append = function(data) {
    // only scroll to bottom if we are currently 
    // scrolled down
	// if the user is browsing earlier content, 
    // don't force them down
	// the page when the console updates
	scrollToBottom = false
	if (this.isAtBottom()) {
		scrollToBottom = true;
	}
	this.fig.html(data);
	if (scrollToBottom) this.scrollToBottom();
};
/**
 * scroll the console to the bottom
 */
Figure.prototype.scrollToBottom = function() {
	this.fig.scrollTop(this.fig[0].scrollHeight);
};
/**
 * determine if the console is currently 
 * scrolled to the bottom
 */
Figure.prototype.isAtBottom = function() {
    return (this.fig[0].scrollHeight - this.fig[0].clientHeight <= this.fig.scrollTop());
}
/**
 * encode HTML so it's safe for printing
 */
Figure.prototype.encodeHTML = function(message) {
    // this method taken from:
    // http://stackoverflow.com/questions/1219860/html-encoding-in-javascript-jquery
    //create a in-memory div, set it's inner text(which jQuery automatically encodes)
    //then grab the encoded contents back out.  The div never exists on the page.
    return $('<div/>').text(message).html();
}
