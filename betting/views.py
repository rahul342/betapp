# Create your views here.
from django.shortcuts import render_to_response
from django.core.cache import cache
from djangoappengine.utils import on_production_server
from betting.models import *
import logging, settings
logger = logging.getLogger(__name__)


def start(request):
    if on_production_server:
        app_id = settings.FACEBOOK_APP_ID_MAIN
        app_uri = 'https://apps.facebook.com/cricbets/'
    else:
        app_id = settings.FACEBOOK_APP_ID_LOCAL
        app_uri = 'https://apps.facebook.com/cricbetslocal/'
    
    logger.info(app_id)
    return render_to_response('user_bet_home.html', dict(app_id = app_id, app_uri=app_uri))

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
    user, created = User.objects.get_or_create(fb_id = request.GET['fb_id'])
    if created:
        user.name = request.GET['name']
        user.username = request.GET['username']
        user.save()
    elif user.has_deactivated == True:
        user.has_deactivated = False
        user.save()
    
    leader = User.objects.order_by('cash').values('fb_id', 'name', 'username', 'cash')[:10]
    #friend_leader = User.objects.filter(fb_id__in = friends_list)
    #Check cache, if betting data exists
    #else fetch, *process* and store in cache
    #TODO: can check the checksum with last cached, then increase the time 
    betting_data = cache.get('betting_data')
    if betting_data is None:
        pass
       # fetch & process betting data
       
    
    
        