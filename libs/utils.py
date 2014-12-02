"""
    @author Vojtech Miksu
    utility functions for loading datasets to Theano shared memory
"""
import sys
import csv
import numpy
import theano
import theano.tensor as T

# load data from CSV file to theano shared memory variables
def load_data(train, valid, test, targetColumn, targets = 4):
    train_xy = load_csv_data(train, ',')
    valid_xy = load_csv_data(valid, ',')
    test_xy = load_csv_data(test, ',')

    targetColumnNumber = labelToPos(test_xy, targetColumn)

    test_set_x, test_set_y = transform(test_xy, targetColumnNumber, targets)
    valid_set_x, valid_set_y = transform(valid_xy, targetColumnNumber, targets)
    train_set_x, train_set_y = transform(train_xy, targetColumnNumber, targets)

    rval = [(train_set_x, train_set_y), (valid_set_x, valid_set_y),
            (test_set_x, test_set_y)]
    return rval

# loads data from CSV file
def load_csv_data(path, delim):
        try:
            f_csv_in = open(path)
        except:
            print 'file ' + path + ' does not exist'
            sys.exit(2)

        print 'file ' + path + ' successfully loaded'
        f_csv_in = csv.reader(f_csv_in, delimiter=delim)
        data = [row for row in f_csv_in]
        return data

# split datasets to targets and attributes and save it as theano share memory variables
def transform(data, targetColumnNumber, targets):
    label = []

    del data[0]
    for i in xrange(len(data)):
        label.append(data[i][targetColumnNumber]) #labels: 1 - predictClass, 0 - reg. predict
    data = zip(*data)
    data = map(list, zip(*data[targets:]))

    # conversion to numpy
    data = numpy.array(data, numpy.float32)
    label = numpy.array(label, numpy.int32)

    # conversion to theano shared variables
    shared_x = theano.shared(numpy.asarray(data, dtype=theano.config.floatX), borrow=True)
    shared_y = theano.shared(numpy.asarray(label, dtype=theano.config.floatX), borrow=True)
    return shared_x, T.cast(shared_y, 'int32')

# converts column name to its position
def labelToPos(data, label):
        header = {}
        for i in xrange(len(data[0])):
            header[data[0][i]] = i

        try:
            return header[label]
        except KeyError:
            print 'ERROR: Target with name ' + label + ' does not exist'
            sys.exit()
