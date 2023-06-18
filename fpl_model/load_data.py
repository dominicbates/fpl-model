import numpy as np
import pandas as pd
'''
Contains functions for loading and processing data in 
to the right form for the model
'''

def process_name(name):
	'''
	Turns the various name formats in to a single format
	'''
	if len(name.split('_')) > 1:
		try: 
			int(name.split('_')[-1]) # See if last bit is a number
			out = ' '.join(name.split('_')[0:-1]).lower()
		except:
			out = ' '.join(name.split('_')).lower()
	else:
		out = name.lower()
	return out



def get_team_names_dict(year, fpl_dir, encoding):

	'''
	Get team names. Note that these are in a seperate file for
	most recent years (2021-22 onwards)
	'''
	if year not in ['2020-21','2019-20', '2018-19','2017-18','2016-17']:
		df_teams_tmp = pd.read_csv(fpl_dir+'data/'+year+'/teams.csv', encoding=encoding)
		df_teams_tmp['team'] = df_teams_tmp['id'] #df_teams_tmp['code'] # Resets to 1-20 from this year onwards
		df_teams_tmp['team_name'] = df_teams_tmp['name']
	else:
		df_teams = pd.read_csv(fpl_dir+'data/master_team_list.csv')
		df_teams_tmp = df_teams[df_teams['season']==year]

	# Turn to dict
	df_teams_dict = {}
	for team, name in zip(df_teams_tmp['team'], df_teams_tmp['team_name']):
		df_teams_dict[team] = name
	
	return df_teams_dict



def get_player_positions_dict(year, fpl_dir, encoding):
	'''
	Get player positions (slightly different format for last two years)
	'''
	if year in ['2019-20', '2018-19','2017-18','2016-17']:
		
		mapping = {'1':'GKP',
				   '2':'DEF',
			       '3':'MID',
				   '4':'FWD'}

		# Read file
		df_players_tmp = pd.read_csv(fpl_dir+'data/'+year+'/players_raw.csv', encoding='utf_8')

		# Turn to mapping dict (with name in correct form)
		df_pos_dict = {}
		if year in ['2019-20','2018-19']:
			for first_name, second_name, p_id, element_type in zip(df_players_tmp['first_name'], 
																	df_players_tmp['second_name'],
																	df_players_tmp['id'],
																	df_players_tmp['element_type']):
				df_pos_dict[first_name+'_'+second_name+'_'+str(p_id)] = mapping[str(element_type)]

		# Slightly different name format for these earlier two years (no id)
		else:
			for first_name, second_name, p_id, element_type in zip(df_players_tmp['first_name'], 
																	df_players_tmp['second_name'],
																	df_players_tmp['id'],
																	df_players_tmp['element_type']):
				df_pos_dict[first_name+'_'+second_name] = mapping[str(element_type)]

	# Return null for other years
	else:
		df_pos_dict = None


	return df_pos_dict




def load_data(fpl_dir = '/Users/dominicbates/Documents/Github/Fantasy-Premier-League/'):
    

	'''
	Load data and combine 
	'''

	# Set cols
	print('\nLoading data...')
	cols = ['season','GW','name','position','opponent_name','opponent_team', 'kickoff_time', 'was_home', 'selected','selected_weight','minutes','total_points','saves','bonus','clean_sheets','goals_conceded','goals_scored','assists','red_cards','yellow_cards']
	
	#     df_teams = pd.read_csv(fpl_dir+'data/master_team_list.csv')
	df_all = pd.DataFrame()

	# Loop through all years
	all_years = ['2022-23', '2021-22', '2020-21','2019-20', '2018-19','2017-18','2016-17']
	print('Loading data for years:',all_years)
	for year in all_years:
		print('... Processing year:',year)

		# Set encoding to avoid errors
		if year in ['2018-19', '2017-18', '2016-17']:
			encoding = 'latin-1'
		else:
			encoding = 'utf_8'

		# Load season data
		df_tmp = pd.read_csv(fpl_dir+'data/'+year+'/gws/merged_gw.csv', encoding=encoding)
		df_tmp['season'] = year

		# Get team names
		id_to_team = get_team_names_dict(year, fpl_dir, encoding)
		df_tmp['opponent_name'] = [id_to_team[team] for team in df_tmp['opponent_team']]
        
		# Get positions
		name_to_pos = get_player_positions_dict(year, fpl_dir, encoding)
		if name_to_pos is not None:
			df_tmp['position'] = [name_to_pos[name] if name in list(name_to_pos) else None for name in df_tmp['name']]
		df_tmp.loc[(df_tmp['position'] == 'GK'),'position'] = 'GKP'
		# Set selected weight
		df_tmp['selected_weight'] = df_tmp['selected'] / df_tmp['selected'].mean()

		# Get final columns set and add to dataframe
		df_tmp = df_tmp[cols]
		df_all = pd.concat([df_all, df_tmp])


	# Clean up final dataframe
	df_all = df_all.sort_values(['season','GW','opponent_name','kickoff_time','name'])
	df_all['name_cleaned'] = [process_name(name) for name in df_all['name']]

	print('\nDropping Nulls')
	print('... Size:',len(df_all))
	m_nonulls = pd.notnull(df_all).all(axis=1)
	df_all = df_all[m_nonulls].reset_index(drop=True)
	print('... New Size:',len(df_all))    
	print('...',(m_nonulls==0).sum(),'rows dropped')
	print('\nData loaded!')
	return df_all







