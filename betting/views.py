# Create your views here.
from betting.models import *
from datetime import datetime
from django.shortcuts import render_to_response
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

def placebets(request):
    if on_production_server:
        app_id = settings.FACEBOOK_APP_ID_MAIN
        app_uri = 'https://apps.facebook.com/cricbets/'
    else:
        app_id = settings.FACEBOOK_APP_ID_LOCAL
        app_uri = 'https://apps.facebook.com/cricbetslocal/'
    
    logger.info(app_id)
    return render_to_response('placebets.html', dict(app_id = app_id, app_uri=app_uri))

def home(request):
    logger.debug("In home(), POST = ", request.POST)
    user, created = User.objects.get_or_create(fb_id = request.POST['uid'] )
    request.session['user'] = user
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
    logger.info(home_bet_data)
    #return HttpResponse("hello")
    #TODO: return rendered HTML
    return render_to_response('user_home.html', dict(home_bet_data = home_bet_data, user_bets=user_bets))


def get_leader_board(request):
    friends = request.POST['friends']
    if friends:
        friend_uids = [f['uid'] for f in friends] + [request.session.get('user').fb_id]
        friend_data = User.objects.filter(fb_id__in = friend_uids).values("fb_id", "cash").order_by('rank')
    else:
        friend_data = []
    
    leader_data = User.objects.order_by('rank').values('fb_id', 'cash')[:10]
    
    return render_to_response('leader_board.html', dict(leader_data=leader_data, friend_data=friend_data))
    

def get_bets(request):
    event_id = request.GET.getattr('event_id', None)
    if event_id:
        match_bets = bet_data_views.get_match_bet_data(event_id)
        if match_bets:
            #TODO: return rendered HTML
            return match_bets
        else:
            return errors.MATCH_ID_NOT_FOUND
    else:
        return errors.MISSING_PARAMTER
    
def place_bets(request):
    user = request.session.get('user')
    if not user:
        return errors.USER_NOT_FOUND
    bets = request.POST.getattr()
    for bet in bets:
        #verify if bet is active
        #verify if bet odds are valid
        #verify if sufficient cash
        #place bet (create obj, deduct cash)
        #on success, return success, html to be pushed in recent bets and cash
        pass
    
def _home_bet_data(data):
    return_dict = dict(live=[], upcoming=[])
    for match in data['live_data']:
        return_dict['live'].append(dict(name=match['name'], id=match['match_obj'].id))
    
    for match in data['upcoming_data']:
        return_dict['upcoming'].append(dict(name=match['name'], id=match['match_obj'].id, date=match['date']))
        
    return return_dict