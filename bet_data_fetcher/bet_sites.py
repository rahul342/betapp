from bs4 import BeautifulSoup
from datetime import datetime
from bet_data_fetcher.utils import *
import re, urllib2, logging

logger = logging.getLogger(__name__)

class StanJamer:
    _map = [
            ("Match Prices|Match Winner", "Match Winner"), 
            ("Highest Opening Partnership", "Highest Opening Partnership"),
            ("Highest Score 1st 6 Overs","Highest Score 1st 6 Overs"),
            ("Team of Top Runscorer","Team of Top Runscorer"),
            ("Best Economy Rate", "Best Economy Rate"),
            ("Most Sixes", "Most Sixes"),
            ("Top (.+) Batsman.*", "Top %s Batsman"),
            ("Top (.+) Wicket-taker.*", "Top %s Wicket-taker"),
            ("Will There Be A Century?", "Will There Be A Century?"),
            ("Next Man Out", "Next Man Out"),
            ("(.+) Total Runs 3-Way \(20 Overs\)","%s Total Runs 3-Way (20 Overs)"),
            ("(.+) Total Runs 2-Way \(20 Overs\)", "%s Total Runs 2-Way (20 Overs)"),
            ("(.+) Total Runs \(Odd/Even\)", "%s Total Runs (Odd/Even)"),
            ("(.+) Runs 1st 6 Overs \(2-Way\)", "%s Runs 1st 6 Overs (2-Way)"),
            ("(.+) Warriors Wicket Dismissal Method", "%s Warriors Wicket Dismissal Method"),
        ]
    _tournaments_urls = [r"http://xml.stanjames.com/cricket-ante-post.XML", r"ftp://xml.stanjames.com/cricket-ante-post.XML"]
    _match_urls = ["http://xml.stanjames.com/cricket.XML","ftp://xml.stanjames.com/cricket.XML"]
    def __init__(self):
        pass
    
    def _map_data(self):
        pass
    
    def _get_tournament_data(self, data):
        return_val = dict(name="Indian Premier League 2012", date=datetime.today(), bets=[])
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
        bet_dict = dict()
        bet_dict['name'] = "Tournament Winner"
        bet_dict['date'] = datetime.strptime(bet['bet-start-date']+bet['bet-start-time'], '%Y%m%d%H%M')
        bet_dict['values'] = []
        for bet_val in bet.find_all('bet'):
            bet_dict['values'].append(dict(name=bet_val['name'], odd = convert_fraction_to_decimal(bet_val['price'])))
            
        return_val['bets'].append(bet_dict)
        
        
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
            
            
    def _get_matches_data(self, data):
        return_val = dict(live_data=[], upcoming_data=[])
        try:
            xml = BeautifulSoup(data, 'xml')
        except TypeError:
            return return_val
        logger.info("total events = %d" % len(xml.find_all('event')))
        matches = filter(is_valid_match_names('name'), xml.find_all('event'))
        logger.info("Found %d matches" % len(matches))
        for match in matches:
            if match['date'].strip() != '':
                live = False
                match_dict = dict(name=match['name'], bets = [], date = datetime.strptime(match['date']+match['time'], '%Y%m%d%H%M'))
            else:
                live = True
                match_dict = dict(name=match['name'], bets = [], date = datetime.now())
            bets = match.find_all('bettype')
            logger.info("Match %s has total %d bets" % (match['name'],len(bets)))
            for bet in bets:
                if bet['suspended'] == 'true':
                    continue
                matched_betname = self._get_matched_betname(bet['name'])
                if matched_betname is not None:
                    bet_data = dict(name = matched_betname, is_running = bool(bet['inrunning']), values = [])
                    for bet_val in bet.find_all('bet'):
                        bet_data['values'].append(dict(name=bet_val['name'], odd = convert_fraction_to_decimal(bet_val['price'])))
                    match_dict['bets'].append(bet_data)
            if live:
                return_val['live_data'].append(match_dict)
            else:
                return_val['upcoming_data'].append(match_dict)
        
        return return_val
        
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
        matches_data = self._get_matches_data(self._fetch_xml_from_url(StanJamer._match_urls))
        return dict(tournament_data = self._get_tournament_data(self._fetch_xml_from_url(StanJamer._tournaments_urls)),
                    upcoming_data = matches_data['upcoming_data'],
                    live_data = matches_data['live_data']
                    )
                     
