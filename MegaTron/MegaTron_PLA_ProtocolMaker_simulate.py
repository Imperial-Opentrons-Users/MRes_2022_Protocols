"""
Description:

MegaTron (Group 1) code for Proximity Ligation Assay. Will produce a 'Simulation' version of the protocol.

Authors: Diya Agrawal, Robin Blackwell, Daniel Boros, Henry Chippindale, Vincent Fideli
"""

import numpy as np
import pandas as pd
import sys
import math

# Change file name
# input_file = '//icnas1.cc.ic.ac.uk/rmb5017/Desktop/OpenTrons Hackathon/test_input.xlsx'
input_file = 'test_input.xlsx'


# Reading the file into a DataFrame and taking number of dilutions
# Dealing with different Excel types and csv
if input_file.endswith('.xlsx'):
    df = pd.read_excel(input_file, skiprows=14, engine='openpyxl').iloc[0:28,0:3]
    df_dil = pd.read_excel(input_file, skiprows=10).iloc[0:2,0:2]
elif input_file.endswith('.xls'):
    df = pd.read_excel(input_file, engine='xlrd', skiprows=14).iloc[0:28,0:3]
    df_dil = pd.read_excel(input_file, skiprows=10).iloc[0:2,0:2]
elif input_file.endswith('.csv'):
    df = pd.read_csv(input_file, engine='openpyxl', skiprows=14).iloc[0:28,0:3]
    df_dil = pd.read_csv(input_file, skiprows=10).iloc[0:2,0:2]


# Counts how many of protein A and drug candidates there are
no_A = sum(df['Concentrations (uM)'].iloc[0:3].notnull())
no_Drugs = sum(df['Concentrations (uM)'].iloc[4:27].notnull())

# DataFrames for wells of present A and Drug candidates
df_present = df.loc[df['Concentrations (uM)'].notnull()]

# Outputs wells of present protein A and Drug candidates
df_A = df_present[df_present['Type of species'] == 'Protein A']['Wells']
df_Drugs = df_present[df_present['Type of species'] == 'Drug candidate']['Wells']


### Dilutions
# How many dilutions? What is the dilution factor?
no_dilutions, dilution_factor = df_dil.iloc[0,1], df_dil.iloc[1,1]

# Validating number of wells and dilution factors
# Program stops if error here
if no_Drugs > 23:
    print("Number of drugs ({}) too high! Upper limit is 23.".format(no_Drugs))
elif np.logical_and(no_Drugs >= 16, no_Drugs <= 23):
    if no_dilutions > 4:
        sys.exit(f"The number of drugs is {no_Drugs}. The maximum number of dilutions is 4.")
elif np.logical_and(no_Drugs >= 9, no_Drugs <= 15):
    if no_dilutions > 6:
        sys.exit(f"The number of drugs is {no_Drugs}. The maximum number of dilutions is 6.")
elif no_Drugs == 8:
    if no_dilutions > 10:
        sys.exit(f"The number of drugs is {no_Drugs}. The maximum number of dilutions is 10.")
elif np.logical_and(no_Drugs >= 1 & no_Drugs <= 7):    
    if no_dilutions > 12:
        sys.exit(f"The number of drugs is {no_Drugs}. The maximum number of dilutions is 12.")
else:
    sys.exit("The number of drugs must be between 1 and 23 (inclusive).")

### Print output for user 
print(df)
print("""\
Number of protein A: {}
Number of drugs: {}          
Dilution factor: {}
Number of dilutions: {}
""".format(no_A, no_Drugs, dilution_factor, no_dilutions))

# Defining the metadata
a = {
    "apiLevel": "2.0",
    "protocolName": "PLA protocol",
    "description": "Protocol for automated PLA assays for PPI-disturbing drugs",
    "author": "Robin Blackwell, Diya Agrawal, Vincent Fideli, Henry Chippindale,  Daniel Boros"
    }


# Defining number of drug columns
no_drug_cols = math.floor(no_Drugs/8)
# Getting the drugs in and serially diluting them

# Choosing volume of diluent/drug to pipette into wells
if dilution_factor == 2:
    vol_diluent = 120
    vol_drug = 120
elif dilution_factor == 5:
    vol_diluent = 120
    vol_drug = 30

