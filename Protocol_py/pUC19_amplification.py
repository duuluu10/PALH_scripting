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

    # Reagent loading
    preload_volume(tube3_rimless, '13', 30, 'F406_primer')
    preload_volume(tube3_rimless, '14', 30, 'F204_primer')
    preload_volume(tube3_rimless, '15', 30, 'R_uni_primer')
    preload_volume(tube3_rimless, '16', 150, 'Hot_start')
    preload_volume(tube3_rimless, '17', 60, 'pUC19')
    preload_volume(tube2, '1', 0, 'Premix')

    # 1. Start the system by homing!
    # start()
    G28()

    # Your code from here
    new_tip(E1_yellow_tips)
    iterations = 2
    for i in range(iterations):
        aspirate_volume(137.5/iterations, custom_name='Hot_start', air_gap=True)
        dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    eject()

    primers_list = ['F406_primer', 'F204_primer', 'R_uni_primer']
    for i in primers_list:
        new_tip(E1_yellow_tips)
        aspirate_volume(27.5, custom_name=i, air_gap=True)
        dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)
        eject()

    new_tip(E1_yellow_tips)
    aspirate_volume(55.5, custom_name='pUC19', air_gap=True)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    mix(20, mix_volume=100, custom_name='Premix')

    well_locations_plate = ['19', '20', '21', '22', '23']
    for i in well_locations_plate:
        aspirate_volume(50, custom_name='Premix', air_gap=10)
        dispense_volume(dispense_modules=tube3_rimless, well_locations=i, direct=True, touch_tip=True)
    eject()
    end()

    # Reset stdout
    sys.stdout = sys.__stdout__

    print(f"G-code has been saved to {__file__[:-3]}.gcode")
    # print("G-code commands:")
    # print(gcode_printer.gcode_buffer.getvalue())


if __name__ == "__main__":
    generate_and_save_gcode()
