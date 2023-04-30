import pandas as pd
import requests
from bs4 import BeautifulSoup
import utilities
import Timer


# First step - get the html response of the URL containing all UFC events
url = "http://www.ufcstats.com/statistics/events/completed?page=all"
response = requests.get(url)
html_response = response.content

# Second step - parse it into 'BeautifulSoup' object
soup = BeautifulSoup(html_response, "html.parser")

# Step three - find all links from the initial URL to specific events
# Note that the 'insert' method was used to inverse the chronology (on that page, it is sorted
# from the newest to the oldest event)
links = []
for link in soup.find_all('a'):
    if 'event-details' in str(link):
        links.insert(0, link.get('href'))
links = links[:-1] # first link is an up-coming event

# Step four - for each of these links, we need to go in, find EACH fight and extract stats
# Also, we need to keep track of the metrics since the beginning, so that the values in the dataset
# are 'at the time' instead of the cumulative totals (as is in default on the page)
fighters = dict()
final_data = []
counter = 0 # SET A COUNTER TO TRACK THE PROGRESS IN THE COMMANDLINE
timer = Timer.Timer()

for event_link in links: 
    counter += 1
    print(f'ITERATION: {str(counter).ljust(3)} / {len(links)}     ||     CURRENT ITERATION TIME: {timer.format_time(timer.checkpoint())} TOTAL TIME: {timer.format_time(timer.total_time_elapsed())}')
    
    event_response = requests.get(str(event_link))
    event_soup = BeautifulSoup(event_response.content, 'html.parser')
    
    # before we get the links of all fights, let's extract some event-specific data
    event_name = event_soup.find(class_='b-content__title-highlight').string.strip()
    event_info = filter(lambda x: x != '\n', event_soup.find(class_='b-list__box-list').children)
    event_date = next(event_info).contents[2].strip()
    event_location = next(event_info).contents[2].strip()
    
    fight_links = []
    for link in event_soup.find_all('a', class_='b-flag'): 
        if link.get('href') in fight_links:
            pass
        else: 
            fight_links.insert(0, link.get('href'))
    
    # going into fight details
    for fight_link in fight_links:
        fight_response = requests.get(str(fight_link))
        fight_soup = BeautifulSoup(fight_response.content, 'html.parser')
        
        # getting the data about the fight and its conclusion
        fight_type = fight_soup.find(class_='b-fight-details__fight-title').text.strip().lower()
        fight_title_bout = True if ('title' in fight_type) or ('superfight' in fight_type) else False
        # decinding on weight of the fight
        fight_weight = ''
        if 'atomweight' in fight_type: fight_weight = 'Atomweight'
        elif 'strawweight' in fight_type: fight_weight = 'Strawweight'
        elif 'flyweight' in fight_type: fight_weight = 'Flyweight'
        elif 'bantamweight' in fight_type: fight_weight = 'Bantamweight'
        elif 'featherweight' in fight_type: fight_weight = 'Featherweight'
        elif 'lightweight' in fight_type: fight_weight = 'Lightweight'
        elif 'super lightweight' in fight_type: fight_weight = 'Super Lightweight'
        elif 'welterweight' in fight_type: fight_weight = 'Welterweight'
        elif 'super welterweight' in fight_type: fight_weight = 'Super Welterweight'
        elif 'middleweight' in fight_type: fight_weight = 'Middleweight'
        elif 'super middleweight' in fight_type: fight_weight = 'Super Middleweight'
        elif 'light heavyweight' in fight_type: fight_weight = 'Light Heavyweight'
        elif 'cruiserweight' in fight_type: fight_weight = 'Cruiserweight'
        elif 'heavyweight' in fight_type: fight_weight = 'Heavyweight'
        elif 'super heavyweight' in fight_type: fight_weight = 'Super Heavyweight'
        elif 'catch' in fight_type: fight_weight = 'Catchweight'
        elif 'open weight' in fight_type: fight_weight = 'Open Weight'
        
        fight_gender = 'Female' if "women's" in fight_type else 'Male'
        fight_details = filter(lambda x: x != '\n', fight_soup.find(class_='b-fight-details__text').children)
        conclusion_method = next(fight_details).contents[3].string.strip()
        rounds = next(fight_details).contents[2].string.strip()
        time_last_round = utilities.minutes_to_seconds(next(fight_details).contents[2].string.strip())
        time_format = next(fight_details).contents[2].string.strip()
        referee = next(fight_details).contents[3].string.strip()
        
        # getting fighters names and links to fighter page
        fighters_links = fight_soup.find(class_='b-fight-details__persons clearfix').find_all('a')
        R_link = str(fighters_links[0].get('href'))
        R_name = fighters_links[0].string.strip()
        B_link = str(fighters_links[1].get('href'))
        B_name = fighters_links[1].string.strip()
        
        # adding fighters, if necessary (note that their physical attributes are constant along the years)
        if R_name not in fighters.keys():
            utilities.add_fighters(R_name, fighters, R_link)
        
        if B_name not in fighters.keys():    
            utilities.add_fighters(B_name, fighters, B_link)
            
        # adding row of data in the form of inner array (we will convert it to dataframe later using pandas)
        final_data.append([
            # event details
            event_name,
            event_date,
            event_location,
            fight_weight,
            fight_title_bout,
            fight_gender,
            # data about the RED fighter
            R_name,
            fighters.get(R_name).get("Height_cm"),
            fighters.get(R_name).get("Weight_kg"),
            fighters.get(R_name).get("Reach"),
            fighters.get(R_name).get("Stance"),
            int(event_date[-4:]) - fighters.get(R_name).get("Year of birth") if str(fighters.get(R_name).get("Year of birth")).isnumeric() else '--',
            fighters.get(R_name).get("Average knockdowns"),
            fighters.get(R_name).get("Average Significant strikes attempted"),
            fighters.get(R_name).get("Average Significant strikes landed"),
            fighters.get(R_name).get("Significant strikes % Landed"),
            fighters.get(R_name).get("Average Strikes Attempted"),
            fighters.get(R_name).get("Average Strikes Landed"),
            fighters.get(R_name).get("Total Strikes % Landed"),
            fighters.get(R_name).get("Average Takedowns Attempted"),
            fighters.get(R_name).get("Average Takedowns Landed"),
            fighters.get(R_name).get("Takedowns % Landed"),
            fighters.get(R_name).get("Average Submission attempts"),
            fighters.get(R_name).get("Average Reversals"),
            fighters.get(R_name).get("Average Control"),
            fighters.get(R_name).get("Average Significant Strikes on Head Attempted"),
            fighters.get(R_name).get("Average Significant Strikes on Head Landed"),
            fighters.get(R_name).get("Significant Strikes on Head % Landed"),
            fighters.get(R_name).get("Average Significant Strikes on Body Attempted"),
            fighters.get(R_name).get("Average Significant Strikes on Body Landed"),
            fighters.get(R_name).get("Significant Strikes on Body % Landed"),
            fighters.get(R_name).get("Average Significant Strikes on Leg Attempted"),
            fighters.get(R_name).get("Average Significant Strikes on Leg Landed"),
            fighters.get(R_name).get("Significant Strikes on Leg % Landed"),
            fighters.get(R_name).get("Average Significant Strikes at Distance Attempted"),
            fighters.get(R_name).get("Average Significant Strikes at Distance Landed"),
            fighters.get(R_name).get("Significant Strikes at Distance % Landed"),
            fighters.get(R_name).get("Average Significant Strikes in Clinch Attempted"),
            fighters.get(R_name).get("Average Significant Strikes in Clinch Landed"),
            fighters.get(R_name).get("Significant Strikes in Clinch % Landed"),
            fighters.get(R_name).get("Average Significant Strikes on Ground Attempted"),
            fighters.get(R_name).get("Average Significant Strikes on Ground Landed"),
            fighters.get(R_name).get("Significant Strikes on Ground % Landed"),
            fighters.get(R_name).get("Winning streak"),
            fighters.get(R_name).get("Losing streak"),
            fighters.get(R_name).get("Total number of wins"),
            fighters.get(R_name).get("Total number of title wins"),
            fighters.get(R_name).get("Total number of wins by unanimous decision"),
            fighters.get(R_name).get("Total number of wins by KO/TKO"),
            fighters.get(R_name).get("Total number of wins by submission"),
            fighters.get(R_name).get("Total number of wins by split decision"),
            fighters.get(R_name).get("Total number of wins by majority vote"),
            fighters.get(R_name).get("Total number of wins by doctor stoppage"),
            fighters.get(R_name).get("Total number of fights"),
            fighters.get(R_name).get("Total number of fights for title"),
            fighters.get(R_name).get("Win %"),
            # for the oponents of R_name in the career
            fighters.get(R_name).get("Opp. Average knockdowns"),
            fighters.get(R_name).get("Opp. Average Significant strikes attempted"),
            fighters.get(R_name).get("Opp. Average Significant strikes landed"),
            fighters.get(R_name).get("Opp. Significant strikes % Landed"),
            fighters.get(R_name).get("Opp. Average Strikes Attempted"),
            fighters.get(R_name).get("Opp. Average Strikes Landed"),
            fighters.get(R_name).get("Opp. Total Strikes % Landed"),
            fighters.get(R_name).get("Opp. Average Takedowns Attempted"),
            fighters.get(R_name).get("Opp. Average Takedowns Landed"),
            fighters.get(R_name).get("Opp. Takedowns % Landed"),
            fighters.get(R_name).get("Opp. Average Submission attempts"),
            fighters.get(R_name).get("Opp. Average Reversals"),
            fighters.get(R_name).get("Opp. Average Control"),
            fighters.get(R_name).get("Opp. Average Significant Strikes on Head Attempted"),
            fighters.get(R_name).get("Opp. Average Significant Strikes on Head Landed"),
            fighters.get(R_name).get("Opp. Significant Strikes on Head % Landed"),
            fighters.get(R_name).get("Opp. Average Significant Strikes on Body Attempted"),
            fighters.get(R_name).get("Opp. Average Significant Strikes on Body Landed"),
            fighters.get(R_name).get("Opp. Significant Strikes on Body % Landed"),
            fighters.get(R_name).get("Opp. Average Significant Strikes on Leg Attempted"),
            fighters.get(R_name).get("Opp. Average Significant Strikes on Leg Landed"),
            fighters.get(R_name).get("Opp. Significant Strikes on Leg % Landed"),
            fighters.get(R_name).get("Opp. Average Significant Strikes at Distance Attempted"),
            fighters.get(R_name).get("Opp. Average Significant Strikes at Distance Landed"),
            fighters.get(R_name).get("Opp. Significant Strikes at Distance % Landed"),
            fighters.get(R_name).get("Opp. Average Significant Strikes in Clinch Attempted"),
            fighters.get(R_name).get("Opp. Average Significant Strikes in Clinch Landed"),
            fighters.get(R_name).get("Opp. Significant Strikes in Clinch % Landed"),
            fighters.get(R_name).get("Opp. Average Significant Strikes on Ground Attempted"),
            fighters.get(R_name).get("Opp. Average Significant Strikes on Ground Landed"),
            fighters.get(R_name).get("Opp. Significant Strikes on Ground % Landed"),
            # data about the BLUE fighter
            B_name,
            fighters.get(B_name).get("Height_cm"),
            fighters.get(B_name).get("Weight_kg"),
            fighters.get(B_name).get("Reach"),
            fighters.get(B_name).get("Stance"),
            int(event_date[-4:]) - fighters.get(B_name).get("Year of birth") if str(fighters.get(B_name).get("Year of birth")).isnumeric() else '--',
            fighters.get(B_name).get("Average knockdowns"),
            fighters.get(B_name).get("Average Significant strikes attempted"),
            fighters.get(B_name).get("Average Significant strikes landed"),
            fighters.get(B_name).get("Significant strikes % Landed"),
            fighters.get(B_name).get("Average Strikes Attempted"),
            fighters.get(B_name).get("Average Strikes Landed"),
            fighters.get(B_name).get("Total Strikes % Landed"),
            fighters.get(B_name).get("Average Takedowns Attempted"),
            fighters.get(B_name).get("Average Takedowns Landed"),
            fighters.get(B_name).get("Takedowns % Landed"),
            fighters.get(B_name).get("Average Submission attempts"),
            fighters.get(B_name).get("Average Reversals"),
            fighters.get(B_name).get("Average Control"),
            fighters.get(B_name).get("Average Significant Strikes on Head Attempted"),
            fighters.get(B_name).get("Average Significant Strikes on Head Landed"),
            fighters.get(B_name).get("Significant Strikes on Head % Landed"),
            fighters.get(B_name).get("Average Significant Strikes on Body Attempted"),
            fighters.get(B_name).get("Average Significant Strikes on Body Landed"),
            fighters.get(B_name).get("Significant Strikes on Body % Landed"),
            fighters.get(B_name).get("Average Significant Strikes on Leg Attempted"),
            fighters.get(B_name).get("Average Significant Strikes on Leg Landed"),
            fighters.get(B_name).get("Significant Strikes on Leg % Landed"),
            fighters.get(B_name).get("Average Significant Strikes at Distance Attempted"),
            fighters.get(B_name).get("Average Significant Strikes at Distance Landed"),
            fighters.get(B_name).get("Significant Strikes at Distance % Landed"),
            fighters.get(B_name).get("Average Significant Strikes in Clinch Attempted"),
            fighters.get(B_name).get("Average Significant Strikes in Clinch Landed"),
            fighters.get(B_name).get("Significant Strikes in Clinch % Landed"),
            fighters.get(B_name).get("Average Significant Strikes on Ground Attempted"),
            fighters.get(B_name).get("Average Significant Strikes on Ground Landed"),
            fighters.get(B_name).get("Significant Strikes on Ground % Landed"),
            fighters.get(B_name).get("Winning streak"),
            fighters.get(B_name).get("Losing streak"),
            fighters.get(B_name).get("Total number of wins"),
            fighters.get(B_name).get("Total number of title wins"),
            fighters.get(B_name).get("Total number of wins by unanimous decision"),
            fighters.get(B_name).get("Total number of wins by KO/TKO"),
            fighters.get(B_name).get("Total number of wins by submission"),
            fighters.get(B_name).get("Total number of wins by split decision"),
            fighters.get(B_name).get("Total number of wins by majority vote"),
            fighters.get(B_name).get("Total number of wins by doctor stoppage"),
            fighters.get(B_name).get("Total number of fights"),
            fighters.get(B_name).get("Total number of fights for title"),
            fighters.get(B_name).get("Win %"),
            # for the B_name OPPONENTS in the career
            fighters.get(B_name).get("Opp. Average knockdowns"),
            fighters.get(B_name).get("Opp. Average Significant strikes attempted"),
            fighters.get(B_name).get("Opp. Average Significant strikes landed"),
            fighters.get(B_name).get("Opp. Significant strikes % Landed"),
            fighters.get(B_name).get("Opp. Average Strikes Attempted"),
            fighters.get(B_name).get("Opp. Average Strikes Landed"),
            fighters.get(B_name).get("Opp. Total Strikes % Landed"),
            fighters.get(B_name).get("Opp. Average Takedowns Attempted"),
            fighters.get(B_name).get("Opp. Average Takedowns Landed"),
            fighters.get(B_name).get("Opp. Takedowns % Landed"),
            fighters.get(B_name).get("Opp. Average Submission attempts"),
            fighters.get(B_name).get("Opp. Average Reversals"),
            fighters.get(B_name).get("Opp. Average Control"),
            fighters.get(B_name).get("Opp. Average Significant Strikes on Head Attempted"),
            fighters.get(B_name).get("Opp. Average Significant Strikes on Head Landed"),
            fighters.get(B_name).get("Opp. Significant Strikes on Head % Landed"),
            fighters.get(B_name).get("Opp. Average Significant Strikes on Body Attempted"),
            fighters.get(B_name).get("Opp. Average Significant Strikes on Body Landed"),
            fighters.get(B_name).get("Opp. Significant Strikes on Body % Landed"),
            fighters.get(B_name).get("Opp. Average Significant Strikes on Leg Attempted"),
            fighters.get(B_name).get("Opp. Average Significant Strikes on Leg Landed"),
            fighters.get(B_name).get("Opp. Significant Strikes on Leg % Landed"),
            fighters.get(B_name).get("Opp. Average Significant Strikes at Distance Attempted"),
            fighters.get(B_name).get("Opp. Average Significant Strikes at Distance Landed"),
            fighters.get(B_name).get("Opp. Significant Strikes at Distance % Landed"),
            fighters.get(B_name).get("Opp. Average Significant Strikes in Clinch Attempted"),
            fighters.get(B_name).get("Opp. Average Significant Strikes in Clinch Landed"),
            fighters.get(B_name).get("Opp. Significant Strikes in Clinch % Landed"),
            fighters.get(B_name).get("Opp. Average Significant Strikes on Ground Attempted"),
            fighters.get(B_name).get("Opp. Average Significant Strikes on Ground Landed"),
            fighters.get(B_name).get("Opp. Significant Strikes on Ground % Landed"),
            # data about the fight and conclusion
            rounds,
            time_last_round,
            time_format,
            referee,
            conclusion_method,
            utilities.winner(fight_soup)
            ])
        
        # update statistics after fight    
        utilities.update_fighters(R_name, "Red", fighters, fight_soup, fight_title_bout, conclusion_method)
        utilities.update_fighters(B_name, "Blue", fighters, fight_soup, fight_title_bout, conclusion_method)

