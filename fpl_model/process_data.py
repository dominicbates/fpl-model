def get_df_goals_conceded(df):
    '''
    Group dataframe to get goald conceded for each team per GW. 
    This is split out for speed, as below function must be run
    many times.
    '''
    return (df.groupby(['season','GW','opponent_name'])['goals_scored'].sum()).reset_index(name='goals_conceded')

    
def get_gc(df_goals_conceded, 
           history_size, 
           team, 
           season, 
           gameweek):
    '''
    gets goals conceded by a team in specific time window. Can be used to generate features for team difficulty
    '''

    gc_team = df_goals_conceded[df_goals_conceded['opponent_name']==team].sort_values(['season','GW']).reset_index(drop=True)

    # Get index of selected row (i.e. team X at gameweek X)
    index = gc_team[(gc_team['season']==season)&(gc_team['GW']==gameweek)].index[0]
    # Get avg goals conceded over last N games if possible
    if (index-history_size) >= 0:
        gc_last_n = gc_team.iloc[(index-history_size):index]['goals_conceded'].mean()
        gc_last_n_possible = True
    else:
        gc_last_n = 0
        gc_last_n_possible = False
        
    return gc_last_n, gc_last_n_possible



def one_hot_encode(df):
    '''
    One-hot encodes all columns ending in "|"
    '''
    print('\nOne-hot encoding all columns ending in "|"...')
    for col in list(df):
        # If ends in '|' one hot encode features
        if col[-1] == '|':
            features = list(set(df[col]))
            for f in features:
                df[col+f] = (df[col]==f).astype(int)
            df = df.drop(columns=[col])
    print('Finished!')
    return df




def process_opponent_feature(df, df_goals_conceded, history_size=5):
    '''
    Creates feature representing goals conceded of opponent
    over last N weeks. Does this for every row in dataframe
    Define range of bins ([0,1] means just last game, i.e. not current week [0,2] would be last two games)
    '''
    print('\nProcessing opponent feature (goals conceded over last N weeks)...')

    'f|current|opponent_gc_history|'
    # List for storing vals
    opponent_gc_history = []
    opponent_gc_history_available = []

    for n in range(len(df)):
        team = df['opponent_name'].iloc[n]
        season = df['season'].iloc[n]
        gameweek = df['GW'].iloc[n]
        out = get_gc(df_goals_conceded, history_size, team, season, gameweek)
        opponent_gc_history.append(out[0])
        opponent_gc_history_available.append(out[1])
        
        if ((n%10000)==0):
            print('...',n,'/',len(df),'rows complete')

    df['opponent_gc_history'] = opponent_gc_history
    df['opponent_gc_history_available'] = opponent_gc_history_available


    print('\nFeature processed!')
    return df




        
def process_row(df_all, n, bins, binned_features, vals):

    # Create current featurs
    vals['f|current|position|'].append(df_all['position'].iloc[n])
    vals['f|current|is_home'].append(df_all['was_home'].iloc[n])
        
    # Loop through binned features
    for bin_range in bins:
        # Get bin limits
        bin_start = n-bin_range[0]
        bin_end = n-bin_range[1]
        name_cleaned = df_all['name_cleaned'].iloc[n]
        season = df_all['season'].iloc[n]
        
        # Work out if bin possible
        if (bin_end<0) or (df_all['name_cleaned'].iloc[bin_end] != name_cleaned): # If bin outside of dataframe or different player
            # No player in data for this bin, so set vals to 0
            for col in binned_features+['current_season']:
                vals['f|'+col+'|'+str(bin_range[0])+'_to_'+str(bin_range[1])].append(0.0)
            vals['f|player_exists|'+str(bin_range[0])+'_to_'+str(bin_range[1])].append(0.0)

        # If possible, get bin average for each feature
        else:
            # Bin available
            vals['f|player_exists|'+str(bin_range[0])+'_to_'+str(bin_range[1])].append(1.0)
            for col in binned_features:
                mean = df_all[col].iloc[bin_end:bin_start].mean()
                vals['f|'+col+'|'+str(bin_range[0])+'_to_'+str(bin_range[1])].append(mean)

            # Create feature to say if bin is (entirely) within this season
            if season != df_all['season'].iloc[bin_end]:
                vals['f|current_season|'+str(bin_range[0])+'_to_'+str(bin_range[1])].append(0.0)
            else:
                vals['f|current_season|'+str(bin_range[0])+'_to_'+str(bin_range[1])].append(1.0)
    return vals




def process_features(df, bins = [[0,1], [1,2], [2,3], [3,4],  [4,5], [5,10], [10,20]]):
    '''
    # Define range of bins ([0,1] means just last game, i.e. not current week [0,2] would be last two games)

    '''
    print('\nProcessing features...')

    # Dict for storing vals (for speed)
    vals = {}
    binned_features = ['total_points', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'bonus','was_home', 'opponent_gc_history', 'opponent_gc_history_available']
    for col in binned_features+['current_season','player_exists']:
        for bin_range in bins:
            vals['f|'+col+'|'+str(bin_range[0])+'_to_'+str(bin_range[1])] = []
    for col in ['f|current|position|', 'f|current|is_home']: # ending in '|' means one hot encode
        vals[col] = []

    # Sort to allow "windowing" to calculate stats
    df = df.sort_values(by = ['name_cleaned','season','GW','kickoff_time'],
                                ascending = [True,True,True,True]).reset_index(drop=True)
    print('Processing dataframe binned features')
    # loop through all rows
    for n in range(len(df)):
        vals = process_row(df, n, bins, binned_features, vals)
        if ((n%10000)==0):
            print('...',n,'/',len(df),'rows complete')

            
    for col in vals:
        df[col] = vals[col]
    print('\nFeatures processed!')
    return df





def do_all_processing_steps(df, history_size=5):
    '''
    Do all steps required for generating triaining data
    '''
    df_goals_conceded = get_df_goals_conceded(df) # Get goals conceded df
    df = process_opponent_feature(df, df_goals_conceded, history_size=history_size) # Use this to generate featuremfor all rows
    df = process_features(df) # Create all other features
    df = one_hot_encode(df) # One hot encode any which need to be
    
    return df



