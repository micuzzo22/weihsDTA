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
os.chdir(r"C:\Users\Mikey\Documents\Materials\JHU\Projects\Anneal_Project\DTA")
spread_sheet_ar = "Argon DTA Results.xlsx"
im = 11.469 # initial mass
run_data = get_dta_data(spread_sheet_ar,"AlZr_081722_Ar_022123_R1",im) # get main data
```

### Heat Data Adjustment
Before integrating to get the intermetallic heat we have to make sure the heat curves are properly adjusted.

Running the `get_dta_data` function will already give you normalized baseline subtracted heat flow, however, sometimes the curve still needs adjusting. Ideally, the curve should start at 0 W/g and end at 0 W/g assuming all reactions have fully completed. Looking at the graph below, you can see that the unadjusted curve starts below 0. To change this, we can use the `perform_adjustment` function which modifies the extracted data from `get_dta_data`

The `perform_adjustment` function requires the user to specify the lower and upper temperature bounds. You want to choose bounds around the region where there is a local minimum that can be adjusted. Don't do it below 50C since the DTA is full of artifacts early on. I normally choose around 120-250C. It's also possible that the curve needs to shift down, the `perform_adjustment` function will handle both cases.

### Intermetallic Heat
Now that the curve has been properly adjusted you can integrate to find the intermetallic heat. 

When comparing the intermetallic heats of different chemistry powders, you can use the molar heat by converting from J/g to kJ/mol by using the molar mass per atom. The `molar_mass_calculator.py` script easily allows you to find the molar mass per atom of a compound by running 

### Mass Gain Curve Adjustment
To calculate the heat 

### Heat of Oxidation
We can estimate the heat of oxidation by looking at the mass gain in an oxidizing environment like Ar+O2. We assume that for Al/Zr powders, ZrO2 will primarily be forming as the powder oxidizes (Wainwright 2020[^1]). All the mass gain shown by the DTA balance is due to oxygen being added. So for every 1 g of O2 added we can calculate how much ZrO2 is formed.

In Eliot's paper (Wainwright 2020[^1]), he cites a value of 263 kcal/mol for the formation of ZrO2 which is equal to 1100.392 kJ/mol (8.907 kJ/g)[^2]. By performing some dimensional analysis we see that for every 1 g of O2 added, 2.85 g of Zr is reacted (=3.85 total g). This gives us a value of 34.3 kJ/mol for every 1 g of O2 gained.

After performing the necessary adjustments to the data, we can calculate the heat of oxidation with the `get_heat_oxidation` function in the `dta_analysis_funcs` library.

### Heat of Nitridation

[^1]: https://link.springer.com/article/10.1007/s10853-020-05031-5.
[^2]: https://www.osti.gov/servlets/purl/372665 






