'''
	Chop.py tool for fast editing, splitting and normalizing of CSV files
	It also creates new columns (labels)
	for more info "python chop.py -h"

	@Author: Vojtech Miksu <vojtech@miksu.cz>
	Last update: 4/21/2014
'''

import csv
import sys
import math
import numpy as np
from copy import copy, deepcopy
import getopt
from random import shuffle

class chop(object):

	def __init__(self, params):
		data = self.load_csv_data(params['inputfile'], params['delimiter_in'])
		self.get_data_info(data)

		if params['shuffle'] and params['shuffleFirst']:
			data = self.shuffle_data(data)

		# adds new labels - history close price diffs
		if params['history_column']:
			data = self.addLabelsHistory(data, params['history_column'], params['history_steps'])

		# adds new labels - prediction close price classes (more than x, less than -x, between -x and x... or just plus/minus)
		if params['predict_column']:
			data = self.addLabelPredict(data, params['predict_column'])
			data = self.addLabelPredictClass(data, 'predictDiff')
			data = self.addLabelPredictClass3(data, params['predict_column'])
			#data = self.addLabelPredictClassNum(data, params['predict_column'], 0.03)
			#data = self.addLabelPredictClassNum(data, params['predict_column'], 0.05)
			#data = self.addLabelPredictClassNum(data, params['predict_column'], 0.10)
			#data = self.addLabelPredictClassNum(data, params['predict_column'], 0.15)
			#data = self.addLabelPredictClassNum(data, params['predict_column'], 0.20)
		data = self.delete_incomplete_rows(data) # deletes rows with missing values

		# selects chosen attributes and removes the rest
		if params['selected_attr']:
			headerPos = self.labelsToPosition(data, params['selected_attr'])
			data = self.select_columns(data, headerPos)

		# normalize all attributes in training part of a dataset, except these that are on the blacklist
		if params['normalize']:
			if params['normalize_blacklist']:
				headerPos = self.labelsToPosition(data, params['normalize_blacklist'])
				data = self.normalize(data, params['split_ratio'], headerPos)
			else:
				data = self.normalize(data, params['split_ratio'])

		# split data to 3 files for training, validating and testing
		train_data, valid_data, test_data = self.split_data(data, params['split_ratio'])
		if params['shuffle'] and not params['shuffleFirst']:
			train_data = self.shuffle_data(train_data)
		self.save_to_csv(train_data, params['outputfile_train'], params['delimiter_out'])
		if params['split_ratio'] != 1:
			self.save_to_csv(valid_data, params['outputfile_valid'], params['delimiter_out'])
			self.save_to_csv(test_data, params['outputfile_test'], params['delimiter_out'])

	def shuffle_data(self, data):
		labels = data[0]
		del data[0]
		shuffle(data)
		data.insert(0,labels)
		return data

	# loads dataset from CSV
	def load_csv_data(self, path, delim):
		try:
			f_csv_in = open(path)
		except:
			print 'file ' + path + ' does not exist'
			sys.exit(2)

		print 'file ' + path + ' successfully loaded'
		f_csv_in = csv.reader(f_csv_in, delimiter=delim)
		data = [row for row in f_csv_in]
		return data

	# prints info about dataset
	def get_data_info(self, data):
		print 'number of rows: {}'.format(len(data))
		print 'number of attributes: {}'.format(len(data[0]))

	# deletes rows with missing values
	def delete_incomplete_rows(self, data):
		print 'deleting missing rows'
		new_data = []
		incomplete_row_count = 0
		for row in xrange(len(data)):
			flag_missing = False
			for column in xrange(len(data[0])):
				if data[row][column] == '':
					incomplete_row_count+=1
					flag_missing = True
					break
			if flag_missing is False:
				new_data.append(data[row])

		print 'number of incomplete rows deleted: {}'.format(incomplete_row_count)
		return new_data

	# splits data to 3 subsets for training, validating and testing by given ratio
	def split_data(self, data, split_ratio):
		train_test_border = int(len(data)*split_ratio)
		trainPerc = split_ratio*100
		print 'splitting data for training, validating ({}%) and testing ({}%)'.format(trainPerc, 100 - trainPerc)

		test_data = data[train_test_border:]
		test_data.insert(0, data[0])
		valid_data = data[train_test_border-len(test_data):train_test_border]
		valid_data.insert(0, data[0])
		train_data = data[:train_test_border-len(test_data)]

		return [train_data, valid_data, test_data]

	# normalize data, just training part (according to split_ratio), testing data must be normalized separately
	def normalize(self, data, split_ratio = 0.9, columns_blacklist = []):
		print 'normalizing data'
		train_test_border = int(len(data)*split_ratio)

		for col in xrange(len(data[0])):
			if col in columns_blacklist:
				continue

			min = float("inf")
			max = float("-inf")

			for row in xrange(1, train_test_border):
				data[row][col] = float(data[row][col])
				if max < data[row][col]:
					max = data[row][col]
				if min > data[row][col]:
					min = data[row][col]

			# normalizing training part of data
			for row in xrange(1, train_test_border):
				if max - min == 0:
					data[row][col] = 0
				else:
					data[row][col] = (data[row][col] - min)/(max-min)

			# normalizing testing part of data with min/max from training part
			for row in xrange(train_test_border, len(data)):
				if max - min == 0:
					data[row][col] = 0
				else:
					data[row][col] = (float(data[row][col]) - min)/(max-min)
		return data

	# save data to CSV
	def save_to_csv(self, data, path, delim):
		print 'saving data to csv ' + path

		with open(path, 'wb') as csvfile:
			writer = csv.writer(csvfile, delimiter=delim)
			writer.writerows(data)

	# converts labels to column positions
	def labelsToPosition(self, data, labels):
		header = {}
		for i in xrange(len(data[0])):
			header[data[0][i]] = i

		position = []
		for label in labels:
			try:
				position.append(header[label])
			except KeyError:
				print 'ERROR: column with name ' + label + ' does not exist'
				sys.exit()
		return position

	#  converts label to column position
	def labelToPos(self, data, label):
		header = {}
		for i in xrange(len(data[0])):
			header[data[0][i]] = i

		try:
			return header[label]
		except KeyError:
			print 'ERROR: column with name ' + label + ' does not exist'
			sys.exit()

	# selects given columns and removes the rest
	def select_columns(self, data, columns):
		data = zip(*data)
		new_data = []
		for i in columns:
			new_data.append(data[i])
		new_data = map(list, zip(*new_data))
		return new_data

	# adds history close price diffs as new labels
	def addLabelsHistory(self, data, close_label, steps):
		print 'adding history labels'
		for step in xrange(1, steps+1):
			data = self.addLabelHistory(data, close_label, step)
		return data

	# adds new label with history close price (diff of history price and current price)
	def addLabelHistory(self, data, close_label, step):
		print 'adding history{} label'.format(step)
		label = 'history{}'.format(step)
		step += 1
		minit = self.labelToPos(data, 'minit')
		column = self.labelToPos(data, close_label)
		history = []
		history.append(label)
		for i in xrange(1, len(data)):
			if i < step or int(data[i][minit]) - int(data[i-step+1][minit]) != step-1:
				history.append('')
				continue
			diff = float(data[i-step+1][column])/(float(data[i][column]))
			diff = (diff - 1) * 100
			history.append(diff)

		data = zip(*data)
		data.insert(0, history)
		data = map(list, zip(*data))
		return data

	# adds new label with prediction of close price (diff of future price and current price)
	def addLabelPredict(self, data, close_label):
		print 'adding predict label'
		column = self.labelToPos(data, close_label)
		minit = self.labelToPos(data, 'minit')
		data[0][0:0] = ['predictDiff']
		for i in xrange(1, len(data)):
			if i >= len(data) - 5 or int(data[i+5][minit]) - int(data[i][minit]) != 5:
				data[i][0:0] = ['']
				continue
			diff = float(data[i+5][column])/(float(data[i][column]))
			diff = (diff - 1) * 100
			data[i][0:0] = [diff]
		return data


	# adds new label with prediction of close price (diff of future price and current price)
	def addLabelPredictClass3(self, data, close_label):
		print 'adding predictClass3 label'
		column = self.labelToPos(data, close_label)
		minit = self.labelToPos(data, 'minit')

		diffs = []
		for i in xrange(1, len(data)):
			if i >= len(data) - 5 or int(data[i+5][minit]) - int(data[i][minit]) != 5:
				continue
			diffs.append(float(data[i+5][column]) - float(data[i][column]))

		diffs.sort()
		perc33 = abs(np.percentile(np.array(diffs), 33.33))
		perc66 = abs(np.percentile(np.array(diffs), 66.66))
		right_diff = (perc33 + perc66) / 2

		print 'Split diff for this labeling is {}'.format(right_diff)
		data[0][0:0] = ['predictClass3']
		for i in xrange(1, len(data)):
			if i >= len(data) - 5 or int(data[i+5][minit]) - int(data[i][minit]) != 5:
				data[i][0:0] = ['']
				continue
			diff = float(data[i+5][column]) - float(data[i][column])
			if diff > right_diff:
				data[i][0:0] = [2]
			elif diff < -right_diff:
				data[i][0:0] = [0]
			else:
				data[i][0:0] = [1]
		return data

	'''
		adds new label
		0 = in 5 minutes close price will be lower than now
		1 = will be higher
	'''
	def addLabelPredictClass(self, data, close_label):
		print 'adding predict class label'
		column = self.labelToPos(data, close_label)
		data[0][0:0] = ['predictClass']
		for i in xrange(1, len(data)):
			if data[i][column] > 0:
				data[i][0:0] = [1]
			else:
				data[i][0:0] = [0]
		return data

	'''
		adds new label
		0 = in 5 minutes close price will be lower than 'current price - d'
		1 = in 5 minutes close price will be between 'current price - d' and 'current price + d'
		2 = in 5 minutes close price will be higher than 'current price + d'
	'''
	def addLabelPredictClassNum(self, data, close_label, d):
		print 'adding predict class label'
		column = self.labelToPos(data, close_label)
		minit = self.labelToPos(data, 'minit')
		label = 'predictClass{}'.format(int(d*100))
		data[0][0:0] = [label]
		for i in xrange(1, len(data)):
			if i >= len(data) - 5 or int(data[i+5][minit]) - int(data[i][minit]) != 5:
				data[i][0:0] = ['']
				continue
			diff = float(data[i+5][column]) - float(data[i][column])
			if diff > d:
				data[i][0:0] = [2]
			elif diff < -d:
				data[i][0:0] = [0]
			else:
				data[i][0:0] = [1]
		return data

