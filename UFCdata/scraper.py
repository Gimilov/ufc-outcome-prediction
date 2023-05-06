import pandas as pd
import requests
from bs4 import BeautifulSoup
import utilities
import Timer
import pickle

if input("Do you want to scrap the fight statistics from ufcstats.com? Y/N: ") == 'Y':
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
    
    x = input("Do you need to load the last saved state of the fighters dictionary? If so, input the last SAVED index. Otherwise, click ENTER: ")
    checkpoint_ind = 0 
    if x.isnumeric():
        try:
            with open('fighters_dict_backup.pkl', 'rb') as file:
                fighters = pickle.load(file)
                checkpoint_ind = int(x) + 1
        except FileNotFoundError:
            print("The file was not found. Terminating the program...")
            exit()
    else:
        print("Fine. Then let's start all over again.")
        
    timer = Timer.Timer()
    
    for event_index, event_link in enumerate(links[checkpoint_ind:]):
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
                fighters.get(R_name).get("Total Significant Strikes on Head Attempted"),
                fighters.get(R_name).get("Total Significant Strikes on Head Landed"),
                fighters.get(R_name).get("Significant Strikes on Head % Landed"),
                fighters.get(R_name).get("Total Significant Strikes on Body Attempted"),
                fighters.get(R_name).get("Total Significant Strikes on Body Landed"),
                fighters.get(R_name).get("Significant Strikes on Body % Landed"),
                fighters.get(R_name).get("Total Significant Strikes on Leg Attempted"),
                fighters.get(R_name).get("Total Significant Strikes on Leg Landed"),
                fighters.get(R_name).get("Significant Strikes on Leg % Landed"),
                fighters.get(R_name).get("Total Significant Strikes at Distance Attempted"),
                fighters.get(R_name).get("Total Significant Strikes at Distance Landed"),
                fighters.get(R_name).get("Significant Strikes at Distance % Landed"),
                fighters.get(R_name).get("Total Significant Strikes in Clinch Attempted"),
                fighters.get(R_name).get("Total Significant Strikes in Clinch Landed"),
                fighters.get(R_name).get("Significant Strikes in Clinch % Landed"),
                fighters.get(R_name).get("Total Significant Strikes on Ground Attempted"),
                fighters.get(R_name).get("Total Significant Strikes on Ground Landed"),
                fighters.get(R_name).get("Significant Strikes on Ground % Landed"),
                fighters.get(R_name).get("Average knockdowns"),
                fighters.get(R_name).get("Average Significant strikes attempted"),
                fighters.get(R_name).get("Average Significant strikes landed"),
                fighters.get(R_name).get("Average Strikes Attempted"),
                fighters.get(R_name).get("Average Strikes Landed"),
                fighters.get(R_name).get("Average Takedowns Attempted"),
                fighters.get(R_name).get("Average Takedowns Landed"),
                fighters.get(R_name).get("Average Submission attempts"),
                fighters.get(R_name).get("Average Reversals"),
                fighters.get(R_name).get("Average Control"),
                fighters.get(R_name).get("Average Significant Strikes on Head Attempted"),
                fighters.get(R_name).get("Average Significant Strikes on Head Landed"),
                fighters.get(R_name).get("Average Significant Strikes on Body Attempted"),
                fighters.get(R_name).get("Average Significant Strikes on Body Landed"),
                fighters.get(R_name).get("Average Significant Strikes on Leg Attempted"),
                fighters.get(R_name).get("Average Significant Strikes on Leg Landed"),
                fighters.get(R_name).get("Average Significant Strikes at Distance Attempted"),
                fighters.get(R_name).get("Average Significant Strikes at Distance Landed"),
                fighters.get(R_name).get("Average Significant Strikes in Clinch Attempted"),
                fighters.get(R_name).get("Average Significant Strikes in Clinch Landed"),
                fighters.get(R_name).get("Average Significant Strikes on Ground Attempted"),
                fighters.get(R_name).get("Average Significant Strikes on Ground Landed"),
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
                # for the average oponents of R_name in the career
                fighters.get(R_name).get("Opp. Average knockdowns"),
                fighters.get(R_name).get("Opp. Average Significant strikes attempted"),
                fighters.get(R_name).get("Opp. Average Significant strikes landed"),
                fighters.get(R_name).get("Opp. Significant strikes % Landed"),
                fighters.get(R_name).get("Opp. Average Strikes Attempted"),
                fighters.get(R_name).get("Opp. Average Strikes Landed"),
                fighters.get(R_name).get("Opp. Strikes % Landed"),
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
                fighters.get(B_name).get("Total Significant Strikes on Head Attempted"),
                fighters.get(B_name).get("Total Significant Strikes on Head Landed"),
                fighters.get(B_name).get("Significant Strikes on Head % Landed"),
                fighters.get(B_name).get("Total Significant Strikes on Body Attempted"),
                fighters.get(B_name).get("Total Significant Strikes on Body Landed"),
                fighters.get(B_name).get("Significant Strikes on Body % Landed"),
                fighters.get(B_name).get("Total Significant Strikes on Leg Attempted"),
                fighters.get(B_name).get("Total Significant Strikes on Leg Landed"),
                fighters.get(B_name).get("Significant Strikes on Leg % Landed"),
                fighters.get(B_name).get("Total Significant Strikes at Distance Attempted"),
                fighters.get(B_name).get("Total Significant Strikes at Distance Landed"),
                fighters.get(B_name).get("Significant Strikes at Distance % Landed"),
                fighters.get(B_name).get("Total Significant Strikes in Clinch Attempted"),
                fighters.get(B_name).get("Total Significant Strikes in Clinch Landed"),
                fighters.get(B_name).get("Significant Strikes in Clinch % Landed"),
                fighters.get(B_name).get("Total Significant Strikes on Ground Attempted"),
                fighters.get(B_name).get("Total Significant Strikes on Ground Landed"),
                fighters.get(B_name).get("Significant Strikes on Ground % Landed"),
                fighters.get(B_name).get("Average knockdowns"),
                fighters.get(B_name).get("Average Significant strikes attempted"),
                fighters.get(B_name).get("Average Significant strikes landed"),
                fighters.get(B_name).get("Average Strikes Attempted"),
                fighters.get(B_name).get("Average Strikes Landed"),
                fighters.get(B_name).get("Average Takedowns Attempted"),
                fighters.get(B_name).get("Average Takedowns Landed"),
                fighters.get(B_name).get("Average Submission attempts"),
                fighters.get(B_name).get("Average Reversals"),
                fighters.get(B_name).get("Average Control"),
                fighters.get(B_name).get("Average Significant Strikes on Head Attempted"),
                fighters.get(B_name).get("Average Significant Strikes on Head Landed"),
                fighters.get(B_name).get("Average Significant Strikes on Body Attempted"),
                fighters.get(B_name).get("Average Significant Strikes on Body Landed"),
                fighters.get(B_name).get("Average Significant Strikes on Leg Attempted"),
                fighters.get(B_name).get("Average Significant Strikes on Leg Landed"),
                fighters.get(B_name).get("Average Significant Strikes at Distance Attempted"),
                fighters.get(B_name).get("Average Significant Strikes at Distance Landed"),
                fighters.get(B_name).get("Average Significant Strikes in Clinch Attempted"),
                fighters.get(B_name).get("Average Significant Strikes in Clinch Landed"),
                fighters.get(B_name).get("Average Significant Strikes on Ground Attempted"),
                fighters.get(B_name).get("Average Significant Strikes on Ground Landed"),
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
                # for the B_name average OPPONENTS in the career
                fighters.get(B_name).get("Opp. Average knockdowns"),
                fighters.get(B_name).get("Opp. Average Significant strikes attempted"),
                fighters.get(B_name).get("Opp. Average Significant strikes landed"),
                fighters.get(B_name).get("Opp. Significant strikes % Landed"),
                fighters.get(B_name).get("Opp. Average Strikes Attempted"),
                fighters.get(B_name).get("Opp. Average Strikes Landed"),
                fighters.get(B_name).get("Opp. Strikes % Landed"),
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
        
        # printing progress to the console
        print(f'ITERATION: {str(event_index).ljust(3)} / {len(links[checkpoint_ind:])} DONE    ||     CURRENT ITERATION TIME: {timer.format_time(timer.checkpoint())} TOTAL TIME: {timer.format_time(timer.total_time_elapsed())}  EVENT NAME: {event_name}')
        # making checkpoints in case scraper crashes
        if event_index % 50 == 0 and event_index != 0: 
            print(f"Making checkpoint at {event_index} iterations. Results saved.")
            df = utilities.save_to_df(final_data) # colnames defined in utilities.save_to_df
            df.to_excel('datasets/UFC_fights_stats.xlsx')
            
            # saving the current state of the dictionary to file
            with open('fighters_dict_backup.pkl', 'wb') as file:
                pickle.dump(fighters, file)

    # make dataframe out of set of arrays
    df = utilities.save_to_df(final_data) # colnames defined in utilities.save_to_df

    # saving to excel
    df.to_excel('datasets/UFC_fights_stats.xlsx')


