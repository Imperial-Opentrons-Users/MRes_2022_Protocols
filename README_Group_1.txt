Hello! Welcome to the MegaTron (Group 1) Proximity Ligation Assay README
Authors: Diya Agrawal, Robin Blackwell, Daniel Boros, Henry Chippindale, Vincent Fideli

Project Title: Automated Proximity Ligation Assay using Opentrons

### About ###
The aim of this protocol is to use proximity ligation assay (PLA) to study the binding interactions between two proteins: A and B, by adding a series of drugs and studying the change in output signal.
The user has the option of choosing various parameters, such as the number of drugs, number of dilutions, and dilution factors.

The protocol is split into three parts: 
	1) reading and parsing through the input Excel (or csv) file, 
	2) setting up the plate: incubating proteins A and B with the combination of diluted drugs
	3) running the PLA: adding antibodies, washing steps

### Input ###
- Find the template input file 'test_input.xlsx'. There is a diagram showing the setup locations of the proteins and drugs.
- Pipette in the wells in order of the table (e.g. A2, B2, C2...).
- Fill in the concentration column in the table! This detects whether there are proteins or drugs present in that well.
- Fill in number of dilutions and dilution factor.
- This Excel file is this input to the python script.

### Output ###
- Running this script will yield a python script to be run on the Opentrons.
- Input a plate with the same wells as the submitted input Excel file, then run the Opentrons code.
- The overall output will be a plate with serially diluted drugs, with positive and negative controls, fully completed PLA, ready for fluorescence staining.

### Parameters to edit ###
- Number of drugs (min 1, max 23)
- Number of dilutions 
	if 1 <= number of drugs < 8, max 12 
	if number of drugs = 8, max 10
	if 8 < number of drugs <=15, max 6
	if 15 < number of drugs <= 23, max 4
- Dilution factor (choose between 1 in 2, 5 or 10)

### What cannot be changed? ###
- The starting dilution for each drug must be the maximum dilution (this will be diluted).

### Limitations and future directions ###
- For now, only one protein A can be run (future implementation of combinations between different As and drugs)
- Future tip management improvements with bespoke A+B combinations
- Variable dilution factors for different drugs
- Antibody concentrations to be optimised
- Wider range of dilution factors