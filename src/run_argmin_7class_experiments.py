''' 
Created on Sep 26, 2017

@author: Melvin Laux
'''
from evaluation.experiment import Experiment
from data import load_data
import numpy as np
import os

output_dir = '../../data/bayesian_annotator_combination/output/argmin7/'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

gt, annos, doc_start = load_data.load_argmin_7class_data()

exp = Experiment(None, 7, annos.shape[1], None)
exp.methods = ['bac', 'best', 'worst', 'majority']#['ibcc','mace','majority']#, 'clustering', 'ibcc', 'mace','bac',

exp.save_results = True
exp.exclusions = None # should not be needed now as dealt with through the inside/outside/beginning logic {0:[3,5], 2:[3,5], 3:[0,5], 4:[0,5], 5:[0,3], 6:[0,3]}
exp.opt_hyper = True

results, preds, _ = exp.run_methods(annos, gt, doc_start, output_dir)

if __name__ == '__main__':
    pass