# prints command line help
def print_help():
	print '\nChop command line arguments:\n'
	commands = []
	commands.append(['-h', '-', '-', 'this help'])
	commands.append(['-i', '--input', 'path', 'input CSV file (mandatory)'])
	commands.append(['-o', '--output-train', 'path', 'output CSV file with a subset for training'])
	commands.append(['-p', '--output-test', 'path', 'output CSV file with a subset for testing'])
	commands.append(['-q', '--output-valid', 'path', 'output CSV file with a subset for validating'])
	commands.append(['-n', '--normalize', '-', 'normalize all columns into the <0,1>'])
	commands.append(['-e', '--normalize-blacklist', 'list of labels', 'names of columns excluded from normalizing'])
	commands.append(['-s', '--select-columns', 'list of labels', 'all other columns are removed'])
	commands.append(['-r', '--data-split-ratio', 'float', 'train subset:test subset ratio, when 1 just train file is created'])
	commands.append(['-d', '--delimiter-in', 'character', 'input file delimiter, default is tab'])
	commands.append(['-c', '--delimiter-out', 'character', 'output file delimiter, default is tab'])
	commands.append(['-q', '--history', '#number,label', 'add "history#" labels based on label'])
	commands.append(['-w', '--predict', 'label', 'add label "predict" base on label'])
	template = "{0:10}{1:30}{2:20}{3:50}"
	print template.format("SHORT", "LONG", "PARAM", "DESCRIPTION")
	print '========================================================================================='
	for rec in commands:
	  print template.format(*rec)

