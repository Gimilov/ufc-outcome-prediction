from bs4 import BeautifulSoup
import requests
import pandas as pd

def feets_to_metric(feets):
    if feets == '--':
        return '--'
    
    feets = feets.strip().replace(' ', '')
    feet = int(feets.split("'")[0])
    inches = int(feets.split("'")[1][:-1])
    
    result = feet * 30.48 + inches * 2.54
    return result


def inches_to_cm(inches):
    if inches == '--':
        return '--'
    
    return int(inches[:-1]) * 2.54


def lbs_to_kg(lbs):
    if lbs == '--':
        return '--'
    
    return int(lbs.replace(' lbs.', '')) / 2.205


def birthdate_to_year(birthdate):
    if birthdate == '--':
        return '--'
    
    return int(birthdate[-4:])


def minutes_to_seconds(minutes):
    if minutes == '--':
        return 0
    
    mins = int(minutes.split(':')[0])
    seconds = int(minutes.split(':')[1])
    
    return mins* 60 + seconds


def winner(fighter_soup: BeautifulSoup) -> str:
    R_outcome = fighter_soup.find(class_='b-fight-details__person-status').string.strip() # finds the first occurence, which is for Red
    if R_outcome == 'W':
        return 'Red'
    elif R_outcome == 'D':
        return 'Draw'
    elif R_outcome == 'NC':
        return 'No contest'
    else:
        return 'Blue'
    
    
def add_fighters(fighter: str, fighters_dict: dict, fighter_link: str) -> dict:
    response = requests.get(str(fighter_link))
    soup = BeautifulSoup(response.content, 'html.parser')
    info = soup.find(class_='b-list__info-box_style_small-width').find_all(class_='b-list__box-list-item')
    height = list(info[0])[2].strip()
    weight = list(info[1])[2].strip()
    reach = list(info[2])[2].strip()
    stance = list(info[3])[2].strip()
    birth = list(info[4])[2].strip()

    fighters_dict.update(
        {fighter: dict(
            {
            # for this fighter 
            "Height_cm": feets_to_metric(height), 
            "Weight_kg": lbs_to_kg(weight),
            "Reach": inches_to_cm(reach),
            "Stance": stance,
            "Year of birth":birthdate_to_year(birth),
            "Average knockdowns": 0.00,
            "Average Significant strikes attempted": 0.00,
            "Average Significant strikes landed": 0.00,
            "Significant strikes % Landed": 0.00,
            "Average Strikes Attempted": 0.00,
            "Average Strikes Landed": 0.00,
            "Total Strikes % Landed": 0.00,
            "Average Takedowns Attempted": 0.00,
            "Average Takedowns Landed": 0.00,
            "Takedowns % Landed": 0.00,
            "Average Submission attempts": 0.00,
            "Average Reversals": 0.00,
            "Average Control": 0.00,
            "Average Significant Strikes on Head Attempted": 0.00,
            "Average Significant Strikes on Head Landed": 0.00,
            "Significant Strikes on Head % Landed": 0.00,
            "Average Significant Strikes on Body Attempted": 0.00,
            "Average Significant Strikes on Body Landed": 0.00,
            "Significant Strikes on Body % Landed": 0.00,
            "Average Significant Strikes on Leg Attempted": 0.00,
            "Average Significant Strikes on Leg Landed": 0.00,
            "Significant Strikes on Leg % Landed": 0.00,
            "Average Significant Strikes at Distance Attempted": 0.00,
            "Average Significant Strikes at Distance Landed": 0.00,
            "Significant Strikes at Distance % Landed": 0.00,
            "Average Significant Strikes in Clinch Attempted": 0.00,
            "Average Significant Strikes in Clinch Landed": 0.00,
            "Significant Strikes in Clinch % Landed": 0.00,
            "Average Significant Strikes on Ground Attempted": 0.00,
            "Average Significant Strikes on Ground Landed": 0.00,
            "Significant Strikes on Ground % Landed": 0.00,
            # for opponents of this fighter
            "Opp. Average knockdowns": 0.00,
            "Opp. Average Significant strikes attempted": 00.00,
            "Opp. Average Significant strikes landed": 0.00,
            "Opp. Significant strikes % Landed": 0.00,
            "Opp. Average Strikes Attempted": 0.00,
            "Opp. Average Strikes Landed": 0.00,
            "Opp. Strikes % Landed": 0.00,
            "Opp. Average Takedowns Attempted": 0.00,
            "Opp. Average Takedowns Landed": 0.00,
            "Opp. Takedowns % Landed": 0.00,
            "Opp. Average Submission attempts": 0.00,
            "Opp. Average Reversals": 0.00,
            "Opp. Average Control": 0.00,
            "Opp. Average Significant Strikes on Head Attempted": 0.00,
            "Opp. Average Significant Strikes on Head Landed": 0.00,
            "Opp. Significant Strikes on Head % Landed": 0.00,
            "Opp. Average Significant Strikes on Body Attempted": 0.00,
            "Opp. Average Significant Strikes on Body Landed": 0.00,
            "Opp. Significant Strikes on Body % Landed": 0.00,
            "Opp. Average Significant Strikes on Leg Attempted": 0.00,
            "Opp. Average Significant Strikes on Leg Landed": 0.00,
            "Opp. Significant Strikes on Leg % Landed": 0.00,
            "Opp. Average Significant Strikes at Distance Attempted": 0.00,
            "Opp. Average Significant Strikes at Distance Landed": 0.00,
            "Opp. Significant Strikes at Distance % Landed": 0.00,
            "Opp. Average Significant Strikes in Clinch Attempted": 0.00,
            "Opp. Average Significant Strikes in Clinch Landed": 0.00,
            "Opp. Significant Strikes in Clinch % Landed": 0.00,
            "Opp. Average Significant Strikes on Ground Attempted": 0.00,
            "Opp. Average Significant Strikes on Ground Landed": 0.00,
            "Opp. Significant Strikes on Ground % Landed": 0.00,
            "Winning streak": 0,
            "Losing streak": 0,
            "Total number of wins": 0,
            "Total number of title wins": 0,
            "Total number of wins by unanimous decision": 0,
            "Total number of wins by KO/TKO": 0,
            "Total number of wins by submission": 0,
            "Total number of wins by split decision": 0,
            "Total number of wins by majority vote": 0,
            "Total number of wins by doctor stoppage": 0,
            "Total number of fights": 0,
            "Total number of fights for title": 0,
            "Win %": 0.00})})
    
    return fighters_dict


