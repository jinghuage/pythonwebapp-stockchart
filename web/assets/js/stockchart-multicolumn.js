var columns = ['1', '2', '3'];
$.each(columns, function(i,s){
    var optionString = '<option value=' + i + '>' + s + '</option>';
    //console.log(optionString);
    $('#column').append(optionString);
});

$("#column").val(0); //0, 1, 2

$("#column").on("change", function(e){
    var value = this.value;
    create_columns(parseInt(value)+1);
});

var $table = $('<table></table>').appendTo('#figcontrol');
var rmtserver = "ws://jge1-1.lsu.edu:9997/ws";
var lcserver = "ws://localhost:9999/ws";
var chart =  websocketwidget.stockchart().server(lcserver);//rmtserver); // returns a websocket chart widget generator function
//console.log(chart);


// initially, single column view
create_columns(1);

function create_columns(ncol) {

    var chartwidth = 1200;
    var figwidth = 11*80;


    var trs = $("tr");
    var cncol = trs.length;


    console.log("ncol:", ncol, "current td:", cncol);


    if(ncol < cncol){
        for(var i=ncol; i<cncol; i++){
            $("#chart"+i).trigger("remove");
            trs[i].remove();
        }
    }
    else{
        for(var i=cncol; i<ncol; i++){
            var $tr = $('<tr></tr>').appendTo($table);
            $tr.id = 'chart'+i;

            var $td1 = $('<td></td>').appendTo($tr);
            $td1.width(chartwidth - figwidth);
            var $td2 = $('<td></td>').appendTo($tr);
            $td2.css('background-color', '#f6f6f6');
            $td2.width(figwidth);

            chart($tr); //generate chart widget and attach to $tr
        }
    }

    //$table.children().width(tdwidth);
}



