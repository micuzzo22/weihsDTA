# weihsDTA
A collection of functions that are used for DTA analysis in python

The functions in this repository are only meant to be used for analysis of DTA runs with the SDT Q600 in MD 11a.
You can adapt them to whatever you want. I tried to include as much documentation in the functions themselves and I believe that the 
sample scripts give clear enough examples where you can adapt the process flow to your data. If you run into any issues or have features 
you'd like to add feel free to ask.

- Michael

## How to Use 
1) Make sure your libraries / modules are up to date with the latest versions.
2) The following files must be in the python path in order for you to use the functions:
      a. molar_mass_calculator.py
      b. dta_analysis_funcs.py
      c. dta_mass_gain_funcs.py
      
3) Place the text from the output .txt that TA analysis gives into an appropriately filled out excel file. See the format
  of the example file.
4) Perform analysis

## DTA Analysis 

### Formatting Data
- After running an initial scan and baseline scan, you can export the data into a text file
- Place the text from the output .txt that TA analysis gives into an appropriately filled out excel file. See the format
  of the example file.
- It is important to note the starting mass of the sample for each run, which I record under the “comment” section when running the DTA. 
  The DTA mass balance is sometimes different than that of the microbalance even after taring.
- Once the data is put into a properly formatted excel sheet you can begin analyzing.

### Data Extraction / Analysis
- The main function that gets and manipulates the data gathered from the excel sheet is `get_dta_data`. This function takes in the filenames of the excel document and sheet as well as the initial mass of the sample. Look at the details of the function to see what the list it outputs contains.

```python
# Example
os.chdir(r"C:\Users\Mikey\Documents\Materials\JHU\Projects\Anneal_Project\DTA")
spread_sheet_ar = "Argon DTA Results.xlsx"
sheetname = "AlZr_081722_Ar_022123_R1"
im = 11.469 # initial mass
run_data = get_dta_data(spread_sheet_ar,sheetname,im) # get main data
```

### Heat Curve Data Adjustment
Before integrating to get the intermetallic heat we have to make sure the heat curves are properly adjusted.

Running the `get_dta_data` function will already give you normalized baseline subtracted heat flow, however, sometimes the curve still needs adjusting. Ideally, the curve should start at 0 W/g and end at 0 W/g assuming all reactions have fully completed. Looking at the graph below, you can see that the unadjusted curve starts below 0. To change this, we can use the `perform_adjustment` function which modifies the extracted data from `get_dta_data`
```python
run_data = perform_adjustment(run_data, 100, 200)
```
![dta-baseline-scan1-blshf-adj](https://github.com/micuzzo22/weihsDTA/assets/114498532/688484e9-5cba-4000-9568-4945310a8b93)

The `perform_adjustment` function requires the user to specify the lower and upper temperature bounds. You want to choose bounds around the region where there is a local minimum that can be adjusted. Don't do it below 50C since the DTA is full of artifacts early on. I normally choose around 120-250C. It's also possible that the curve needs to shift down, the `perform_adjustment` function will handle both cases.

### Intermetallic Heat
Now that the curve has been properly adjusted you can integrate to find the intermetallic heat. 

When comparing the intermetallic heats of different chemistry powders, you will get the molar heat by converting from J/g to kJ/mol by using the molar mass per atom. The `molar_mass_calculator.py` script easily allows you to find the molar mass of a compound with the `get_molar_mass` function. This function has a particular syntax it expects. Use the empirical formula of the compound as a string in the form "XmYn" where X and Y are the chemical symbols and m and n are integers. It can handle all multi element compounds. 

```python
# Get the intermetallic heat in J/g and kJ/mol
im_heat_J_g = get_intermetallic_heat(run_data, lower_temp, upper_temp, im)
im_heat_kJ_mol = convert_Jg_kJmol(im_heat_J_g,chemstring,numatoms)

# print out results
print("The intermetallic heat in J/g is: " + "{:.2f}".format(im_heat_J_g))
print("The intermetallic heat in kJ/mol is: " + "{:.2f}".format(im_heat_kJ_mol))
```

### Mass Gain Curve Adjustment
To calculate the heat of oxidation or nitridation we use the mass gain. The DTA often shows an initial fast rise and then dip in the mass gain curve, which should not happen. We therefore adjust the mass gain curve to 0 while the slope is negative and use the mass at the inflection point for calculating mass gain. The functions that are used to modify the mass gain curve for a trial run are in `dta_mass_gain_funcs.py`. 

```python
run_data_mg_avg, run_data_mg_stdev = get_mg_percentage_avg_stdev(run_data_list,initial_masses_list)
initial_idx, temp = get_start_mass_gain(avg_mass_change,aro2_run_data,cutoff_temp,threshold=1e-4,smooth_value=51,plot=False)
run_mg_avg_adj = adjust_avg_mass_gain(run_mg_avg,mg_start_idx)
aro2_run_data = modify_run_mass_diff(aro2_run_data,mg_start_idx,im)
```

The method I use follows these steps:
1. For one run, or multiple runs, find the average percentage mass gain at each temperature
2. Using the averaged data, create a smoothed curve that approximates the average, and find the difference in mass gain between the current and previous mass. Then a threshold value is used to determine when the difference exceeds an appropriate value of mass gain difference. Temperatures below the cutoff temperature are not considered. Find the index and temperature where this occurs.
3. Adjust the average mass gain. The new initial mass is the mass at the thresholded point and that part of the curve is shifted to 0. 

### Heat of Oxidation
We can estimate the heat of oxidation by looking at the mass gain in an oxidizing environment like Ar+O2. We assume that for Al/Zr powders, ZrO2 will primarily be forming as the powder oxidizes (Wainwright 2020[^1]). All the mass gain shown by the DTA balance is due to oxygen being added. So for every 1 g of O2 added we can calculate how much ZrO2 is formed.

In Eliot's paper (Wainwright 2020[^1]), he cites a value of 263 kcal/mol for the formation of ZrO2 which is equal to 1100.392 kJ/mol (8.907 kJ/g)[^2]. By performing some dimensional analysis we see that for every 1 g of O2 added, 2.85 g of Zr is reacted (=3.85 total g). This gives us a value of 34.3 kJ/mol for every 1 g of O2 gained.

After performing the necessary adjustments to the data, we can calculate the heat of oxidation with the `get_heat_oxidation` function in the `dta_analysis_funcs` library.

### Heat of Nitridation


### Cumulative & Incremental Heat Release

[^1]: https://link.springer.com/article/10.1007/s10853-020-05031-5.
[^2]: https://www.osti.gov/servlets/purl/372665 






