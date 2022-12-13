# sets the version of Opentrons API to be used
from opentrons import protocol_api
metadata = {'apiLevel':'2.8'}

## SETS VARIABLES IN PIPETTING TECHNIQUE ##
# style, can be 'normal' or 'reverse'
style = 'normal'

# blow out from tip? can be True or False
blow = False

# use pre-wetting? can be any integer
prewet = 1

# use an air gap? can be True or False
air_gap = False

# dispense/aspirate speed, can be 'slow' or 'fast'
speed = 'fast'

# mix during serial dilution? can be True or False
mixing = True

# tip touching? can be True or False
touch = True

# what column are the first tips in?
ini_tip_col = 1

tip1 = 'A'+str(ini_tip_col)
tip2 = 'A'+str(ini_tip_col + 1)
tip3 = 'A'+str(ini_tip_col + 2)

# runs the protocol
def run(protocol: protocol_api.ProtocolContext):    
    
    # Identifies labware type and locations
    tips = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    reservoir = protocol.load_labware('4ti0131_12_reservoir_21000ul', 2)
    cell_plate = protocol.load_labware('4ti0960rig_96_wellplate_200ul', 3)
    drug_plate = protocol.load_labware('4ti0960rig_96_wellplate_200ul', 6)
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks = [tips])
    
    # Identifies the location of the three solutions
    medium = reservoir['A1']
    cells = reservoir['A2']
    drug = reservoir['A3']
    
# FUNCTIONS TO IMPLEMENT VARIABLES
    # pre-wetting
    if (prewet == 0):
        def pre_wet():
            pass
    elif (prewet > 0):
        def pre_wet():
            p300.mix(prewet, volume, source)
            
    # speed
    if (speed == 'slow'):
        p300.speed.aspirate = 5
        p300.speed.dispense = 5
    elif (speed == 'fast'):
        p300.speed.aspirate = 20
        p300.speed.dispense = 20
    
    # tip touch is automatically done in the commands by setting: touch_tip = touch (boolean set earlier)
    
    # blowing out is automatically done in the commands by setting: blow_out = blow (boolean set earlier)
    
    # gives volume an arbitrary value so referencing it in the mix if clause doesn't give a error
    volume = 100
    # mixing
    if (mixing == True):
        mix = (3, volume / 2)
    elif (mixing == False):
        mix = (0, 0)
        
    # air gap
    if (air_gap == True):
        air = 5
    elif (air_gap == False):
        air = 0
      
    ## SEEDING CELLS ###
    # identifies source location and volume to be used
    source = cells; volume = 100
    p300.pick_up_tip(tips[tip1])
    pre_wet()
    p300.well_bottom_clearance.dispense = 10
    
    if (style == 'normal'):
        p300.transfer(volume, source, [cell_plate.columns_by_name()[col_name]
                                       for col_name in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']],
                      new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = blow, blowout_location = 'destination well')
        p300.transfer(200, source, cell_plate.columns_by_name()['12'],
                     new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = blow, blowout_location = 'destination well')
        
    elif (style == 'reverse'):
        p300.distribute(volume, source, [cell_plate.columns_by_name()[col_name]
                                         for col_name in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']],
                        new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = True, blowout_location = 'source well')
        p300.distribute(200, source, cell_plate.columns_by_name()['12'],
                     new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = True, blowout_location = 'source well')
    
    p300.drop_tip()
        
    ## PREPARING DRUG DILUTION PLATE ##

    # adding medium to columns 2-12
    volume = 130; source = medium
    p300.pick_up_tip(tips[tip2])     
    pre_wet()
    p300.well_bottom_clearance.dispense = 10
    
    if (style == 'normal'):
        p300.transfer(volume, source, [drug_plate.columns_by_name()[col_name]
                                         for col_name in ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11']],
                      new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = blow, blowout_location = 'destination well')
    
    elif (style == 'reverse'):
        volume = 140
        p300.distribute(volume, source, [drug_plate.columns_by_name()[col_name]
                                         for col_name in ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11']],
                      new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = True, blowout_location = 'source well')
    p300.drop_tip()

    # adding drug to column 1
    volume = 250; source = drug; destination = drug_plate.columns_by_name()['1']
    p300.pick_up_tip(tips[tip3])
    pre_wet()
    p300.well_bottom_clearance.dispense = 10
    
    if (style == 'normal'):
        p300.transfer(volume, source, destination,
                      new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = blow, blowout_location = 'destination well')
    elif (style == 'reverse'):
        volume = 270
        p300.distribute(volume, source, destination,
                      new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = True, blowout_location = 'source well')

    ## PERFORMING SERIAL DILUTION
    drug_row = drug_plate.rows()[0]
    volume = 130; source = drug_row[:10]; destination = drug_row[1:11]
    p300.well_bottom_clearance.dispense = 10
    p300.well_bottom_clearance.aspirate = 3
    
    if (style == 'normal'):
        p300.transfer(volume, source, destination,
                      mix_after = mix, new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = blow, blowout_location = 'destination well')
    
    elif (style == 'reverse'):
        def reverse(x):
            p300.distribute(volume, source[x], destination[x], mix_after = mix, new_tip = 'never', touch_tip = touch,
                            air_gap = air, blow_out = True, blowout_location = 'source well')
        for i in range(10):
            reverse(i)
            if (mixing == True):
                p300.mix(3, 120, destination[i])

    ## TRANSFERING TO CELL PLATE ##
    cell_row = cell_plate.rows()[0] 
    source = drug_row[10]; pre_wet()
    volume = 100; source = drug_row[10::-1]; destination = cell_row[10::-1]  #move from A11 to A1, direction is -1
    p300.well_bottom_clearance.dispense = 10
    p300.well_bottom_clearance.aspirate = 3
    
    if (style == 'normal'):
        p300.transfer(volume, source, destination,
                      mix_after = mix, new_tip = 'never', touch_tip = touch, air_gap = air, blow_out = blow, blowout_location = 'destination well')
    
    elif (style == 'reverse'):
        for i in range(11):
            reverse(i)
            if (mixing == True):
                p300.mix(3, 100, destination[i])