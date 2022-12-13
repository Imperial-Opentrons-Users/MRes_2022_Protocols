metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Serial Dilution Tutorial',
    'description': '''This protocol is the outcome of following the
                   Python Protocol API Tutorial located at
                   https://docs.opentrons.com/v2/tutorial.html. It takes a
                   solution and progressively dilutes it by transferring it
                   stepwise across a plate.''',
    'author': 'New API User'
    }

def run(protocol: protocol_api.ProtocolContext):
    metadata = {'apiLevel': '2.0'}
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)
    p300 = protocol.load_instrument('p300_multi_gen2', 'right',
    tip_racks=[tiprack_1])
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 3)

    row = plate.rows()[0]
    p300.pick_up_tip()
    p300.transfer(100, reservoir['A1'], row[1:], new_tip='never')
    p300.blow_out()
    p300.transfer(200, reservoir['A2'], row[0], new_tip='never')
    p300.blow_out()
    p300.transfer(100, row[:10], row[1:11], mix_after=(3, 50), new_tip='never', blow_out=True)
    p300.aspirate(100, row[10])
    p300.drop_tip()    