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
            {"Height_cm": feets_to_metric(height), 
            "Weight_kg": lbs_to_kg(weight),
            "Reach": inches_to_cm(reach),
            "Stance": stance,
            "Year of birth":birthdate_to_year(birth),
            "Total knockdowns": 0,
            "Total Significant strikes attempted": 0,
            "Total Significant strikes landed": 0,
            "Significant strikes % Landed": 0.00,
            "Total Strikes Attempted": 0,
            "Total Strikes Landed": 0,
            "Total Strikes % Landed": 0,
            "Total Takedowns Attempted": 0,
            "Total Takedowns Landed": 0,
            "Takedowns % Landed": 0.00,
            "Total Submission attempts": 0,
            "Total Reversals": 0,
            "Total Control": 0,
            "Average Control": 0,
            "Total Significant Strikes on Head Attempted": 0,
            "Total Significant Strikes on Head Landed": 0,
            "Total Significant Strikes on Head % Landed": 0.00,
            "Total Significant Strikes on Body Attempted": 0,
            "Total Significant Strikes on Body Landed": 0,
            "Total Significant Strikes on Body % Landed": 0.00,
            "Total Significant Strikes on Leg Attempted": 0,
            "Total Significant Strikes on Leg Landed": 0,
            "Total Significant Strikes on Leg % Landed": 0.00,
            "Total Significant Strikes at Distance Attempted": 0,
            "Total Significant Strikes at Distance Landed": 0,
            "Total Significant Strikes at Distance % Landed": 0.00,
            "Total Significant Strikes in Clinch Attempted": 0,
            "Total Significant Strikes in Clinch Landed": 0,
            "Total Significant Strikes in Clinch % Landed": 0.00,
            "Total Significant Strikes on Ground Attempted": 0,
            "Total Significant Strikes on Ground Landed": 0,
            "Total Significant Strikes on Ground % Landed": 0.00,
            "Winning streak": 0,
            "Losing streak": 0,
            "Total number of wins": 0,
            "Total number of fights": 0,
            "Win %": 0.00})})
    
    return fighters_dict


