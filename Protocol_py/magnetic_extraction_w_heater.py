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

    # Load samples
    preload_volume(tube3_rimless, '13', 0, 'waste1')
    preload_volume(tube3_rimless, '14', 0, 'waste2')
    preload_volume(tube3_rimless, '15', 0, 'waste3')
    preload_volume(tube3_rimless, '16', 0, 'waste4')
    preload_volume(tube3_rimless, '17', 0, 'waste5')
    preload_volume(tube3_rimless, '24', 0, 'Elution_final')
    preload_volume(plate_96_biorad, 'B1', 100, 'Sample')
    preload_volume(plate_96_biorad, 'B2', 100, 'LB1') #Proteinase K (5uL) and Lysis buffer mixed (95ul)
    # preload_volume(plate_96_biorad, 'A3', 30, 'PK')
    # preload_volume(plate_96_biorad, 'A4', 100, 'Water')
    preload_volume(plate_96_biorad, 'B3', 50, 'EB6')
    preload_volume(tube2, '1', 0, 'Premix')
    preload_volume(tube2, '2', 360, 'BB2+MB') #Binding buffer (350uL) and magnetic beads (10uL) mixed
    preload_volume(tube2, '3', 200, 'WB3')
    preload_volume(tube2, '4', 200, 'WB4')

    # 1. Start the system by homing!
    G28()

    # Your code from here
    # Premix samples and lysis
    new_tip(E1_yellow_tips)
    aspirate_volume(100, custom_name='Sample', air_gap=True, deadpump_vol=5)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    eject()
    new_tip(E1_yellow_tips)
    aspirate_volume(100, custom_name='LB1', air_gap=True, deadpump_vol=5)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    # eject()
    # new_tip(E1_yellow_tips)
    # aspirate_volume(10, custom_name='PK', air_gap=True)
    # dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)

    mix(20, mix_volume=100, custom_name='Premix', aspirate_feedrate=2500, dispense_feedrate=2500)
    eject()
    incubation_duration = 8 * 60
    print(f'G4 P{incubation_duration * 1000}\n')

    new_tip(E1_yellow_tips)
    for i in range(3):
        aspirate_volume(100, custom_name='BB2+MB', air_gap=False, deadpump_vol=5)
        dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)
    aspirate_volume(60, custom_name='BB2+MB', air_gap=False, deadpump_vol=5)
    dispense_volume(custom_name='Premix', blowout=True, touch_tip=True, direct=True)

    mix(15, mix_volume=100, custom_name='Premix', aspirate_feedrate=2500, dispense_feedrate=2500)
    incubation_duration = 4 * 60
    print(f'G4 P{incubation_duration * 1000}\n')
    mix(15, mix_volume=100, custom_name='Premix', aspirate_feedrate=2500, dispense_feedrate=2500)

    # Pellet magnetic beads
    waste_containers = ['waste1', 'waste2']
    for j in waste_containers:
        for i in range(2):
            aspirate_volume(100, custom_name='Premix', air_gap=False, deadpump_vol=5)
            pipette_pellet(feedrate=50, pellet_duration=10, pellet_height=12.2, custom_name=j, action='dispense',
                           direct=True, touch_tip=True)

    aspirate_volume(100, custom_name='Premix', air_gap=False, deadpump_vol=5)
    pipette_pellet(feedrate=40, pellet_duration=10, pellet_height=12.2, custom_name='waste3', action='dispense',
                   direct=True, touch_tip=True)
    aspirate_volume(80, custom_name='Premix', air_gap=False, deadpump_vol=10)
    pipette_pellet(feedrate=40, pellet_duration=10, pellet_height=12.2, custom_name='waste3', action='dispense',
                   double_pellet=True, double_pellet_height=30, double_pellet_duration=30,
                   direct=True, touch_tip=True)

    # Wash magnetic beads (WB3)
    mix(20, mix_volume=100, custom_name='WB3', aspirate_feedrate=2500, dispense_feedrate=2500)
    for i in range(2):
        aspirate_volume(100, custom_name='WB3', air_gap=False, deadpump_vol=5)
        pipette_pellet(feedrate=40, pellet_duration=5, pellet_height=12.2, custom_name='waste4', action='dispense',
                       double_pellet=True, double_pellet_height=30, double_pellet_duration=30,
                       direct=True)

    # Wash magnetic beads (WB4)
    mix(20, mix_volume=100, custom_name='WB4', aspirate_feedrate=2500, dispense_feedrate=2500)
    for i in range(2):
        aspirate_volume(100, custom_name='WB4', air_gap=False, deadpump_vol=5)
        pipette_pellet(feedrate=50, pellet_duration=5, pellet_height=12.2, custom_name='waste5', action='dispense',
                       double_pellet=True, double_pellet_height=30, double_pellet_duration=30,
                       direct=True)

    # Heat up pipette beads
    heat(temperature=65, duration=4*60, height_adj=+3, direct=True)

    # # Wash pipette before elution
    # aspirate_volume(25, custom_name='Water', air_gap=False, air_gap_vol=50, deadpump_vol=20)
    # dispense_volume(custom_name='Water', blowout=True, touch_tip=True, direct=True, safe_dist=False)

    # Elute DNA (EB6)
    mix(50, mix_volume=90, custom_name='EB6', aspirate_feedrate=2500, dispense_feedrate=2500)
    aspirate_volume(50, custom_name='EB6', air_gap=True, air_gap_vol=50, deadpump_vol=10)
    pipette_pellet(feedrate=50, pellet_duration=2 * 60, pellet_height=12.2, custom_name='Elution_final', action='dispense',
                   direct=True, touch_tip=True)
    eject()

    end()

    # Reset stdout
    sys.stdout = sys.__stdout__

    print(f"G-code has been saved to {__file__[:-3]}.gcode")
    # print("G-code commands:")
    # print(gcode_printer.gcode_buffer.getvalue())


if __name__ == "__main__":
    generate_and_save_gcode()
