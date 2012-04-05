from django.db import models

# Create your models here.
class User(models.Model):
    fb_id = models.IntegerField()
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    cash = models.PositiveIntegerField(default=200)
    has_deactivated = models.BooleanField(default =False) 
    cash_update_time = models.DateTimeField(null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    
    def __unicode__(self):
        return ("fbid=%s username=%s name=%s") % (self.fb_id, self.name, self.username)
    
class PlacedBets(models.Model):
    user = models.ForeignKey(User)
    bet_value = models.ForeignKey('bet_data_fetcher.BetValue')
    odds = models.FloatField()
    amount = models.PositiveIntegerField()
    add_time = models.DateTimeField(auto_now_add=True)
    
    def get_status_and_cash(self):
        if self.bet_value.bet.is_cancelled:
            return "Cancelled", 0
        elif self.bet_value.bet.is_resolved: 
            if self.bet_value.is_winner:
                return "Won", round(self.amount * self.odds)
            else:
                return "Lost", self.amount
        else:
            return "Placed", self.amount
        
    def get_ui_dict(self):
        if self.bet_value.bet.match:
            top_name = self.bet_value.bet.match.get_shortened_name()
        else:
            top_name = "IPL 2012"
        
        name = self.bet_value.bet.get_name()
        value_name = self.bet_value.name
        status, cash = self.get_status_and_cash()
        
        return dict(top_name=top_name, name=name, value_name=value_name, status=status, cash=cash)
    
    