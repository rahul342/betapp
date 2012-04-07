/* All Javascript functions of betting app will go into this file */	
	function ajax_post(type) {
		if(type == 'home') {
			//FB.Canvas.setAutoResize();
			$("div#bet_container").html("");
			$("div#bet_container").load('https://127.0.0.1:8001/userhome/', function(response, status, xhr) {
			  if (status == "error") {
				var msg = "Sorry but there was an error: ";
				alert(msg + xhr.status + " " + xhr.statusText);
			  }
			  //alert('Load was performed.');
			});
			$("li").removeClass("active");	
			$("#home").addClass("active");
			
		} else if(type == 'placebets') {
			FB.Canvas.setAutoResize();
			$("div#bet_container").html("");
			$("div#bet_container").load('https://127.0.0.1:8001/placebets/', function(response, status, xhr) {
			  if (status == "error") {
				var msg = "Sorry but there was an error: ";
				alert(msg + xhr.status + " " + xhr.statusText);
			  }			  
			  //alert('Load was performed.');
			});
			$("li").removeClass("active");	
			$("#placebets").addClass("active");			
			//alert('hi');
		} else if(type == 'invite') {
				FB.Canvas.setAutoResize();
				//specify redirect uri to handle requests
				FB.ui({
					method: 'apprequests',
					message: 'Become my Buddie',
					filters: ['app_non_users'],
					title: 'Become my Buddie'
				},
				function (response) {
					console.log(response)
				    alert(response.to);
					if (response && response.to) {
				   //if sucess do something
				   //How many people did the user invited?
					var showManyInvites = String(response.to).split(',').length;
					alert(showManyInvites);
					} else {
					  alert('canceled');
					  return false;
					}
				});
		} else if(type == 'betmodal') {
			//FB.Canvas.setAutoResize();	
			FB.Canvas.setSize({ height: 800 });
			alert('in betmodal');
			$("div#myModal").load('https://127.0.0.1:8001/placebets/', function(response, status, xhr) {
				  if (status == "error") {
					var msg = "Sorry but there was an error: ";
					alert(msg + xhr.status + " " + xhr.statusText);
				  }
				 // $('#myModal').css('margin-top', (($('#myModal').outerHeight() / 2) * -1)-50).css('margin-left', ($('#myModal').outerWidth() / 2) * -1);
				  $('#myModal').show();				  
				  $('#myModal').modal();					  				  
					  
			});			
		}
	}
	function appendBet(teamname, odds, betIdElement) {
			var userCash = getUserCash();
			alert(userCash);
			//user cash is hard coded for now..Need to get it from cash div
			var betcontent="<div id='bet_"+$(betIdElement).attr('id')+"' class='alert alert-success' style='padding-top:2px;font-size:11px;margin-bottom: 2px;'>\
								<a class='close'  data-dismiss='alert'>x</a>\
								  <div style='float:left;' id='team_name'><h5>"+ teamname+"</h5> </div>\
								  <div style='margin-left:87px;' id='odds'> "+odds+"</div>\
								  <div id='stakeLabel' style='margin-right:5px;float:left;'>Stake</div>\
								  <div id='valContainer' style='float:left;'>	<input id='stake' name='stake' type='text' style='height:15px;width:40px;margin-top:-2px;'class='span1 stake'></div>\
								  <div id='towinlabel' style='margin-left:5px;margin-right:2px;float:left;'> You Win  </div>\
								  <div id='towin' style=''>23</div>\
							  </div>";
		  //check if bet already exists in betslip with betid
		  if ($("#bet_"+$(betIdElement).attr('id')).length > 0 ){
			  alert('This bet is already in betslip');
		  } else {
		      //remove placebet button if already exists
			  //if ($("#placebet").length > 0 ){
				  //$("#placebet").remove();
			 // }
			  $('#bet_slip_container').append(betcontent);
			  $("#bet_"+$(betIdElement).attr('id')).bind('close', function () {
				alert('hi');
				stakeVal = $($($(this).children().get(4)).children().get(0)).val();
				if(stakeVal > 0) {
				    //alert(stakeVal);
					//alert(userCash);
					//userCash = userCash + stakeVal;
					//$('#user_cash').text("Cash "+userCash);
					//increaseCash(stakeVal, getUserCash());
				}
			  });
			  $(".stake").keyup(function() {
				//to allow only numericals in stake textbox
				if (isNaN($(this).val())) {
				   $(this).val(0);
				   $($($(this).parent().next().next())).text(0);
				} else {
				    var maxCharsAllowed = 5;
					if($(this).val().length <= maxCharsAllowed) {
						//Valid user input
						//check for user cash
						//alert(userCash);
						//alert($(this).val());
						//alert(Number($(this).val()));
						if(userCash >= Number($(this).val())) {
							oddsVal = $($(this).parent().prev().prev()).text();
							values= oddsVal.split('/');				
							towin=($(this).val()*parseFloat(values[0]/values[1])).toFixed(2);
							//alert(towin);
							$($($(this).parent().next().next())).text(towin);
							//userCash = userCash - Number($(this).val()) ;
							//alert(Number($(this).val()));
							//$('#user_cash').text("Cash "+userCash);
							//userCash = getUserCash();
						} else {
							showMessage("Oh snap! You do not have enough cash! Please add cash", 'red');
							$(this).val('');
							//$('#user_cash').text("Cash "+userCash);
						}
					} else {
						alert("Maximum Bet Limit Reached");
						$(this).val($(this).val().substring(0, maxCharsAllowed));						
					}
				}
			  });			  
		  }
		  
		  //placebet button implementation
		  if ($("#placebet").length > 0 ){
			 }
	}
	
	
	function getUserCash(){
		return $('#user_cash').text().split(' ')[1];
	}
	
	function showMessage(message, color) {
	    if(message.length > 0) {
			if(color=='red') {
				var alertHtml = "<div id='alertDiv' style='width:710px;margin-bottom:0px;text-align:center;' class='alert alert-error'><a class='close'  data-dismiss='alert'>x</a><strong>"+message+"</strong></div>";
			} else {
				var alertHtml = "<div id='alertDiv' style='width:710px;margin-bottom:0px;text-align:center;' class='alert alert-info'><a class='close'  data-dismiss='alert'>x</a>"+message+"</div>";
			}
			$("#bet_container").before(alertHtml);
			$("#alertDiv").bind('close', function () {
				alert('hi');
				//alert($($($(this).children().get(4)).children().get(0)).val());
			});
			//close alert after 10 seconds
			window.setTimeout(hideMessage, 10000);
		}		
	}
	
	function hideMessage() {
		if($("#alertDiv").length > 0) {		    
			$("#alertDiv").remove();
		}
	}
	
	function decreaseCash(amount, totalCash) {
		cashUpdate = totalCash - Number(amount);
		cashText = "Cash "+ cashUpdate;
		$('#user_cash').text(cashText);
		totalCash = cashUpdate;
	}
	
	function increaseCash(amount, totalCash) {
		//alert('increasing cash');
		cashUpdate =parseInt(totalCash,10) + parseInt(amount,10);
		//alert(cashUpdate);
		//alert(totalCash + amount);
		cashText = "Cash "+ cashUpdate;
		$('#user_cash').text(cashText);
	}
	
	function showMatch() {
			$('div#match_winner').show();
	}
