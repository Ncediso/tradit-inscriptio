
(function ($) {
	"use strict";
	$('.column100').on('mouseover',function(){
		var table1 = $(this).parent().parent().parent();
		var table2 = $(this).parent().parent();
		var verTable = $(table1).data('vertable')+"";
		var column = $(this).data('column') + ""; 

		$(table2).find("."+column).addClass('hov-column-'+ verTable);
		$(table1).find(".row100.head ."+column).addClass('hov-column-head-'+ verTable);
	});

	$('.column100').on('mouseout',function(){
		var table1 = $(this).parent().parent().parent();
		var table2 = $(this).parent().parent();
		var verTable = $(table1).data('vertable')+"";
		var column = $(this).data('column') + ""; 

		$(table2).find("."+column).removeClass('hov-column-'+ verTable);
		$(table1).find(".row100.head ."+column).removeClass('hov-column-head-'+ verTable);
	});
    

})(jQuery);

$( document ).ready(function(){

  function getData() {
    var canvas = document.getElementById("clientList");
    var clientId = canvas.options[canvas.selectedIndex].value;
    // $.post(url,[data],[callback],[type]);

    if (clientId != "-1"){
        $.post( "/post-filter-report", {
          client_id: JSON.stringify(clientId)
        }, function(err, req, resp){
          window.location.href = "/reports/"+clientId;
            l = 1;
        });
    }
    else{
        $.post( "/post-filter-report", {
          client_id: JSON.stringify(clientId)
        }, function(err, req, resp){
          window.location.href = "/reports";
        });
    }

  }

//  $( "#clearButton" ).click(function(){
//    clearCanvas();
//  });

  $( "#clientList" ).change(function(){
    getData();
  });
});
