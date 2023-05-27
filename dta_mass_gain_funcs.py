# -*- coding: utf-8 -*-
"""
Created on Fri May 26 14:17:30 2023

@author: Mikey
"""
## dta analysis functions
import os
import sys
from sys import path
import pandas as pd
import scipy
from scipy import integrate
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
import statistics
import numpy as np

from molar_mass_calculator import *

#%%
def get_mg_percentage_avg_stdev(run_data_list,initial_masses_list):
    
    mass_gain_percentages = []
    for i in range(len(run_data_list)):
        run_data_mg = 100 * (run_data_list[i][0]['Mass Diff Scan1'] / initial_masses_list[i])
        mass_gain_percentages.append(run_data_mg)
        
    run_data_mg_df = pd.DataFrame(mass_gain_percentages).T
    run_data_mg_avg = run_data_mg_df.mean(axis=1)
    run_data_mg_stdev = run_data_mg_df.std(axis=1)
        
    return run_data_mg_avg, run_data_mg_stdev

#%% 
def get_start_mass_gain(avg_mass_change,aro2_run_data,cutoff_temp,threshold=1e-4,smooth_value=51,plot=False):
    
    avg_mass_change_diff = avg_mass_change.diff().fillna(0)
    avg_mass_change_diff_smooth = savgol_filter(avg_mass_change_diff, smooth_value, 3)
    
    if plot != False:
        # plot
        ax = plt.subplot(111)
    
        ax.plot(aro2_run_data[1],avg_mass_change_diff,color="black",label="raw")
        ax.plot(aro2_run_data[1],avg_mass_change_diff_smooth,color="lightgreen",label="smooth")
    
    avg_mass_change_diff_smooth = pd.Series(avg_mass_change_diff_smooth)
    # cutoff beginning data
    cutoff_idx = aro2_run_data[1].sub(cutoff_temp).abs().idxmin()
    #cutoff_idx = aro2_run_data[1][aro2_run_data[1].gt(cutoff_temp)].index[0]
    avg_mass_change_diff_smooth = avg_mass_change_diff_smooth[avg_mass_change_diff_smooth.index > cutoff_idx] 
    #print(avg_mass_change_diff_smooth.size)


    # find temperature at which that occurs
    #initial_idx = avg_mass_change_diff_smooth.sub(threshold).abs().idxmin() #
    initial_idx = avg_mass_change_diff_smooth[avg_mass_change_diff_smooth.gt(threshold)].index[0]
    #print(initial_idx)
    temp = aro2_run_data[1][initial_idx]
    
    if plot != False:
        ax.scatter(temp,avg_mass_change_diff[initial_idx],color="r",marker="*",s=100)
    
    return initial_idx, temp
    
#%%
def adjust_avg_mass_gain(run_mg_avg,mg_start_idx):
    
    # make a new column that has "true" mass gain differential
    run_avg_new_im = run_mg_avg[mg_start_idx]
    
    # adjust the curve by subtracting by that amount for each point and then plot the avg
    run_mg_avg_adj = run_mg_avg - run_avg_new_im 
    
    # replace everything below with 0s
    run_mg_avg_adj.loc[0:mg_start_idx] = 0
    
    return run_mg_avg_adj

#%%
def modify_run_mass_diff(aro2_run_data,mg_start_idx,im):
    
    aro2_run_data[0]['Mass Diff Scan1'] - aro2_run_data[0]['Mass Diff Scan1'].loc[mg_start_idx] 
    aro2_run_data[0]['Mass Diff Scan1'][0:mg_start_idx] = 0
    
    # also need to change the "true mass column to make it the original mass
    aro2_run_data[0]['True Mass Scan1'][0:mg_start_idx] = im
    
    return aro2_run_data