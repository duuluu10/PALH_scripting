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

    # Your code from here


    # Reset stdout
    sys.stdout = sys.__stdout__

    print(f"G-code has been saved to {__file__[:-3]}.gcode")
    # print("G-code commands:")
    # print(gcode_printer.gcode_buffer.getvalue())


if __name__ == "__main__":
    generate_and_save_gcode()