# gets and process attributes from command line
def get_args(argv):
	params = {}
	params['inputfile'] = ''
	params['outputfile_train'] = 'output-train.csv'
	params['outputfile_test'] = 'output-test.csv'
	params['outputfile_valid'] = 'output-valid.csv'
	params['normalize'] = False
	params['normalize_blacklist'] = []
	params['selected_attr'] = []
	params['split_ratio'] = 0.9
	params['delimiter_in'] = '\t'
	params['delimiter_out'] = '\t'
	params['history_steps'] = 5
	params['history_column'] = ''
	params['predict_column'] = ''
	params['shuffle'] = False
	params['shuffleFirst'] = False

	try:
		opts, args = getopt.getopt(argv,"hi:o:p:q:ne:s:r:d:c:q:w:",["input=","output-train=","output-test=","output-valid=","normalize", "normalize-blacklist=", "select-columns=", "data-split-ratio=", "delimiter-in=", "delimiter-out=", "history=", "predict="])
	except getopt.GetoptError:
		print_help()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print_help()
			sys.exit()
		elif opt in ("-i", "--input"):
			params['inputfile'] = arg
		elif opt in ("-o", "--output-train"):
			params['outputfile_train'] = arg
		elif opt in ("-p", "--output-test"):
			params['outputfile_test'] = arg
		elif opt in ("-q", "--output-valid"):
			params['outputfile_valid'] = arg
		elif opt in ("-n", "--normalize"):
			params['normalize'] = True
		elif opt in ("-e", "--normalize-blacklist"):
			params['normalize_blacklist'] = arg.split(',')
			params['normalize_blacklist'] = map(str.strip, params['normalize_blacklist'])
		elif opt in ("-s", "--select-columns"):
			params['selected_attr'] = arg.split(',')
			params['selected_attr'] = map(str.strip, params['selected_attr'])
		elif opt in ("-r", "--data-split-ratio"):
			params['split_ratio'] = float(arg)
		elif opt in ("-d", "--delimiter-in"):
			params['delimiter_in'] = arg
		elif opt in ("-c", "--delimiter-out"):
			params['delimiter_out'] = arg
		elif opt in ("-q", "--history"):
			params['history_steps'] = arg.split(',')
			params['history_column'] = map(str.strip, params['selected_attr'])
		elif opt in ("-w", "--predict"):
			params['predict_column'] = arg

	if params['inputfile'] is '':
		print 'ERROR: You have to specify input file with -i'
		print_help()
		sys.exit()

	return params


if __name__ == "__main__":
	params = get_args(sys.argv[1:])
	chop(params)