# make dataframe out of set of arrays
df = pd.DataFrame(final_data,
                  columns = [
                      # event parsing
                      'Event_Name',
                      'Event_Date',
                      'Event_Location',
                      'Fight_Weight',
                      'Fight_Title_Bout',
                      'Fight_Gender',
                      # RED parsing
                      'R_Name',
                      'R_Height_cm',
                      'R_Weight_kg',
                      'R_Reach',
                      'R_Stance',
                      'R_Age',
                      'R_Average_Knockdowns',
                      'R_Average_Significant_Strikes_Attempted',
                      'R_Average_Significant_Strikes_Landed',
                      'R_Significant_Strikes_%_Landed',
                      'R_Average_Strikes_Attempted',
                      'R_Average_Strikes_Landed',
                      'R_Total_Strikes_%_Landed',
                      'R_Average_Takedowns_Attempted',
                      'R_Average_Takedowns_Landed',
                      'R_Takedowns_%_Landed',
                      'R_Average_Submission_Attempts',
                      'R_Average_Reversals',
                      'R_Average_Control',
                      'R_Average_Significant_Strikes_on_Head_Attempted',
                      'R_Average_Significant_Strikes_on_Head_Landed',
                      'R_Significant_Strikes_on_Head_%_Landed',
                      'R_Average_Significant_Strikes_on_Body_Attempted',
                      'R_Average_Significant_Strikes_on_Body_Landed',
                      'R_Significant_Strikes_on_Body_%_Landed',
                      'R_Average_Significant_Strikes_on_Leg_Attempted',
                      'R_Average_Significant_Strikes_on_Leg_Landed',
                      'R_Significant_Strikes_on_Leg_%_Landed',
                      'R_Average_Significant_Strikes_at_Distance_Attempted',
                      'R_Average_Significant_Strikes_at_Distance_Landed',
                      'R_Significant_Strikes_at_Distance_%_Landed',
                      'R_Average_Significant_Strikes_in_Clinch_Attempted',
                      'R_Average_Significant_Strikes_in_Clinch_Landed',
                      'R_Significant_Strikes_in_Clinch_%_Landed',
                      'R_Average_Significant_Strikes_on_Ground_Attempted',
                      'R_Average_Significant_Strikes_on_Ground_Landed',
                      'R_Significant_Strikes_on_Ground_%_Landed',
                      'R_Winning_Streak',
                      'R_Losing_Streak',
                      'R_Total_Number_of_Wins',
                      'R_Total_Number_of_Title_Wins',
                      'R_Total_Number_of_Wins_By_KO/TKO',
                      'R_Total_Number_of_Wins_By_Unanimous_Decision',
                      'R_Total_Number_of_Wins_By_Submission',
                      'R_Total_Number_of_Wins_By_Split_Decision',
                      'R_Total_Number_of_Wins_By_Majority_Vote',
                      'R_Total_Number_of_Wins_by_Doctor_Stoppage',
                      'R_Total_Number_of_Fights',
                      'R_Total_Number_of_Fights_for_Title',
                      'R_Win_%',
                      
 
                       # FOR RED OPPONENTS IN THE WHOLE CAREER
                      'R_Opp_Average_Knockdowns',
                      'R_Opp_Average_Significant_Strikes_Attempted',
                      'R_Opp_Average_Significant_Strikes_Landed',
                      'R_Opp_Significant_Strikes_%_Landed',
                      'R_Opp_Average_Strikes_Attempted',
                      'R_Opp_Average_Strikes_Landed',
                      'R_Opp_Total_Strikes_%_Landed',
                      'R_Opp_Average_Takedowns_Attempted',
                      'R_Opp_Average_Takedowns_Landed',
                      'R_Opp_Takedowns_%_Landed',
                      'R_Opp_Average_Submission_Attempts',
                      'R_Opp_Average_Reversals',
                      'R_Opp_Average_Control',
                      'R_Opp_Average_Significant_Strikes_on_Head_Attempted',
                      'R_Opp_Average_Significant_Strikes_on_Head_Landed',
                      'R_Opp_Significant_Strikes_on_Head_%_Landed',
                      'R_Opp_Average_Significant_Strikes_on_Body_Attempted',
                      'R_Opp_Average_Significant_Strikes_on_Body_Landed',
                      'R_Opp_Significant_Strikes_on_Body_%_Landed',
                      'R_Opp_Average_Significant_Strikes_on_Leg_Attempted',
                      'R_Opp_Average_Significant_Strikes_on_Leg_Landed',
                      'R_Opp_Significant_Strikes_on_Leg_%_Landed',
                      'R_Opp_Average_Significant_Strikes_at_Distance_Attempted',
                      'R_Opp_Average_Significant_Strikes_at_Distance_Landed',
                      'R_Opp_Significant_Strikes_at_Distance_%_Landed',
                      'R_Opp_Average_Significant_Strikes_in_Clinch_Attempted',
                      'R_Opp_Average_Significant_Strikes_in_Clinch_Landed',
                      'R_Opp_Significant_Strikes_in_Clinch_%_Landed',
                      'R_Opp_Average_Significant_Strikes_on_Ground_Attempted',
                      'R_Opp_Average_Significant_Strikes_on_Ground_Landed',
                      'R_Opp_Significant_Strikes_on_Ground_%_Landed',
                      # BLUE parsing
                      'B_Name',
                      'B_Height_cm',
                      'B_Weight_kg',
                      'B_Reach',
                      'B_Stance',
                      'B_Age',
                      'B_Average_Knockdowns',
                      'B_Average_Significant_Strikes_Attempted',
                      'B_Average_Significant_Strikes_Landed',
                      'B_Significant_Strikes_%_Landed',
                      'B_Average_Strikes_Attempted',
                      'B_Average_Strikes_Landed',
                      'B_Total_Strikes_%_Landed',
                      'B_Average_Takedowns_Attempted',
                      'B_Average_Takedowns_Landed',
                      'B_Takedowns_%_Landed',
                      'B_Average_Submission_Attempts',
                      'B_Average_Reversals',
                      'B_Average_Control',
                      'B_Average_Significant_Strikes_on_Head_Attempted',
                      'B_Average_Significant_Strikes_on_Head_Landed',
                      'B_Significant_Strikes_on_Head_%_Landed',
                      'B_Average_Significant_Strikes_on_Body_Attempted',
                      'B_Average_Significant_Strikes_on_Body_Landed',
                      'B_Significant_Strikes_on_Body_%_Landed',
                      'B_Average_Significant_Strikes_on_Leg_Attempted',
                      'B_Average_Significant_Strikes_on_Leg_Landed',
                      'B_Significant_Strikes_on_Leg_%_Landed',
                      'B_Average_Significant_Strikes_at_Distance_Attempted',
                      'B_Average_Significant_Strikes_at_Distance_Landed',
                      'B_Significant_Strikes_at_Distance_%_Landed',
                      'B_Average_Significant_Strikes_in_Clinch_Attempted',
                      'B_Average_Significant_Strikes_in_Clinch_Landed',
                      'B_Significant_Strikes_in_Clinch_%_Landed',
                      'B_Average_Significant_Strikes_on_Ground_Attempted',
                      'B_Average_Significant_Strikes_on_Ground_Landed',
                      'B_Significant_Strikes_on_Ground_%_Landed',
                      'B_Winning_Streak',
                      'B_Losing_Streak',
                      'B_Total_Number_of_Wins',
                      'B_Total_Number_of_Title_Wins',
                      'B_Total_Number_of_Wins_By_KO/TKO',
                      'B_Total_Number_of_Wins_By_Unanimous_Decision',
                      'B_Total_Number_of_Wins_By_Submission',
                      'B_Total_Number_of_Wins_By_Split_Decision',
                      'B_Total_Number_of_Wins_By_Majority_Vote',
                      'B_Total_Number_of_Wins_by_Doctor_Stoppage',
                      'B_Total_Number_of_Fights',
                      'B_Total_Number_of_Fights_for_Title',
                      'B_Win_%',
                      # FOR BLUE OPPONENTS IN THE WHOLE CAREER
                      'B_Opp_Average_Knockdowns',
                      'B_Opp_Average_Significant_Strikes_Attempted',
                      'B_Opp_Average_Significant_Strikes_Landed',
                      'B_Opp_Significant_Strikes_%_Landed',
                      'B_Opp_Average_Strikes_Attempted',
                      'B_Opp_Average_Strikes_Landed',
                      'B_Opp_Total_Strikes_%_Landed',
                      'B_Opp_Average_Takedowns_Attempted',
                      'B_Opp_Average_Takedowns_Landed',
                      'B_Opp_Takedowns_%_Landed',
                      'B_Opp_Average_Submission_Attempts',
                      'B_Opp_Average_Reversals',
                      'B_Opp_Average_Control',
                      'B_Opp_Average_Significant_Strikes_on_Head_Attempted',
                      'B_Opp_Average_Significant_Strikes_on_Head_Landed',
                      'B_Opp_Significant_Strikes_on_Head_%_Landed',
                      'B_Opp_Average_Significant_Strikes_on_Body_Attempted',
                      'B_Opp_Average_Significant_Strikes_on_Body_Landed',
                      'B_Opp_Significant_Strikes_on_Body_%_Landed',
                      'B_Opp_Average_Significant_Strikes_on_Leg_Attempted',
                      'B_Opp_Average_Significant_Strikes_on_Leg_Landed',
                      'B_Opp_Significant_Strikes_on_Leg_%_Landed',
                      'B_Opp_Average_Significant_Strikes_at_Distance_Attempted',
                      'B_Opp_Average_Significant_Strikes_at_Distance_Landed',
                      'B_Opp_Significant_Strikes_at_Distance_%_Landed',
                      'B_Opp_Average_Significant_Strikes_in_Clinch_Attempted',
                      'B_Opp_Average_Significant_Strikes_in_Clinch_Landed',
                      'B_Opp_Significant_Strikes_in_Clinch_%_Landed',
                      'B_Opp_Average_Significant_Strikes_on_Ground_Attempted',
                      'B_Opp_Average_Significant_Strikes_on_Ground_Landed',
                      'B_Opp_Significant_Strikes_on_Ground_%_Landed',
                      # fight data parsing 
                      'Number_of_Rounds',
                      'Last_Round_Duration',
                      'Time_Format',
                      'Referee',
                      'Conclusion_Method',
                      'Winner'])

df = df.sort_values('Event_Date', ascending=True).reset_index(drop=True)
df = df.replace('--', pd.NA)

# We'll also try to introduce some new variables. ----------------------------------------
#--------------------------------------------------------------------------------------------------

# 1. Underdog. This will signify if a fighter can be considered as an underdog for the fight.
# It may impact fighter performance from the mental perspective where, potentially, a fighter may have a hard time recently.
# We define it as having a losing streak of 2:
R_streak = df['R_Losing_Streak'] > 2
B_streak = df['B_Losing_Streak'] > 2

i = 0
underdog = []
for i in range(len(R_streak)):
    if (R_streak[i] == True) and (B_streak[i] == False):
        underdog.append('Red')
    elif (R_streak[i] == False) and (B_streak[i] == True):
        underdog.append('Blue')
    else:
        underdog.append('No one')

df['Underdog'] = underdog



# saving to excel
df.to_excel('UFCdata_final.xlsx')

    