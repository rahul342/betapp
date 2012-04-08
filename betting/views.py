# Create your views here.
from betting.models import *
from datetime import datetime
from decorators import jsonify
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.utils import simplejson
from djangoappengine.utils import on_production_server
import bet_data_fetcher.views as bet_data_views
import errors
import logging
import settings
import time
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def start(request):
    if on_production_server:
        app_id = settings.FACEBOOK_APP_ID_MAIN
        app_uri = 'https://apps.facebook.com/cricbets/'
        server_url = settings.SERVER_URL_MAIN
    else:
        app_id = settings.FACEBOOK_APP_ID_LOCAL
        app_uri = 'https://apps.facebook.com/cricbetslocal/'
        server_url = settings.SERVER_URL_LOCAL

    return render_to_response('start.html', dict(app_id = app_id, app_uri=app_uri, server_url=server_url))

def home(request):
    logger.debug("In home(), POST = ", request.POST)
    user, created = User.objects.get_or_create(fb_id = request.POST['uid'])
    request.session.flush()
    request.session['user_id'] = user.id
    request.session['fb_id'] = user.fb_id
    request.session.set_expiry(int(request.POST['expiry']))
    request.session['timezone'] = float(request.POST['timezone'])
    
    
    if created:
        user.name = request.POST['name']
        user.username = request.POST['user_name']
        user.cash_update_time = datetime.now()
        user.add_time = datetime.now()
        user.save()
        logger.info("Created new user - %s" % str(user))
    elif user.has_deactivated == True:
        user.has_deactivated = False
        user.save()
    
    
    bet_data = bet_data_views.get_all_bet_data()
    if not created:
        user_bets = [i.get_ui_dict() for i in PlacedBets.objects.filter(user=user).select_related().order_by('-add_time')]
    else:
        user_bets = []
    home_bet_data = _home_bet_data(bet_data)
    logger.debug(home_bet_data)
    #return HttpResponse("hello")
    #TODO: return rendered HTML
    return render_to_response('user_home.html', dict(home_bet_data = home_bet_data, user_bets=user_bets, user=user))


def get_leader_board(request):
    friends = request.POST['friends']
    if friends:
        friend_uids = [f['uid'] for f in friends] + [request.session.get('fb_id')]
        friend_data = User.objects.filter(fb_id__in = friend_uids).values("fb_id", "cash", "rank_cash").order_by('rank_cash')
    else:
        friend_data = []
    
    leader_data = User.objects.order_by('rank_cash').values('fb_id', 'cash', 'rank_cash')[:10]
    
    return render_to_response('leader_board.html', dict(leader_data=leader_data, friend_data=friend_data))
    
@jsonify
def get_bets(request):
    event_id = request.GET.get('event_id', None)
    if not event_id:
        raise errors.MISSING_PARAMETER()
    event_id = int(event_id)
    if event_id == -1:
        bet_data = bet_data_views.get_tournament_bet_data()
    else:
        bet_data = bet_data_views.get_match_bet_data(event_id)
    if bet_data:
        #First split into columns
        cols = [[],[]]
        col0_ht = col1_ht = 0 #height of the HTML columsn ~ number of bet values
        for bet in bet_data['bets']:
            if col0_ht == 0 or col0_ht <= col1_ht:
                col0_ht= col0_ht + len(bet['values']) + 1
                cols[0].append(bet)
            else:
                col1_ht= col1_ht + len(bet['values']) + 1
                cols[1].append(bet)
        return render_to_string('place_bets.html', dict(name=bet_data['name'], date=bet_data['date'], columns=cols))
    else:
        raise errors.EVENT_ID_NOT_FOUND()
    
@jsonify
def place_bets(request):
    user = User.objects.get(id=request.session.get('user_id'))
    if not user:
        raise errors.USER_NOT_FOUND
    bets = request.POST.get('bet_arr', None)
    if not bets:
        raise errors.MISSING_PARAMETER;
    bets = simplejson.loads(bets)
    if not bets:
        raise errors.MISSING_PARAMETER
    for bet in bets:
        bet_val_data = bet_data_views.get_bet_value_data(int(bet['bet_id']))
        if not bet_val_data:
            raise errors.BET_ID_NOT_FOUND
        #TODO: verify if bet is active
        if bet_val_data['odd'] != float(bet['odds']):
            raise errors.BET_ODD_EXPIRED
            
        stake = int(bet['stake'])
        if user.cash - stake < 0:
            raise errors.NOT_ENOUGH_CASH
        #place bet (create obj, deduct cash)
        PlacedBets.objects.create(user=user, bet_value=bet_val_data['bet_val_obj'], odds=bet_val_data['odd'], amount=stake)
        user.cash = user.cash - stake
        user.save()
    return "success"

def _home_bet_data(data):
    return_dict = dict(live=[], upcoming=[])
    for match in data['live_data']:
        return_dict['live'].append(dict(match_name=match['name'], id=match['match_obj'].id))
    
    for match in data['upcoming_data']:
        return_dict['upcoming'].append(dict(match_name=match['name'], id=match['match_obj'].id, date=match['date']))
        
    return return_dict