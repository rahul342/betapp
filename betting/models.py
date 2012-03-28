from django.db import models


class Tournament(models.Model):
    name = models.CharField(max_length=500)
    bet365_url = models.URLField(verify_exists=False)
   
class Match(models.Model):
    name = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True)
    bet365_url = models.URLField(verify_exists=False)
    tournament = models.ForeignKey(Tournament, null=True)
    
class BetCategory(models.Model):
    name = models.CharField(max_length=500)

class Bet(models.Model):
    category = models.ForeignKey(BetCategory)
    match = models.ForeignKey(Match, null=True)
    tournament = models.ForeignKey(Tournament, null=True)
    
class BetValue(models.Model):
    name = models.CharField(max_length=500)
    bet = models.ForeignKey(Bet)
    is_winner = models.BooleanField(default=False)

# Create your models here.
class User(models.Model):
    fb_id = models.IntegerField()
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    cash = models.PositiveIntegerField(default=20)
    has_deactivated = models.BooleanField(default=False) 
    
class PlacedBets(models.Model):
    user = models.ForeignKey(User)
    bet_value = models.ForeignKey(BetValue)
    odds = models.FloatField()
    amount = models.PositiveIntegerField()
    is_resolved = models.BooleanField(default=False)
    
    