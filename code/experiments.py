import NKmodel

import numpy as np
from numpy import linalg as LA
import random
import json
import gzip
import os


################ Universal Parameters #################

# Solution space complexity:
N = 4 
k = 2
A = 2

runs = 100 # number of times to run this exchange
max_iter = 5000 #number of iterations

min_noise = 1
max_noise = 210

noise = list(range(min_noise, max_noise + 1))

################ User Specified Parameters #################

def check_openness(openness):
	try:
		if np.abs(float(openness)) <= 1:
			return True
		else:
			return False

	except:
		return False

def check_n_users(n_users):
	try:
		n_users = int(n_users)
		return True

	except:
		return False

def check_n_intel(n_intel, n_users):
	try:
		n_intel = int(n_intel)

		if n_intel > n_users:
			return False
		elif n_intel > 0:
			return True
		else:
			return False

	except:
		return False

def get_parameters():

	################ Agent Parameters #################

	n_users = input('Please enter the number of agents you would like.\n')

	while check_n_users(n_users) == False:
		n_users = input('Please enter the number of agents you would like. Must be a valid integer.\n')

	n_users = int(n_users)



	agent_type = input('\nPlease enter agent type.\nChoices are: uninformed, ideologues, maj_ideologues, maj_intellectual, portion_intellectual.\n')

	while agent_type not in ['uninformed', 'ideologues', 'maj_ideologues', 'maj_intellectuals', 'portion_intellectual']:
		agent_type = input('Please enter a valid agent type.\nChoices are: uninformed, ideologues, maj_ideologues, maj_intellectuals, portion_intellectual.\n')


	if agent_type == 'portion_intellectual':
		n_intel = input('\nHow many of the %s agents should be intellectuals?\n' %n_users)

		while check_n_intel == False:
			n_intel = input('Please enter a valid number of intellectual agents. Must be a positive integer not exceeding %s\n' %n_users)

		n_intel = int(n_intel)

	else:
		n_intel = 0

	openness = input('\nEnter the openness level. Must be between -1 (always accept) and 1 (always reject).\n')

	while check_openness(openness) == False:
		openness = input('Please enter a valid openness level. Must be between -1 (always accept) and 1 (always reject).\n')	

	openness = float(openness)

	if openness == 0.0:
		cos_text = '0'
	else:
		num = str(np.abs(openness))[2:]

		if len(num) < 2:
			num += '0'

		if np.sign(openness) == 1:
			cos_text = 'Pos' + num
		else:
			cos_text = 'Neg' + num 


	################# Output Parameters ################
	path = '../data/raw/'

	#create path to save these data
	if agent_type != 'portion_intellectual':
		path_vars = [str(agent_type) + '/', str(n_users) + '_people/', 'cos' + cos_text + '/']

	else:
		path_vars = [str(agent_type) + '/', str(n_users) + '_people/', str(n_intel) + '_intellectuals/', 'cos' + cos_text + '/']		

	for val in path_vars:
		path += val

		if not os.path.isdir(path):
			os.mkdir(path) 
	
	os.chdir(path)

	print('\nData will be written to %s' %path)

	return n_users, n_intel, agent_type, openness



################# Boundary conditions ################

def get_bounds(n_users, n_intel, agent_type, i):
	half = n_users // 2 # half of users, rounded down

	if agent_type == 'uninformed':
		bounds = [[-i, i] for user in range(n_users)]

	elif agent_type == 'ideologues':
	    over = [[i-2, i] for user in range(half + 1)]
	    under = [[-i, -i + 2] for user in range(half)]

	    bounds = over + under

	elif agent_type == 'maj_ideologues':

		#if we have an even number of users, save room for the intellectuals!
		if n_users % 2 == 0:
			half -= 1

		intellectuals = n_users - (half * 2) #either 1 or 2 since half is rounded down

		over = [[i-2, i] for user in range(half)]
		under = [[-i, -i + 2] for user in range(half)]
		mod = [[-1, 1] for user in range(intellectuals)]

		bounds = over + under + mod

	elif agent_type == 'maj_intellectuals':

		quarter = half // 2
		intellectuals = n_users - (quarter * 2) #gives intellectuals the majority

		over = [[i-2, i] for user in range(quarter)]
		under = [[-i, -i + 2] for user in range(quarter)]
		mod = [[-1, 1] for user in range(intellectuals)]

		bounds = over + under + mod

	elif agent_type == 'portion_intellectual':
		n_ideologues = n_users - n_intel

		half = n_ideologues // 2 # half of users, rounded down

		over = [[i-2, i] for user in range(half)]
		under = [[-i, -i + 2] for user in range(half)]
		mod = [[-1, 1] for user in range(n_intel)]

		bounds = over + under + mod


	else: 
		print('A valid agent type was not provided.')

	return bounds



###################################################
################# Main Function ###################
###################################################

def main():

	n_users, n_intel, agent_type, openness = get_parameters()

	print('\nBeginning experiment')
	print('Landscape: N = %s, k = %s' %(N, k))
	print('Number of agents: %s' %n_users)
	print('Agent type: %s' %agent_type)
	print('Openness level: %s\n' %openness)

	for index, i in enumerate(noise):
	    print('********%s*********' %i)

	    bounds = get_bounds(n_users, n_intel, agent_type, i)
	    
	    multi_run_output = NKmodel.multi_run(N, k, A, n_users, runs, bounds, max_iter, openness)
	    
	    # save data
	    filename = 'noise_%s.json.gzip' %i
	    
	    with gzip.open(filename, 'w') as fp:
	        fp.write(json.dumps(multi_run_output).encode())

	print('\n*********************************\n')
	print('Experiment complete. All data written to:')
	print(os.getcwd())
	print('\nExperiment parameters:')
	print('Landscape: N = %s, k = %s' %(N, k))
	print('Number of agents: %s' %n_users)
	print('Agent type: %s' %agent_type)
	print('Openness level: %s\n' %openness)

main()