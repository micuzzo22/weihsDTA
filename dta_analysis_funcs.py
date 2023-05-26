# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 14:33:59 2022

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

def get_dta_data(filename,sheetname,initial_mass):
    '''
    This function takes in the data from DTA run and returns a list with useful information
    that can be used with the other functions for analysis
    
    Parameters
    ----------
    filename : string
        name of excel file (properly formatted) where the data is
    sheetname : string
        name of excel sheet where the data is
    initial_mass : float
        initial mass of sample in milligrams

    Returns
    -------
    list
        list that has the following data in each index: dataframe with 
            [0] excel data,
            [1] temperature 
            [2] time in seconds 
            [3] baseline subtracted 
            [4] mass at each step based on real mass instead of DTA read mass 
            [5] true mass normalized heat flow (W/g)
            [6] true mass normalized baseline heat flow (W/g)
            [7] true mass normalized baseline subtracted heatflow (W/g)

    '''
       
    data = pd.read_excel(filename,sheet_name=sheetname, skiprows=1)
    temp = data.iloc[:,1]
    time_min = data.iloc[:,0]
    time_sec = time_min*60
    heatflow = data.iloc[:,3]
    heatflow_bl = data.iloc[:,10]
    bls_hf = heatflow - heatflow_bl
    
    # mass
    im = initial_mass
    data['Mass Diff Scan1'] = data.iloc[:,2] - data.iat[0, 2]
    data['True Mass Scan1'] = data['Mass Diff Scan1'] + im
    true_mass = data['True Mass Scan1']
    
    norm_hf = heatflow.divide(true_mass)                        #norm_hf = heatflow.divide(im)
    norm_hf_bl = heatflow_bl.divide(true_mass)                  #norm_hf_bl = heatflow_bl.divide(im)
    norm_hf_bls = norm_hf - norm_hf_bl
       
    return [data, temp, time_sec, bls_hf, true_mass, norm_hf, norm_hf_bl, norm_hf_bls]

def get_lower_upper_idxs(temperatures,ltb,utb):
    '''
    Finds the dataframe index that corresponds to the temperature bounds you will want for 
    curve adjustment or integration
    
    Parameters
    ----------
    temperatures : Pandas Series
        series of temperatures from run, must be a series and not a list! Use [1] from the 
        extracted data
    ltb : int or float
        ltb = lower temperature bound (in Celsius)
    utb : int or float
        utb = upper temperature bound (in Celsius)

    Returns
    -------
    initial_idx : int
        index corresponding to lower temperature 
    final_idx : int
        index corresponding to upper temperature

    '''
    
    initial_idx = temperatures.sub(ltb).abs().idxmin() 
    final_idx = temperatures.sub(utb).abs().idxmin()
    
    return initial_idx, final_idx

def perform_adjustment(run_data, ltb, utb):
    '''
    Provides an adjustment to the non-normalized and normalized baseline subtracted heat flow.
    It looks for a local minimum in the region of interest, finds the heat flow at that point and
    subtracts that from the non and normalized blshf. 

    Parameters
    ----------
    run_data : list
        Result from running get_dta_data function
    ltb : int or float
        ltb = lower temperature bound (in Celsius)
    utb : int or float
        tb = upper temperature bound (in Celsius)

    Returns
    -------
    run_data_adj : list
        The adjusted data replaces the non and normalized blshf which corresponds to 
        in column [3], [7] of original extracted data list

    '''   
    # get data
    bls_hf = run_data[3]
    norm_hf_bls = run_data[7]
    temperatures = run_data[1]
    
    # find idxs of pandas df temperatures
    initial_temp_idx,final_temp_idx = get_lower_upper_idxs(temperatures,ltb,utb)
       
    # get local min in range of idxs
    min_hf_idx_bls_hf = bls_hf[initial_temp_idx:final_temp_idx].idxmin()
    min_hf_idx_norm_hf_bls = norm_hf_bls[initial_temp_idx:final_temp_idx].idxmin()
    
    # find bls_hf value at 
    min_hf_bls_hf = bls_hf[min_hf_idx_bls_hf]
    min_hf_norm_bls_hf = norm_hf_bls[min_hf_idx_norm_hf_bls]
      
    # make dta adjustment, replace bls_hf with adjusted
    run_data_adj = run_data.copy()
    run_data_adj[3] = run_data[3] - min_hf_bls_hf
    run_data_adj[7] = run_data[7] - min_hf_norm_bls_hf      
        
    return run_data_adj

