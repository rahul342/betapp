from bet_data_fetcher import bet_data_settings
from datetime import datetime
import logging
import os
import re

def is_valid_match_names(attr):
    def return_func(tag):
        logging.debug(tag[attr])
        pattern = "^(%s) v (%s)$" % ('|'.join(bet_data_settings.IPL_TEAMS), "|".join(bet_data_settings.IPL_TEAMS))
        return bool(re.match(pattern, tag[attr], flags=re.IGNORECASE))
    return return_func

def store_schedule():
    from bet_data_fetcher.models import Match, Tournament
    if Tournament.objects.count() == 0:
        Tournament.objects.create(name="IPL 2012", betsite_url='')
    if Match.objects.count() != 0:
        return
    all_data = map(lambda x: x.strip().split(','), open(os.path.join(os.path.dirname(__file__), 'data/matches.csv'),'r').readlines())
    for data in all_data:
        Match.objects.create(name=data[1], match_date=datetime.strptime(data[0],"%Y%m%dT%H%M%SZ").date(), betsite_url='')
        
def get_team_short_name(team_name):
    for team_map in bet_data_settings.IPL_TEAMS_MAP:
        if team_map[0] == team_name:
            return team_map[1]
    
    return None

def get_team_acronym(team_name):
    for team_map in bet_data_settings.IPL_TEAMS_MAP:
        if team_map[0] == team_name:
            return team_map[2]
    
    return None

def convert_fraction_to_decimal(odd):
    num, den = map(float, odd.strip().split('/'))
    return round(num/den, 2)
    