# -------------------- ODDS DATA ---------------------
# -------------------- AND MERGING -------------------

if input("Do you want to scrap odds data for these fights? Y/N: ") == 'Y':
    # I'll get the odds for EACH FIGHTER FIGHTS, then we will parse it into main dataset
    base_url = "https://www.bestfightodds.com/search?query="

    # getting unique fighter names that we have
    ufc_data = pd.read_excel('datasets/UFC_fights_stats.xlsx')
    unique_R_names = ufc_data['R_Name'].unique() # the other side will be accounted as well
    timer = Timer.Timer()
    counter = 0

    first_prompt = input('Do we want to get fighters links again? Y/N: ')
    if first_prompt == 'Y':
        fighter_links = [] # initializing an array to store pages of all odds a fighter had
        for name in unique_R_names:
            print(f'GETTING FIGHTER LINKS ITERATION: {str(counter).ljust(3)} / {len(unique_R_names)}     ||     CURRENT ITERATION TIME: {timer.format_time(timer.checkpoint())} TOTAL TIME: {timer.format_time(timer.total_time_elapsed())}')    
            counter +=1 
            
            formatted_name_search = name.replace(' ', '+')
            formatted_name_link = formatted_name_search.replace('+', '-')
            search_url = base_url + formatted_name_search
            
            response = requests.get(search_url)
            html_response = response.content
            url_response = response.url # we need it as sometimes it redirects to a different page >:(
            soup = BeautifulSoup(html_response, "html.parser")

            for link in soup.find_all('a'):
                if '/events/' in link.get('href'):
                    continue # truly an edge case
                
                if '/fighters/' in url_response: # in case it redirects early and breaks the flow
                    fighter_links.append(url_response)
                    break
                
                if formatted_name_link.lower() in str(link).lower():
                    fighter_links.append('https://www.bestfightodds.com' + link.get('href'))

        print(str(len(fighter_links)) + ' links extracted')
        with open('fighter_links.txt', 'w') as file:
            for line in fighter_links:
                file.write(line + '\n')

    else: 
        pass # we just go further

    # At this point we have all the links to pages of specific fighters, where we can see the matchups
    # a specific fighter had and what the odds were. For now we are concerned to get as much data as
    # possible. Later, we will deal with proper augmentation of the UFCdata.xlsx file. 

    second_prompt = input('Do you want to get the odds for each fight each fighter had? Y/N: ')
    if second_prompt == 'Y':
        odds_data = [] # initializing an array to later be converted into DataFrame object
        with open('fighter_links.txt', 'r') as file:
            lines = file.readlines()
            counter = 0
            for line in lines:
                print(f'GETTING FIGHTER ODDS ITERATION: {str(counter).ljust(3)} / {len(lines)}     ||     CURRENT ITERATION TIME: {timer.format_time(timer.checkpoint())} TOTAL TIME: {timer.format_time(timer.total_time_elapsed())}')    
                counter += 1 
                
                # extract the proper names again (since it's not the same number as before so we cant use zip(s))
                name = ' '.join(line.replace('https://www.bestfightodds.com/fighters/', '').split('-')[:-1])
                
                # making a request
                response_fgt = requests.get(line.strip())
                html_response_fgt = response_fgt.content
                soup_fgt = BeautifulSoup(html_response_fgt, "html.parser")
                
                # wrestling with the formatting
                table_fgt = soup_fgt.find(class_='team-stats-table')
                table_body_fgt = table_fgt.find('tbody')
                filtered_tr_fgt = table_body_fgt.select('tr:not(.item-mobile-only-row)')
                for i in range(0, len(filtered_tr_fgt), 2):
                    # first row of the pair
                    tmp_name_x = filtered_tr_fgt[i].find(class_='oppcell').find('a').text
                    tmp_odds_x = filtered_tr_fgt[i].find_all(class_='moneyline')
                    for j in range(len(tmp_odds_x)):
                        cursor = tmp_odds_x[j].find('span')
                        if cursor is None:
                            if j == 0:
                                tmp_open_x = pd.NaT
                            elif j == 1:
                                tmp_closed_x = pd.NaT
                            elif j == 2:
                                tmp_range_x = pd.NaT
                        else:
                            if j == 0:
                                tmp_open_x = cursor.text
                            elif j == 1:
                                tmp_closed_x = cursor.text
                            elif j == 2:
                                tmp_range_x = cursor.text
                                
                    tmp_event_name = filtered_tr_fgt[i].find(class_='item-non-mobile').find('a').text
                    # second row of the pair
                    tmp_name_y = filtered_tr_fgt[i+1].find(class_='oppcell').find('a').text
                    tmp_odds_y = filtered_tr_fgt[i+1].find_all(class_='moneyline')
                    for j in range(len(tmp_odds_y)):
                        cursor = tmp_odds_y[j].find('span')
                        if cursor is None:
                            if j == 0:
                                tmp_open_y = pd.NaT
                            elif j == 1:
                                tmp_closed_y = pd.NaT
                            elif j == 2:
                                tmp_range_y = pd.NaT
                        else:
                            if j == 0:
                                tmp_open_y = cursor.text
                            elif j == 1:
                                tmp_closed_y = cursor.text
                            elif j == 2:
                                tmp_range_y = cursor.text
                                
                    tmp_event_date = filtered_tr_fgt[i+1].find(class_='item-non-mobile').text
                    
                    # appending sub-array into final array that will be converted into df
                    odds_data.append([tmp_name_x,
                                    tmp_open_x,
                                    tmp_closed_x,
                                    tmp_range_x,
                                    tmp_name_y,
                                    tmp_open_y,
                                    tmp_closed_y,
                                    tmp_range_y,
                                    tmp_event_name,
                                    tmp_event_date])
        
        df = pd.DataFrame(odds_data,
                        columns=[
                            '1_Name',
                            '1_Open_Odds',
                            '1_Closed_Odds',
                            '1_Odds_Range',
                            '2_Name',
                            '2_Open_Odds',
                            '2_Closed_Odds',
                            '2_Odds_Range',
                            'Event_Name',
                            'Event_Date'
                        ])    
        df = df.sort_values('Event_Name', ascending=True).reset_index(drop=True)
        df.to_excel(f'datasets/fight_odds.xlsx')

    else:
        pass # just pass

    third_prompt = input('Do you want to merge odds data to the main fight dataset? Y/N: ')
    if third_prompt == 'Y':
        if second_prompt == 'Y':
            pass # since we already have dataframe in df
        else:
            df = pd.read_excel('datasets/fight_odds.xlsx')
        pass

        ufc_data['Event_Date'] = pd.to_datetime(ufc_data['Event_Date'], format = '%B %d, %Y').dt.date
        df['Event_Date'] = pd.to_datetime(df['Event_Date'].str.replace(r'st|nd|rd|th', '', regex=True), format='%b %d %Y').dt.date
        
        # setting NA as a default value for the column
        ufc_data['R_Open_Odds'] = pd.NaT
        ufc_data['B_Open_Odds'] = pd.NaT
        ufc_data['R_Closing_Odds'] = pd.NaT
        ufc_data['B_Closing_Odds'] = pd.NaT
        
        # iterating...
        for index, row in ufc_data.iterrows():
            # finding matches...
            R_Name_cond1 = df.loc[(df['Event_Date'] == row['Event_Date']) 
                                & (df['1_Name'].str.lower() == row['R_Name'].lower())]
            R_Name_cond2 = df.loc[(df['Event_Date'] == row['Event_Date']) 
                                & (df['2_Name'].str.lower() == row['R_Name'].lower())]

            
            if len(R_Name_cond1) > 0:
                try:
                    ufc_data.at[index, 'R_Open_Odds'] = int(R_Name_cond1['1_Open_Odds'].iloc[0])
                    ufc_data.at[index, 'R_Closing_Odds'] = int(R_Name_cond1['1_Closed_Odds'].iloc[0])
                except ValueError:
                    # it shall be NaN, so we add this just to avoid the exception
                    ufc_data.at[index, 'R_Open_Odds'] = R_Name_cond1['1_Open_Odds'].iloc[0]
                    ufc_data.at[index, 'R_Closing_Odds'] = R_Name_cond1['1_Closed_Odds'].iloc[0]
                try:
                    ufc_data.at[index, 'B_Open_Odds'] = int(R_Name_cond1['2_Open_Odds'].iloc[0])
                    ufc_data.at[index, 'B_Closing_Odds'] = int(R_Name_cond1['2_Closed_Odds'].iloc[0])
                except ValueError:
                    ufc_data.at[index, 'B_Open_Odds'] = R_Name_cond1['2_Open_Odds'].iloc[0]
                    ufc_data.at[index, 'B_Closing_Odds'] = R_Name_cond1['2_Closed_Odds'].iloc[0]
                    
            elif len(R_Name_cond2) > 0:
                try:
                    ufc_data.at[index, 'R_Open_Odds'] = int(R_Name_cond2['2_Open_Odds'].iloc[0])
                    ufc_data.at[index, 'R_Closing_Odds'] = int(R_Name_cond2['2_Closed_Odds'].iloc[0])
                except ValueError:
                    ufc_data.at[index, 'R_Open_Odds'] = R_Name_cond2['2_Open_Odds'].iloc[0]
                    ufc_data.at[index, 'R_Closing_Odds'] = R_Name_cond2['2_Closed_Odds'].iloc[0]
                try:
                    ufc_data.at[index, 'B_Open_Odds'] = int(R_Name_cond2['1_Open_Odds'].iloc[0])
                    ufc_data.at[index, 'B_Closing_Odds'] = int(R_Name_cond2['1_Closed_Odds'].iloc[0])
                except ValueError:
                    ufc_data.at[index, 'B_Open_Odds'] = R_Name_cond2['1_Open_Odds'].iloc[0]
                    ufc_data.at[index, 'B_Closing_Odds'] = R_Name_cond2['1_Closed_Odds'].iloc[0]
                
        x = input('Please state the name of the output .xlsx file: ')
        ufc_data.to_excel('datasets/UFC_fights_stats_complete.xlsx')
        
    else:    
        pass