from bs4 import BeautifulSoup
from datetime import datetime
from bet_data_fetcher.utils import *
import re, urllib2, logging

logger = logging.getLogger(__name__)

class StanJamer:
    _map = [
            ("Match Prices", "Match Winner"), 
            ("Highest Opening Partnership", "Highest Opening Partnership"),
            ("Highest Score 1st 6 Overs","Highest Score 1st 6 Overs"),
            ("Team of Top Runscorer","Team of Top Runscorer"),
            ("Best Economy Rate", "Best Economy Rate"),
            ("Most Sixes", "Most Sixes"),
            ("Top (.+) Batsman.*", "Top %s Batsman"),
            ("Top (.+) Wicket-taker.*", "Top %s Wicket-taker"),
            ("Will There Be A Century?", "Will There Be A Century?"),
        ]
    _tournaments_urls = [r"http://xml.stanjames.com/cricket-ante-post.XML", r"ftp://xml.stanjames.com/cricket-ante-post.XML"]
    _live_match_urls = [r"http://xml.stanjames.com/Cricket-In-Running.XML", r"ftp://xml.stanjames.com/Cricket-In-Running.XML"]
    _upcoming_match_urls = ["http://xml.stanjames.com/cricket.XML","ftp://xml.stanjames.com/cricket.XML"]
    def __init__(self):
        pass
    
    def _map_data(self):
        pass
    
    def _get_tournament_data(self, data):
        return_val = dict()
        try:
            xml = BeautifulSoup(data, 'xml')
        except TypeError:
            return return_val
        ipl_tourn = xml.find('event',dict(eventid='1821212.20'))
        if ipl_tourn is None:
            return return_val

        bet = ipl_tourn.find('bettype',dict(name="Tournament Outright"))
        if bet is None  or bet['suspended']  == 'true':
            return return_val
        return_val['date'] = datetime.strptime(bet['bet-start-date']+bet['bet-start-time'], '%Y%m%d%H%M')
        return_val['values'] = []
        for bet_val in bet.find_all('bet'):
            return_val['values'].append(dict(name=bet_val['name'], odd = bet_val['price']))
        
        return return_val
    
    def _get_matched_betname(self, bet_name):
        for tup in StanJamer._map:
            match = re.search(tup[0], bet_name, flags=re.IGNORECASE)
            if match is None:
                continue
            logger.info("Matched %s with %s" % (bet_name, tup[0]))
            if match.groups():
                return tup[1] % match.groups()
            else:
                return tup[1]
        return None
            
            
    def _get_match_data(self, data):
        return_val = []
        try:
            xml = BeautifulSoup(data, 'xml')
        except TypeError:
            return return_val
        logger.info("total events = %d" % len(xml.find_all('event')))
        matches = filter(is_valid_match_names('name'), xml.find_all('event'))
        logger.info("Found %d matches" % len(matches))
        for match in matches:
            match_dict = dict(name=match['name'], bets = [], date = datetime.strptime(match['date']+match['time'], '%Y%m%d%H%M'))
            bets = match.find_all('bettype')
            logger.info("Match %s has total %d bets" % (match['name'],len(bets)))
            for bet in bets:
                if bet['suspended'] == 'true':
                    continue
                matched_betname = self._get_matched_betname(bet['name'])
                if matched_betname is not None:
                    logger.info("Matched %s bet" % matched_betname)
                    bet_data = dict(name = matched_betname, is_running = bool(bet['inrunning']), values = [])
                    for bet_val in bet.find_all('bet'):
                        bet_data['values'].append(dict(name=bet_val['name'], odd = bet_val['price']))
                    match_dict['bets'].append(bet_data)
            return_val.append(match_dict)
        
        return return_val
        
    def _get_live_match_data(self, data):
        logger.info("Geting Live data")
        return self._get_match_data(data)
            
    def _get_upcoming_match_data(self, data):
        return self._get_match_data(data)
    
    
    def _fetch_xml_from_url(self, urls):
        """
        Helper function to fetch data after iterating in urls. Checks for outdated time and Urlerror.
        If could not get data, returns None
        """
        data = None
        for url in urls:
            try:
                data_f = urllib2.urlopen(url)
            except urllib2.URLError:
                continue
            data = data_f.read()
            #fetched data, check if the xml is outdated
            category = BeautifulSoup(data, 'xml').find('category')
            if category is not None:
                update_time = datetime.strptime(category['timeGenerated'], "%Y-%m-%dT%H:%M:%S")
                if (datetime.now() - update_time).days > 1:
                    data = None
                    continue
                else:
                    return data
        return data
    
    def get_data(self):
        return dict(tournament_data = self._get_tournament_data(self._fetch_xml_from_url(StanJamer._tournaments_urls)),
                    upcoming_data = self._get_upcoming_match_data(self._fetch_xml_from_url(StanJamer._upcoming_match_urls)),
                    live_data = self._get_live_match_data(self._fetch_xml_from_url(StanJamer._live_match_urls))
                    )
                     
