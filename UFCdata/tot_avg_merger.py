import pandas as pd

criteria_col = ['Event_Name', 'R_Name', 'B_Name', 'Referee', 'Conclusion_Method', 'Time_Format']

avg_df = pd.read_excel('datasets/UFC_complete_averages.xlsx')
print('Dataset with average stats about UFC fights loaded.')
tot_df = pd.read_excel('datasets/UFC_fight_totals.xlsx')
print('Dataset with total stats about UFC fights')

cols_to_merge = [x for x in tot_df.columns 
                 if 'total' in x.lower()
                and '%' not in x
                and 'streak' not in x.lower()
                and 'number' not in x.lower()]

tot_df = tot_df[[x for x in tot_df.columns
                 if x in criteria_col 
                 or x in cols_to_merge]]


merged_df = pd.merge(avg_df, tot_df, on=criteria_col, how='left')
merged_df.to_excel('datasets/UFC_complete_merged.xlsx')