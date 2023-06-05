# -*- coding: utf-8 -*-
"""
Created on Sat May 27 13:51:51 2023

@author: Mikey
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from molar_mass_calculator import *
from dta_analysis_funcs import *

# Global plotting parameters
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"
plt.rcParams['axes.linewidth'] = 1.7
plt.rcParams["figure.figsize"] = (10,6)
plt.rcParams.update({'font.size': 18,
                     'xtick.labelsize' : 18,
                     'ytick.labelsize' : 18})

# IBM color blind color scheme
b = "#648fff"; p = "#785ef0"; r = "#dc267f"; o = "#fe6100"
y = "#ffb000"; black = "black"; gray = "#444655"

# Switch to working directory where the excel file is (keep r in front)
os.chdir(r"C:\Users\Mikey\Documents\Materials\JHU\Projects\Anneal_Project\DTA")
spread_sheet_ar = "Argon DTA Results.xlsx"


#%% view original data and adjust
im = 11.469                                                                     # initial mass
run_data = get_dta_data(spread_sheet_ar,"AlZr_081722_Ar_022123_R1",im)          # get main data

#get the data to plot
run_data_df = run_data[0]
scan1 = run_data_df["Heatflow (mW)"]
baseline = run_data_df["Heatflow (mW).1"]

# plot data
fig, axes = plt.subplots(nrows=1,ncols=2)
axes[0].plot(run_data[1],scan1,lw=2,color=y,label="scan 1")
axes[0].plot(run_data[1],baseline,lw=2,color=r,label="baseline")
axes[0].plot(run_data[1],run_data[3],lw=2,color=b,label="bls hf")
axes[1].plot(run_data[1],run_data[3],lw=2,color=b,label="bls hf")

# adjust data and plot on same graph -- if you use the same variable name as the original run data it overwrites so just beware
run_data = perform_adjustment(run_data, 100, 200)
axes[0].plot(run_data[1],run_data[3],lw=2,color="black",label="adj bls hf")
axes[1].plot(run_data[1],run_data[3],lw=2,color="black",label="adj bls hf")

# Plotting parameters to make it look nice
axes[0].set_ylabel('Heatflow (mW)',fontsize=18)
axes[0].set_xlabel('Temperature (\u00B0C)',fontsize=18)
axes[0].tick_params(axis='both', which='major', labelsize=18,length=6)
axes[0].tick_params(axis='both', which='minor', labelsize=18)
axes[0].tick_params(axis="y", direction='in')
axes[0].tick_params(axis="x", direction='in')
axes[0].legend(frameon=False,prop={'size': 16})

# Plotting parameters to make it look nice
axes[1].set_ylabel('Heatflow (mW)',fontsize=18)
axes[1].set_xlabel('Temperature (\u00B0C)',fontsize=18)
axes[1].tick_params(axis='both', which='major', labelsize=18,length=6)
axes[1].tick_params(axis='both', which='minor', labelsize=18)
axes[1].tick_params(axis="y", direction='in')
axes[1].tick_params(axis="x", direction='in')
axes[1].legend(frameon=False,prop={'size': 16})

#%% Get intermetallic heat

lower_temp = 120
upper_temp = 600
chemstring = "Al1Zr1"
numatoms = 2

ax = plt.subplot(111)

# Plot data
plt.plot(run_data[1],run_data[3],lw=2,color=y)
plt.fill_between(run_data[1],run_data[3],color=y,where=(run_data[1] > lower_temp)&(run_data[1] < upper_temp),alpha=0.3)

# Plot parameters to make it look pretty
ax.set_ylabel('Heatflow (mW)',fontsize=18)
ax.set_xlabel('Temperature (\u00B0C)',fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=18,length=6)
ax.tick_params(axis='both', which='minor', labelsize=18)
ax.tick_params(axis="y", direction='in')
ax.tick_params(axis="x", direction='in')
plt.legend(frameon=False,prop={'size': 16})

# Get the intermetallic heat in J/g and kJ/mol
im_heat_J_g = get_intermetallic_heat(run_data, lower_temp, upper_temp, im)
im_heat_kJ_mol = convert_Jg_kJmol(im_heat_J_g,chemstring,numatoms)

# print out results
print("The intermetallic heat in J/g is: " + "{:.2f}".format(im_heat_J_g))
print("The intermetallic heat in kJ/mol is: " + "{:.2f}".format(im_heat_kJ_mol))





