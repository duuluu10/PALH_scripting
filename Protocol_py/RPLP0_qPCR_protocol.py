from gcode_generator_v1_2 import *  # Import all functions from gcode_generator_v1_1
from io import StringIO
import sys


class GCodePrinter:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.gcode_file = open(filename, 'w')
        self.gcode_buffer = StringIO()

    def write(self, message):
        if message.strip().startswith('G'):
            self.gcode_buffer.write(message)
            self.gcode_file.write(message)
        if message.strip().startswith('M'):
            self.gcode_buffer.write(message)
            self.gcode_file.write(message)
        self.terminal.write(message)

    def flush(self):
        self.terminal.flush()
        self.gcode_file.flush()


def generate_and_save_gcode():
    gcode_printer = GCodePrinter(f"{__file__[:-3]}.gcode")
    sys.stdout = gcode_printer

    # 1. Start the system by homing!
    # start()
    G28()

    # 2. Preload your module and reagents!
    preload_volume(tube3_rimless, '1', 0, '10pg') # at 2pg/uL
    preload_volume(tube3_rimless, '2', 0, '100pg') # at 20pg/uL
    preload_volume(tube3_rimless, '3', 0, '1ng') # at 200pg/uL
    preload_volume(tube3_rimless, '4', 0, '10ng') # at 2ng/uL
    preload_volume(tube3_rimless, '5', 0, '100ng') # at 20ng/uL
    preload_volume(tube3_rimless, '6', 90, '1ug') #input DNA at 200ng/uL
    preload_volume(tube3_rimless, '7', 180, 'PT2X') #qPCR master mix 2X
    preload_volume(tube3_rimless, '8', 30, 'RPLP0_primer') #qPCR primer mix 10X
    preload_volume(tube2, '1', 0, 'Premix')
    preload_volume(tube2, '2', 600, 'NFW')

    # 3. Your main code here
    # Step 0: Create serial dilution of input DNA
    serial_dilution_NFW = ['100ng', '10ng', '1ng', '100pg', '10pg']

    new_tip(E1_yellow_tips)
    for i in serial_dilution_NFW:
        aspirate_volume(90, custom_name='NFW')
        dispense_volume(custom_name=i, blowout=True, touch_tip=True, direct=True)
    eject()

    serial_dilution = ['1ug', '100ng', '10ng', '1ng', '100pg', '10pg']

    for i in range(len(serial_dilution) - 1):
        new_tip(E1_yellow_tips)
        aspirate_volume(10, custom_name=serial_dilution[i])
        dispense_volume(custom_name=serial_dilution[i + 1], blowout=True, touch_tip=True, direct=True, dispense_height=90)
        mix(10, custom_name=serial_dilution[i + 1], safe_dist=False)
        eject()

    # Step 1: Premix qPCR master mix and primers with water
    # Adding qPCR master mix into mixing tube
    new_tip(E1_yellow_tips)
    aspirate_volume(132 / 2, custom_name='PT2X')  # Part 1
    dispense_volume(132 / 2, custom_name='Premix', blowout=False, direct=True)
    aspirate_volume(132 / 2, custom_name='PT2X', air_gap=True)  # Part 2
    dispense_volume(132 / 2, custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    eject()

    # Adding primers into mixing tube
    new_tip(E1_yellow_tips)
    aspirate_volume(13.2, custom_name='RPLP0_primer', air_gap=True)
    dispense_volume(13.2, custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    eject()

    # Adding water into mixing tube and mix
    new_tip(E1_yellow_tips)
    aspirate_volume(52.8, custom_name='NFW', air_gap=True)
    dispense_volume(52.8, custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    mix(10, custom_name='Premix', aspirate_feedrate=1500, dispense_feedrate=1500)

    # Step 2: Aliquot 15uL of the premixed master mix to plate
    well_locations_plate = ['B2', 'B4', 'D2', 'D4']
    transferred_volume = 15
    dispensed_volumes_plate = [transferred_volume] * len(well_locations_plate)

    dispense_iteration = len(well_locations_plate)
    total_mix_asp = transferred_volume*(dispense_iteration) * 1.1 # Part 1
    aspirate_volume(total_mix_asp, custom_name='Premix')
    dispense_volume(dispensed_volumes_plate, dispense_modules=[plate_384_biorad]*dispense_iteration,
                    well_locations=well_locations_plate, touch_tip=True, direct=True)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True)

    well_locations_plate = ['F2', 'F4', 'H2', 'H4']
    transferred_volume = 15
    dispensed_volumes_plate = [transferred_volume] * len(well_locations_plate)

    dispense_iteration = len(well_locations_plate)
    total_mix_asp = transferred_volume * (dispense_iteration) * 1.1  # Part 2
    aspirate_volume(total_mix_asp, custom_name='Premix', direct=True)
    dispense_volume(dispensed_volumes_plate, dispense_modules=[plate_384_biorad] * dispense_iteration,
                    well_locations=well_locations_plate, touch_tip=True, direct=True)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True)

    well_locations_plate = ['J2', 'J4', 'L2', 'L4']
    transferred_volume = 15
    dispensed_volumes_plate = [transferred_volume] * len(well_locations_plate)

    dispense_iteration = len(well_locations_plate)
    total_mix_asp = transferred_volume * (dispense_iteration) * 1.1  # Part 2
    aspirate_volume(total_mix_asp, custom_name='Premix', direct=True)
    dispense_volume(dispensed_volumes_plate, dispense_modules=[plate_384_biorad] * dispense_iteration,
                    well_locations=well_locations_plate, touch_tip=True, direct=True)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True)
    eject()

    # Aliquot 20uL of NFW to the plate as negative control
    new_tip(E1_yellow_tips)
    well_locations_plate = ['N2', 'N4']
    transferred_volume = 20
    dispensed_volumes_plate = [transferred_volume] * len(well_locations_plate)

    dispense_iteration = len(well_locations_plate)
    total_mix_asp = transferred_volume * (dispense_iteration) * 1.1  # Part 3
    aspirate_volume(total_mix_asp, custom_name='NFW')
    dispense_volume(dispensed_volumes_plate, dispense_modules=[plate_384_biorad] * dispense_iteration,
                    well_locations=well_locations_plate, touch_tip=True, direct=True)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True)
    eject()

    # Step 3: Aliquot 5uL of the DNA template to subsequent plate wells
    # 1 - 10pg
    new_tip(E1_yellow_tips)
    well_locations_plate = ['B2']
    transferred_volume = 5
    aspirate_volume(transferred_volume, custom_name='10pg', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)

    well_locations_plate = ['B4']
    aspirate_volume(transferred_volume, custom_name='10pg', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)
    eject()

    # 2 - 100pg
    new_tip(E1_yellow_tips)
    well_locations_plate = ['D2']
    transferred_volume = 5
    aspirate_volume(transferred_volume, custom_name='100pg', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)

    well_locations_plate = ['D4']
    aspirate_volume(transferred_volume, custom_name='100pg', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)
    eject()

    # 3 - 1ng
    new_tip(E1_yellow_tips)
    well_locations_plate = ['F2']
    transferred_volume = 5
    aspirate_volume(transferred_volume, custom_name='1ng', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)

    well_locations_plate = ['F4']
    aspirate_volume(transferred_volume, custom_name='1ng', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)
    eject()

    # 4 - 10ng
    new_tip(E1_yellow_tips)
    well_locations_plate = ['H2']
    transferred_volume = 5
    aspirate_volume(transferred_volume, custom_name='10ng', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)

    well_locations_plate = ['H4']
    aspirate_volume(transferred_volume, custom_name='10ng', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)
    eject()

    # 5 - 100ng
    new_tip(E1_yellow_tips)
    well_locations_plate = ['J2']
    transferred_volume = 5
    aspirate_volume(transferred_volume, custom_name='100ng', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)

    well_locations_plate = ['J4']
    aspirate_volume(transferred_volume, custom_name='100ng', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)
    eject()

    # 6 - NTC
    new_tip(E1_yellow_tips)
    well_locations_plate = ['L2']
    transferred_volume = 5
    aspirate_volume(transferred_volume, custom_name='NFW', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)

    well_locations_plate = ['L4']
    aspirate_volume(transferred_volume, custom_name='NFW', air_gap=True)
    dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                    well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)
    eject()

    # Reset stdout
    sys.stdout = sys.__stdout__

    print(f"G-code has been saved to {__file__[:-3]}.gcode")
    # print("G-code commands:")
    # print(gcode_printer.gcode_buffer.getvalue())


if __name__ == "__main__":
    generate_and_save_gcode()
