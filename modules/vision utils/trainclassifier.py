'''
trainclassifier.py

by David Wurtz, last updated 05-22-13

Running this code will generate a Putty encoded file that contains a trained 
classifier and a feature scaler.

This code assumes that you've already run both pycvtrainingpositive.py and
pycvtrainingnegative.py, and that their ouput files are in the local directory.

'''

from numpy import * 
import pickle
from sklearn import svm, preprocessing

''' open text file and store as python opject, then recover data '''
data_file = open('training_positive.txt', 'r')
true_target = pickle.load(data_file)	# features with target present
data_file = open('training_negative.txt', 'r')
false_target = pickle.load(data_file)	# features with target absent
data_file.close()

''' concatenate true_target and false_target datasets '''
target_data = concatenate((true_target, false_target))

''' generate class labels (1 = target present, 0 = target absent) '''
true_labels = ones(shape(true_target)[0])	# a one for each row in true_target
false_labels = zeros(shape(false_target)[0])	# a zero for each row in false_target

''' concatenate class labels '''
class_labels = concatenate((true_labels, false_labels))

''' scale data for classifier and generate feature scaler '''
scaled_target_data = preprocessing.scale(target_data)
feature_scaler = preprocessing.StandardScaler().fit(target_data)

''' train a classifier '''
classifier = svm.SVC()
classifier.fit(scaled_target_data, class_labels)

''' export classifier and feature_scaler to text file '''
data_file = open('classifier_and_feature_scaler.txt', 'w+')
data_file.write(pickle.dumps([classifier, feature_scaler]))
data_file.close

"""
	features = 	[	xmean,
					xvariance,
					xpeakval,
					x90peakwidth,
					ymean,
					yvariance,
					ypeakval,
					y90peakwidth]
"""