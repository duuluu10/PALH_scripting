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
    preload_volume(tube3_rimless, '1', 0, '1pg') # at 0.2pg/uL
    preload_volume(tube3_rimless, '2', 0, '10pg') # at 2pg/uL
    preload_volume(tube3_rimless, '3', 0, '100pg') # at 20pg/uL
    preload_volume(tube3_rimless, '4', 0, '1ng') # at 200pg/uL
    preload_volume(tube3_rimless, '5', 0, '10ng') # at 2ng/uL
    preload_volume(tube3_rimless, '6', 0, '100ng') # at 20ng/uL
    preload_volume(tube3_rimless, '7', 90, '1ug') #input DNA at 200ng/uL
    preload_volume(tube3_rimless, '8', 180, 'PT2X') #qPCR master mix 2X
    preload_volume(tube3_rimless, '9', 30, 'YWHAZ_primer') #qPCR primer mix 10X
    preload_volume(tube2, '1', 0, 'Premix')
    preload_volume(tube2, '2', 600, 'NFW')

    # 3. Your main code here
    # Step 0: Create serial dilution of input DNA
    serial_dilution_NFW = ['100ng', '10ng', '1ng', '100pg', '10pg', '1pg']

    new_tip(E1_yellow_tips)
    for i in serial_dilution_NFW:
        aspirate_volume(90, custom_name='NFW')
        dispense_volume(custom_name=i, blowout=True, touch_tip=True, direct=True)
    eject()

    serial_dilution = ['1ug', '100ng', '10ng', '1ng', '100pg', '10pg', '1pg']

    for i in range(len(serial_dilution) - 1):
        new_tip(E1_yellow_tips)
        aspirate_volume(10, custom_name=serial_dilution[i], direct=True)
        dispense_volume(custom_name=serial_dilution[i + 1], blowout=True, touch_tip=True, direct=True, dispense_height=90)
        mix(10, custom_name=serial_dilution[i + 1], safe_dist=False)
        eject()

    # Step 1: Premix qPCR master mix and primers with water
    # Adding qPCR master mix into mixing tube
    new_tip(E1_yellow_tips)
    aspirate_volume(297 / 3, custom_name='PT2X', deadpump_vol=5)  # Part 1
    dispense_volume(custom_name='Premix', blowout=False, direct=True)
    aspirate_volume(297 / 3, custom_name='PT2X', deadpump_vol=5)  # Part 2
    dispense_volume(custom_name='Premix', blowout=False, direct=True)
    aspirate_volume(297 / 3, custom_name='PT2X', deadpump_vol=5)  # Part 3
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    eject()

    # Adding primers into mixing tube
    new_tip(E1_yellow_tips)
    aspirate_volume(29.7, custom_name='YWHAZ_primer', air_gap=True)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    eject()

    # Adding water into mixing tube and mix
    new_tip(E1_yellow_tips)
    aspirate_volume(118.8 / 2, custom_name='NFW', air_gap=True)
    dispense_volume(custom_name='Premix', blowout=True, direct=True)
    aspirate_volume(118.8 / 2, custom_name='NFW', air_gap=True, safe_dist=False)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    mix(20, custom_name='Premix', aspirate_feedrate=1500, dispense_feedrate=1500)

    # Step 2: Aliquot 15uL of the premixed master mix to plate
    def aliquot_premix(well_locations_plate):
        transferred_volume = 15
        dispensed_volumes_plate = [transferred_volume] * len(well_locations_plate)

        dispense_iteration = len(well_locations_plate)
        total_mix_asp = transferred_volume*(dispense_iteration) + 10 # Part 1
        aspirate_volume(total_mix_asp, custom_name='Premix', deadpump=False)
        dispense_volume(dispensed_volumes_plate, dispense_modules=[plate_384_biorad]*dispense_iteration,
                        well_locations=well_locations_plate, touch_tip=True, direct=True)

    well_locations_plate = ['B2', 'B4', 'B6', 'B8', 'B10', 'B12']
    aliquot_premix(well_locations_plate)

    well_locations_plate = ['B14', 'B16', 'B18', 'B20', 'B22', 'C2']
    aliquot_premix(well_locations_plate)

    well_locations_plate = ['C4', 'C6', 'C8', 'C10', 'C12', 'C14']
    aliquot_premix(well_locations_plate)

    well_locations_plate = ['C16', 'C18', 'C20']
    aliquot_premix(well_locations_plate)
    eject()

    # Aliquot 20uL of NFW to the plate as negative control
    new_tip(E1_yellow_tips)
    well_locations_plate = ['C22', 'D2', 'D4']
    transferred_volume = 20
    dispensed_volumes_plate = [transferred_volume] * len(well_locations_plate)

    dispense_iteration = len(well_locations_plate)
    total_mix_asp = transferred_volume * (dispense_iteration)
    aspirate_volume(total_mix_asp, custom_name='NFW')
    dispense_volume(dispensed_volumes_plate, dispense_modules=[plate_384_biorad] * dispense_iteration,
                    well_locations=well_locations_plate, touch_tip=True, direct=True)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True)
    eject()

    # Step 3: Aliquot 5uL of the DNA template to subsequent plate wells
    # 1 - 10pg
    transferred_volume = 5
    def aliquot_template(template_name, well_locations_plate):
        new_tip(E1_yellow_tips)
        aspirate_volume(transferred_volume, custom_name=template_name, air_gap=True)
        dispense_volume(transferred_volume, dispense_modules=[plate_384_biorad],
                        well_locations=well_locations_plate, touch_tip=True, direct=True, blowout=True)
        eject()

    aliquot_template('100ng', 'B2')
    aliquot_template('100ng', 'B4')
    aliquot_template('100ng', 'B6')

    aliquot_template('10ng', 'B8')
    aliquot_template('10ng', 'B10')
    aliquot_template('10ng', 'B12')

    aliquot_template('1ng', 'B14')
    aliquot_template('1ng', 'B16')
    aliquot_template('1ng', 'B18')

    aliquot_template('100pg', 'B20')
    aliquot_template('100pg', 'B22')
    aliquot_template('100pg', 'D2')

    aliquot_template('10pg', 'B4')
    aliquot_template('10pg', 'B6')
    aliquot_template('10pg', 'B8')

    aliquot_template('1pg', 'B10')
    aliquot_template('1pg', 'B12')
    aliquot_template('1pg', 'B14')

    aliquot_template('NFW', 'B16')
    aliquot_template('NFW', 'B18')
    aliquot_template('NFW', 'B20')

    end()

    # Reset stdout
    sys.stdout = sys.__stdout__

    print(f"G-code has been saved to {__file__[:-3]}.gcode")
    # print("G-code commands:")
    # print(gcode_printer.gcode_buffer.getvalue())


if __name__ == "__main__":
    generate_and_save_gcode()
