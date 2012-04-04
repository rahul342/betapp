from django.db import models


class Tournament(models.Model):
    name = models.CharField(max_length=500)
    betsite_url = models.URLField(verify_exists=False)
    
class Match(models.Model):
    name = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True)
    match_date = models.DateField()
    betsite_url = models.URLField(verify_exists=False)
    tournament = models.ForeignKey(Tournament, null=True)
    
    def __unicode__(self):
        return "<%s, %s>" % (self.name, str(self.match_date))
    
class BetCategory(models.Model):
    name = models.CharField(max_length=500)
    
    def __unicode__(self):
        return self.name
    
class Bet(models.Model):
    category = models.ForeignKey(BetCategory)
    match = models.ForeignKey(Match, null=True)
    tournament = models.ForeignKey(Tournament, null=True)
    
    def __unicode__(self):
        if self.tournament != None:
            return "<Tournament, %s>" % str(self.category)
        else:
            return "<%s, %s>" % (str(self.category), (self.match))
    
class BetValue(models.Model):
    name = models.CharField(max_length=500)
    bet = models.ForeignKey(Bet)
    is_winner = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "{%s, %s}" % (self.name, str(self.bet)) 