### Script to generate python output script for OpenTrons ###

def MakeFile(file_name):
    with open(file_name, 'w') as f:
        f.write(f'''\
from opentrons import simulate
metadata = {a}
protocol = simulate.get_protocol_api('2.0')

#define what goes in each position of opentrons layout. Add custom labware in labware file of .opentrons file location
tips_1 = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
tips_2 = protocol.load_labware("opentrons_96_tiprack_300ul", 4)
tips_3 = protocol.load_labware("opentrons_96_tiprack_300ul", 7)
reagent_reservoir = protocol.load_labware("4ti0131_12_reservoir_21000ul", 2)
wash_reservoir = protocol.load_labware("4ti0131_12_reservoir_21000ul", 5)
plate_origin = protocol.load_labware("costar3370flatbottomtransparent_96_wellplate_200ul", 3)
plate_target = protocol.load_labware("costar3370flatbottomtransparent_96_wellplate_200ul", 6)
plate_dilution = protocol.load_labware("costar3370flatbottomtransparent_96_wellplate_200ul", 9)
heatblock = protocol.load_module("tempdeck", 10)
cold_tubes = heatblock.load_labware("opentrons_24_aluminumblock_generic_2ml_screwcap", label="Cold_Rack")

#define pipette attachment
p300_multi = protocol.load_instrument("p300_multi_gen2", "left", tip_racks=[tips_2, tips_3])
p300_single = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips_1])

#set heatblock to 4 degrees to cool antibodies and enzymes
heatblock.set_temperature(4)

### Reagent slots #### 
PBS = reagent_reservoir["A1"]
PrimaryAbs = reagent_reservoir["A2"]
SecondaryAbs = reagent_reservoir["A3"]
LigationSolution = reagent_reservoir["A4"]
RCASolution = reagent_reservoir["A5"]
DAPI = reagent_reservoir["A6"]
protein_B = reagent_reservoir["A7"]
liquid_trash = reagent_reservoir["A12"]

cold_primaryAbs = cold_tubes["A1"]
cold_secondaryAbs = cold_tubes["A2"]
cold_ligationMix = cold_tubes["A3"]
cold_RCASolution = cold_tubes["A4"]

# Defining variables to refer to plates and rows
row = plate_target.rows()[0]
op_row = plate_target.rows()[0]
row_2 = plate_target.rows()
last_row = plate_target.rows()[7]
row_dilution = plate_dilution.rows()[0]



### Immobilizing Antibodies, Plating B, Serial Dilution of Drugs, and Plating A ###

##Custom liquid handling function for adding protein B and A to only the necessary wells
def fillup(no_Drugs, no_dilutions, no_drug_cols, species):   
    for i in range (0, no_dilutions * (no_drug_cols+1) ):   #loops through how many dilutions we want, and how many columns of drugs we have, and fills up the appropriate columns
        if (i < no_dilutions):          #first columns
            if no_Drugs < 8:            #if our first column of drugs is not full
                p300_single.pick_up_tip()
                for k in range(no_Drugs):
                    p300_single.distribute(30, species, row_2[k][i], new_tip="never")      
                for j in range(no_Drugs):
                    p300_single.consolidate(30,  row_2[j][i], liquid_trash, new_tip="never") 
                p300_single.drop_tip()                       
            else:               #if its full, we can do the full row - no need to mess about with single channel pipettes!
                p300_multi.pick_up_tip()
                p300_multi.transfer(30, species, row[i], new_tip="never")
                p300_multi.transfer(30, row[i], liquid_trash, new_tip="never")  
                p300_multi.drop_tip()                      
        elif (no_dilutions<=i< 2* no_dilutions): # same as before for second row
            if no_Drugs < 16:
                p300_single.pick_up_tip()
                for k in range(no_Drugs-8):
                    p300_single.distribute(30, species, plate_target.rows()[k][i], new_tip="never")
                for j in range(no_Drugs-8):
                    p300_single.consolidate(30,  row_2[j][i], liquid_trash, new_tip="never")
                p300_single.drop_tip()  
            else:
                p300_multi.pick_up_tip()
                p300_multi.transfer(30, species, row[i], new_tip="never")
                p300_multi.transfer(30, row[i], liquid_trash, new_tip="never")
                p300_multi.drop_tip()   
        else: # three rows are the maximum as we cant have 24
            p300_single.pick_up_tip()
            for k in range(no_Drugs-16):
                p300_single.distribute(30, species, row_2[k][i], new_tip="never")
            for j in range(no_Drugs-16):    
                p300_single.consolidate(30,  row_2[j][i], liquid_trash, new_tip="never")
            p300_single.drop_tip()  

#Checking to see if plating can be done with a multi channel == columns are full when no_Drugs % 8 == 0
if no_Drugs % 8 == 0:   
    p300_multi.pick_up_tip()
    p300_multi.transfer(30, PrimaryAbs, row[0:{no_dilutions}*{no_drug_cols}], new_tip="never")   #adding primary antibodies
    protocol.delay(minutes = 0.5)
    p300_multi.transfer(30, row[0:12], liquid_trash, new_tip="never")                        #removing primary antibodies
    p300_multi.drop_tip()
    p300_multi.pick_up_tip()
    p300_multi.transfer(30, protein_B, row[0:{no_dilutions}*{no_drug_cols}], new_tip="never")      #adding protein B
    protocol.delay(minutes = 0.5)
    p300_multi.transfer(30, row[0:12], liquid_trash, new_tip="never")                #removing liquid with B antibody
    p300_multi.drop_tip()
    p300_multi.pick_up_tip()
    p300_multi.transfer(30, protein_A, row[0:{no_dilutions}*{no_drug_cols}], new_tip="never") #adding A
    p300_multi.drop_tip()
else:
    fillup(no_Drugs, {no_dilutions}, {no_drug_cols}, PrimaryAbs)            #fills it up with primary Abs using functions
    protocol.delay(minutes = 0.5)
    fillup(no_Drugs, {no_dilutions}, {no_drug_cols}, protein_B)             #fills it up with B according to function
    protocol.delay(minutes = 0.5)
    
    p300_multi.pick_up_tip()
    for i in range (0, {no_dilutions} * ({no_drug_cols}+1) ):               # A cant use function, as we dont want liquid to be removed
        if (i < {no_dilutions}):
            if no_Drugs < 8:
                p300_single.pick_up_tip()
                for j in range(no_Drugs):
                    p300_single.distribute(30, protein_A, row_2[j][i], new_tip="never")
                p300_single.drop_tip()                                   
            else:
                p300_multi.transfer(30, protein_A, row[i], new_tip="never")                       
        elif ({no_dilutions}<=i< 2* {no_dilutions}):
            if no_Drugs < 16:
                p300_single.pick_up_tip()
                for k in range(no_Drugs-8):
                    p300_single.distribute(30, protein_A, row_2[k][i], new_tip="never")
                p300_single.drop_tip()    
            else:
                p300_multi.transfer(30, protein_A, row[i], new_tip="never")  
        else:
            p300_single.pick_up_tip()
            for j in range(no_Drugs-16):
                p300_single.distribute(30, protein_A, row_2[j][i], new_tip="never")
            p300_single.drop_tip()

#Plating positive and negative control
p300_single.distribute(30, PrimaryAbs,  [plate_target.wells_by_name()[well_name] for well_name in ['H11', 'H12']])   #adding primary antibodies
protocol.delay(minutes = 0.5)
p300_single.transfer(30,  [plate_target.wells_by_name()[well_name] for well_name in ['H11', 'H12']], liquid_trash)                        #removing primary antibodies
p300_single.transfer(30, protein_B,  [plate_target.wells_by_name()[well_name] for well_name in ['H11', 'H12']])      #adding protein B
protocol.delay(minutes = 0.5)
p300_single.transfer(30, [plate_target.wells_by_name()[well_name] for well_name in ['H11', 'H12']], liquid_trash)                #removing liquid with B antibody
p300_single.transfer(30, protein_A, plate_target.wells_by_name()["H11"]) #adding A


#Setting up the serial dilution for the drugs
for i in range (0,(1+{no_drug_cols})):   
    if (({no_Drugs} % 8) != 0): 
        p300_multi.pick_up_tip()
        p300_multi.transfer({vol_drug}, plate_origin["A" + str(2+i)], row_dilution[i*{no_Drugs}], new_tip = "never")  #get the drug into its first column, where it is diluted
        p300_multi.transfer({vol_drug}, row_dilution[(i*{no_Drugs}):({no_Drugs}-1)+i*{no_Drugs}], #complete serial dilutions on it \        
                            row_dilution[1+i*{no_Drugs}:({no_Drugs})+i*{no_Drugs}], mix_after=(3,50), \
                                touch_tip=True, new_tip="never")
        p300_multi.transfer({vol_drug}, row_dilution[({no_Drugs}-1)+i*{no_Drugs}], liquid_trash, blow_out = True, new_tip='never') # remove excess liquid from last row
        p300_multi.drop_tip() 
    elif (({no_Drugs} % 8) == 0 and i != {no_drug_cols}):
        p300_multi.pick_up_tip()                                                  #needs this, as if we have 8  or 16 we only do x-1 iteration of this, 8 is a special case, but works generally in the same way as above
        p300_multi.transfer({vol_drug}, plate_origin["A" + str(2+i)], row_dilution[i*{no_Drugs}], new_tip = "never")
        p300_multi.transfer({vol_drug}, row_dilution[i*{no_Drugs}:({no_Drugs}-1)+i*{no_Drugs}], \
                            row_dilution[1+i*{no_Drugs}:({no_Drugs})+i*{no_Drugs}], mix_after=(3,50), \
                                touch_tip=True, new_tip="never")
        p300_multi.transfer({vol_drug}, row_dilution[({no_Drugs}-1)+i*{no_Drugs}], liquid_trash, blow_out = True, new_tip='never')
        p300_multi.drop_tip() 



####### Proximity Ligation Assay Protocol #######

# Check is made for full rows if can use multi-channel or need to use single channel for incomplete rows
if {no_Drugs} == 23 or {no_Drugs} == 15 or {no_Drugs} == 8:
    useMulti = True
else:
    useMulti = False

#Check plate set-up - How many drug "blocks", the spacing of each block, and number of rows filled in the last block.
if {no_Drugs} > 15 and {no_Drugs} <= 23:
    blockIterations = 3
    lastBlockRows = 23 - {no_Drugs}
    spacing = {no_dilutions}
elif {no_Drugs} > 8 and {no_Drugs} <= 15:
    blockIterations = 2
    lastBlockRows = 15 - {no_Drugs}
    spacing = {no_dilutions}
elif {no_Drugs} <= 8:
    blockIterations = 1
    lastBlockRows = {no_Drugs}
    spacing = 0
else:
    protocol.pause("AMOUNT OF DRUGS EXCEEDS MAXIMUM OF 23!")



### Custom Liquid handling operations

## Liquid dilution from cold block to reservoir
# takes arguments volume (ul), the source eppendorf on the temperature module, destination well
def dilute_antibodies(volume, source_well, destination_well):
    p300_single.pick_up_tip()
    p300_single.transfer(volume, source_well, destination_well, new_tip="never")
    p300_single.drop_tip()
    p300_multi.pick_up_tip()
    p300_multi.mix(3, 200, destination_well)
    p300_multi.return_tip()


## Liquid transfer from reservoir to plate
# takes arguments volume (ul), and source reservoir well
def liquid_add(volume, source_well):
    #With full column, use multi-channel and iterate over columns in each "block" for number of drug dilutions
    if useMulti == True:
        p300_multi.pick_up_tip()
        for i in range(blockIterations):
            p300_multi.transfer(volume, source_well, op_row[(i*spacing):((i*spacing)+{no_dilutions})], new_tip="never")
        p300_multi.return_tip()
        #Checking if multichannel pipetting overlapped onto control wells
        if {no_Drugs} == 23 and {no_dilutions} < 4:
            fillControls = True
        elif {no_Drugs} == 15 and {no_dilutions} < 6:
            fillControls = True
        elif {no_Drugs} == 8:
            fillControls = True
        else:
            fillControls = False
        #Fill control wells if fillControls is True    
        if fillControls == True:
            p300_single.pick_up_tip()
            p300_single.transfer(volume, source_well, last_row[10:12], new_tip="never")
            p300_single.return_tip()

    #If not all columns filled are full, break liquid handling in multi-channel step and single-channel step
    else: 
        #For less than 8 drugs, no columns are full, so use single-channel pipette
        if {no_Drugs} <= 8:
            p300_single.pick_up_tip()
            for j in range({no_Drugs}):
                single_row = plate_target.rows()[j]
                p300_single.transfer(volume, source_well, single_row[0:{no_dilutions}], new_tip="never")
            p300_single.transfer(volume, source_well, last_row[10:12], new_tip="never")
            p300_single.return_tip()
        #For more than 8 drugs, full "blocks" will have full columns, so use multi-channel for those and single-channel for last block
        elif {no_Drugs} > 8:
            #Full block uses multi-channel
            p300_multi.pick_up_tip()
            for k in range((blockIterations-1)):
                p300_multi.transfer(volume, source_well, op_row[(k*spacing):((k*spacing)+{no_dilutions})], new_tip="never")
            p300_multi.return_tip()
            #Last block uses single-channel
            p300_single.pick_up_tip()
            for l in range(lastBlockRows):
                single_row = plate_target.rows()[l]
                p300_single.transfer(volume, source_well, single_row[((blockIterations-1)*spacing):(((blockIterations-1)*spacing)+{no_dilutions})], new_tip="never")
            p300_single.transfer(volume, source_well, last_row[10:12], new_tip="never")
            p300_single.return_tip()


## Mixing and discarding function
# takes arguments volume to discard, and destination well for waste.            
def mix_discard(volume, waste_destination):
    #Similar to liquid_add function, use multi-channel if all columns filled are full
    if useMulti == True:
        p300_multi.pick_up_tip()
        for m in range(blockIterations):
            for n in range({no_dilutions}):
                p300_multi.mix(3, 50, op_row[((m*spacing)+n)])
                p300_multi.aspirate(volume, op_row[((m*spacing)+n)].bottom(0.8))
                p300_multi.dispense(volume, waste_destination.top(0)) #Dispensing above reservoir so as not to contaminate tip
                p300_multi.blow_out()
        p300_multi.drop_tip()
        #Check if multi-channel pipetting overlapped with control wells
        if {no_Drugs} == 23 and {no_dilutions} < 4:
            discardControls = True
        elif {no_Drugs} == 15 and {no_dilutions} < 6:
            discardControls = True
        elif {no_Drugs} == 8:
            discardControls = True
        else:
            discardControls = False
        #Discard control wells if discardControls is True
        if discardControls == True:
            p300_single.pick_up_tip()
            p300_single.transfer(volume, last_row[11].bottom(0.8), waste_destination.top(0), mix_before=(3, 50), blow_out=True, new_tip="never")
            p300_single.transfer(volume, last_row[10].bottom(0.8), waste_destination.top(0), mix_before=(3, 50), blow_out=True, new_tip="never") 
            p300_single.drop_tip()                       
    
    #Not all columns are full, so liquid handling is broken up into multi-channel step and single-channel step
    else:
        #For less than 8 drugs, no columns are full, so use single-channel pipette
        if {no_Drugs} <= 8:
            #Picking up negative control before positive control to avoid contaminating the former with the latter
            p300_single.pick_up_tip()
            p300_single.transfer(volume, last_row[11].bottom(0.8), waste_destination.top(0), mix_before=(3, 50), blow_out=True, new_tip="never")
            p300_single.transfer(volume, last_row[10].bottom(0.8), waste_destination.top(0), mix_before=(3, 50), blow_out=True, new_tip="never") 
            p300_single.drop_tip()
            for o in range({no_Drugs}):
                single_row = plate_target.rows()[o] 
                p300_single.pick_up_tip()
                for p in range({no_dilutions}):
                    p300_single.mix(3, 50, single_row[({no_dilutions}-(p+1))])
                    p300_single.aspirate(volume, single_row[({no_dilutions}-(p+1))].bottom(0.8))
                    p300_single.dispense(volume, waste_destination.top(0))
                    p300_single.blow_out()
                p300_single.drop_tip()
        #For more than 8 drugs, full "blocks" will have full columns, so use multi-channel for those and single-channel for last block
        elif {no_Drugs} > 8:
            p300_single.pick_up_tip()
            p300_single.transfer(volume, last_row[11], waste_destination.top(0), mix_before=(3, 50), blow_out=True, new_tip="never")
            p300_single.transfer(volume, last_row[10], waste_destination.top(0), mix_before=(3, 50), blow_out=True, new_tip="never") 
            p300_single.drop_tip()
            p300_multi.pick_up_tip()
            for q in range(blockIterations-1):
                for r in range({no_dilutions}):
                    p300_multi.mix(3, 50, op_row[((q*spacing)+({no_dilutions}-(r+1)))])
                    p300_multi.aspirate(volume, op_row[((q*spacing)+({no_dilutions}-(r+1)))].bottom(0.8))
                    p300_multi.dispense(volume, waste_destination.top(0))
                    p300_multi.blow_out()
            p300_multi.drop_tip()
            for s in range(lastBlockRows):
                single_row = plate_target.rows()[s]
                p300_single.pick_up_tip()
                for t in range({no_dilutions}):
                    p300_single.mix(3, 50, single_row[((blockIterations-1)*spacing+({no_dilutions}-(t+1)))])
                    p300_single.aspirate(volume, single_row[((blockIterations-1)*spacing+({no_dilutions}-(t+1)))].bottom(0.8))
                    p300_single.dispense(volume, waste_destination.top(0))
                    p300_single.blow_out()
                p300_single.drop_tip()                                          



## Execute PLA Protocol with custom liquid handling functions

#Bind Primary antibodies
protocol.comment("Diluting primary antibodies")
dilute_antibodies(100, cold_primaryAbs, wash_reservoir["A1"])
protocol.comment("Adding primary antibodies to wells")
liquid_add(100, wash_reservoir["A1"])

#Incubate for 1h
protocol.comment("Incubating primary antibodies")
#protocol.delay(minutes = 60)

#Draw off liquid and wash with buffer
protocol.comment("Drawing off primary antibody mix and washing wells")
mix_discard(100, wash_reservoir["A1"])
liquid_add(100, wash_reservoir["A2"])
mix_discard(100, wash_reservoir["A2"])

#Bind Secondary antibodies
protocol.comment("Diluting secondary antibodies")
dilute_antibodies(100, cold_secondaryAbs, wash_reservoir["A3"])
protocol.comment("Adding secondary antibody to wells")
liquid_add(100, wash_reservoir["A3"])

#Incubate for 1h
protocol.comment("Incubating secondary antibodies")
#protocol.delay(minutes = 60)

#Draw off liquid and wash with buffer
protocol.comment("Drawing off primary antibody mix and washing wells")
mix_discard(100, wash_reservoir["A3"])
liquid_add(100, wash_reservoir["A4"])
mix_discard(100, wash_reservoir["A4"])

#Ligate PLA probes
protocol.comment("Ligating PLA PLUS and MINUS probes")
dilute_antibodies(100, cold_ligationMix, wash_reservoir["A5"])
liquid_add(100, wash_reservoir["A5"])

#Incubate 5min
protocol.comment("5 min Ligation")
#protocol.delay(minutes=5)

#Drawing off ligation mix
protocol.comment("Drawing off ligation mix")
mix_discard(100, wash_reservoir["A5"])

#RCA Reaction
protocol.comment("Diluting RCA reagents")
dilute_antibodies(100, cold_RCASolution, wash_reservoir["A6"])
protocol.comment("Adding RCA reagents to wells")
liquid_add(100, wash_reservoir["A6"])

#Incubate 2h
protocol.comment("RCA Reaction taking place - 2h")
#protocol.delay(minutes=120)

#DAPI stain
protocol.comment("Staining amplified DNA with DAPI")
liquid_add(100, DAPI)
#protocol.delay(minutes=5)
protocol.comment("Washing excess DAPI stain and resuspending in buffer")
mix_discard(200, wash_reservoir["A6"])
liquid_add(100, wash_reservoir["A7"])
mix_discard(100, wash_reservoir["A7"])
liquid_add(100, wash_reservoir["A8"])
protocol.comment("Protocol is complete!")
''')


MakeFile("PLA_automation_protocol_simulate.py")