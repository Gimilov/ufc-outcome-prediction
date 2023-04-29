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
            # data about the RED fighter
            R_name,
            fighters.get(R_name).get("Height_cm"),
            fighters.get(R_name).get("Weight_kg"),
            fighters.get(R_name).get("Reach"),
            fighters.get(R_name).get("Stance"),
            int(event_date[-4:]) - fighters.get(R_name).get("Year of birth") if str(fighters.get(R_name).get("Year of birth")).isnumeric() else '--',
            fighters.get(R_name).get("Total knockdowns"),
            fighters.get(R_name).get("Total Significant strikes attempted"),
            fighters.get(R_name).get("Total Significant strikes landed"),
            fighters.get(R_name).get("Significant strikes % Landed"),
            fighters.get(R_name).get("Total Strikes Attempted"),
            fighters.get(R_name).get("Total Strikes Landed"),
            fighters.get(R_name).get("Total Strikes % Landed"),
            fighters.get(R_name).get("Total Takedowns Attempted"),
            fighters.get(R_name).get("Total Takedowns Landed"),
            fighters.get(R_name).get("Takedowns % Landed"),
            fighters.get(R_name).get("Total Submission attempts"),
            fighters.get(R_name).get("Total Reversals"),
            fighters.get(R_name).get("Total Control"),
            fighters.get(R_name).get("Average Control"),
            fighters.get(R_name).get("Total Significant Strikes on Head Attempted"),
            fighters.get(R_name).get("Total Significant Strikes on Head Landed"),
            fighters.get(R_name).get("Total Significant Strikes on Head % Landed"),
            fighters.get(R_name).get("Total Significant Strikes on Body Attempted"),
            fighters.get(R_name).get("Total Significant Strikes on Body Landed"),
            fighters.get(R_name).get("Total Significant Strikes on Body % Landed"),
            fighters.get(R_name).get("Total Significant Strikes on Leg Attempted"),
            fighters.get(R_name).get("Total Significant Strikes on Leg Landed"),
            fighters.get(R_name).get("Total Significant Strikes on Leg % Landed"),
            fighters.get(R_name).get("Total Significant Strikes at Distance Attempted"),
            fighters.get(R_name).get("Total Significant Strikes at Distance Landed"),
            fighters.get(R_name).get("Total Significant Strikes at Distance % Landed"),
            fighters.get(R_name).get("Total Significant Strikes in Clinch Attempted"),
            fighters.get(R_name).get("Total Significant Strikes in Clinch Landed"),
            fighters.get(R_name).get("Total Significant Strikes in Clinch % Landed"),
            fighters.get(R_name).get("Total Significant Strikes on Ground Attempted"),
            fighters.get(R_name).get("Total Significant Strikes on Ground Landed"),
            fighters.get(R_name).get("Total Significant Strikes on Ground % Landed"),
            fighters.get(R_name).get("Winning streak"),
            fighters.get(R_name).get("Losing streak"),
            fighters.get(R_name).get("Total number of wins"),
            fighters.get(R_name).get("Total number of fights"),
            fighters.get(R_name).get("Win %"),
            # data about the BLUE fighter
            B_name,
            fighters.get(B_name).get("Height_cm"),
            fighters.get(B_name).get("Weight_kg"),
            fighters.get(B_name).get("Reach"),
            fighters.get(B_name).get("Stance"),
            int(event_date[-4:]) - fighters.get(B_name).get("Year of birth") if str(fighters.get(B_name).get("Year of birth")).isnumeric() else '--',
            fighters.get(B_name).get("Total knockdowns"),
            fighters.get(B_name).get("Total Significant strikes attempted"),
            fighters.get(B_name).get("Total Significant strikes landed"),
            fighters.get(B_name).get("Significant strikes % Landed"),
            fighters.get(B_name).get("Total Strikes Attempted"),
            fighters.get(B_name).get("Total Strikes Landed"),
            fighters.get(B_name).get("Total Strikes % Landed"),
            fighters.get(B_name).get("Total Takedowns Attempted"),
            fighters.get(B_name).get("Total Takedowns Landed"),
            fighters.get(B_name).get("Takedowns % Landed"),
            fighters.get(B_name).get("Total Submission attempts"),
            fighters.get(B_name).get("Total Reversals"),
            fighters.get(B_name).get("Total Control"),
            fighters.get(B_name).get("Average Control"),
            fighters.get(B_name).get("Total Significant Strikes on Head Attempted"),
            fighters.get(B_name).get("Total Significant Strikes on Head Landed"),
            fighters.get(B_name).get("Total Significant Strikes on Head % Landed"),
            fighters.get(B_name).get("Total Significant Strikes on Body Attempted"),
            fighters.get(B_name).get("Total Significant Strikes on Body Landed"),
            fighters.get(B_name).get("Total Significant Strikes on Body % Landed"),
            fighters.get(B_name).get("Total Significant Strikes on Leg Attempted"),
            fighters.get(B_name).get("Total Significant Strikes on Leg Landed"),
            fighters.get(B_name).get("Total Significant Strikes on Leg % Landed"),
            fighters.get(B_name).get("Total Significant Strikes at Distance Attempted"),
            fighters.get(B_name).get("Total Significant Strikes at Distance Landed"),
            fighters.get(B_name).get("Total Significant Strikes at Distance % Landed"),
            fighters.get(B_name).get("Total Significant Strikes in Clinch Attempted"),
            fighters.get(B_name).get("Total Significant Strikes in Clinch Landed"),
            fighters.get(B_name).get("Total Significant Strikes in Clinch % Landed"),
            fighters.get(B_name).get("Total Significant Strikes on Ground Attempted"),
            fighters.get(B_name).get("Total Significant Strikes on Ground Landed"),
            fighters.get(B_name).get("Total Significant Strikes on Ground % Landed"),
            fighters.get(B_name).get("Winning streak"),
            fighters.get(B_name).get("Losing streak"),
            fighters.get(B_name).get("Total number of wins"),
            fighters.get(B_name).get("Total number of fights"),
            fighters.get(B_name).get("Win %"),
            # data about the fight and conclusion
            rounds,
            time_last_round,
            time_format,
            referee,
            conclusion_method,
            utilities.winner(fight_soup)
            ])
        
        # update statistics after fight    
        utilities.update_fighters(R_name, "Red", fighters, fight_soup)
        utilities.update_fighters(B_name, "Blue", fighters, fight_soup)

