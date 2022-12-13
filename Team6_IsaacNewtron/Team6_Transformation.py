import opentrons
import opentrons.execute
from opentrons import protocol_api


metadata = {'apiLevel': '2.7'}
def run(protocol: protocol_api.ProtocolContext):

  protocol = simulate.get_protocol_api('2.7')
  plate = protocol.load_labware('nest_96_wellplate_200ul_flat', 1)
  tc_mod = protocol.load_module('Thermocycler Module')
  plate2 = tc_mod.load_labware('nest_96_wellplate_200ul_flat')
  tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)
  p300 = protocol.load_instrument('p300_single_gen2', 'left',
  tip_racks=[tiprack_1])
  reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 3)
  p300.pick_up_tip()
  tot = 0
  # Calculation of amount to be dispensed each time.
  # n1 is a multiple of dispensed amount * total wells therefore equals total volume required
  n1 = 25*64
  for i in range(1, n1+1):
    if n1%i == 0 and i <= 300 and i%25 == 0:
      totvol = i

  tot = 0
  for j in range(1,9):
    for i in range(1,9):
      if tot == 0:
        p300.aspirate(totvol, reservoir['A7'])
        tot = totvol
      p300.dispense(25, plate2[(chr(ord('@')+j)+str(i))])
      tot -= 25
  if tot != 0:
    p300.dispense(tot, reservoir['A7'])
  p300.drop_tip()  
  p300.pick_up_tip()

  for i in range(8):
    row = plate.rows()[i]
    rowdest = plate2.rows()[i]
    p300.transfer(25, row[0:8], rowdest[0:8], new_tip='never',blow_out=True)
    p300.blow_out()
  p300.drop_tip()  

  tc_mod.close_lid() 

  tc_mod.set_block_temperature(4, hold_time_minutes=30)
  tc_mod.set_block_temperature(42, hold_time_minutes=.75)
  tc_mod.set_block_temperature(4, hold_time_minutes=5)
  tc_mod.open_lid()

  p300.pick_up_tip()
  #for i in range(8):
  #  rowdest = plate2.rows()[i]
  #  p300.transfer(150, reservoir["A8"], rowdest[0:8], new_tip='never',blow_out=True,blowout_location='destination well')
  #p300.drop_tip()
  tot = 0
  n1 = 150*64
  for i in range(1, n1+1):
    if n1%i == 0 and i <= 300 and i%150 == 0:
      totvol = i
  for j in range(1,9):
    for i in range(1,9):
      if tot == 0:
        p300.aspirate(totvol, reservoir['A8'])
        tot = totvol
      p300.dispense(150, plate2[(chr(ord('@')+j)+str(i))])
      tot -= 150

  p300.drop_tip()  
  tc_mod.close_lid() 
  tc_mod.set_block_temperature(37, hold_time_minutes=60)
  tc_mod.open_lid()