# Create your views here.
from bet_data_fetcher.models import *
from django.conf import settings
from django.core.cache import cache
from exceptions import *
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def _fetch_data_from_sites():
    """ Fetches data from site classes in bet_sites.
    Supposed to iterate through to fetch
    """
    from bet_sites import StanJamer
    data = StanJamer().get_data()
    if reduce(lambda x, y: bool(x) or bool(y), data.values()):
        logger.info("Fetched data from StanJamer")
        return data
    else:
        #TODO: try other class
        return data
    
def _map_data_to_obj(data):
    def match_bet_values(bet_value_arr, bet_obj):
        bet_val_objs = BetValue.objects.filter(bet=bet_obj)
        logger.debug("Found %d bet values objects for %s bet" % (len(bet_val_objs), str(bet_obj)))
        for bet_val_dict in bet_value_arr:
            for bet_val_obj in bet_val_objs:
                if bet_val_obj.name == bet_val_dict['name']:
                    bet_val_dict['bet_val_obj'] = bet_val_obj
                    break
            if not bet_val_dict.has_key("bet_obj"):
                logger.info('Bet value %s does not exist for %s bet. Creating one.' % (bet_val_dict['name'], str(bet_obj)))
                bet_val_obj = BetValue.objects.create(name=bet_val_dict['name'], bet=bet_obj)
                bet_val_dict['bet_val_obj'] = bet_val_obj
        
    if data['tournament_data']:
        tourn_bet_obj = Bet.objects.exclude(tournament = None)
        if tourn_bet_obj:
            logger.debug('Tournament bet - %s found' % str(tourn_bet_obj))
            tourn_bet_obj = tourn_bet_obj[0]
        else:
            logger.info('No Tournament obj exists. Creating one.')
            categ, created = BetCategory.objects.get_or_create(name="Tournament Winner")
            if created:
                logger.info("New Bet Category %s created" % str(categ))
            tourn_bet_obj = Bet.objects.create(category=categ, match=None, tournament=Tournament.objects.all()[0])
        data['tournament_data']['tourn_obj'] = tourn_bet_obj
        match_bet_values(data['tournament_data']['values'], tourn_bet_obj)
                
    for matches_data in [data['live_data'], data['upcoming_data']]:
        for match_data in matches_data:
            logger.debug("Got match from stie - %s, %s" % (str(match_data['date'].date()), match_data['name']))
            match_data['match_obj'] = match_obj = Match.objects.get(match_date=match_data['date'].date(), name=match_data['name'])
            match_bet_objs = Bet.objects.filter(match=match_obj)
            logger.debug("Found %d bets for match - %s" % (len(match_bet_objs), str(match_obj)))
            for bet in match_data['bets']:
                for match_bet_obj in match_bet_objs:
                    if match_bet_obj.category.name == bet['name']:
                        bet['bet_obj'] = match_bet_obj
                        break
                if not bet.has_key('bet_obj'):
                    logger.info("Bet %s doesn't exists for match %s. Create one" % (bet['name'], str(match_obj)))
                    categ, created = BetCategory.objects.get_or_create(name=bet['name'])
                    if created:
                        logger.info("New Bet Category %s created" % str(categ))
                    match_bet_obj = Bet.objects.create(match=match_obj,category=categ)
                    bet['bet_obj'] = match_bet_obj
                match_bet_values(bet['values'], match_bet_obj)
                
def get_all_bet_data():
    data = cache.get('bet_data')
    if not data:
        data = _fetch_data_from_sites()
        _map_data_to_obj(data)
        cache.set('bet_data', data, settings.REFRESH_TIME)
    return data

def get_match_bet_data(match_id):
    if match_id is None:
        return
    data = get_all_bet_data()
    for match_bet_data in data['live_data'] + data['upcoming_data']:
        if match_bet_data['match_obj'].id == match_id:
            return match_bet_data
    return None

def get_bet_value_data(bet_value_id):
    if bet_value_id is None:
        return

    data = get_all_bet_data()
    for bet_val_data in data['tournament_data']['values'] + [i for match in data['upcoming_data'] for bet in match['bets'] for i in bet['values']]:
        if bet_val_data['bet_val_obj'].id == bet_value_id:
            return bet_val_data
    return None
        
        
        
        