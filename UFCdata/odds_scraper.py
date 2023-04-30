import pandas as pd
import requests
from bs4 import BeautifulSoup
import Timer

# I'll get the odds for EACH FIGHTER FIGHTS, then we will parse it into main dataset
base_url = "https://www.bestfightodds.com/search?query="

# getting unique fighter names that we have
ufc_data = pd.read_excel('UFCData_final.xlsx')
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
    df.to_excel('ODDSdata.xlsx')

else:
    pass # just pass

third_prompt = input('Do you want to merge the ODDS to the main dataset? Y/N: ')
if third_prompt == 'Y':
    if second_prompt == 'Y':
        pass # since we already have dataframe in df
    else:
        df = pd.read_excel('ODDSdata.xlsx')
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
            
    ufc_data.to_excel('test_final.xlsx')
    
else:    
    pass