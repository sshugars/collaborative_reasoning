import os
import json
import gzip
import numpy as np
import random
import matplotlib
import matplotlib.pyplot as plt


################ Plot settings #############

import matplotlib

matplotlib.rc('xtick', labelsize=13) 
matplotlib.rc('ytick', labelsize=13) 
matplotlib.rc('xtick.major', size=4, width=1)
matplotlib.rc('xtick.minor', size=1, width=1)
matplotlib.rc('ytick.major', size=4, width=1)
matplotlib.rc('ytick.minor', size=1, width=1)
matplotlib.rc('axes', edgecolor='504A4B')  # axes edge color
matplotlib.rc('axes', grid=False)  # display grid or not
matplotlib.rc('axes', titlesize=20)   # fontsize of the axes title
matplotlib.rc('axes', labelsize=15)  # fontsize of the x and y labels

matplotlib.rc('lines', linewidth=2.0)     # line width in points

matplotlib.rc('legend', fontsize=16)

matplotlib.rc('figure', figsize=(10, 6))    # figure size in inches
matplotlib.rc('figure', facecolor='ffffff')    # figure facecolor

#matplotlib.rc('xtick', color='504A4B')      # color of the tick labels
#matplotlib.rc('ytick', color='504A4B')    # color of the tick labels
#matplotlib.rc('grid', color='f7f7f5')   # grid color f7f7f5


######### Input / output ###########

inpath = '../data/processed/'
plot_path = '../../figs/'
os.chdir(inpath)


#uninformed, ideologues, majority intellectuals
fig4 = ['uninformed_25people_cos0.json.gzip', 'ideologues_25people_cos0.json.gzip',
             'maj_intellectuals_25people_cos0.json.gzip']

#majority intellectuals, majority ideologues
fig5 = ['maj_intellectuals_25people_cos0.json.gzip', 'maj_ideologues_25people_cos0.json.gzip']


#ideologues cos 0, ideologues cos 75, ideologues cos -75
fig6 = ['ideologues_25people_cosPos75.json.gzip', 'ideologues_25people_cos0.json.gzip', 
            'ideologues_25people_cosNeg75.json.gzip']



def load_data(filename):
    with gzip.open(filename, 'r') as fp:
        data = json.loads(fp.read().decode())
        
    return data


def get_policies(data):
    all_runs = np.stack([details['good_policies'] for run, details in data.items()])
    perfect = np.zeros(np.shape(all_runs))

    for row, col in zip(*np.where(all_runs >= 1)):
        perfect[row][col] = 1   
        
    return perfect

#distance from optimal
def get_distance(data):
    all_runs = np.stack([details['distance'] for run, details in data.items()])

    return all_runs #average_distance

def get_coal_size(data):
    all_runs = np.stack([details['largest_coal'] for run, details in data.items()])
    
    return all_runs

def get_coal_count(data):
    all_runs = np.stack([details['coal_count'] for run, details in data.items()])
    
    return all_runs

def get_time(data):
    all_runs = np.stack([details['timesteps'] for run, details in data.items()])
    
    return all_runs


def merge_data(data_matrix, window = 10):
    cols = np.shape(data_matrix)[0] - (window - 1)
    rows = np.shape(data_matrix)[1] * window
    merged = np.zeros((cols, rows))

    for i, row in enumerate(data_matrix):
        row_index = i

        while row_index >= max([0, i - (window - 1)]):
            if row_index < 200:
                for j, val in enumerate(row):
                    col_index = j + ((i - row_index) * np.shape(data_matrix)[1])

                    merged[row_index][col_index] = val

            row_index -= 1
            
    return merged


def get_error(merged, sample_size = 100, n_samples = 20, measure_type = 'Mean'):
    N = np.shape(merged)[0]
    
    samples = np.zeros((N, n_samples))

    for i in range(N):
        for j in range(n_samples):
            sample = random.sample(list(merged[i]), sample_size) #sample 100 runs

            if measure_type == 'Percent':
                percent = sample.count(1) / len(sample)

                samples[i][j] = percent
                
            elif measure_type == 'Mean':
                samples[i][j] = np.mean(sample)

    sigma = np.std(samples, axis = 1)
    
    return sigma