def update_fighters(fighter: str, colour: str, fighters_dict: dict, fighter_soup: BeautifulSoup) -> dict:
    fighter_stats = list(fighter_soup.find(class_='b-fight-details').children)
    if len(fighter_stats) < 19: # it means that the page can be assumed as 'missing'
        return fighters_dict 
    totals = fighter_stats[7]
    sig_strikes = fighter_stats[13]
    index = 0 if colour == "Red" else 1
    
    # taking TOTAL stats for the fight
    totals_stats = list(totals.find_all(class_='b-fight-details__table-row')[1].children)[2:] # omit the first one, as these are fighters
    totals_stats = [x for x in totals_stats if x != '\n']
    
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

    
    # Taking SIG_STRIKES stats for the fight 
    sig_strikes_stats = list(sig_strikes.find_all(class_='b-fight-details__table-row')[1].children)[2:]
    sig_strikes_stats = [x for x in sig_strikes_stats if x != '\n']
    
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
    
    # computing win-related stats
    # I assume that win-streak is broken by a lose, and a lose-break is broken by a win
    win_streak = fighters_dict.get(fighter).get("Winning streak") 
    lose_streak = fighters_dict.get(fighter).get("Losing streak") 
    no_of_wins = fighters_dict.get(fighter).get("Total number of wins")
    no_of_fights = fighters_dict.get(fighter).get("Total number of fights")
    
    fight_outcome = winner(fighter_soup)
    if fight_outcome == colour:
        win_streak += 1
        lose_streak = 0
        no_of_wins += 1
    elif fight_outcome != 'Draw' and fight_outcome != 'No contest':
        win_streak = 0
        lose_streak += 1
    else:
        pass # do nothing as chat Google tells me that the streak is not broken
    
    no_of_fights += 1 # increment anyway

    # updating the fighters dictionary
    fighters_dict.get(fighter)["Total knockdowns"] += int(knockdowns) if knockdowns.isnumeric() else 0
    fighters_dict.get(fighter)["Total Significant strikes attempted"] += int(sig_strikes_attempted) if sig_strikes_attempted.isnumeric() else 0
    fighters_dict.get(fighter)["Total Significant strikes landed"] += int(sig_strikes_landed) if sig_strikes_landed.isnumeric() else 0
    temp_sig_landed = fighters_dict.get(fighter).get("Total Significant strikes landed")
    temp_sig_attempted = fighters_dict.get(fighter).get("Total Significant strikes attempted")
    fighters_dict.get(fighter)["Significant strikes % Landed"] = temp_sig_landed / temp_sig_attempted if temp_sig_attempted > 0 else 0
    fighters_dict.get(fighter)["Total Strikes Attempted"] += int(tot_strikes_attempted) if tot_strikes_attempted.isnumeric() else 0
    fighters_dict.get(fighter)["Total Strikes Landed"] += int(tot_strikes_landed) if tot_strikes_landed.isnumeric() else 0
    temp_tot_landed = fighters_dict.get(fighter).get("Total Strikes Landed")
    temp_tot_attempted = fighters_dict.get(fighter).get("Total Strikes Attempted")
    fighters_dict.get(fighter)["Total Strikes % Landed"] = temp_tot_landed / temp_tot_attempted if temp_tot_attempted > 0 else 0
    fighters_dict.get(fighter)["Total Takedowns Attempted"] += int(takedowns_attempted) if takedowns_attempted.isnumeric() else 0
    fighters_dict.get(fighter)["Total Takedowns Landed"] += int(takedowns_landed) if takedowns_landed.isnumeric() else 0
    temp_td_landed = fighters_dict.get(fighter).get("Total Takedowns Landed")
    temp_td_attempted = fighters_dict.get(fighter).get("Total Takedowns Attempted")
    fighters_dict.get(fighter)["Takedowns % Landed"] = temp_td_landed / temp_td_attempted if temp_td_attempted > 0 else 0
    fighters_dict.get(fighter)["Total Submission attempts"] += int(sub_attempts) if sub_attempts.isnumeric() else 0
    fighters_dict.get(fighter)["Total Reversals"] += int(reversals) if reversals.isnumeric() else 0
    fighters_dict.get(fighter)["Total Control"] += control # it's int primarily
    fighters_dict.get(fighter)["Average Control"] = fighters_dict.get(fighter)['Total Control'] / no_of_fights if no_of_fights > 0 else 0 
    
    fighters_dict.get(fighter)["Total Significant Strikes on Head Attempted"] += int(heads_attempted) if heads_attempted.isnumeric() else 0
    fighters_dict.get(fighter)["Total Significant Strikes on Head Landed"] += int(heads_landed) if heads_landed.isnumeric() else 0
    temp_head_landed = fighters_dict.get(fighter).get("Total Significant Strikes on Head Landed")
    temp_head_attempted = fighters_dict.get(fighter).get("Total Significant Strikes on Head Attempted")
    fighters_dict.get(fighter)["Total Significant Strikes on Body % Landed"] = temp_head_landed / temp_head_attempted if temp_head_attempted > 0 else 0
    
    fighters_dict.get(fighter)["Total Significant Strikes on Body Attempted"] += int(body_attempted) if body_attempted.isnumeric() else 0
    fighters_dict.get(fighter)["Total Significant Strikes on Body Landed"] += int(body_landed) if body_landed.isnumeric() else 0
    temp_body_landed = fighters_dict.get(fighter).get("Total Significant Strikes on Body Landed")
    temp_body_attempted = fighters_dict.get(fighter).get("Total Significant Strikes on Body Attempted")
    fighters_dict.get(fighter)["Total Significant Strikes on Body % Landed"] = temp_body_landed / temp_body_attempted if temp_body_attempted > 0 else 0
    
    fighters_dict.get(fighter)["Total Significant Strikes on Leg Attempted"] += int(leg_attempted) if leg_attempted.isnumeric() else 0
    fighters_dict.get(fighter)["Total Significant Strikes on Leg Landed"] += int(leg_landed) if leg_landed.isnumeric() else 0
    temp_leg_landed = fighters_dict.get(fighter).get("Total Significant Strikes on Leg Landed")
    temp_leg_attempted = fighters_dict.get(fighter).get("Total Significant Strikes on Leg Attempted")
    fighters_dict.get(fighter)["Total Significant Strikes on Leg % Landed"] = temp_leg_landed / temp_leg_attempted if temp_leg_attempted > 0 else 0
    
    fighters_dict.get(fighter)["Total Significant Strikes at Distance Attempted"] += int(distance_attempted) if distance_attempted.isnumeric() else 0
    fighters_dict.get(fighter)["Total Significant Strikes at Distance Landed"] += int(distance_landed) if distance_landed.isnumeric() else 0
    temp_dist_landed = fighters_dict.get(fighter).get("Total Significant Strikes at Distance Landed")
    temp_dist_attempted = fighters_dict.get(fighter).get("Total Significant Strikes at Distance Attempted")
    fighters_dict.get(fighter)["Total Significant Strikes at Distance % Landed"] = temp_dist_landed / temp_dist_attempted if temp_dist_attempted > 0 else 0
    
    fighters_dict.get(fighter)["Total Significant Strikes in Clinch Attempted"] += int(clinch_attempted) if clinch_attempted.isnumeric() else 0
    fighters_dict.get(fighter)["Total Significant Strikes in Clinch Landed"] += int(clinch_landed) if clinch_landed.isnumeric() else 0
    temp_clinch_landed = fighters_dict.get(fighter).get("Total Significant Strikes in Clinch Landed")
    temp_clinch_attempted = fighters_dict.get(fighter).get("Total Significant Strikes in Clinch Attempted")
    fighters_dict.get(fighter)["Total Significant Strikes in Clinch % Landed"] = temp_clinch_landed / temp_clinch_attempted if temp_clinch_attempted > 0 else 0
    
    fighters_dict.get(fighter)["Total Significant Strikes on Ground Attempted"] += int(ground_attempted) if ground_attempted.isnumeric() else 0
    fighters_dict.get(fighter)["Total Significant Strikes on Ground Landed"] += int(ground_landed) if ground_landed.isnumeric() else 0
    temp_ground_landed = fighters_dict.get(fighter).get("Total Significant Strikes on Ground Landed")
    temp_ground_attempted = fighters_dict.get(fighter).get("Total Significant Strikes on Ground Attempted")
    fighters_dict.get(fighter)["Total Significant Strikes on Ground % Landed"] = temp_ground_landed / temp_ground_attempted if temp_ground_attempted > 0 else 0
    
    fighters_dict.get(fighter)["Winning streak"] = win_streak
    fighters_dict.get(fighter)["Losing streak"] = lose_streak
    fighters_dict.get(fighter)["Total number of wins"] = no_of_wins
    fighters_dict.get(fighter)["Total number of fights"] = no_of_fights
    fighters_dict.get(fighter)["Win %"] = no_of_wins / no_of_fights if no_of_fights > 0 else 0