def update_fighters(fighter: str, colour: str, fighters_dict: dict, fighter_soup: BeautifulSoup, isTitle: bool, conclusion: str) -> dict:
    fighter_stats = list(fighter_soup.find(class_='b-fight-details').children)
    if len(fighter_stats) < 19: # it means that the page can be assumed as 'missing'
        return fighters_dict 
    totals = fighter_stats[7]
    sig_strikes = fighter_stats[13]
    index = 0 if colour == "Red" else 1
    opp_index = 1 if index == 0 else 0
    
    # taking TOTAL stats for the fight
    totals_stats = list(totals.find_all(class_='b-fight-details__table-row')[1].children)[2:] # omit the first one, as these are fighters
    totals_stats = [x for x in totals_stats if x != '\n']
    
    # for THIS fighter
    knockdowns = [x for x in list(totals_stats[0].children) if x != '\n'][index].string.strip() # gets upper for Red, lower for Blue
    sig_strikes_landed = [x for x in list(totals_stats[1].children) if x != '\n'][index].string.strip().split(' of ')[0]
    sig_strikes_attempted = [x for x in list(totals_stats[1].children) if x != '\n'][index].string.strip().split(' of ')[1]
    tot_strikes_landed = [x for x in list(totals_stats[3].children) if x != '\n'][index].string.strip().split(' of ')[0]
    tot_strikes_attempted = [x for x in list(totals_stats[3].children) if x != '\n'][index].string.strip().split(' of ')[1]
    takedowns_landed = [x for x in list(totals_stats[4].children) if x != '\n'][index].string.strip().split(' of ')[0]
    takedowns_attempted = [x for x in list(totals_stats[4].children) if x != '\n'][index].string.strip().split(' of ')[1]
    sub_attempts = [x for x in list(totals_stats[6].children) if x != '\n'][index].string.strip()
    reversals = [x for x in list(totals_stats[7].children) if x != '\n'][index].string.strip()
    control = minutes_to_seconds([x for x in list(totals_stats[8].children) if x != '\n'][index].string.strip())
    
    # for OPPONENT fighter
    opp_knockdowns = [x for x in list(totals_stats[0].children) if x != '\n'][opp_index].string.strip() # gets upper for Red, lower for Blue
    opp_sig_strikes_landed = [x for x in list(totals_stats[1].children) if x != '\n'][opp_index].string.strip().split(' of ')[0]
    opp_sig_strikes_attempted = [x for x in list(totals_stats[1].children) if x != '\n'][opp_index].string.strip().split(' of ')[1]
    opp_tot_strikes_landed = [x for x in list(totals_stats[3].children) if x != '\n'][opp_index].string.strip().split(' of ')[0]
    opp_tot_strikes_attempted = [x for x in list(totals_stats[3].children) if x != '\n'][opp_index].string.strip().split(' of ')[1]
    opp_takedowns_landed = [x for x in list(totals_stats[4].children) if x != '\n'][opp_index].string.strip().split(' of ')[0]
    opp_takedowns_attempted = [x for x in list(totals_stats[4].children) if x != '\n'][opp_index].string.strip().split(' of ')[1]
    opp_sub_attempts = [x for x in list(totals_stats[6].children) if x != '\n'][opp_index].string.strip()
    opp_reversals = [x for x in list(totals_stats[7].children) if x != '\n'][opp_index].string.strip()
    opp_control = minutes_to_seconds([x for x in list(totals_stats[8].children) if x != '\n'][opp_index].string.strip())
    
    # Taking SIG_STRIKES stats for the fight 
    sig_strikes_stats = list(sig_strikes.find_all(class_='b-fight-details__table-row')[1].children)[2:]
    sig_strikes_stats = [x for x in sig_strikes_stats if x != '\n']
    
    # for THIS fighter
    heads_landed = [x for x in list(sig_strikes_stats[2].children) if x != '\n'][index].string.strip().split(' of ')[0]
    heads_attempted = [x for x in list(sig_strikes_stats[2].children) if x != '\n'][index].string.strip().split(' of ')[1]
    body_landed = [x for x in list(sig_strikes_stats[3].children) if x != '\n'][index].string.strip().split(' of ')[0]
    body_attempted = [x for x in list(sig_strikes_stats[3].children) if x != '\n'][index].string.strip().split(' of ')[1]
    leg_landed = [x for x in list(sig_strikes_stats[4].children) if x != '\n'][index].string.strip().split(' of ')[0]
    leg_attempted = [x for x in list(sig_strikes_stats[4].children) if x != '\n'][index].string.strip().split(' of ')[1]
    distance_landed = [x for x in list(sig_strikes_stats[5].children) if x != '\n'][index].string.strip().split(' of ')[0]
    distance_attempted = [x for x in list(sig_strikes_stats[5].children) if x != '\n'][index].string.strip().split(' of ')[1]
    clinch_landed = [x for x in list(sig_strikes_stats[6].children) if x != '\n'][index].string.strip().split(' of ')[0]
    clinch_attempted = [x for x in list(sig_strikes_stats[6].children) if x != '\n'][index].string.strip().split(' of ')[1]
    ground_landed = [x for x in list(sig_strikes_stats[7].children) if x != '\n'][index].string.strip().split(' of ')[0]
    ground_attempted = [x for x in list(sig_strikes_stats[7].children) if x != '\n'][index].string.strip().split(' of ')[1]
    
    # for OPPONENT fighter
    opp_heads_landed = [x for x in list(sig_strikes_stats[2].children) if x != '\n'][opp_index].string.strip().split(' of ')[0]
    opp_heads_attempted = [x for x in list(sig_strikes_stats[2].children) if x != '\n'][opp_index].string.strip().split(' of ')[1]
    opp_body_landed = [x for x in list(sig_strikes_stats[3].children) if x != '\n'][opp_index].string.strip().split(' of ')[0]
    opp_body_attempted = [x for x in list(sig_strikes_stats[3].children) if x != '\n'][opp_index].string.strip().split(' of ')[1]
    opp_leg_landed = [x for x in list(sig_strikes_stats[4].children) if x != '\n'][opp_index].string.strip().split(' of ')[0]
    opp_leg_attempted = [x for x in list(sig_strikes_stats[4].children) if x != '\n'][opp_index].string.strip().split(' of ')[1]
    opp_distance_landed = [x for x in list(sig_strikes_stats[5].children) if x != '\n'][opp_index].string.strip().split(' of ')[0]
    opp_distance_attempted = [x for x in list(sig_strikes_stats[5].children) if x != '\n'][opp_index].string.strip().split(' of ')[1]
    opp_clinch_landed = [x for x in list(sig_strikes_stats[6].children) if x != '\n'][opp_index].string.strip().split(' of ')[0]
    opp_clinch_attempted = [x for x in list(sig_strikes_stats[6].children) if x != '\n'][opp_index].string.strip().split(' of ')[1]
    opp_ground_landed = [x for x in list(sig_strikes_stats[7].children) if x != '\n'][opp_index].string.strip().split(' of ')[0]
    opp_ground_attempted = [x for x in list(sig_strikes_stats[7].children) if x != '\n'][opp_index].string.strip().split(' of ')[1]
    
    # computing win-related stats
    # I assume that win-streak is broken by a lose, and a lose-break is broken by a win
    win_streak = fighters_dict.get(fighter).get("Winning streak") 
    lose_streak = fighters_dict.get(fighter).get("Losing streak") 
    no_of_wins = fighters_dict.get(fighter).get("Total number of wins")
    no_of_title_wins = fighters_dict.get(fighter).get("Total number of title wins")
    no_of_wins_ud = fighters_dict.get(fighter).get("Total number of wins by unanimous decision")
    no_of_wins_ko_tko = fighters_dict.get(fighter).get("Total number of wins by KO/TKO")
    no_of_wins_subm = fighters_dict.get(fighter).get("Total number of wins by submission")
    no_of_wins_split = fighters_dict.get(fighter).get("Total number of wins by split decision")
    no_of_wins_maj = fighters_dict.get(fighter).get("Total number of wins by majority vote")
    no_of_wins_doc = fighters_dict.get(fighter).get("Total number of wins by doctor stoppage")
    no_of_fights = fighters_dict.get(fighter).get("Total number of fights")
    no_of_fights_title = fighters_dict.get(fighter).get("Total number of fights for title")
    
    fight_outcome = winner(fighter_soup)
    if fight_outcome == colour:
        if isTitle: no_of_title_wins += 1
        if conclusion == 'Decision - Unanimous': no_of_wins_ud += 1
        elif conclusion == 'KO/TKO': no_of_wins_ko_tko += 1
        elif conclusion == 'Submission': no_of_wins_subm += 1
        elif conclusion == 'Decision - Split': no_of_wins_split += 1
        elif conclusion == 'Decision - Majority': no_of_wins_maj += 1
        elif conclusion == "TKO - Doctor's Stoppage": no_of_wins_doc += 1
        
        win_streak += 1
        lose_streak = 0
        no_of_wins += 1
    elif fight_outcome != 'Draw' and fight_outcome != 'No contest':
        win_streak = 0
        lose_streak += 1
    else:
        pass # do nothing as chat Google tells me that the streak is not broken
    
    no_of_fights += 1 # increment anyway
    if isTitle: no_of_fights_title += 1
    
    # updating the fighters dictionary
    #
    # FOR THIS FIGHTER ----------------------------------------------------------------------------
    #
    current = fighters_dict.get(fighter)["Average knockdowns"]
    fighters_dict.get(fighter)["Average knockdowns"] = ((current * (no_of_fights - 1)) + int(knockdowns)) / no_of_fights if knockdowns.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Significant strikes attempted"]
    fighters_dict.get(fighter)["Average Significant strikes attempted"] = ((current * (no_of_fights - 1)) + int(sig_strikes_attempted)) / no_of_fights if sig_strikes_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Significant strikes landed"]
    fighters_dict.get(fighter)["Average Significant strikes landed"] = ((current * (no_of_fights - 1)) + int(sig_strikes_landed)) / no_of_fights if sig_strikes_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_sig_landed = fighters_dict.get(fighter).get("Average Significant strikes landed")
    temp_sig_attempted = fighters_dict.get(fighter).get("Average Significant strikes attempted")
    fighters_dict.get(fighter)["Significant strikes % Landed"] = (temp_sig_landed * no_of_fights) / (temp_sig_attempted * no_of_fights) if temp_sig_attempted > 0 and no_of_fights > 0 else 0
    
    current = fighters_dict.get(fighter)["Average Strikes Attempted"]
    fighters_dict.get(fighter)["Average Strikes Attempted"] = ((current * (no_of_fights - 1)) + int(tot_strikes_attempted)) / no_of_fights if tot_strikes_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Strikes Landed"]
    fighters_dict.get(fighter)["Average Strikes Landed"] = ((current * (no_of_fights - 1)) + int(tot_strikes_landed)) / no_of_fights if tot_strikes_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_tot_landed = fighters_dict.get(fighter).get("Average Strikes Landed")
    temp_tot_attempted = fighters_dict.get(fighter).get("Average Strikes Attempted")
    fighters_dict.get(fighter)["Total Strikes % Landed"] = (temp_tot_landed * no_of_fights) / (temp_tot_attempted * no_of_fights) if temp_tot_attempted > 0 and no_of_fights > 0 else 0
    
    current = fighters_dict.get(fighter)["Average Takedowns Attempted"]
    fighters_dict.get(fighter)["Average Takedowns Attempted"] = ((current * (no_of_fights - 1)) + int(takedowns_attempted)) / no_of_fights if takedowns_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Takedowns Landed"] 
    fighters_dict.get(fighter)["Average Takedowns Landed"] = ((current * (no_of_fights - 1)) + int(takedowns_landed)) / no_of_fights if takedowns_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_td_landed = fighters_dict.get(fighter).get("Average Takedowns Landed")
    temp_td_attempted = fighters_dict.get(fighter).get("Average Takedowns Attempted")
    fighters_dict.get(fighter)["Takedowns % Landed"] = (temp_td_landed * no_of_fights) / (temp_td_attempted * no_of_fights) if temp_td_attempted > 0 and no_of_fights > 0 else 0
    
    current = fighters_dict.get(fighter)["Average Submission attempts"]
    fighters_dict.get(fighter)["Average Submission attempts"] = ((current * (no_of_fights - 1)) + int(sub_attempts)) / no_of_fights if sub_attempts.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Reversals"]
    fighters_dict.get(fighter)["Average Reversals"] = ((current * (no_of_fights - 1)) + int(reversals)) / no_of_fights if reversals.isnumeric() and no_of_fights > 0 else current

    current = fighters_dict.get(fighter)["Average Control"]
    fighters_dict.get(fighter)["Average Control"] = ((current * (no_of_fights - 1)) + control) / no_of_fights if no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Significant Strikes on Head Attempted"]
    fighters_dict.get(fighter)["Average Significant Strikes on Head Attempted"] = ((current * (no_of_fights - 1)) + int(heads_attempted)) / no_of_fights if heads_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Significant Strikes on Head Landed"]
    fighters_dict.get(fighter)["Average Significant Strikes on Head Landed"] = ((current * (no_of_fights - 1)) + int(heads_landed)) / no_of_fights if heads_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_head_landed = fighters_dict.get(fighter).get("Average Significant Strikes on Head Landed")
    temp_head_attempted = fighters_dict.get(fighter).get("Average Significant Strikes on Head Attempted")
    fighters_dict.get(fighter)["Significant Strikes on Head % Landed"] = (temp_head_landed * no_of_fights) / (temp_head_attempted * no_of_fights) if temp_head_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Average Significant Strikes on Body Attempted"]
    fighters_dict.get(fighter)["Average Significant Strikes on Body Attempted"] = ((current * (no_of_fights - 1)) + int(body_attempted)) / no_of_fights if body_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Significant Strikes on Body Landed"]
    fighters_dict.get(fighter)["Average Significant Strikes on Body Landed"] = ((current * (no_of_fights - 1)) + int(body_landed)) / no_of_fights if body_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_body_landed = fighters_dict.get(fighter).get("Average Significant Strikes on Body Landed")
    temp_body_attempted = fighters_dict.get(fighter).get("Average Significant Strikes on Body Attempted")
    fighters_dict.get(fighter)["Significant Strikes on Body % Landed"] = (temp_body_landed * no_of_fights) / (temp_body_attempted * no_of_fights) if temp_body_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Average Significant Strikes on Leg Attempted"]
    fighters_dict.get(fighter)["Average Significant Strikes on Leg Attempted"] = ((current * (no_of_fights - 1)) + int(leg_attempted)) / no_of_fights if leg_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Significant Strikes on Leg Landed"]
    fighters_dict.get(fighter)["Average Significant Strikes on Leg Landed"] = ((current * (no_of_fights - 1)) + int(leg_landed)) / no_of_fights if leg_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_leg_landed = fighters_dict.get(fighter).get("Average Significant Strikes on Leg Landed")
    temp_leg_attempted = fighters_dict.get(fighter).get("Average Significant Strikes on Leg Attempted")
    fighters_dict.get(fighter)["Significant Strikes on Leg % Landed"] = (temp_leg_landed * no_of_fights) / (temp_leg_attempted * no_of_fights) if temp_leg_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Average Significant Strikes at Distance Attempted"]
    fighters_dict.get(fighter)["Average Significant Strikes at Distance Attempted"] = ((current * (no_of_fights - 1)) + int(distance_attempted)) / no_of_fights if distance_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Significant Strikes at Distance Landed"]
    fighters_dict.get(fighter)["Average Significant Strikes at Distance Landed"] = ((current * (no_of_fights - 1)) + int(distance_landed)) / no_of_fights if distance_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_dist_landed = fighters_dict.get(fighter).get("Average Significant Strikes at Distance Landed")
    temp_dist_attempted = fighters_dict.get(fighter).get("Average Significant Strikes at Distance Attempted")
    fighters_dict.get(fighter)["Significant Strikes at Distance % Landed"] = (temp_dist_landed * no_of_fights) / (temp_dist_attempted * no_of_fights) if temp_dist_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Average Significant Strikes in Clinch Attempted"] 
    fighters_dict.get(fighter)["Average Significant Strikes in Clinch Attempted"] = ((current * (no_of_fights - 1)) + int(clinch_attempted)) / no_of_fights if clinch_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Significant Strikes in Clinch Landed"]
    fighters_dict.get(fighter)["Average Significant Strikes in Clinch Landed"] = ((current * (no_of_fights - 1)) + int(clinch_landed)) / no_of_fights if clinch_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_clinch_landed = fighters_dict.get(fighter).get("Average Significant Strikes in Clinch Landed")
    temp_clinch_attempted = fighters_dict.get(fighter).get("Average Significant Strikes in Clinch Attempted")
    fighters_dict.get(fighter)["Significant Strikes in Clinch % Landed"] = (temp_clinch_landed * no_of_fights) / (temp_clinch_attempted * no_of_fights) if temp_clinch_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Average Significant Strikes on Ground Attempted"]
    fighters_dict.get(fighter)["Average Significant Strikes on Ground Attempted"] = ((current * (no_of_fights - 1)) + int(ground_attempted)) / no_of_fights if ground_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Average Significant Strikes on Ground Landed"]
    fighters_dict.get(fighter)["Average Significant Strikes on Ground Landed"] = ((current * (no_of_fights - 1)) + int(ground_landed)) / no_of_fights if ground_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_ground_landed = fighters_dict.get(fighter).get("Average Significant Strikes on Ground Landed")
    temp_ground_attempted = fighters_dict.get(fighter).get("Average Significant Strikes on Ground Attempted")
    fighters_dict.get(fighter)["Significant Strikes on Ground % Landed"] = (temp_ground_landed * no_of_fights) / (temp_ground_attempted * no_of_fights) if temp_ground_attempted > 0 and no_of_fights > 0 else 0 
    
    fighters_dict.get(fighter)["Winning streak"] = win_streak
    fighters_dict.get(fighter)["Losing streak"] = lose_streak
    fighters_dict.get(fighter)["Total number of wins"] = no_of_wins
    fighters_dict.get(fighter)["Total number of title wins"] = no_of_title_wins
    fighters_dict.get(fighter)["Total number of wins by unanimous decision"] = no_of_wins_ud
    fighters_dict.get(fighter)["Total number of wins by KO/TKO"] = no_of_wins_ko_tko
    fighters_dict.get(fighter)["Total number of wins by submission"] = no_of_wins_subm
    fighters_dict.get(fighter)["Total number of wins by split decision"] = no_of_wins_split
    fighters_dict.get(fighter)["Total number of wins by majority vote"] = no_of_wins_maj
    fighters_dict.get(fighter)["Total number of wins by doctor stoppage"] = no_of_wins_doc
    fighters_dict.get(fighter)["Total number of fights"] = no_of_fights
    fighters_dict.get(fighter)["Total number of fights for title"] = no_of_fights_title
    fighters_dict.get(fighter)["Win %"] = no_of_wins / no_of_fights if no_of_fights > 0 else 0
    
    # 
    # FOR OPPONENT FIGHTER ----------------------------------------------------------------------------
    #
    current = fighters_dict.get(fighter)["Opp. Average knockdowns"]
    fighters_dict.get(fighter)["Opp. Average knockdowns"] = ((current * (no_of_fights - 1)) + int(opp_knockdowns)) / no_of_fights if opp_knockdowns.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Significant strikes attempted"]
    fighters_dict.get(fighter)["Opp. Average Significant strikes attempted"] = ((current * (no_of_fights - 1)) + int(opp_sig_strikes_attempted)) / no_of_fights if opp_sig_strikes_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Significant strikes landed"]
    fighters_dict.get(fighter)["Opp. Average Significant strikes landed"] = ((current * (no_of_fights - 1)) + int(opp_sig_strikes_landed)) / no_of_fights if opp_sig_strikes_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_sig_landed = fighters_dict.get(fighter).get("Opp. Average Significant strikes landed")
    temp_sig_attempted = fighters_dict.get(fighter).get("Opp. Average Significant strikes attempted")
    fighters_dict.get(fighter)["Opp. Significant strikes % Landed"] = (temp_sig_landed * no_of_fights) / (temp_sig_attempted * no_of_fights) if temp_sig_attempted > 0 and no_of_fights > 0 else 0
    
    current = fighters_dict.get(fighter)["Opp. Average Strikes Attempted"]
    fighters_dict.get(fighter)["Opp. Average Strikes Attempted"] = ((current * (no_of_fights - 1)) + int(opp_tot_strikes_attempted)) / no_of_fights if opp_tot_strikes_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Strikes Landed"]
    fighters_dict.get(fighter)["Opp. Average Strikes Landed"] = ((current * (no_of_fights - 1)) + int(opp_tot_strikes_landed)) / no_of_fights if opp_tot_strikes_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_tot_landed = fighters_dict.get(fighter).get("Opp. Average Strikes Landed")
    temp_tot_attempted = fighters_dict.get(fighter).get("Opp. Average Strikes Attempted")
    fighters_dict.get(fighter)["Opp. Strikes % Landed"] = (temp_tot_landed * no_of_fights) / (temp_tot_attempted * no_of_fights) if temp_tot_attempted > 0 and no_of_fights > 0 else 0
    
    current = fighters_dict.get(fighter)["Opp. Average Takedowns Attempted"]
    fighters_dict.get(fighter)["Opp. Average Takedowns Attempted"] = ((current * (no_of_fights - 1)) + int(opp_takedowns_attempted)) / no_of_fights if opp_takedowns_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Takedowns Landed"] 
    fighters_dict.get(fighter)["Opp. Average Takedowns Landed"] = ((current * (no_of_fights - 1)) + int(opp_takedowns_landed)) / no_of_fights if opp_takedowns_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_td_landed = fighters_dict.get(fighter).get("Opp. Average Takedowns Landed")
    temp_td_attempted = fighters_dict.get(fighter).get("Opp. Average Takedowns Attempted")
    fighters_dict.get(fighter)["Opp. Takedowns % Landed"] = (temp_td_landed * no_of_fights) / (temp_td_attempted * no_of_fights) if temp_td_attempted > 0 and no_of_fights > 0 else 0
    
    current = fighters_dict.get(fighter)["Opp. Average Submission attempts"]
    fighters_dict.get(fighter)["Opp. Average Submission attempts"] = ((current * (no_of_fights - 1)) + int(opp_sub_attempts)) / no_of_fights if opp_sub_attempts.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Reversals"]
    fighters_dict.get(fighter)["Opp. Average Reversals"] = ((current * (no_of_fights - 1)) + int(opp_reversals)) / no_of_fights if opp_reversals.isnumeric() and no_of_fights > 0 else current

    current = fighters_dict.get(fighter)["Opp. Average Control"]
    fighters_dict.get(fighter)["Opp. Average Control"] = ((current * (no_of_fights - 1)) + opp_control) / no_of_fights if no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes on Head Attempted"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes on Head Attempted"] = ((current * (no_of_fights - 1)) + int(opp_heads_attempted)) / no_of_fights if opp_heads_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes on Head Landed"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes on Head Landed"] = ((current * (no_of_fights - 1)) + int(opp_heads_landed)) / no_of_fights if opp_heads_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_head_landed = fighters_dict.get(fighter).get("Opp. Average Significant Strikes on Head Landed")
    temp_head_attempted = fighters_dict.get(fighter).get("Opp. Average Significant Strikes on Head Attempted")
    fighters_dict.get(fighter)["Opp. Significant Strikes on Body % Landed"] = (temp_head_landed * no_of_fights) / (temp_head_attempted * no_of_fights) if temp_head_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes on Body Attempted"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes on Body Attempted"] = ((current * (no_of_fights - 1)) + int(opp_body_attempted)) / no_of_fights if opp_body_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes on Body Landed"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes on Body Landed"] = ((current * (no_of_fights - 1)) + int(opp_body_landed)) / no_of_fights if opp_body_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_body_landed = fighters_dict.get(fighter).get("Opp. Average Significant Strikes on Body Landed")
    temp_body_attempted = fighters_dict.get(fighter).get("Opp. Average Significant Strikes on Body Attempted")
    fighters_dict.get(fighter)["Opp. Significant Strikes on Body % Landed"] = (temp_body_landed * no_of_fights) / (temp_body_attempted * no_of_fights) if temp_body_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes on Leg Attempted"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes on Leg Attempted"] = ((current * (no_of_fights - 1)) + int(opp_leg_attempted)) / no_of_fights if opp_leg_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes on Leg Landed"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes on Leg Landed"] = ((current * (no_of_fights - 1)) + int(opp_leg_landed)) / no_of_fights if opp_leg_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_leg_landed = fighters_dict.get(fighter).get("Opp. Average Significant Strikes on Leg Landed")
    temp_leg_attempted = fighters_dict.get(fighter).get("Opp. Average Significant Strikes on Leg Attempted")
    fighters_dict.get(fighter)["Opp. Significant Strikes on Leg % Landed"] = (temp_leg_landed * no_of_fights) / (temp_leg_attempted * no_of_fights) if temp_leg_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes at Distance Attempted"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes at Distance Attempted"] = ((current * (no_of_fights - 1)) + int(opp_distance_attempted)) / no_of_fights if opp_distance_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes at Distance Landed"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes at Distance Landed"] = ((current * (no_of_fights - 1)) + int(opp_distance_landed)) / no_of_fights if opp_distance_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_dist_landed = fighters_dict.get(fighter).get("Opp. Average Significant Strikes at Distance Landed")
    temp_dist_attempted = fighters_dict.get(fighter).get("Opp. Average Significant Strikes at Distance Attempted")
    fighters_dict.get(fighter)["Opp. Significant Strikes at Distance % Landed"] = (temp_dist_landed * no_of_fights) / (temp_dist_attempted * no_of_fights) if temp_dist_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes in Clinch Attempted"] 
    fighters_dict.get(fighter)["Opp. Average Significant Strikes in Clinch Attempted"] = ((current * (no_of_fights - 1)) + int(opp_clinch_attempted)) / no_of_fights if opp_clinch_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes in Clinch Landed"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes in Clinch Landed"] = ((current * (no_of_fights - 1)) + int(opp_clinch_landed)) / no_of_fights if opp_clinch_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_clinch_landed = fighters_dict.get(fighter).get("Opp. Average Significant Strikes in Clinch Landed")
    temp_clinch_attempted = fighters_dict.get(fighter).get("Opp. Average Significant Strikes in Clinch Attempted")
    fighters_dict.get(fighter)["Opp. Average Significant Strikes in Clinch % Landed"] = (temp_clinch_landed * no_of_fights) / (temp_clinch_attempted * no_of_fights) if temp_clinch_attempted > 0 and no_of_fights > 0 else 0 
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes on Ground Attempted"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes on Ground Attempted"] = ((current * (no_of_fights - 1)) + int(opp_ground_attempted)) / no_of_fights if opp_ground_attempted.isnumeric() and no_of_fights > 0 else current
    
    current = fighters_dict.get(fighter)["Opp. Average Significant Strikes on Ground Landed"]
    fighters_dict.get(fighter)["Opp. Average Significant Strikes on Ground Landed"] = ((current * (no_of_fights - 1)) + int(opp_ground_landed)) / no_of_fights if opp_ground_landed.isnumeric() and no_of_fights > 0 else current
    
    temp_ground_landed = fighters_dict.get(fighter).get("Opp. Average Significant Strikes on Ground Landed")
    temp_ground_attempted = fighters_dict.get(fighter).get("Opp. Average Significant Strikes on Ground Attempted")
    fighters_dict.get(fighter)["Opp. Significant Strikes on Ground % Landed"] = (temp_ground_landed * no_of_fights) / (temp_ground_attempted * no_of_fights) if temp_ground_attempted > 0 and no_of_fights > 0 else 0 