def get_fig_4a(legend = False):
	for filename in fig4:
	    agent_type = filename.split('_')[0]

	    if agent_type == 'maj':
	    	agent_type = filename.split('_')[1]
	    
	    if agent_type == 'uninformed':
	        sty = '--'
	        
	    elif agent_type == 'ideologues':
	        sty = ':'
	        
	    elif agent_type == 'intellectuals':
	        ideo_type = 'majority intellectuals'
	        sty = 'solid'
	    
	    data = load_data(filename)
	    
	    perfect = get_policies(data)
	    merged = merge_data(perfect, window=10)
	    percent_perfect = np.mean(merged, axis = 1)
	    sigma = get_error(merged, sample_size = 100, n_samples = 20, measure_type='Percent')
	    
	    high = percent_perfect + sigma*2
	    low = percent_perfect - sigma*2
	    
	    x = len(percent_perfect) - 1
	    
	    plt.plot(range(x),  percent_perfect[:-1], label = agent_type, ls = sty, lw = 2)
	    plt.fill_between(range(x), low[:-1], high[:-1], alpha = 0.4)

	plt.yticks(np.arange(0, 1.2, .2))
	plt.xlabel('Noise')
	plt.ylabel('% good policies enacted')

	if legend:
		plt.legend(bbox_to_anchor=(1,1))
	
	plt.savefig(plot_path + 'comp_ideo_policies.png', format = 'png', dpi = 300, bbox_inches= 'tight')
	plt.close()

	print('Figure 4a written to file comp_ideo_policies.png')

def get_fig_4b(legend = False):
	for filename in fig4:
	    agent_type = filename.split('_')[0]

	    if agent_type == 'maj':
	    	agent_type = filename.split('_')[1]

	    
	    if agent_type == 'uninformed':
	        sty = '--'
	        
	    elif agent_type == 'ideologues':
	        sty = ':'
	        
	    elif agent_type == 'intellectuals':
	        agent_type = 'majority intellectuals'
	        sty = 'solid'
	    
	    data = load_data(filename)
	    
	    distance = get_distance(data)
	    merged = merge_data(distance)
	    sigma = get_error(merged, measure_type='Mean')
	    
	    avg = np.mean(merged, axis = 1)
	    high = avg + sigma*2
	    low = avg - sigma*2
	    
	    x = len(avg) - 1
	    
	    plt.plot(range(x), avg[:-1], label = agent_type, ls = sty, lw = 2)
	    plt.fill_between(range(x), low[:-1], high[:-1], alpha = 0.4)

	plt.xlabel('Noise')
	plt.ylabel('Distance from Optimal')
	if legend:
		plt.legend(bbox_to_anchor=(1,1))
	
	plt.savefig(plot_path + 'comp_ideo_distance.png', format = 'png', dpi = 300, bbox_inches= 'tight')

	plt.close()
	print('Figure 4b written to file comp_ideo_distance.png')

def get_fig_4c(legend = False):
	for filename in fig4:
	    agent_type = filename.split('_')[0]

	    if agent_type == 'maj':
	    	agent_type = filename.split('_')[1]

	    n_users = int(filename.split('_')[-2][:2])
	    
	    if agent_type == 'uninformed':
	        sty = '--'
	        
	    elif agent_type == 'ideologues':
	        sty = ':'
	        
	    elif agent_type == 'intellectuals':
	        agent_type = 'majority intellectuals'
	        sty = 'solid'
	        
	    data = load_data(filename)
	    largest_coal = get_coal_size(data)
	    
	    merged = merge_data(largest_coal)
	    normed = [val / n_users for val in merged]
	    
	    sigma = get_error(normed)
	    
	    avg = np.mean(normed, axis = 1)
	    high = avg + sigma*2
	    low = avg - sigma*2
	    
	    x = len(avg) - 1
	    
	    plt.plot(range(x), avg[:-1], label = agent_type, ls = sty, lw = 2)
	    plt.fill_between(range(x), low[:-1], high[:-1], alpha = 0.4)

	plt.yticks(np.arange(0, 1.1, .2))
	plt.xlabel('Noise')
	plt.ylabel('% of Agents in Largest Coalition')

	if legend:
		plt.legend(bbox_to_anchor=(2,1))
	
	plt.savefig(plot_path + 'comp_ideo_coal.png', format = 'png', dpi = 300, bbox_inches= 'tight')
	plt.close()

	print('Figure 4c written to file: comp_ideo_coal.png')

def get_fig_5a(legend = False):
	for filename in fig5:
	    agent_type = filename.split('_')[1]
	    
	    if agent_type == 'intellectuals':
	        agent_type = 'majority intellectuals'
	        sty = '-'
	        
	    elif agent_type == 'ideologues':
	        agent_type = 'majority ideologues'
	        sty = ':'
	    
	    data = load_data(filename)
	    
	    perfect = get_policies(data)
	    merged = merge_data(perfect, window=10)
	    percent_perfect = np.mean(merged, axis = 1)
	    sigma = get_error(merged, sample_size = 100, n_samples = 20, measure_type='Percent')
	    
	    high = percent_perfect + sigma*2
	    low = percent_perfect - sigma*2
	    
	    x = len(percent_perfect) - 1
	    
	    plt.plot(range(x),  percent_perfect[:-1], label = agent_type, ls = sty, lw = 2)
	    plt.fill_between(range(x), low[:-1], high[:-1], alpha = 0.4)


	plt.yticks(np.arange(0, 1.2, .2))

	plt.xlabel('Noise')
	plt.ylabel('% good policies enacted')

	if legend:
		plt.legend(bbox_to_anchor=(1.1,1))
	
	plt.savefig(plot_path + 'comp_mod_policies.png', format = 'png', dpi = 300, bbox_inches= 'tight')
	plt.close()

	print('Figure 5a written to file: comp_mod_policies.png')

