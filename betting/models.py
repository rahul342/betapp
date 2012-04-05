from django.db import models

# Create your models here.
class User(models.Model):
    fb_id = models.IntegerField()
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    cash = models.PositiveIntegerField(default=20)
    has_deactivated = models.BooleanField(default=False) 
    
    def __unicode__(self):
        return ("fbid=%s username=%s name=%s") % (self.fb_id, self.name, self.username)
    
class PlacedBets(models.Model):
    user = models.ForeignKey(User)
    bet_value = models.ForeignKey('bet_data_fetcher.BetValue')
    odds = models.FloatField()
    amount = models.PositiveIntegerField()
    is_resolved = models.BooleanField(default=False)
    add_time = models.DateTimeField(auto_now_add=True)
    
    