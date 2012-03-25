from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    ('^channel/$', direct_to_template, {'template': 'channel.html'}),
    ('^start/$', direct_to_template,  {'template': 'fb_login.html'}),
#    (r'^facebook/', include('django_facebook.urls')),
    ('^$', direct_to_template, {'template': 'home.html'}),
    
)