def get_fig_5b(legend = False):
	for filename in fig5:
	    agent_type = filename.split('_')[1]
	    
	    if agent_type == 'intellectuals':
	        agent_type = 'majority intellectuals'
	        sty = '-'
	        
	    elif agent_type == 'ideologues':
	        agent_type = 'majority ideologues'
	        sty = ':' 
	        
	    data = load_data(filename)
	    
	    distance = get_distance(data)
	    merged = merge_data(distance)
	    sigma = get_error(merged, measure_type='Mean')

	    avg = np.mean(merged, axis = 1)
	    high = avg + sigma*2
	    low = avg - sigma*2

	    x = len(avg) - 1

	    plt.plot(range(x), avg[:-1], label = agent_type, ls = sty, lw = 2)
	    plt.fill_between(range(x), low[:-1], high[:-1], alpha = 0.4)


	plt.yticks(np.arange(-5, 1, 1))
	plt.xlabel('Noise')
	plt.ylabel('Distance from Optimal')

	if legend:
		plt.legend(bbox_to_anchor=(1,.2))
	
	plt.savefig(plot_path + 'comp_mod_distance.png', format = 'png', dpi = 300, bbox_inches= 'tight')
	plt.close()

	print('Figure 5b written to file: comp_mod_distance.png')

def get_fig_6a(legend = False):
	for filename in fig6:
	    ideo_type = filename.split('_')[-1].split('.')[0]
	    
	    if ideo_type == 'cos0':
	        agent_type = 'ideologues - moderate'
	        sty = '--'
	        
	    elif ideo_type == 'cosPos75':
	        agent_type = 'ideologues - skeptical'
	        sty = '-'
	        
	    elif ideo_type == 'cosNeg75':
	        agent_type = 'ideologues - open'
	        sty = ':'
	    
	    data = load_data(filename)
	    
	    perfect = get_policies(data)
	    merged = merge_data(perfect, window=10)
	    percent_perfect = np.mean(merged, axis = 1)
	    sigma = get_error(merged, sample_size = 100, n_samples = 20, measure_type='Percent')
	    
	    high = percent_perfect + sigma*2
	    low = percent_perfect - sigma*2
	    
	    x = len(percent_perfect) - 1
	    
	    plt.plot(range(x),  percent_perfect[:-1], label = agent_type, ls = sty, lw = 2)
	    plt.fill_between(range(x), low[:-1], high[:-1], alpha = 0.4)


	plt.yticks(np.arange(0, 1.2, .2))
	plt.xlabel('Noise')
	plt.ylabel('% good policies enacted')

	if legend:
		plt.legend(bbox_to_anchor=(1,.3))
	
	plt.savefig(plot_path + 'comp_cos_policies.png', format = 'png', dpi = 300, bbox_inches= 'tight')
	plt.close()

	print('Figure 6a written to file: comp_cos_policies.png')

def get_fig_6b(legend = False):
	for filename in fig6:
	    ideo_type = filename.split('_')[-1].split('.')[0]
	    
	    if ideo_type == 'cos0':
	        agent_type = 'ideologues - moderate'
	        sty = '--'
	        
	    elif ideo_type == 'cosPos75':
	        agent_type = 'ideologues - skeptical'
	        sty = '-'
	        
	    elif ideo_type == 'cosNeg75':
	        agent_type = 'ideologues - open'
	        sty = ':'
	    
	    
	    data = load_data(filename)
	    
	    distance = get_distance(data)
	    merged = merge_data(distance)
	    sigma = get_error(merged, measure_type='Mean')

	    avg = np.mean(merged, axis = 1)
	    high = avg + sigma*2
	    low = avg - sigma*2

	    x = len(avg) - 1

	    plt.plot(range(x), avg[:-1], label = agent_type, ls = sty, lw = 2)
	    plt.fill_between(range(x), low[:-1], high[:-1], alpha = 0.4)


	plt.yticks(np.arange(-5, 1, 1))
	plt.xlabel('Noise')
	plt.ylabel('Distance from Optimal')
	
	if legend:
		plt.legend(bbox_to_anchor=(1,.3))
	
	plt.savefig(plot_path + 'comp_cos_distance.png', format = 'png', dpi = 300, bbox_inches= 'tight')
	plt.close()

	print('Figure 6b written to file: comp_cos_distance.png')

def main():
	get_fig_4a()
	get_fig_4b()
	get_fig_4c()

	get_fig_5a()
	get_fig_5b(legend = True)

	get_fig_6a()
	get_fig_6b(legend = True)

	print('All figures saved to file')

main()