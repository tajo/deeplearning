'''
	@author Vojtech Miksu <vojtech@miksu.cz>

	This is the main script, it runs training, validating and testing for all datasets based on
	preferred parameters.
'''
import datetime
import time
import csv
import os
import json
import sys

from libs import SdA

'''
	iterates over the tasks in json config
'''
def run(tasks):
	task_num = 1
	for task_params in tasks:
		print '#####################      PROCESSING TASK #{}      #####################'.format(task_num)
		run_task(task_params)
		task_num += 1

'''
	prepare and run single task
'''
def run_task(params):
	if not os.path.isfile(params['logfile']) or os.stat(params['logfile'])[6] == 0:
		with open(params['logfile'], "wb") as myfile:
			data = ['date_time',
					'dataset',
					'target_name',
					'finetune_lr',
					'pretraining_epochs',
					'pretrain_lr',
					'training_epochs',
					'batch_size',
					'n_ins',
					'n_outs',
					'hidden_layers_sizes',
					'corruption_levels (%)',
					'valid_perf (%)',
					'test_perf (%)',
					'test_recall',
					'run_time (min)']

			writer = csv.writer(myfile, delimiter=',')
			writer.writerow(data)

	# number of target columns in dataset, so SdA can split them from the rest
	try:
		targets = params['targets']
	except:
		targets = 3 # default for stock datasets

	for dataset in params['datasets']:
		SdA.test_SdA(params['finetune_lr'],
				 params['target_name'],
				 params['pretraining_epochs'],
				 params['pretrain_lr'],
				 params['training_epochs'],
				 dataset,
				 params['batch_size'],
				 params['n_ins'],
				 params['hidden_layers_sizes'],
				 params['n_outs'],
				 params['corruption_levels'],
				 params['logfile'],
				 targets)

if __name__ == '__main__':
	try:
		json_data=open(sys.argv[1]) # expects json config as command line parameter
	except:
		print 'You have to specify some valid "task.json" as the input argument'
		#print 'ERROR: file ' + sys.argv[1] + ' does not exist'
		sys.exit()
	data = json.load(json_data)
	run(data['tasks'])
