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
    '''
    This function takes in a list of run data (from get_dta_data) and their corresponding
    iniital masses and finds the average and standard deviation mass gain at each point. You can 
    use just 1 run but remember it must be inside a list!

    Parameters
    ----------
    run_data_list : list
        list of run data (from get_dta_data)
    initial_masses_list : list
        list of orresponding iniital masses of each run

    Returns
    -------
    run_data_mg_avg : Pandas Series
        The average mass gain at each point
    run_data_mg_stdev : Pandas Series
        The standard deviation for the mass gain at each point

    '''
    
    
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
    '''
    Using the averaged data, create a smoothed curve that approximates the average, and find the difference in 
    mass gain between the current and previous mass. Then a threshold value is used to determine when the difference 
    exceeds an appropriate value of mass gain difference. Temperatures below the cutoff temperature are not 
    considered.Find the index and temperature where this occurs.

    Parameters
    ----------
    avg_mass_change : Pandas Series
        From get_mg_percentage_avg_stdev, a series of the average mass at each point
    aro2_run_data : list
        Use a single trial's run data
    cutoff_temp : float
        Everything below this temperature is ignored when finding the start of mass gain (I would make it at least > 50C)
    threshold : float, optional
        The threshold that must be crossed to find the start of mass gain. Looking at the difference between mass at current
        point and the previous point. The default is 1e-4.
    smooth_value : int (odd), optional
        Smoothing factor for the savgol filter that filters the average mass gain curve. The default is 51.
    plot : Bool, optional
        You can plot the curve and where the function thinks the mass gain begins to troubleshoot. The default is False.

    Returns
    -------
    initial_idx : int
        Index of pandas series where the mass gain begins
    temp : float
        Temperature at which mass gain begins

    '''
    
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
    '''
    Finds the mass where the mass rise begins and makes that the new initial mass. Then it subtracts
    by that mass value to make it start at 0. Every point below this index is set to 0.

    Parameters
    ----------
    run_mg_avg : Pandas Series
        From get_mg_percentage_avg_stdev, a series of the average mass at each point
    mg_start_idx : int
        From get_start_mass_gain, the index of the run_mg_avg pandas series where mass gain begins

    Returns
    -------
    run_mg_avg_adj : Pandas Series
        The modified pandas series that has the avg mass gain at each point

    '''
    
    # make a new column that has "true" mass gain differential
    run_avg_new_im = run_mg_avg[mg_start_idx]
    
    # adjust the curve by subtracting by that amount for each point and then plot the avg
    run_mg_avg_adj = run_mg_avg - run_avg_new_im 
    
    # replace everything below with 0s
    run_mg_avg_adj.loc[0:mg_start_idx] = 0
    
    return run_mg_avg_adj

#%%
def modify_run_mass_diff(aro2_run_data,mg_start_idx,im):
    '''
    Modifies the original extracted dataframe and sets the mass below the starting index to 0
    and changes the True Mass column to reflect the true starting mass

    Parameters
    ----------
    aro2_run_data : list
        From get_dta_data
    mg_start_idx : int
        From get_start_mass_gain, the index of the run_mg_avg pandas series where mass gain begins
    im : float
        true initial starting mass

    Returns
    -------
    aro2_run_data : list
        Returns the modified dataframe

    '''
    
    aro2_run_data[0]['Mass Diff Scan1'] - aro2_run_data[0]['Mass Diff Scan1'].loc[mg_start_idx] 
    aro2_run_data[0]['Mass Diff Scan1'][0:mg_start_idx] = 0
    
    # also need to change the "true mass column to make it the original mass
    aro2_run_data[0]['True Mass Scan1'][0:mg_start_idx] = im
    
    return aro2_run_data
