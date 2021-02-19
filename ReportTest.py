import pandas as pd
import numpy as np
import os 
from Reports import *
from functools import reduce

if __name__ == '__main__':
	shifts = pd.read_csv(os.getcwd() + r'/Data/shift.csv')
	name_map = pd.read_csv(os.getcwd() + r'/Data/people.csv')
	roles = pd.read_csv(os.getcwd() + r'/Data/roles.csv')
	transactions = pd.read_csv(os.getcwd() + r'/Data/transactions.csv')
	accounts = pd.read_csv(os.getcwd() + r'/Data/accounts.csv')

	### Dealer report generation
	# Rake 
	# shifts["end_float"] = shifts["end_float"].astype(float)
	# shifts["start_float"] = shifts["start_float"].astype(float)
	# shifts["rake"] = shifts["end_float"] - shifts["start_float"]
	# rake_summary = shifts.groupby(["person_id"])["rake"].agg("sum").reset_index(name="rake")
	
	# # Tips
	# tip_summary = shifts.groupby(["person_id"])["tips"].agg("sum").reset_index(name="tips")
	
	# # Shift count
	# shift_count = shifts.groupby(["person_id"]).agg('size').reset_index(name='shift_count')
	
	# # Merging dataframes on dealer id to form summary frame
	# summary = rake_summary.merge(tip_summary, left_on='person_id', right_on='person_id', how='inner').merge(shift_count, left_on='person_id', right_on='person_id')
	
	# # Calculate Average
	# summary['avg_rake'] = summary['rake'] / summary['shift_count']
	# summary['avg_tips'] = summary['tips'] / summary['shift_count']
	
	# print(summary)

	### Player report generation
	player_list = roles.iloc[np.where(roles['role'] == 'Player')]
	groupby_player_df = transactions[np.isin(transactions['person_id'], player_list)].iloc[np.where(transactions['chip_purchase'].astype(int) == 1)].groupby('person_id')

	amount = groupby_player_df['quantity'].apply(lambda x: x[x > 0].sum()).reset_index(name='Total_buyin_amount')
	count = groupby_player_df['quantity'].count().reset_index(name='Total_buyin_count')
	cash_count = groupby_player_df['transaction_type'].apply(lambda x: x[x == 'cash'].count()).reset_index(name='cash')
	credit_count = groupby_player_df['transaction_type'].apply(lambda x: x[x == 'credit'].count()).reset_index(name='credit')

	player_summary = reduce(lambda left,right: pd.merge(left, right, left_on='person_id',right_on='person_id', how='inner'), [amount, count, cash_count, credit_count])
	player_summary.loc[:, 'cash'] = player_summary['cash'] / player_summary['Total_buyin_count']
	player_summary.loc[:, 'credit'] = player_summary['credit'] / player_summary['Total_buyin_count']
	
	# Outstanding debts/balance
	accounts['balance'] = accounts['cash'] - accounts['credit'] + accounts['float']

	print(player_summary)
	