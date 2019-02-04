'''
Created on Sep 7, 2017

@author: Melvin Laux
'''

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from evaluation import metrics, experiment
import sklearn.metrics as skm
from data import data_utils

def load_results(config):
    
    exp = experiment.Experiment(None, config)
    
    all_dirs = glob.glob(os.path.join(exp.output_dir, "data/param*/"))
    all_dirs.sort(key=lambda s: int(s.split('/')[4][5:]))
    
    print(all_dirs)
    
    results = np.zeros((len(exp.param_values), len(exp.SCORE_NAMES), len(exp.methods), exp.num_runs))
    
    param_id = 0
    for direc in all_dirs:
        all_runs = glob.glob(os.path.join(direc, "set*/"))
        run_id = 0
        
        
        for run in all_runs:
            
            gt = np.loadtxt(os.path.join(run, "ground_truth.csv"))
            agg = np.loadtxt(os.path.join(run, "predictions.csv"))
            
            if exp.param_idx == 4:
                doc_length = exp.param_values[param_id]
            else:
                doc_length = exp.doc_length
            num_docs = exp.num_docs
            doc_start = np.zeros((num_docs * int(doc_length), 1))
            doc_start[list(range(0, num_docs * doc_length, doc_length))] = 1
            
            result = -np.ones((9, agg.shape[1]))
            for i in range(agg.shape[1]):
                
        
                result[7, i] = metrics.num_invalid_labels(agg[:, i], doc_start)
        
                # postprocess
                agg[:, i] = data_utils.postprocess(agg[:, i], doc_start)
        
                result[0, i] = skm.accuracy_score(gt, agg[:, i])
                result[1, i] = skm.precision_score(gt, agg[:, i], average='macro')
                result[2, i] = skm.recall_score(gt, agg[:, i], average='macro')
                result[3, i] = skm.f1_score(gt, agg[:, i], average='macro')
                auc_score = skm.roc_auc_score(gt == 0, agg[:, i] == 0) * np.sum(gt == 0)
                auc_score += skm.roc_auc_score(gt == 1, agg[:, i] == 1) * np.sum(gt == 1)
                auc_score += skm.roc_auc_score(gt == 2, agg[:, i] == 2) * np.sum(gt == 2)
                result[4, i] = auc_score / float(gt.shape[0])
                # result[5] = skm.log_loss(gt, probs, eps=1e-100)
                result[6, i] = metrics.count_error(agg[:, i], gt)
                result[8, i] = metrics.mean_length_error(agg[:, i], gt, doc_start)
                
            results[param_id, :, :, run_id] = result
            # np.append(results, np.mean(result, axis=1), axis=0)
            
            run_id += 1
        param_id += 1 
            
    exp.plot_results(results, False, True, exp.output_dir+'new')
    
    
def plot_crowdsourcing_results():
    exp = experiment.Experiment(None, None)
    exp.param_values = np.arange(1,9)
    exp.param_idx = -1
    exp.methods = np.array(['bac', 'majority'])#'clustering', 'HMM_crowd', 'ibcc', 'mace', 'majority'])
    
    num_runs = 2
    
    all_dirs = glob.glob('../../data/bayesian_sequence_combination/output/crowdsourcing/k*')
    all_dirs.sort(key=lambda s: int(s.split('/')[3][1:]))
    
    scores = np.zeros((len(exp.param_values), len(exp.SCORE_NAMES), len(exp.methods), num_runs))
    
    for j in range(len(all_dirs)):
        for i in range(num_runs):
            scores[j,:,:,i] = np.genfromtxt(all_dirs[j] + '/run' + str(i) + '/results2.csv', delimiter=',')
    
    exp.plot_results(scores, False, True, '../../data/bayesian_sequence_combination/output/crowdsourcing/plots/')

            
def plot_hyperparameter_results():
    exp = experiment.Experiment(None, 3, 3)
    
    alpha0_factors = np.arange(1, 20) ** 2 # 100.0 --> the working value
    exp.param_values = alpha0_factors[:-1]
    
    exp.PARAM_NAMES = ['alpha0 factor']
    exp.param_idx = 0
    exp.methods = np.array(['bac_seq'])#, 'majority'])#'clustering', 'HMM_crowd', 'ibcc', 'mace', 'majority'])
     
    num_runs = 2
     
    #all_dirs = glob.glob('../../data/bayesian_sequence_combination/output/hyperparameters_crowdsourcing/alphafactor*')
    all_dirs = glob.glob('../../data/bayesian_sequence_combination/output/hyperparameters_argmin/nu0factor*_'
                         + exp.methods[0])
    all_dirs.sort(key=lambda s: float(s.split('/')[6][9:].split('_')[0]))
     
    scores = np.zeros((len(all_dirs),len(exp.SCORE_NAMES),len(exp.methods),num_runs))
    lb = np.zeros((len(all_dirs), len(exp.methods), num_runs))
     
    for j in range(len(all_dirs)):
        print(all_dirs[j])
        for i in range(num_runs):
            result_file = glob.glob(all_dirs[j] + '/run' + str(i) + '/result_started*')[-1]
            scores_ji = np.genfromtxt(result_file, delimiter=',')
            if scores_ji.ndim == 1:
                scores_ji = scores_ji[:, None]
            scores[j,:,:,i] = scores_ji[:len(exp.SCORE_NAMES), :]
            if scores_ji.shape[0] > len(exp.SCORE_NAMES):
                lb[j, :, i] = scores_ji[len(exp.SCORE_NAMES), :] # the lower bound values 
                 
    exp.plot_results(scores, False, True, '../../data/bayesian_sequence_combination/output/hyperparameters_crowdsourcing/plots/')
    exp.plot_results(lb[:, None, :, :], False, True, '../../data/bayesian_sequence_combination/output/hyperparameters_crowdsourcing/plots/', ['ELBO'])


def plot_tuning_results():

    diags = [1, 5, 10, 50]
    factors = [1, 4, 9, 16, 25]
    methods_to_tune = ['ibcc'] # 'bac_mace', 'bac_acc', 'bac_ibcc', 'bac_seq',
    output_dir = '../../data/bayesian_sequence_combination/output/ner/'

    # all_dirs = glob.glob('../../data/bayesian_sequence_combination/output/hyperparameters_crowdsourcing/alphafactor*')

    for method in methods_to_tune:

        plt.figure()
        scores = np.zeros((len(diags), len(factors)))

        for i, diag in enumerate(diags):
            for j, fac in enumerate(factors):

                dirname = output_dir + '_%i_%i_%s' % (i, j, method)
                scores_ijm = np.genfromtxt(dirname + '/scores.csv', skip_header=1, delimiter=',')

                scores[i, j] = scores_ijm[0]

            plt.plot(factors, scores[i], label='%i' % diag)

        plt.xlabel('factors')
        plt.ylabel('f1 scores')
        plt.legend(loc='best')
        plt.show()

if __name__ == '__main__':
    plot_tuning_results()
    #plot_hyperparameter_results()
#    plot_crowdsourcing_results()    
    #load_results('./config/acc_experiment.ini')
    #load_results('./config/class_bias_experiment.ini')
    #load_results('./config/short_bias_experiment.ini')
    #load_results('./config/doc_length_experiment.ini')
    #load_results('./config/crowd_size_experiment.ini')
    #load_results('./config/group_ratio_experiment.ini')

