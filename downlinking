def get_change_counts(df):
    df['sample_trace_sp'].ffill(inplace=True)
    df['sample_trace_changed'] = ((df['sample_trace_sp'].diff().apply(abs) > 20) #sp changed by at least 20
                         & (df['sample_trace_sp'].rolling(5).min() > 5) #sp did not start or end at 0
                         & (df['sample_trace_sp'][::-1].rolling(5).min()[::-1] > 5)
                         & (df['sample_condition'] == 0)
                         & (df['sample_state'] == 1)).astype(int) #we are currently not in-slips
    df['sample_trace_changed_general'] = ((df['sample_trace_sp'].diff().apply(abs) > 3) 
                         & (df['sample_condition'] == 0)
                         & (df['sample_state'] == 1)).astype(int) #we are currently not in-slips
    df['change_num'] = df['sample_trace_changed'].cumsum().astype(int)
    df['change_counts_downlink_width'] = df['sample_trace_changed'].rolling((2*61), center=False).sum()
    df['change_counts_downlink_width_reverse'] = df[::-1]['sample_trace_changed'].rolling((2*61), center=False).sum()[::-1]

def get_downlink(df):
    df['downlink'] = (df['change_counts_downlink_width'] > 0) & \
                     (df['change_counts_downlink_width_reverse'] > 0)# & \
    condition = (df['downlink'].shift(1) == 0) & (df['downlink'].shift(-1) == 0) & (df['downlink'] == 1)
    df.loc[condition, 'downlink'] = False
    df['unfiltered_downlink_num'] = (df['downlink'].astype(int).diff() == 1).cumsum() 
    df['number_of_bits'] = df[df['downlink'] == 1].groupby('unfiltered_downlink_num').transform('sum')['sample_trace_changed']
    condition = (df['number_of_bits'] < 10)
    df.loc[condition, 'downlink'] = False
    df['downlink_num'] = (df['downlink'].astype(int).diff() == 1).cumsum() 

def get_quiet_period(df):
    df['sample_trace_changed_before_downlink'] = df[::-1].groupby('downlink_num').transform('cumsum')[::-1]['sample_trace_changed_general']
    df['quiet_period'] = (df['sample_trace_changed_before_downlink'] == 0) & \
                         (df['sample_trace'] > 0) & \
                         (df['sample_trace_sp'] > 0) 
    
def get_high_and_low_point(df):
    df['high_point'] = df[df['downlink'] == 1].groupby('downlink_num').transform('max')['sample_trace']
    df['low_point'] = df[df['downlink'] == 1].groupby('downlink_num').transform('min')['sample_trace']
    
def get_bit_period(df):
    df['index'] = df.index
    df['change_num_index'] = np.where((df['change_num'].diff() != 0), df['index'], np.nan)
    df['change_num_index'].ffill(inplace=True)
    df['change_num_index_diff'] = df['change_num_index'].diff()
    df['bit_length'] = np.where((df['change_num_index_diff'] >= 17) & 
                                (df['change_num_index_diff'] <= 61), df['change_num_index_diff'], 0)
