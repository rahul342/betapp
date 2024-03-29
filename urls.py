from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from betting import views

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    ('^channel/$', direct_to_template, {'template': 'channel.html'}),
    ('^start/$', views.start),
    ('^home/$', views.home),
    ('getbets/$', views.get_bets),
	('^placebets/$', views.place_bets),	
    ('^fetchbets/$', views.get_bets),
    ('^updatefreecash/$', views.update_free_cash),
    ('^addcash/$', views.add_cash),
#    ('^$', start),
#    (r'^facebook/', include('django_facebook.urls')),
    ('^$', direct_to_template, {'template': 'home.html', 'extra_context': {'app_id':'direct_to_template'}}),
    
)
