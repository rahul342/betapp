# Create your views here.
from betting.models import *
from django.core.cache import cache
from django.shortcuts import render_to_response
from djangoappengine.utils import on_production_server
import bet_data_fetcher.views as bet_data_views
import errors
import logging
import settings
logger = logging.getLogger(__name__)


def start(request):
    if on_production_server:
        app_id = settings.FACEBOOK_APP_ID_MAIN
        app_uri = 'https://apps.facebook.com/cricbets/'
    else:
        app_id = settings.FACEBOOK_APP_ID_LOCAL
        app_uri = 'https://apps.facebook.com/cricbetslocal/'
    
    logger.info(app_id)
    return render_to_response('fb_login.html', dict(app_id = app_id, app_uri=app_uri))


def home(request):
    user, created = User.objects.get_or_create(fb_id = request.GET['fb_id'])
    if created:
        user.name = request.GET['name']
        user.username = request.GET['username']
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
    
    #TODO: return rendered HTML
    
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
    
