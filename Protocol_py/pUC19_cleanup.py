from gcode_generator_v1_1 import *  # Import all functions from gcode_generator_v1_1
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
    sample_vol = 50
    preload_volume(plate_96_biorad, 'A1', sample_vol, 'Sample')
    preload_volume(plate_96_biorad, 'A2', 33, 'RB') #Resuspension buffer
    preload_volume(tube3_rimless, '13', 0, 'Waste')
    preload_volume(tube3_rimless, '14', 100, 'Wash1')
    preload_volume(tube3_rimless, '15', 100, 'Wash2')
    preload_volume(tube3_rimless, '16', 100, 'Wash3')
    preload_volume(tube3_rimless, '17', 0, 'Eluted_DNA')
    preload_volume(tube2, '1', 400, 'AmpureXP')

    # 1. Start the system by homing!
    # start()
    G28()

    # Your code from here
    new_tip(E1_yellow_tips)

    # Mix magnetic beads and Sample
    ampureXP_vol = 60
    aspirate_volume(ampureXP_vol, custom_name='AmpureXP', air_gap=True)
    dispense_volume(custom_name='Sample', blowout=True, touch_tip=True, direct=True)
    mix(15, mix_volume=100, custom_name='Sample', direct=False)
    incubation_duration = 30
    print(f'G4 P{incubation_duration * 1000}\n')  # G4 P<duration in milliseconds>
    mix(15, mix_volume=100, custom_name='Sample', direct=False)

    # Remove supernatant
    iterations = 2
    total_vol = ampureXP_vol + sample_vol + 5
    for _ in range(iterations):
        aspirate_volume(total_vol/iterations, custom_name='Sample', air_gap=True, deadpump_vol=5)
        pipette_pellet(feedrate=10, pellet_duration=80, pellet_height=12.2, custom_name='Waste',
                       action='dispense', direct=True, touch_tip=True)

    # IPA washing steps
    ipa_list = ['Wash1', 'Wash2', 'Wash3']
    for ipa in ipa_list:
        pipette_pellet(feedrate=1000, pellet_duration=5, pellet_height=12.2, custom_name=ipa,
                       action='aspirate', action_feedrate=500, volume=100, direct=True)
        pipette_pellet(feedrate=100, pellet_duration=5, pellet_height=12.2, custom_name=ipa,
                       action='dispense', action_feedrate=500, direct=True, safe_dist=False, touch_tip=True)

    # Heat up pipette beads
    heat(temperature=45, duration=30, direct=True)

    # Elute DNA
    # mix(20, mix_volume=90, custom_name='RB', aspirate_feedrate=2500, dispense_feedrate=2500)
    # incubation_duration = 2 * 60
    # print(f'G4 P{incubation_duration * 1000}\n')  # G4 P<duration in milliseconds>
    # aspirate_volume(33, custom_name='RB', air_gap=True, air_gap_vol=50, deadpump_vol=10, safe_dist=False)
    aspirate_volume(33, custom_name='RB', air_gap=True, air_gap_vol=40, deadpump_vol=25)
    pipette_mix(20, lower_limit=60, upper_limit=100, mix_feedrate=2500)
    incubation_duration = 60
    print(f'G4 P{incubation_duration * 1000}\n')  # G4 P<duration in milliseconds>
    pipette_pellet(feedrate=30, pellet_duration=60, pellet_height=12.2, custom_name='Eluted_DNA',
                   action='dispense', direct=True, touch_tip=True)
    eject()

    end()

    # Reset stdout
    sys.stdout = sys.__stdout__

    print(f"G-code has been saved to {__file__[:-3]}.gcode")
    # print("G-code commands:")
    # print(gcode_printer.gcode_buffer.getvalue())


if __name__ == "__main__":
    generate_and_save_gcode()