def get_intermetallic_heat(ar_run_data,ltb,utb,ar_initial_mass):
    
    '''
    Function that outputs the intermetallic heat over a given temperature range based
    on a DTA run done in Argon.

    Parameters
    ----------
    ar_run_data : list
        Result from running get_dta_data function (ran in Argon)
    ltb : int or float
        ltb = lower temperature bound (in Celsius)
    utb : int or float
        tb = upper temperature bound (in Celsius)
    ar_initial_mass : float
        Initial sample mass in milligrams (I tend to trust the microbalance more than the DTA)

    Returns
    -------
    intermetallic_heat : float
        The intermetallic heat over a given temperature range in J/g

    '''   
    
    # get temps, time, bls_hf
    temperatures = ar_run_data[1]
    times = ar_run_data[2]
    ar_bls_hf = ar_run_data[3]
        
    # get idx of lower and upper temperature bounds
    initial_idx, final_idx = get_lower_upper_idxs(temperatures,ltb,utb)
    
    # calc intermetallic heat release in J/g (doesn't factor in chemistry)
    raw_total_area = scipy.integrate.trapz(ar_bls_hf[initial_idx:final_idx],times[initial_idx:final_idx])
    intermetallic_heat = raw_total_area / (ar_initial_mass / 1000) / 1000
    
    return intermetallic_heat

def mass_gain_over_temp_range(aro2_run_data, ltb,utb):
    '''
    Calculates mass gain over given temperature range. Can be used for Ar + O2 or
    Ar + N2.

    Parameters
    ----------
    aro2_run_data : list
        Result from running get_dta_data function (ran in Ar + O2 or Ar + N2)
    ltb : int or float
        ltb = lower temperature bound (in Celsius)
    utb : int or float
        utb = upper temperature bound (in Celsius)

    Returns
    -------
    mg : float
        mass gain in milligrams

    '''
    
    # get masses and temperatures
    mass_list = aro2_run_data[4]
    temperatures = aro2_run_data[1]
    
    # get idx of lower and upper temperature bounds
    initial_idx, final_idx = get_lower_upper_idxs(temperatures,ltb,utb)
    
    # find the mass at initial and final idx
    initial_mass = mass_list[initial_idx]
    final_mass = mass_list[final_idx]
    
    mg = final_mass - initial_mass
    
    return mg

def get_heat_oxidation(aro2_run_data,ltb,utb,initial_mass):
    '''
    Calculates the heat of oxidation. Assumes that all mass gain is from O2 that
    reacts with Zr to form ZrO2.

    Parameters
    ----------
    aro2_run_data : list
        Result from running get_dta_data function (ran in Ar + O2)
    ltb : int or float
        ltb = lower temperature bound (in Celsius)
    utb : int or float
        tb = upper temperature bound (in Celsius)
    initial_mass : float
        Initial sample mass in milligrams (I tend to trust the microbalance more than the DTA)

    Returns
    -------
    oxidation_heat : float
        The heat from oxidation over a given temperature range in J/g

    '''
        
    mass_gain = mass_gain_over_temp_range(aro2_run_data,ltb,utb)  # mass gain in mg
    zro2_form_heat = 34.3     # kJ/g  Zirconia formation per 1 g O2 added in mass gain
    oxidation_heat = zro2_form_heat * mass_gain / (initial_mass / 1000)
    
    return oxidation_heat

def get_heat_nitridation(arn2_run_data,ltb,utb,initial_mass):
    '''
    Calculates the heat of nitridation. Assumes an average value between the heat of
    nitridation from AlN formation and ZrN formation.

    Parameters
    ----------
   arn2_run_data : list
       Result from running get_dta_data function (ran in Ar + N2)
   ltb : int or float
       ltb = lower temperature bound (in Celsius)
   utb : int or float
       utb = upper temperature bound (in Celsius)
   initial_mass : float
       Initial sample mass in milligrams (I tend to trust the microbalance more than the DTA)

   Returns
   -------
   nitridation_heat : float
       The heat from nitridation over a given temperature range in J/g

    '''
        
    mass_gain = mass_gain_over_temp_range(arn2_run_data,ltb,utb)  # mass gain in mg
    zrn_form_heat = 14.79     # kJ/g  zirconium nitride formation per 1 g N2 added in mass gain
    aln_form_heat = 22.7       # kJ/g  aluminum nitride formation per 1 g N2 added in mass gain 
    
    form_heat = (zrn_form_heat + aln_form_heat) / 2
    nitridation_heat = form_heat * mass_gain / (initial_mass / 1000)
    
    return nitridation_heat

