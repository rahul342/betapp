# Create your views here.
from betting.models import *
from datetime import datetime
from decorators import jsonify
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from djangoappengine.utils import on_production_server
import bet_data_fetcher.views as bet_data_views
import errors
import logging
import settings
import time
logger = logging.getLogger(__name__)


def start(request):
    if on_production_server:
        app_id = settings.FACEBOOK_APP_ID_MAIN
        app_uri = 'https://apps.facebook.com/cricbets/'
        server_url = settings.SERVER_URL_MAIN
    else:
        app_id = settings.FACEBOOK_APP_ID_LOCAL
        app_uri = 'https://apps.facebook.com/cricbetslocal/'
        server_url = settings.SERVER_URL_LOCAL
    
    logger.info(app_id)
    return render_to_response('start.html', dict(app_id = app_id, app_uri=app_uri, server_url=server_url))

def home(request):
    logger.debug("In home(), POST = ", request.POST)
    user, created = User.objects.get_or_create(fb_id = request.POST['uid'])
    request.session.flush()
    request.session['user'] = user
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
    dummy_user_bets = [dict(match_name='Rajashtan v Deccan', bet_name='Highest Opening Partnerships', bet_value_name='Rajasthan Royals',
                            cash=200, status="Lost", date=datetime.today().date()),
                       dict(match_name='Rajashtan v Deccan', bet_name='Highest Opening Partnerships', bet_value_name='Rajasthan Royals',
                            cash=200, status="Won", date=datetime.today().date()),
                       dict(match_name='Rajashtan v Deccan', bet_name='Highest Opening Partnerships', bet_value_name='Rajasthan Royals',
                            cash=200, status="Cancelled", date=datetime.today().date()),
                       dict(match_name='Rajashtan v Deccan', bet_name='Highest Opening Partnerships', bet_value_name='Rajasthan Royals',
                            cash=200, status="Placed", date=datetime.today().date())]
    return render_to_response('user_home.html', dict(home_bet_data = home_bet_data, user_bets=dummy_user_bets))


def get_leader_board(request):
    friends = request.POST['friends']
    if friends:
        friend_uids = [f['uid'] for f in friends] + [request.session.get('user').fb_id]
        friend_data = User.objects.filter(fb_id__in = friend_uids).values("fb_id", "cash", "rank_cash").order_by('rank_cash')
    else:
        friend_data = []
    
    leader_data = User.objects.order_by('rank_cash').values('fb_id', 'cash', 'rank_cash')[:10]
    
    return render_to_response('leader_board.html', dict(leader_data=leader_data, friend_data=friend_data))
    
@jsonify
def get_bets(request):
    event_id = request.GET.getattr('event_id', None)
    if not event_id:
        raise errors.MISSING_PARAMETER()
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
                col0_ht= col0_ht + len(bet['values'])
                cols[0].append(bet)
            else:
                col1_ht= col1_ht + len(bet['values'])
                cols[1].append(bet)
        return render_to_string('place_bets.html', dict(name=bet_data['name'], date=bet_data['date'], columns=cols))
    else:
        raise errors.EVENT_ID_NOT_FOUND()
    
def place_bets(request):
    user = request.session.get('user')
    if not user:
        raise errors.USER_NOT_FOUND
    #bets = request.POST.getattr()
    #for bet in bets:
        #verify if bet is active
        #verify if bet odds are valid
        #verify if sufficient cash
        #place bet (create obj, deduct cash)
        #on success, return success, html to be pushed in recent bets and cash
     #   pass
    return render_to_response('place_bets.html')
def _home_bet_data(data):
    return_dict = dict(live=[], upcoming=[])
    for match in data['live_data']:
        return_dict['live'].append(dict(match_name=match['name'], id=match['match_obj'].id))
    
    for match in data['upcoming_data']:
        return_dict['upcoming'].append(dict(match_name=match['name'], id=match['match_obj'].id, date=match['date']))
        
    return return_dict