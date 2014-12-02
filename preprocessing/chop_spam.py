'''
   @author Vojtech Miksu <vojtech@miksu.cz>

'''

from chop import chop

sets = ['spambase']

for fnc in sets:
   params = {}
   params['inputfile'] = '../datasets/raw/'+fnc+'.csv'
   params['outputfile_train'] = '../datasets/output-'+ fnc +'-train.csv'
   params['outputfile_valid'] = '../datasets/output-'+ fnc +'-valid.csv'
   params['outputfile_test'] = '../datasets/output-'+ fnc +'-test.csv'
   params['normalize'] = True
   params['normalize_blacklist'] = ['class']
   params['selected_attr'] = ['class',
                              'word_freq_make',
                              'word_freq_address',
                              'word_freq_all',
                              'word_freq_3d',
                              'word_freq_our',
                              'word_freq_over',
                              'word_freq_remove',
                              'word_freq_internet',
                              'word_freq_order',
                              'word_freq_mail',
                              'word_freq_receive',
                              'word_freq_will',
                              'word_freq_people',
                              'word_freq_report',
                              'word_freq_addresses',
                              'word_freq_free',
                              'word_freq_business',
                              'word_freq_email',
                              'word_freq_you',
                              'word_freq_credit',
                              'word_freq_your',
                              'word_freq_font',
                              'word_freq_000',
                              'word_freq_money',
                              'word_freq_hp',
                              'word_freq_hpl',
                              'word_freq_george',
                              'word_freq_650',
                              'word_freq_lab',
                              'word_freq_labs',
                              'word_freq_telnet',
                              'word_freq_857',
                              'word_freq_data',
                              'word_freq_415',
                              'word_freq_85',
                              'word_freq_technology',
                              'word_freq_1999',
                              'word_freq_parts',
                              'word_freq_pm',
                              'word_freq_direct',
                              'word_freq_cs',
                              'word_freq_meeting',
                              'word_freq_original',
                              'word_freq_project',
                              'word_freq_re',
                              'word_freq_edu',
                              'word_freq_table',
                              'word_freq_conference',
                              'char_freq_semicolon',
                              'char_freq_(',
                              'char_freq_[',
                              'char_freq_!',
                              'char_freq_$',
                              'char_freq_#',
                              'capital_run_length_average',
                              'capital_run_length_longest',
                              'capital_run_length_total']
   params['split_ratio'] = 0.85
   params['delimiter_in'] = ','
   params['delimiter_out'] = ','
   params['history_steps'] = 0
   params['history_column'] = ''
   params['predict_column'] = ''
   params['shuffle'] = True
   params['shuffleFirst'] = True
   chop(params)