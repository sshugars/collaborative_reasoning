Replication materials for _Collaborative Reasoning on Value-Laden Topics: A Game of Giving and Asking for Reasons_. Sarah Shugars _(under review)_.  Documentation for this paper is sorted into three folders:

* code/
Contains all code for running and analyzing simulations. Specific files detailed below.

* data/
Contains summary data from simulations presented in the paper. These data are used to create all figures which appear in the paper. Raw data from the simulations can be downloaded from https://www.dropbox.com/sh/iv5gsgs8g0zxidm/AACS6HcIBHGtXmpD3-E-2mLBa?dl=0 

* figs/
Contains all figures used within the paper

# Included scripts
**experiments.py**
Main function for running simulations. This code can be run from the terminal using the command `python3 experiments.py'. Code will prompt you for the following simulation parameters:
* number of agents in the simulation. Must be an integer > 0.
* Type(s) of agents in the simulation. Choices are uninformed, ideologues, maj_ideologues, maj_intellectual, portion_intellectual. 
* Openness: the required cosine similarity for accepting or rejecting a proposal. Must be between -1 and 1, inclusive.

Given these parameters, the script will create a new folder called `raw/[agent_type]/[n_users]_people/cos[openness]` and will run 100 simulations for noise level 1-210. Results of each noise level will be stored in a .json.gzip file with the the name `noise[noise].json.gzip'

	Input: Simulation parameters: number of agents, types of agents, openness level
	
	Output: Folder within `raw` containing output from a 100 simulations at each noise level from 1-210.

**NKmodel.py**
Helper functions for initializing NK model and model and running exchange

     Called by experiments.py


**process.py**
Processes data in `/raw`. This code can be run from the terminal with `python3 process.py`. Code will prompt you for a path to process. This can be a path to the output from a single experiment, or can be a higher path containing multiple experiments output. Can also enter 'all' to process all simulations in the `raw/' folder.

	Input: A path of raw output from `experiments.py'.
	
	Output: A .json.gzip file summarizing the experiment's results.


**visualizations.py**

Create all visualizations used within the paper. Will take data from `processed/` folder and save .png images to `figs/`.

	Input: Processed data. The images in the paper requires the following processed files:
		*  `uninformed_25people_cos0.json.gzip` (Fig 4)
		* `ideologues_25people_cos0.json.gzip` (Fig 4 & Fig 6)
		* `maj_intelectuals_25people_cos0.json.gzip` (Fig 4 & Fig 5)
		*  `maj_ideologues_25people_cos0.json.gzip' (Fig 5)
		*   `ideologues_25people_cosNeg75.json.gzip` (Fig 6)
		*   `ideologues_25people_cosPos75.json.gzip` (Fig 6)
	
	Output: .png images.