/* All Javascript functions of betting app will go into this file */	
	function invite_friends() {
		//FB.Canvas.setAutoResize();
		//specify redirect uri to handle requests
		$("div#bet_container").before("<div id='loading_image'><img style='margin-left:330px;margin-top:20px;' src='/static/images/loading.gif' /></div>");
		FB.api( {
					method: 'fql.query',
					query: 'select uid, name from user where is_app_user = 1 and uid in (SELECT uid2 FROM friend WHERE uid1 = me())'
				  },
				  function(response) {
				    appFriends=response;
					//store fuids in array
					var friends_arr = [];
					for (obj in appFriends) {
						friends_arr.push(appFriends[obj].uid);
					}
					FB.ui({
						method: 'apprequests',
						message: 'Become my Buddie in this cool betting application',
						filters: ['app_non_users'],
						title: 'Become my Buddie',
						exclude_ids: friends_arr
					},
					function (response) {
						console.log(response)
						$('#loading_image').remove();
						if (response && response.to) {
					   //if sucess do something
					   //How many people did the user invited?
						var showManyInvites = String(response.to).split(',').length;
						} else {
						  return false;
						}
					});
					
				  }
		);		
		
	}
	
	function show_bet_page(parent, event_id) {
		$.get("https://127.0.0.1:8001/getbets/",{event_id:event_id}, function(data) {
			  //TODO: Handle non-success cases
			if(data.result == "ok" ) {
				$("div#myModal").html("");
				$("div#myModal").append(data.html);
				$('#myModal').css({width: '850px','margin-left': function () { return -($(this).width() / 2); }, top:'35%'});
				$('#myModal').modal();
			} else if (data.result == "error") {
				showMessage('refresh', 'red', false );
			}	      
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
				  +"<div id=odds_"+$(betIdElement).attr('id')+" class='span2'><h5>"+odds +" x</h5></div>"
				  +"<div class='span3'><input id='stake_"+$(betIdElement).attr('id')+"' name='stake' type='text' style='height:15px;width:40px;margin-top:-2px;'></div>"
				 +" <div class='span7' id='you_win_"+$(betIdElement).attr('id')+"'>You win 0</div>"					  		
			 +"</div>"
			+"</div>";			
		  //check if bet already exists in betslip with betid
		  if ($("#bet_"+$(betIdElement).attr('id')).length > 0 ){
		  	  showMessage("bet_present", 'red', true);
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
						$("#you_win_"+$(betIdElement).attr('id')).text("You win " + toWin);
					}
				}
			  });			  
		  }		  
	}
	
	function placebet_click() {
	    var betArr = [];
	    var bet_cash=0;
	    if($('#bet_slip_container').children().length > 1) {
			$('#bet_slip_container').children().each(function(index) {
				//avoid betslip label
				if(index!=0) {
					var bet_id= $(this).attr('id').substring(4);
					if(!isNaN(parseInt(bet_id))) {
					stakeVal = parseInt($('#stake_'+bet_id).val());
					if(!isNaN(stakeVal)) {
						bet_cash += stakeVal;
						if(stakeVal != 0) {
							odds = $("#odds_"+bet_id).text().split(" ")[0];
							betArr.push({'bet_id' : bet_id, 'stake' : stakeVal, 'odds': odds});
						}
					}
				}
			}
			});
	    }
		//if bet array containts betlist values to post to server
		if(betArr.length > 0) {			
			if(bet_cash >= getUserCash()) {
				showMessage("less_cash", 'red', true);
			} else {
				//do ajax post toserver with fuid and betArr
				emptyBetList();				
				addNoBetsText("Placing Bets. Hold on.");	
				$.post('/placebets/', {'bet_arr': JSON.stringify(betArr)}, function(response) {
					emptyBetList();
					if(response.result == "ok") {				
						addNoBetsText("Bets successfully Placed");			
						showMessage("bet_success", 'blue', true);
						decreaseCash(bet_cash);
					}
					else {
						addNoBetsText("Please try again.");			
						showMessage("refresh", 'blue', true);
					}	
				});
				
			}
		} else {
	    	showMessage("no_bets", 'red', true);
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
				$(this).remove();				
			}
		});
	}
	
	function getUserCash(){
		return $('#user_cash').text().substring(1);
	}
	
	function showMessage(message, color, onModal) {
	    if(message.length > 0) {
	    	if(message == 'refresh') {
	    		msgText = "Oops! There was an error. Please refresh this page.";
	    	} else if (message == 'no_bets') {
	    		msgText = "Stake some money and place bets, punter!";
	    	} else  if(message == 'less_cash' ) {
	    		msgText = "Oh snap! You don't have enough cash to place bets.";
	    	} else if(message == "bet_success") {
	    		msgText = "Bets successfully placed & Fingers crossed."
	    	} else if(message == "odds expired") {
	    		msgText = "These odds have expired. Please try again."
	    	} else if(message == "bet_present") {
	    		msgText = "These bet is already present in the slip."
	    	}
	    	if(color=='red') {
				var alertHtml = "<div id='alertDiv' style='margin-bottom:0px;text-align:center;' class='alert alert-error'><a class='close'  data-dismiss='alert'>x</a><strong>"+msgText+"</strong></div>";
			} else {
				var alertHtml = "<div id='alertDiv' style='margin-bottom:0px;text-align:center;' class='alert alert-info'><a class='close'  data-dismiss='alert'>x</a>"+msgText+"</div>";
			}
	    	if(onModal) {
	    		$(".modal-body").before(alertHtml);
	    	}
	    	else {
	    		$("#bet_container").before(alertHtml);
	    	}
			$("#alertDiv").bind('close', function () {
				//for something if alert is closed
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
	
	function decreaseCash(amount) {
		cashUpdate = parseInt(getUserCash(),10) - Number(amount);
		$('#user_cash').text("$"+cashUpdate);
	}
	
	function increaseCash(amount) {
		cashUpdate = parseInt(getUserCash(),10) + parseInt(amount,10);
		$('#user_cash').text("$"+cashUpdate);
	}
	
	function setUserCash(amount) {
		$('#user_cash').text("$"+amount);
	}
	
	function showMatch() {
			$('div#match_winner').show();
	}
