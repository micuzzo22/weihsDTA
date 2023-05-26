# weihsDTA
A collection of functions that are used for DTA analysis in python

The functions in this repository are only meant to be used for analysis of DTA runs with the SDT Q600 in MD 11a.
You can adapt them to whatever you want, idrc about licensing.

I tried to include as much documentation in the functions themselves and I believe that the sample scripts give clear enough examples
where you can adapt the process flow to your data.

If you run into any issues or have features you'd like to add feel free to ask.

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

#### Formatting Data
- After running an initial scan and baseline scan, you can export the data into a text file
- I like to put the data scans for each run in one excel sheet (see excel file as an example)
- It is important to note the starting mass of the sample for each run, which I record under the “comment” section. The DTA mass balance is sometimes different than that of the microbalance even after taring

#### Data Extraction / Analysis


#### Heat of Oxidation
Here is a simple footnote[^1].

[^1]: [My reference](https://link.springer.com/article/10.1007/s10853-020-05031-5).





