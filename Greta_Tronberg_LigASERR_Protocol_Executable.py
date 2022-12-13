#!/usr/bin/env python
# coding: utf-8

# ## Opentrons - LigASERR protocol
# ---

# In[ ]:


from opentrons import protocol_api

metadata = {'apiLevel': '2.13'}

def run(protocol: protocol_api.ProtocolContext):

    # Labware
    mag_mod = protocol.load_module('Magnetic Module', 1)
    mag_plate = mag_mod.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul')
    plate = protocol.load_labware('costar3370flatbottomtransparent_96_wellplate_200ul', 2)
    tips_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 4)
    tips_2 = protocol.load_labware('opentrons_96_tiprack_300ul', 5)
    reservoir_1 = protocol.load_labware('4ti0131_12_reservoir_21000ul', 6)
    thermocycler = protocol.load_module('thermocycler')
    thermocycler_plate = thermocycler.load_labware('4ti0960rig_96_wellplate_200ul')
    reservoir_2 = protocol.load_labware('4ti0131_12_reservoir_21000ul', 9)

    # Pipettes
    p300 = protocol.load_instrument('p300_multi_gen2', 'left', tip_racks = [tips_1, tips_2])
    
    # TRT reaction
    thermocycler.open_lid()
    thermocycler.set_block_temperature(25)

    thermocycler_top_row = thermocycler_plate.rows()[0]
    p300.transfer(80, reservoir_1['A1'], thermocycler_top_row[0], mix_before = (3, 80), blow_out = True, blowout_location = 'destination well', new_tip = 'once')

    p300.pick_up_tip()
    p300.transfer(80, reservoir_1['A2'], thermocycler_top_row[0], mix_before = (3, 80), mix_after = (3, 80), blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.return_tip()

    thermocycler.close_lid()

    thermocycler.set_lid_temperature(70)
    thermocycler.set_block_temperature(37, hold_time_minutes = 30)
    thermocycler.set_block_temperature(65, hold_time_minutes = 20)
    thermocycler.set_block_temperature(25)
    thermocycler.deactivate_lid()
    thermocycler.open_lid()

    plate_top_row = plate.rows()[0]
    p300.pick_up_tip(tips_1['A2'])
    p300.transfer(70, thermocycler_top_row[0], plate_top_row[0], mix_before = (3, 70), blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.drop_tip()

    # Purification of cDNA with SPRI beads
    thermocycler.open_lid()
    thermocycler.set_block_temperature(25)

    p300.pick_up_tip()
    p300.transfer(126, reservoir_1['A3'], plate_top_row[0], mix_before = (3, 126), mix_after = (10, 126), blow_out = True, blowout_location = 'destination well', new_tip = 'never')

    protocol.delay(minutes = 5)

    mag_top_row = mag_plate.rows()[0]
    p300.transfer(150, plate_top_row[0], mag_top_row[0], mix_before = (3, 150), blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.drop_tip()

    mag_mod.engage(height = 11.9)

    protocol.delay(minutes = 2)

    p300.transfer(130, mag_top_row[0], reservoir_2['A12'], new_tip = 'once')

    p300.pick_up_tip()
    p300.transfer(180, reservoir_1['A4'], mag_top_row[0], mix_before = (3, 180), air_gap = 10, blow_out = True, blowout_location = 'destination well', new_tip = 'never')

    protocol.delay(seconds = 30)

    p300.transfer(180, mag_top_row[0], reservoir_2['A12'], air_gap = 10, new_tip = 'never')
    p300.drop_tip()

    p300.pick_up_tip()
    p300.transfer(180, reservoir_1['A4'], mag_top_row[0], mix_before = (3, 180), air_gap = 10, blow_out = True, blowout_location = 'destination well', new_tip = 'never')

    protocol.delay(seconds = 30)

    p300.transfer(180, mag_top_row[0], reservoir_2['A12'], air_gap = 10, new_tip = 'never')
    p300.drop_tip()

    mag_mod.disengage()

    p300.pick_up_tip()
    p300.transfer(180, reservoir_1['A5'], mag_top_row[0], mix_before = (3, 180), mix_after = (10, 180), new_tip = 'never')
    p300.transfer(180, mag_top_row[0], plate_top_row[1], blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.return_tip()

    protocol.delay(minutes = 2)

    p300.pick_up_tip(tips_1['A7'])
    p300.transfer(150, plate_top_row[1], mag_top_row[1], mix_before = (10, 150), blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.drop_tip()

    mag_mod.engage(height = 11.9)

    protocol.delay(minutes = 1)

    p300.transfer(100, mag_top_row[1], thermocycler_top_row[1], blow_out = True, blowout_location = 'destination well', new_tip = 'once')

    mag_mod.disengage()

    # RNA digestion
    thermocycler.open_lid()
    thermocycler.set_block_temperature(25)

    p300.pick_up_tip()
    p300.transfer(50, reservoir_1['A6'], thermocycler_top_row[1], mix_before = (3, 50), mix_after = (3, 50), blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.return_tip()

    thermocycler.close_lid()

    thermocycler.set_lid_temperature(70)
    thermocycler.set_block_temperature(37, hold_time_minutes = 30)
    thermocycler.deactivate_lid()
    thermocycler.set_block_temperature(4)
    thermocycler.open_lid()

    p300.pick_up_tip(tips_1['A9'])
    p300.transfer(55, thermocycler_top_row[1], thermocycler_top_row[2], blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.drop_tip()

    p300.home()

    protocol.set_rail_lights(True)

    protocol.pause('Please add Ligase Reaction Mix to Reservoir-1 A7, and NEB Taq DNA ligase to Reservoir-1 A8.')

    # Annealing and Ligation Reaction for cDNA
    thermocycler.open_lid()

    protocol.set_rail_lights(False)

    thermocycler.set_block_temperature(4)

    p300.transfer(25, reservoir_1['A7'], thermocycler_top_row[2], mix_before = (3, 25), mix_after = (3, 25), blow_out = True, blowout_location = 'destination well', new_tip = 'once')

    p300.pick_up_tip()
    p300.transfer(20, reservoir_1['A8'], thermocycler_top_row[2], mix_before = (3, 20), mix_after = (3, 20), new_tip = 'never')
    p300.transfer(90, thermocycler_top_row[2], thermocycler_top_row[3], blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.drop_tip()

    thermocycler.close_lid()

    thermocycler.set_lid_temperature(70)
    thermocycler.set_block_temperature(51.7, hold_time_minutes = 30)    # for full-length cDNA (or 46.4C for cleaved cDNA)
    thermocycler.set_block_temperature(25)
    thermocycler.deactivate_lid()
    thermocycler.open_lid()

    p300.pick_up_tip()
    p300.transfer(30, reservoir_1['A9'], thermocycler_top_row[3], mix_before = (3, 30), mix_after = (3, 30), new_tip = 'never')
    p300.transfer(100, thermocycler_top_row[3], plate_top_row[2], blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.drop_tip()

    # Purification of cDNA with Dynabeads
    p300.transfer(50, reservoir_1['A10'], mag_top_row[2], mix_before = (3, 50), blow_out = True, blowout_location = 'destination well', new_tip = 'once')

    for i in range(2):
        p300.pick_up_tip()
        p300.transfer(150, reservoir_1['A11'], mag_top_row[2], mix_before = (3, 150), mix_after = (3, 150), blow_out = True, blowout_location = 'destination well', new_tip = 'never')

        mag_mod.engage(height = 11.9)

        protocol.delay(minutes = 2)

        p300.transfer(150, mag_top_row[2], reservoir_2['A12'], new_tip = 'never')
        p300.drop_tip()

        mag_mod.disengage()

    p300.pick_up_tip()
    p300.transfer(150, reservoir_1['A12'], mag_top_row[2], mix_before = (3, 150), mix_after = (3, 150), blow_out = True, blowout_location = 'destination well', new_tip = 'never')

    mag_mod.engage(height = 11.9)

    protocol.delay(minutes = 2)

    p300.transfer(150, mag_top_row[2], reservoir_2['A12'], new_tip = 'never')
    p300.drop_tip()

    mag_mod.disengage()

    p300.pick_up_tip()
    p300.transfer(150, reservoir_1['A12'], mag_top_row[2], mix_before = (3, 150), mix_after = (10, 150), new_tip = 'never')
    p300.transfer(100, mag_top_row[2], plate_top_row[2], mix_after = (3, 100), blow_out = True, blowout_location = 'destination well', new_tip = 'never')

    for i in range(10):
        protocol.delay(seconds = 75)

        p300.mix(10, 100, plate_top_row[2])
        p300.blow_out(plate_top_row[2])

    p300.transfer(150, plate_top_row[2], mag_top_row[3], mix_before = (10, 150), blow_out = True, blowout_location = 'destination well', new_tip = 'never')

    mag_mod.engage(height = 11.9)

    protocol.delay(minutes = 3)

    p300.transfer(130, mag_top_row[3], reservoir_2['A12'], new_tip = 'never')
    p300.drop_tip()

    for i in range(2):
        p300.pick_up_tip()
        p300.transfer(180, reservoir_1['A11'], mag_top_row[3], mix_before = (3, 180), blow_out = True, blowout_location = 'destination well', new_tip = 'never')

        protocol.delay(seconds = 30)

        p300.transfer(180, mag_top_row[3], reservoir_2['A12'], new_tip = 'never')
        p300.drop_tip()

    p300.pick_up_tip()
    p300.transfer(180, reservoir_1['A11'], mag_top_row[3], mix_before = (3, 180), blow_out = True, blowout_location = 'destination well', new_tip = 'never')

    protocol.delay(seconds = 30)

    p300.transfer(200, mag_top_row[3], reservoir_2['A12'], new_tip = 'never')
    p300.drop_tip()

    mag_mod.disengage()

    p300.pick_up_tip()
    p300.transfer(200, reservoir_2['A1'], mag_top_row[3], mix_before = (3, 200), mix_after = (10, 150), new_tip = 'never')
    p300.transfer(150, mag_top_row[3], thermocycler_top_row[4], blow_out = True, blowout_location = 'destination well', new_tip = 'never')
    p300.drop_tip()

