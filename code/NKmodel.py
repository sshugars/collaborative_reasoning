
import numpy as np
import random
from numpy import linalg as LA
import itertools as it
from collections import Counter
from datetime import datetime
import json



#functions to make unique permutations of bits
class unique_element:
    def __init__(self, value, occurrences):
        self.value = value
        self.occurrences = occurrences

def unique_permutations(elements, r):
    unique_items = set(elements)
    unique_list = [unique_element(i, elements.count(i)) for i in unique_items]
    #u = len(elements)
    
    return unique_permutations_helper(unique_list, [0]*r, r-1)

def unique_permutations_helper(unique_list, result_list, d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in unique_list:
            if i.occurrences > 0:
                result_list[d] = i.value
                i.occurrences -= 1
                for g in unique_permutations_helper(unique_list, result_list, d-1):
                    yield g
                    
                i.occurrences += 1


def init_nodes(N, k, A):
    selection_string = [item for sublist in [[i] * N for i in range(A)] for item in sublist]

    # Make network
    nodes = dict((i, list(item)) for i, item in enumerate(set(unique_permutations(selection_string, N))))
    
    return nodes



def determine_influencers(N, k, A):
    
    influence_dict = dict()

    #first, determine which genes influence each other
    for i in range(N):
        population = [gene for gene in range(N) if gene != i]
        influencers = random.sample(population, k)

        influence_dict[i] = influencers
        
    return influence_dict


def interaction_table(N, k, A, influence_dict, lower_bound, upper_bound):
    selection_string = [item for sublist in [[i] * N for i in range(A)] for item in sublist]
        
    neighbor_vals = list(set(it.permutations(selection_string, k)))
    
    influence_patterns = dict()
    
    for i in range(N):
        influence_patterns.setdefault(i, dict())
        
        for j in range(A):
            influence_patterns[i].setdefault(j, dict())
        
            for neighbor_val in neighbor_vals:
                value = random.uniform(lower_bound, upper_bound)
                influence_patterns[i][j][neighbor_val] = value
    
    return influence_patterns


def get_node_values(nodes, influence_dict, influence_patterns):
    node_values = dict()
    N = len(nodes[0])
    
    for key, node in nodes.items():
        node_values[key] = 0.
        
        #for each bit, look up it's contribution to the value
        for bit, position in enumerate(node):
            
            #find influencer positions
            influence_positions = tuple([node[j] for j in influence_dict[bit]])
            bit_value = influence_patterns[bit][position][influence_positions]
            
            node_values[key] += bit_value
            
        node_values[key] = node_values[key] / N
            
    return node_values


def get_optimum(nodes, node_values):
    opt_index = [i for i in node_values.keys() if node_values[i] == max(node_values.values())]
    
    best_nodes = [nodes[i] for i in opt_index]
    best_values = [node_values[i] for i in opt_index]
    
    return best_nodes, best_values


def init_truth(N, k, A):
    nodes = init_nodes(N, k, A)
    influence_dict = determine_influencers(N, k, A)
    influence_patterns = interaction_table(N, k, A, influence_dict, lower_bound = -10, upper_bound = 10)
    node_values = get_node_values(nodes, influence_dict, influence_patterns)
    
    ground_truth = {
        'nodes': nodes,
        'influence_dict' : influence_dict,
        'influence_patterns' : influence_patterns,
        'node_values' : node_values
    }
    
    return ground_truth


def init_user(N, k, A, ground_truth, stable_influence = True, lower_bound = -10, upper_bound = 10):
    
    selection_string = [item for sublist in [[i] * N for i in range(A)] for item in sublist]
        
    neighbor_vals = list(set(it.permutations(selection_string, k)))
    
    if stable_influence:
        influence_dict = ground_truth['influence_dict']
    else:
        influence_dict = determine_influencers(N, k, A)
    
    #make noisy version of influence_patterns
    user_influence_patterns = dict()
    influence_patterns = ground_truth['influence_patterns']
    
    for i in range(N):
        user_influence_patterns.setdefault(i, dict())
        
        for j in range(A):
            user_influence_patterns[i].setdefault(j, dict())
                    
            for neighbor_val in neighbor_vals:
                true_val = influence_patterns[i][j][neighbor_val]

                noise = random.uniform(lower_bound, upper_bound) * np.sign(true_val)
                user_influence_patterns[i][j][neighbor_val] = noise + true_val
    
    node_values = get_node_values(ground_truth['nodes'], influence_dict, user_influence_patterns) 
    
    user_info = {
        'influence_dict' : influence_dict,
        'influence_patterns' : user_influence_patterns,
        'node_values' : node_values
    }
    
    return user_info



def voting(N, ground_truth, users):
    votes = dict()
    elected = list() #records individual preferences


    for user, user_info in users.items():
        best_nodes, best_values = get_optimum(ground_truth['nodes'], user_info['node_values'])
        
        for node in best_nodes:
            elected.append(''.join(list(map(str, node)))) #save as string so these can be keys

            for position, val in enumerate(node):
                votes.setdefault(position, list())
                votes[position].append(val)

    coalitions = Counter(elected)
                
    tally = np.zeros(N)
    raw_vote = np.zeros(N)
    
    for position, vote_list in votes.items():
        yes_vote = vote_list.count(1)
        yes_percent = yes_vote / len(vote_list)

        raw_vote[position] = yes_percent
        
        if yes_percent > 0.5:
            tally[position] = 1
        else:
            tally[position] = 0
            
    tally = list(map(int, tally))
    opt_val_index = [k for k, v in ground_truth['nodes'].items() if v == tally][0]
    opt_val = ground_truth['node_values'][opt_val_index]

    return tally, opt_val, raw_vote, coalitions



def get_outcome(N, ground_truth, users):
    
    true_best_node, true_best_value = get_optimum(ground_truth['nodes'], ground_truth['node_values'])
    tally, opt_val, raw_vote, coalitions = voting(N, ground_truth, users)

    # how much worse is elected decision?
    diff = -np.abs(true_best_value[0] - opt_val)

    # What percentage of good policies were implemented?
    good_policy_percent = np.mean([1 - np.abs(i - j) for i, j in zip(true_best_node[0], tally)])
    
    
    true_pos = true_best_node * raw_vote # people who voted for true things
    true_neg = (np.ones(N) - true_best_node) * (np.ones(N) - raw_vote) # people who didn't vote for wrong things
    good_votes = true_pos + true_neg
    good_vote_percent = np.mean(good_votes)

    return diff, good_policy_percent, good_vote_percent, coalitions


def init_users(n_users, N, k, A, ground_truth, bounds):
    users = dict()

    for i in range(n_users):
        user_info = init_user(N, k, A, ground_truth, lower_bound=bounds[i][0], upper_bound=bounds[i][1])
        users[i] = user_info
        
    return users


def iterate_exchange(N, A, ground_truth, users, max_iter, exchange, openness):
    outcome = dict()

    good_vote_percent = 0.

    while good_vote_percent < 1. and max_iter > 0:
        outcome.setdefault('diff', list())
        outcome.setdefault('policies', list())
        outcome.setdefault('votes', list())
        outcome.setdefault('cos', list())
        outcome.setdefault('coalitions', list())

        diff, good_policy_percent, good_vote_percent, coalitions = get_outcome(N, ground_truth, users)

        outcome['diff'].append(diff)
        outcome['policies'].append(good_policy_percent)
        outcome['votes'].append(good_vote_percent)
        outcome['coalitions'].append(coalitions)

        #update user beliefs
        users, cos = exchange(N, A, ground_truth, users, openness)
        outcome['cos'].append(cos) # list of cos traceable to time stamp and mappable to % agreement, etc
        
        max_iter -= 1 # to save from non-convergence
    
    return outcome



def multi_run(N, k, A, n_users, runs, bounds, max_iter, exchange, openness):
    
    ground_truth = init_truth(N, k, A) # Create ground truth ## DO THIS ONCE
    
    multi_run_output = dict()  
    
    for run in range(runs):

        verbose = int(runs / 2)

        if run%verbose == 0:
            print(run, datetime.now())

        users = init_users(n_users, N, k, A, ground_truth, bounds) #re-init each run
        
        outcome = iterate_exchange(N, A, ground_truth, users, max_iter, exchange, openness) #outcome of this run
        
        multi_run_output.setdefault(run, dict())
        
        for item in outcome.keys():
            multi_run_output[run][item] = outcome[item]        
        
    return multi_run_output

