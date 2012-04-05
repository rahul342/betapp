# Create your views here.
from betting.models import *
from django.core.cache import cache
from django.shortcuts import render_to_response
from djangoappengine.utils import on_production_server
from datetime import datetime
import time
import bet_data_fetcher.views as bet_data_views
import errors
import logging
import settings
from django.http import HttpResponse
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

def userhome(request):
    if on_production_server:
        app_id = settings.FACEBOOK_APP_ID_MAIN
        app_uri = 'https://apps.facebook.com/cricbets/'
    else:
        app_id = settings.FACEBOOK_APP_ID_LOCAL
        app_uri = 'https://apps.facebook.com/cricbetslocal/'
    
    logger.info(app_id)
    return render_to_response('userhome.html', dict(app_id = app_id, app_uri=app_uri))

def home(request):
    logger.info('in home view')
    logger.info(request.POST)
    time.sleep(5)
    user, created = User.objects.get_or_create(fb_id = request.POST['uid'] )
    if created:
        user.name = request.POST['name']
        user.username = request.POST['username']
        user.cash_update_time = datetime.now()
        user.add_time = datetime.now()
        user.save()
        logger.info("Created new user - %s" % str(user))
    elif user.has_deactivated == True:
        user.has_deactivated = False
        user.save()
    
    leader = User.objects.order_by('cash').values('fb_id', 'name', 'username', 'cash')[:10]
    #friend_leader = User.objects.filter(fb_id__in = friends_list)
    bet_data = bet_data_views.get_all_bet_data()
    if not created:
        user_bets = PlacedBets.objects.filter(user=user).select_related()
    else:
        user_bets = []
    home_bet_data = _home_bet_data(bet_data)
    logger.info(home_bet_data)
    #return HttpResponse("hello")
    #TODO: return rendered HTML
    return render_to_response('user_home.html', dict(home_bet_data = home_bet_data, leader=leader))
def get_match_bets(request):
    match_id = request.GET.getattr('match_id', None)
    if match_id:
        match_bets = bet_data_views.get_match_bet_data(match_id)
        if match_bets:
            #TODO: return rendered HTML
            return match_bets
        else:
            return errors.MATCH_ID_NOT_FOUND
    else:
        return errors.MISSING_PARAMTER
    
def place_bets(request):
    #use sessions for user id
    #configure sessoins
    bets = request.POST.getattr()
    
def _home_bet_data(data):
    return_dict = dict(live=[], upcoming=[])
    for match in data['live_data']:
        return_dict['live'].append(dict(name=match['name'], id=match['match_obj'].id))
    
    for match in data['upcoming_data']:
        return_dict['upcoming'].append(dict(name=match['name'], id=match['match_obj'].id, date=match['date']))
        
    return return_dict