def avg_stdev_heat(run_data_list,ltb,utb,initial_mass_list,heat_type):
    '''
    Calculates the avg and standard deviation heat release over a given temperature
    range for a list of dta run data. Can be used to get averages across multiple runs
    for same chemistry.

    Parameters
    ----------
    run_data_list : list
        list containing the names of the extracted data for each run
    ltb : int or float
        ltb = lower temperature bound (in Celsius)
    utb : int or float
        utb = upper temperature bound (in Celsius)
    initial_mass_list : list
        list containing the initial masses of the extracted data for each run
    heat_type : string
        Can be either "im", "ox", or "nit" depending on what kind of heat you are
        trying to average.

    Returns
    -------
    avg_heat : float
        average heat out in J/g over a temperature range
    heat_stdev : float
        standard deviation of avg heat released in J/g over a temperature range

    '''
    
    # make a list with calc heat from either im, ox, nit for each trial in the run data list
    heats = []
    for i in range(len(run_data_list)):
        if heat_type == "im":
            heats.append(get_intermetallic_heat(run_data_list[i],ltb,utb,initial_mass_list[i]))
                
        elif heat_type == "ox":
            heats.append(get_heat_oxidation(run_data_list[i],ltb,utb,initial_mass_list[i]))
            
        elif heat_type == "nit":
            heats.append(get_heat_nitridation(run_data_list[i],ltb,utb,initial_mass_list[i]))
            
        else:
            print("heat type incorrect. use either 'im', 'ox', or 'nit'")
    
    # get average of the heat list
    avg_heat = sum(heats) / len(run_data_list)
    
    # stdev
    if len(run_data_list) > 1:
        heat_stdev = statistics.stdev(heats)
    else:
        heat_stdev = 0
        
    return avg_heat, heat_stdev

def calculate_incremental_cumulative_heat(run_data_list,start_temp,end_temp,step,initial_mass_list,heat_type):
    '''
    Calculates the incremental heat release over a given temperature range at a given step size
    (ex: 25C increments from 125 to 700C) in J/g. Can be done for 1 trials or many trials with an avg

    Parameters
    ----------
    run_data_list : list
        list containing the names of the extracted data for each run
    start_temp : float
        starting temperature of range
    end_temp : float
        ending temperature of range
    step : int
        step size of increment to integrate over
    initial_mass_list : list
        list containing the initial masses of the extracted data for each run
    heat_type : string
        Can be either "im", "ox", or "nit" depending on what kind of heat you are
        trying to average.

    Returns
    -------
    incremental_heat : list
        list with the incremental heat released at each interval in J/g
    incremental_heat_stdev : list
        list with standard deviation of heat release at each interval in J/g
    cumulative_heats : list
        list with cumulative heat release at each interval in J/g

    '''
    
    # create a list that is the temp array. 
    temps = np.arange(start_temp, end_temp+step, step)
    
    # calculate the heat release 
    incremental_heat = []
    incremental_heat_stdev = []
    bound0 = temps[0]
    
    for i in range(1,len(temps)):
        
        avg_heat, stdev_heat = avg_stdev_heat(run_data_list,bound0, temps[i],initial_mass_list,heat_type)
        incremental_heat.append(avg_heat)
        incremental_heat_stdev.append(stdev_heat)
        
        # increment to next temperature range
        bound0 = temps[i]
        
    cumulative_heats = np.cumsum(incremental_heat)

    return incremental_heat, incremental_heat_stdev, cumulative_heats

def convert_Jg_kJmol(heat_J_g,chemstring,numatoms):
    '''
    Converts heat in J/g to kJ/mol

    Parameters
    ----------
    heat_J_g : float
        Heat in J/g
    chemstring : string
        String representing chemistry of powder. Refer to molar mass calculator script to 
        use proper syntax
    numatoms : int
        Number of atoms per compound

    Returns
    -------
    im_heat_kJ_mol : float
        Heat in kJ/mol

    '''
    molar_mass = get_molar_mass(chemstring) / numatoms

    # heat in kJ/mol 
    im_heat_kJ_mol = heat_J_g / 1000 * (molar_mass)
    
    return im_heat_kJ_mol
 
    
    
    
    
    
    
    
