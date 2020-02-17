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
max_iter = 5000 # number of iterations

min_noise = 1
max_noise = 160

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

def check_n_manual(n_type, n_total):
    try:
        n_type = int(n_type)

        if n_type > n_total:
            return False
        elif n_type > 0:
            return True
        else:
            return False

    except:
        return False


def get_parameters():

    ################ Agent Parameters #################

    n_users = input('Please enter the number of agents you would like.\n')
    agent_mix = dict()

    while check_n_users(n_users) == False:
        n_users = input('Please enter the number of agents you would like. Must be a valid integer.\n')

    n_users = int(n_users)
    half = n_users // 2  # half of users, rounded down

    choices = ['uninformed', 'intellectuals', 'ideologues', 'maj_ideologues', 'maj_intellectual', 'manual']

    agent_type = input('\nPlease enter agent type.\nChoices are: %s\n' %(', '.join(choices)))

    while agent_type not in choices:
        agent_type = input('Please enter a valid agent type.\nChoices are: %s\n' %(', '.join(choices)))

    if agent_type == 'uninformed':
        agent_mix[agent_type] = n_users

    elif agent_type == 'intellectuals':
        agent_mix[agent_type] = n_users

    elif agent_type == 'ideologues':
        agent_mix['ideologues (positive)'] = n_users - half
        agent_mix['ideologues (negative)'] = half

    elif agent_type == 'maj_ideologues':
        # if we have an even number of users, save room for the intellectuals!
        if n_users % 2 == 0:
            half -= 1

        agent_mix['ideologues (positive)'] = half
        agent_mix['ideologues (negative)'] = half

        agent_mix['intellectuals'] = n_users - (half * 2)

    elif agent_type == 'maj_intellectuals':
        quarter = half // 2

        agent_mix['ideologues (positive)'] = quarter
        agent_mix['ideologues (negative)'] = quarter

        agent_mix['intellectuals'] = n_users - (quarter * 2)

    elif agent_type == 'manual':
        n_total = n_users

        for item in ['uninformed', 'intellectuals', 'ideologues (positive)', 'ideologues (negative)']:
            n_type = input('\nHow many of the %s agents should be %s?\n' % (n_users, item))

            while check_n_manual(n_type, n_total) == False:
                n_type = input('Please enter a valid number of agents. Must be a positive integer not exceeding %s\n' %n_total)

            n_type = int(n_type)
            agent_mix[item] = n_type

            n_total -= n_type

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
    # path = '../data/raw/'
    path = '/Users/Shugars/Dropbox/Dissertation/replication/Additional analysis/02_ABM/data/raw/'

    # create path to save these data
    if agent_type != 'manual':
        path_vars = [str(agent_type) + '/', str(n_users) + '_people/', 'cos' + cos_text + '/']

    else:
        agent_list = '_'.join([str(val) + name for name, val in agent_mix.items()])

        path_vars = [str(agent_type) + '/', str(n_users) + '_people/',   agent_list + '/', 'cos' + cos_text + '/']

    for val in path_vars:
        path += val

        if not os.path.isdir(path):
            os.mkdir(path)

    os.chdir(path)

    print('\nData will be written to %s' %path)

    return n_users, agent_mix, openness



################# Boundary conditions ################


def get_bounds(agent_mix, i):
    bounds = list()

    for agent_type, n_agents in agent_mix.items():
        if agent_type == 'uninformed':
            bounds += [[-i, i] for user in range(n_agents)]

        elif agent_type == 'ideologues (positive)':
            bounds += [[i-2, i] for user in range(n_agents)]

        elif agent_type == 'ideologues (negative)':
            bounds += [[-i, -i + 2] for user in range(n_agents)]

        elif agent_type == 'intellectuals':
            bounds += [[-1, 1] for user in range(n_agents)]

    return bounds



###################################################
################# Main Function ###################
###################################################

def main():

    n_users, agent_mix, openness = get_parameters()

    print('\nBeginning experiment')
    print('Landscape: N = %s, k = %s' %(N, k))
    print('Number of agents: %s' %n_users)
    print('Agent types:')
    for agent_type, val in agent_mix.items():
        print('   %s : %s' %(agent_type, val))
    print('Openness level: %s\n' %openness)

    for index, i in enumerate(noise):
        print('********%s*********' %i)

        bounds = get_bounds(agent_mix, i)
        
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
    print('Number of agents: %s' % n_users)
    print('Agent types:')
    for agent_type, val in agent_mix.items():
        print('   %s : %s' % (agent_type, val))

    print('Openness level: %s\n' %openness)

main()