# make dataframe out of set of arrays
df = pd.DataFrame(final_data,
                  columns = [
                      # event parsing
                      'Event_Name',
                      'Event_Date',
                      'Event_Location',
                      # RED parsing
                      'R_Name',
                      'R_Height_cm',
                      'R_Weight_kg',
                      'R_Reach',
                      'R_Stance',
                      'R_Age',
                      'R_Total_Knockdowns',
                      'R_Total_Significant_Strikes_Attempted',
                      'R_Total_Significant_Strikes_Landed',
                      'R_Significant_Strikes_%_Landed',
                      'R_Total_Strikes_Attempted',
                      'R_Total_Strikes_Landed',
                      'R_Total_Strikes_%_Landed',
                      'R_Total_Takedowns_Attempted',
                      'R_Total_Takedowns_Landed',
                      'R_Takedowns_%_Landed',
                      'R_Total_Submission_Attempts',
                      'R_Total_Reversals',
                      'R_Total_Control',
                      'R_Average_Control',
                      'R_Total_Significant_Strikes_on_Head_Attempted',
                      'R_Total_Significant_Strikes_on_Head_Landed',
                      'R_Total_Significant_Strikes_on_Head_%_Landed',
                      'R_Total_Significant_Strikes_on_Body_Attempted',
                      'R_Total_Significant_Strikes_on_Body_Landed',
                      'R_Total_Significant_Strikes_on_Body_%_Landed',
                      'R_Total_Significant_Strikes_on_Leg_Attempted',
                      'R_Total_Significant_Strikes_on_Leg_Landed',
                      'R_Total_Significant_Strikes_on_Leg_%_Landed',
                      'R_Total_Significant_Strikes_at_Distance_Attempted',
                      'R_Total_Significant_Strikes_at_Distance_Landed',
                      'R_Total_Significant_Strikes_at_Distance_%_Landed',
                      'R_Total_Significant_Strikes_in_Clinch_Attempted',
                      'R_Total_Significant_Strikes_in_Clinch_Landed',
                      'R_Total_Significant_Strikes_in_Clinch_%_Landed',
                      'R_Total_Significant_Strikes_on_Ground_Attempted',
                      'R_Total_Significant_Strikes_on_Ground_Landed',
                      'R_Total_Significant_Strikes_on_Ground_%_Landed',
                      'R_Winning_Streak',
                      'R_Losing_Streak',
                      'R_Total_Number_of_Wins',
                      'R_Total_Number_of_Fights',
                      'R_Win_%',
                      # BLUE parsing
                      'B_Name',
                      'B_Height_cm',
                      'B_Weight_kg',
                      'B_Reach',
                      'B_Stance',
                      'B_Age',
                      'B_Total_Knockdowns',
                      'B_Total_Significant_Strikes_Attempted',
                      'B_Total_Significant_Strikes_Landed',
                      'B_Significant_Strikes_%_Landed',
                      'B_Total_Strikes_Attempted',
                      'B_Total_Strikes_Landed',
                      'B_Total_Strikes_%_Landed',
                      'B_Total_Takedowns_Attempted',
                      'B_Total_Takedowns_Landed',
                      'B_Takedowns_%_Landed',
                      'B_Total_Submission_Attempts',
                      'B_Total_Reversals',
                      'B_Total_Control',
                      'B_Average_Control',
                      'B_Total_Significant_Strikes_on_Head_Attempted',
                      'B_Total_Significant_Strikes_on_Head_Landed',
                      'B_Total_Significant_Strikes_on_Head_%_Landed',
                      'B_Total_Significant_Strikes_on_Body_Attempted',
                      'B_Total_Significant_Strikes_on_Body_Landed',
                      'B_Total_Significant_Strikes_on_Body_%_Landed',
                      'B_Total_Significant_Strikes_on_Leg_Attempted',
                      'B_Total_Significant_Strikes_on_Leg_Landed',
                      'B_Total_Significant_Strikes_on_Leg_%_Landed',
                      'B_Total_Significant_Strikes_at_Distance_Attempted',
                      'B_Total_Significant_Strikes_at_Distance_Landed',
                      'B_Total_Significant_Strikes_at_Distance_%_Landed',
                      'B_Total_Significant_Strikes_in_Clinch_Attempted',
                      'B_Total_Significant_Strikes_in_Clinch_Landed',
                      'B_Total_Significant_Strikes_in_Clinch_%_Landed',
                      'B_Total_Significant_Strikes_on_Ground_Attempted',
                      'B_Total_Significant_Strikes_on_Ground_Landed',
                      'B_Total_Significant_Strikes_on_Ground_%_Landed',
                      'B_Winning_Streak',
                      'B_Losing_Streak',
                      'B_Total_Number_of_Wins',
                      'B_Total_Number_of_Fights',
                      'B_Win_%',
                      # fight data parsing 
                      'Number_of_Rounds',
                      'Last_Round_Duration',
                      'Time_Format',
                      'Referee',
                      'Conclusion_Method',
                      'Winner'])

df = df.sort_values('Event_Date', ascending=True).reset_index(drop=True)
df = df.replace('--', pd.NA)
# saving to excel
df.to_excel('UFCdata.xlsx')

    