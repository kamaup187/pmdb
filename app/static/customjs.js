'use strict';

var delay = $("#delay").text()

if (delay == "yes"){}else{
	$(window).on('load', function() {
		/*------------------
			Preloder
		--------------------*/
		$(".loader-alt").fadeOut(); 
		$("#preloder-alt").delay(400).fadeOut("slow");
	
	});
	
	'use strict';
	
	$(window).on('load', function() {
		/*------------------
			Preloder
		--------------------*/
		$(".loader").fadeOut(); 
		$("#preloder").delay(1).fadeOut("fast");
	
	});
}

