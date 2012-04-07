/* All Javascript functions of betting app will go into this file */	
	function invite_friends() {
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
	}
	
	function show_bet_page(event_id) {
		$("div#myModal").load('https://127.0.0.1:8001/placebets/', function(response, status, xhr) {
			  if (status == "error") {
				var msg = "Sorry but there was an error: ";
				alert(msg + xhr.status + " " + xhr.statusText);
			  }
			  $('#myModal').css({width: '800px','margin-left': function () { return -($(this).width() / 2); }, top:'35%'});
			  $('#myModal').modal();					  				  
				  
		});			
	}
	
	function appendBet(betname, teamname, betIdElement) {
			var odds=$(betIdElement).text();
			//remove no bets placed intially
			if ($("#no_bets").length > 0 ){
				$("#no_bets").remove();
			 }
			//user cash is hard coded for now..Need to get it from cash div			
			var betcontent="<div id='bet_"+$(betIdElement).attr('id')+"' class='alert alert-success' style='padding-bottom:0px;padding-right:0px;padding-top:2px;font-size:11px;margin-bottom: 2px;'>"
			 +" <a class='close'  style='margin-right:25px;' data-dismiss='alert'>x</a>"
			  +"<div class='row-fluid'>"
				+"  <div class='span12' style='margin-top:-10px;'>"+betname+" : "+teamname+"</div>"					  		
			 +"</div>"
			 +"<div class='row-fluid' style='margin-top:10px;'>"
				  +"<div class='span2'>"+odds +" x </div>"
				  +"<div class='span3'><input id='stake_"+$(betIdElement).attr('id')+"' name='stake' type='text' style='height:15px;width:40px;margin-top:-2px;'></div>"
				 +" <div class='span7' id='you_win_"+$(betIdElement).attr('id')+"'>You win 0</div>"					  		
			 +"</div>"
			+"</div>";			
		  //check if bet already exists in betslip with betid
		  if ($("#bet_"+$(betIdElement).attr('id')).length > 0 ){
			  alert('This bet is already in betslip');
		  } else {
		     $('#bet_slip_container').append(betcontent);
			 $("#bet_"+$(betIdElement).attr('id')).bind('close', function () {
				//close handler for one bet list
				if( $('#bet_slip_container').children().length == 2) {
					//all bets removed
					addNoBetsText("No Bets Placed");
				}
				
			  });
			  $("#stake_"+$(betIdElement).attr('id')).keyup(function() {
				//to allow only numericals in stake textbox
				if (isNaN($(this).val())) {
				   $(this).val("");
				   $("#you_win_"+$(betIdElement).attr('id')).text("You win 0");
				} else {
				    var maxCharsAllowed = 5;
					if($(this).val().length < maxCharsAllowed) {
						//Valid user input
						//check for user cash
						toWin=($(this).val()*parseFloat(odds)).toFixed(2);
						$("#you_win_"+$(betIdElement).attr('id')).text("You win "+toWin);						
					} else {
						// If Maximum Bet Limit Reaches
						$(this).val($(this).val().substring(0, maxCharsAllowed));
						toWin=($(this).val()*parseFloat(odds)).toFixed(2);
						$("#you_win_"+$(betIdElement).attr('id')).text("You win "+toWin);
					}
				}
			  });			  
		  }		  
	}
	
	function placebet_click() {
		alert("placebt click");
	    var betArr = [];
	    var bet_cash=0;
	    if($('#bet_slip_container').children().length > 1) {
			$('#bet_slip_container').children().each(function(index) {
				//avoid betslip label
				if(index!=0) {
					var bet_id= $(this).attr('id').substring(4);
					alert(bet_id);
					if(!isNaN(parseInt(bet_id))) {
					stakeVal = parseInt($('#stake_'+bet_id).val());
					if(!isNaN(stakeVal)) {
						bet_cash += stakeVal;
						if(stakeVal != 0) {
							betArr.push({'betId' : bet_id, 'stake' : stakeVal});
						}
					}
				}
			}
			});
	    }
		//if bet array containts betlist values to post to server
		if(betArr.length > 0) {			
			alert(bet_cash);
			if(bet_cash >= getUserCash()) {
				showMessage("You don't have enough cash. Please buy cash", 'red');
			} else {
				//do ajax post toserver with fuid and betArr
				emptyBetList();
				addNoBetsText("Bets successfully Placed");			
				showMessage("Bets Placed successfully", 'blue');
			}
		} else {
	    	showMessage("Please place bets", 'red');
	    }
	}
	
	function addNoBetsText(message) {
		$('#bet_slip_container').append("<div id='no_bets'>"+message+" </div>");
	}
	
	function emptyBetList() {
		$('#bet_slip_container').children().each(function(index) {
			//avoid betslip label
			if(index!=0) {
				var bet_id= $(this).attr('id').substring(4);
				//alert(bet_id);
				//alert($('#you_win_'+bet_id).text());
				$(this).remove();				
			}
		});
	}
	
	function getUserCash(){
		return $('#user_cash').text().substring(1);
	}
	
	function showMessage(message, color) {
	    if(message.length > 0) {
			if(color=='red') {
				var alertHtml = "<div id='alertDiv' style='margin-bottom:0px;text-align:center;' class='alert alert-error'><a class='close'  data-dismiss='alert'>x</a><strong>"+message+"</strong></div>";
			} else {
				var alertHtml = "<div id='alertDiv' style='margin-bottom:0px;text-align:center;' class='alert alert-info'><a class='close'  data-dismiss='alert'>x</a>"+message+"</div>";
			}
			$(".modal-body").before(alertHtml);
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
