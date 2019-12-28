'''
This code will process the output of experiments.py

Takes: A folder containing full data from a single experiment,
where each file contains data for all timesteps over multiple runs.
These data are output by experiments.py

Returns: Single file with data from final state for all runs.
Data are saved are for following items of iterest:
    'good_policies' -- the % of good policies enacted in end state
    'distance' -- distance of final enacted policy from ground truth
    'largest_coal' -- size of the largest coalition
    'coal_count' -- number of coalitions
    'timesteps' -- number of timesteps to final state

Output is saved as a json of form:
    noise : {
            item of interest : [vector of length N runs]
            }
'''

import os
import glob
import numpy as np
import json
import gzip
import re


################ System Parameters #################
runs = 100 # number of times to run this exchange
max_iter = 5000 #number of iterations

min_noise = 1
max_noise = 210

#fields to save final state of
fields = ['good_policies', 'distance', 'largest_coal', 'coal_count', 'timesteps']

################# Input/Output ################
path_root = '../data/raw/'
filename_format = '/noise_'

outpath = '../data/processed/'

def get_outfile(path):
    details = path.split('/')

    cos_text = details[-1]
    user_text = ''.join(details[-2].split('_'))
    agent_type = details[-3]

    outfile = '%s_%s_%s.json.gzip' %(agent_type, user_text, cos_text)

    return outfile

def process_folder(path):
    print('Processing data in %s...' %path)

    outfile = get_outfile(path)

    processed = dict()
       
    for noise in range(min_noise, max_noise + 1):
            
        filename = filename_format + '%s.json.gzip' %noise

        try:
            with gzip.open(path + filename, 'r') as fp:
                data = json.loads(fp.read().decode())
                    
                noise_data = dict()

                for item in fields:
                    noise_data.setdefault(item, np.zeros(runs))
                    
                #iterate through runs to get data we need
                for run in range(runs):
                    end_policy = data[str(run)]['policies'][-1] 
                    end_distance = data[str(run)]['diff'][-1]
                    largest_coal = max(data[str(run)]['coalitions'][-1].values())
                    coal_count = len(data[str(run)]['coalitions'][-1]) 
                    
                    timesteps = len(data[str(run)]['policies'])
                    
                    
                    #add this info to dictionary
                    noise_data['good_policies'][run] = end_policy
                    noise_data['distance'][run] = end_distance
                    noise_data['largest_coal'][run] = largest_coal
                    noise_data['coal_count'][run] = coal_count
                    noise_data['timesteps'][run] = timesteps
                    
                #save in our overall dict
                processed[noise] = noise_data
        except:
            print('No file found for noise level %s. Passing for now.' %noise)
            pass

    print('%s files out of expected %s files processed' %(len(processed), (max_noise - min_noise) + 1))
    print('Writing data to file: %s' %outfile)

    for run in processed:
        for field in fields:
            processed[run][field] = processed[run][field].tolist()

    with gzip.open(outpath + outfile, 'w') as fp:
        fp.write(json.dumps(processed).encode())
                
    print('Processed data written to file\n')


###################################################
################# Main Function ###################
###################################################

def main():

    print('Please indicate the data you would like to process.')

    process = input('Enter a directory you would like to process, or enter "all" to process everything in data/raw/\n')

    paths = list()
    
    if process.lower() == 'all':    
        for root, dirs, files in os.walk(path_root):
            if len(dirs) == 0 :
                paths.append(root)

    else:
        if os.path.isdir(process):
            for root, dirs, files in os.walk(process):
                if len(dirs) == 0 :
                    paths.append(root)
        else:
            print('No folder found with path: %s' %process)

    if paths:
        print('Will process data in paths:')
        for path in paths:
            print(path)
     

        for i, path in enumerate(paths):
            process_folder(path)

            if i < len(paths): 
                print('%s folders remainining' %(len(paths) - i))

            else:
                print('***ALL DATA PROCESSED AND WRITTEN TO FILE***')
    else:
        print('No valid paths found to process.')

main()
