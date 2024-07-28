import numpy as np

# Custom output function

# Globals
current_aspirated_volume = 0
current_deadpump_volume = 0
current_air_gap_volume = 0
custom_preloads = {}

# Setting up deck positions:

# Tube locations:

# Generic Epindorf 5mL tubes:
tube1 = {
    'X': np.arange(130, 130 + 20.3 * 6, 20.3),
    'Y': np.full(6, 40.5),
    'Z0': 1.5,
    'top': 60,  # safe Z-axis distance
    'height': lambda v: round(
        tube1['Z0'] if v <= 3 else
        1.08 * (v ** 0.435) if v <= 950 else
        (6.65E-03 * v + 15.3), 2
    ),
    'radius': 7.6,  # mm
    'V': np.zeros(6),  # Preload condition, initially set to zero
    'name': 'Tube 1 (5.0mL)'
}

# Generic 1.5mL tubes:
tube2 = {
    'X': [129, 149.3, 169.6, 189.9, 210.2, 230.5, 230.5, 230.5, 230.5, 230.5, 230.5, 230.5],
    'Y': [61.6, 61.6, 61.6, 61.6, 61.6, 61.6, 81.9, 102.2, 122.5, 142.8, 163.1, 183.4],
    'Z0': 2.9,
    'top': 40,
    'height': lambda v: round(
        tube2['Z0'] if v <= 3 else
        0.75 * (v ** 0.507) if v <= 410 else
        (0.0164 * v + 9.56), 2
    ),
    'radius': 4,  # mm
    'V': np.zeros(12),  # Preload condition, initially set to zero
    'name': 'Tube 2 (1.5mL)'
}

# Generic 0.2mL tubes: (with rim!)
tube3 = {
    'X': np.concatenate((np.full(12, 112.4), np.full(12, 130.4))),
    'Y': np.concatenate((np.arange(114.6, 222.6, 9), np.arange(110.1, 218.1, 9))),
    'Z0': 5.2,
    'top': 25.2,
    'height': lambda v: round(
        tube3['Z0'] if v <= 3 else
        5.8 + 0.193 * v + -1.28E-03 * (v ** 2) if v <= 62 else
        (0.0484 * v + 9.7), 2
    ),
    'radius': 2.0,  # mm
    'V': np.zeros(24),  # Preload condition, initially set to zero
    'name': 'Tube 3 (0.2mL)'
}

# Generic 0.2mL tubes: (without rim!)
tube3_rimless = {
    'X': np.concatenate((np.full(12, 112.4), np.full(12, 130.4))),
    'Y': np.concatenate((np.arange(114.6, 222.6, 9), np.arange(110.1, 218.1, 9))),
    'Z0': 2.8,
    'top': 22.2,
    'height': lambda v: round(
        tube3_rimless['Z0'] if v <= 3 else
        3.1 + 0.193 * v + -1.28E-03 * (v ** 2) if v <= 62 else
        (0.0484 * v + 7.3), 2
    ),
    'radius': 2.0,  # mm
    'V': np.zeros(24),  # Preload condition, initially set to zero
    'name': 'Tube 3 rimless (0.2mL)'
}

# E1 clip tips: (200uL yellow rack, Thermofisher, catalog no: 94420318)
tiprows = 12  # Number of rows
tipcols = 8  # Number of columns
tipspacing = 9  # Horizontal spacing (in mm)
tipXorig = 93.5  # bottom right corner coordination X
tipYorig = 112.7  # bottom right corner coordination Y

tipX, tipY = np.meshgrid(
    np.arange(tipXorig, tipXorig - tipcols * tipspacing, -tipspacing),
    np.arange(tipYorig, tipYorig + tiprows * tipspacing, tipspacing)
)

E1_yellow_tips = {
    'locs': np.column_stack((tipX.ravel(), tipY.ravel())),
    'top': 65,
    'rim': 10,
    'bottom': 3.0,
    'next': 1
}

pipette_heater = {
    'X': 231,
    'Y': 184,
    'top': 65,
    'bottom': 26
}


# Well plate locations:
def well_creator(rows, cols, spacing, Z0, top, well1_diff_X, well1_diff_Y,
                 height, well_radius, name):  # preload should either be a single zero or a matrix
    """
        Create a well plate configuration with volume height correlation.

        :param rows: Number of rows in the plate
        :param cols: Number of columns in the plate
        :param spacing: Spacing between wells
        :param Z0: Initial Z height
        :param top: Top height of the wells
        :param well1_diff_X: X offset for the first well from bottom left corner of the plate slot
        :param well1_diff_Y: Y offset for the first well from bottom left corner of the plate slot
        :param height: Function to calculate height based on volume
        :param name: Name of the custom plate
        :return: Dictionary representing the well plate
    """
    well = {
        'X': np.zeros((rows, cols)),
        'Y': np.zeros((rows, cols)),
        'Z0': Z0,
        'top': top,
        'height': height,
        'V': np.zeros((rows, cols)),  # Preload condition, initially set to zero
        'radius': well_radius,
        'name': name
    }
    for i in range(rows):
        for j in range(cols):
            well['X'][i, j] = 136.2 + well1_diff_X + i * spacing
            well['Y'][i, j] = 86 + well1_diff_Y + j * spacing
    return well


plate_384_biorad = well_creator(rows=16, cols=24, spacing=4.5, Z0=1.05, top=11.4, well1_diff_X=8.84,
                                well1_diff_Y=12.28, height=lambda v: 0.202 * v + 1.05, well_radius=1.2,
                                name='384-well plate (BioRad)')

plate_96_biorad = well_creator(rows=8, cols=12, spacing=9.0, Z0=2.8, top=18.2, well1_diff_X=11.11, well1_diff_Y=14.25,
                               height=lambda v: round(tube3_rimless['Z0'] if v <= 5 else
                                                      3.1 + 0.193 * v + -1.28E-03 * (v ** 2)
                                                      if v <= 62 else (0.0484 * v + 7.3), 2), well_radius=2.4,
                               name='96-well plate (BioRad)')


# Sequence of functions:
def start():
    print('M92 X80 Y80 Z400 V165\n')  # set the steps per unit (X, Y, Z: mm; V: uL)
    print('M203 X6000 Y1000 Z30 V20\n')  # set maximum feedrate unit per second (X, Y, Z: mm/s; V: uL/s)
    print('G1 Z50\n')
    print('G1 Y50\n')
    print('G28 X V\n')
    print('G28 Y\n')
    print('G1 Y100\n')
    print('G28 Z\n')
    print('G1 V0\n')
    print('G1 Z65\n')


def G1(x=None, y=None, z=None, p=None, feedrate=None, accel=None):
    gcode = 'G1'
    if accel is not None:
        print(f'M204 S{accel}\n')

    if x is not None:
        if isinstance(x, np.ndarray):
            gcode += f' X{np.round(x, 3)}'
        else:
            gcode += f' X{round(x, 3)}'

    if y is not None:
        if isinstance(y, np.ndarray):
            gcode += f' Y{np.round(y, 3)}'
        else:
            gcode += f' Y{round(y, 3)}'

    if z is not None:
        if isinstance(z, np.ndarray):
            gcode += f' Z{np.round(z, 3)}'
        else:
            gcode += f' Z{round(z, 3)}'

    if p is not None:
        if isinstance(p, np.ndarray):
            gcode += f' V{np.round(p, 4)}'
        else:
            gcode += f' V{round(p, 4)}'

    if feedrate is not None:
        gcode += f' F{feedrate}'

    print(gcode + '\n')


def G2(x=None, y=None, i=None, j=None, feedrate=None):
    gcode = 'G2'
    # Add X and Y coordinates (same as start point for a full circle). Add I and J offsets (from start point to center)
    gcode += f" X{x:.3f} Y{y:.3f} I{-i:.3f} J{j:.3f}"

    # Add feedrate if specified
    if feedrate is not None:
        gcode += f" F{feedrate}"

    print(gcode + '\n')


def G28(feedrate=3000):
    print('M92 X80 Y80 Z400 V165\n')  # set the steps per unit (X, Y, Z: mm; V: uL)
    print('M203 X6000 Y1000 Z30 V20\n')  # set maximum feedrate unit per second (X, Y, Z: mm/s; V: uL/s)
    print(f'G1 F{feedrate}\n')
    print('G1 Z100\n')
    print('G1 Y100\n')
    print('G28 X V\n')
    print('G28 Y\n')
    print('G1 Y100\n')
    print('G28 Z\n')
    print('G1 Z65 V0\n')


def homing_pos(feedrate=3000):
    print(f'G1 F{feedrate}\n')
    print('G1 Z100\n')
    print('G1 Y100 X10\n')


def new_tip(tips):
    global next_tip
    if 'next_tip' not in globals():
        next_tip = tips['next']
    G1(z=tips['top'], feedrate=3000)
    G1(x=tips['locs'][next_tip - 1, 0], y=tips['locs'][next_tip - 1, 1])
    G1(z=tips['rim'])
    G1(z=tips['bottom'], feedrate=200)
    G1(z=tips['top'], feedrate=3000)
    next_tip += 1
    print('-Added new tip\n')


def eject():
    G1(z=100, feedrate=3000)
    G1(x=62.5, y=75)
    G1(z=65)
    G1(x=62.5, y=48)
    G1(z=75, feedrate=200)
    G1(z=70, feedrate=500)
    G1(y=75, feedrate=3000)
    print('Ejected tip\n')

############ Calibration Functions ############

def calibration():
    print('M0 Make sure the stage is removed! Press button to continue')
    positions = [
        (232, 13, 0),
        (232, 235, 0),
        (19, 235, 0),
        (19, 13, 0)
    ]
    print(f'G1 Z10\n')
    for _ in range(3):  # Repeat the sequence 3 times
        for x, y, z in positions:
            # Move to the position
            print(f'G1 X{x} Y{y} Z10\n')
            print(f'G4 P200\n')  # Pause for 200ms
            print(f'G1 Z{z}\n')

            # Pause and wait for user input
            print('M0 Press button to continue\n')

            print(f'G1 Z10\n')

    print(f'G1 Z100\n')
    print(f'G1 Y100\n')


def move_to_module_cal_test(module):
    """
    :param module: Name of the module 'e.g. Tube1'
    :return:
    """
    if isinstance(module, dict) and 'X' in module and isinstance(module['X'], np.ndarray) and module['X'].ndim == 2:
        # It's a plate (2D array of wells)
        first_move = True
        for row in list(range(0, 2)) + list(range(14, 16)):  # 4 rows (A to B and 23 to 24)
            for col in range(2):  # 2 columns (1 to 2)
                well = f'{chr(65 + row)}{col + 1}'  # Generate well names (A1, A2, B1, B2, etc.)
                if first_move:
                    move_to_well_location(module, well, safe_dist=True, direct=False)
                    first_move = False
                else:
                    move_to_well_location(module, well, safe_dist=False, direct=True)
                print('M0 Press button to continue\n')
        first_move = True
        for row in list(range(0, 2)) + list(range(14, 16)):  # 4 rows (A to B and 23 to 24)
            for col in list(range(22, 24)):  # 2 columns (23 to 24)
                well = f'{chr(65 + row)}{col + 1}'  # Generate well names (A1, A2, B1, B2, etc.)
                if first_move:
                    move_to_well_location(module, well, safe_dist=True, direct=False)
                    first_move = False
                else:
                    move_to_well_location(module, well, safe_dist=False, direct=True)
                print('M0 Press button to continue\n')
    elif isinstance(module, dict) and 'X' in module and isinstance(module['X'], (list, np.ndarray)):
        # It's a tube rack (1D array of tubes)
        G1(z=100)  # Move to a safe height first
        for i in range(len(module['X'])):
            G1(x=module['X'][i])
            G1(y=module['Y'][i])
            G1(z=module['top'])
            print('M0 Press button to continue\n')
        # Pause and wait for user input
    else:
        print("-Invalid module type")
        return

    homing_pos()  # Return to home position after completing all wells/tubes


def aspirate_iteratively_tube_bottom_cal(module, location, volume, initial_height='Z0', iterations=5, z_decrement=1,
                                         dead_vol=20, adj_z_increment=0.5):
    global tube1, tube2, tube3, tube3_rimless, plate_384_biorad

    # Move to the well location using move_to_well_location
    move_to_well_location(module, location, safe_dist=True, direct=False)

    for i in range(iterations):
        # Aspirate dead volume
        G1(p=0)
        G1(p=dead_vol)
        print('G4 P1000\n')  # Pause for 1000ms
        volume_adj = dead_vol + volume

        # Calculate the current Z position
        if initial_height == 'Z0':
            current_z = module[initial_height] + i * z_decrement
        else:
            current_z = initial_height + i * z_decrement

        # Move to the current Z position
        G1(z=current_z, feedrate=1000)  # Slower feedrate for precision

        # Aspirate the specified volume
        G1(p=volume_adj, feedrate=100)  # Adjust feedrate as needed for aspiration
        print('G4 P1000\n')  # Pause for 1000ms

        # Aspirate all remaining liquid by moving z height up
        adj_z = current_z + adj_z_increment
        G1(z=adj_z)

        # Move to a safe height
        G1(z=100, feedrate=3000)

        # Pause and dispense the full volume
        print('M0 Press button to dispense\n')
        G1(p=0)


def height_cal(tube_type, tube_number, initial_z_height, iterations=5, z_decrement=1):
    tubes = {
        'tube1': tube1,
        'tube2': tube2,
        'tube3': tube3,
        'tube3_rimless': tube3_rimless,
        'plate_384_biorad': plate_384_biorad
    }

    if tube_type not in tubes:
        print(f"-Invalid tube type: {tube_type}. Please choose 'tube1', 'tube2', or 'tube3'.")
        return

    tube = tubes[tube_type]

    if tube_number < 1 or tube_number > len(tube['X']):
        print(f"-Invalid tube number for {tube_type}. Please choose a number between 1 and {len(tube['X'])}.")
        return

    # Adjust for 0-based indexing
    index = tube_number - 1

    # Move to a safe height first
    G1(z=100, feedrate=3000)

    # Move to the tube's X and Y coordinates
    G1(x=tube['X'][index])
    G1(y=tube['Y'][index])

    # Move to the top of the tube
    G1(z=tube['top'])

    for i in range(iterations):
        # Calculate the current Z position
        current_z = initial_z_height + i * z_decrement

        # Move to the current Z position
        G1(z=current_z, feedrate=1000)  # Slower feedrate for precision

        # Pause briefly
        print('G4 P500\n')  # Pause for 500ms

        # Move to a safe height
        safe_height = tube['top'] + 20
        G1(z=safe_height, feedrate=3000)

        # Pause and dispense the full volume
        print('M0 Press button to dispense\n')


############ Action Functions ############
def move_to_well_location(module, well, safe_dist=True, direct=False, feedrate=3000):
    """
    Move the pipette to the well top of the tube/well location

    :param module: The module being used (e.g.,tube1, tube2, plate_384_biorad)
    :param well: The well location (e.g., '1', '2', 'A1')
    :param safe_dist: Boolean to make the Z-axis height safe (Z100)
    :param direct: Boolean to move pipette tips directly to the well location
    :param feedrate: Velocity of the motors when moving to the new well location (default is 3000)
    """
    # Check if the input is for a plate well (e.g., 'A1') or a tube well (e.g., '1')
    if isinstance(well, str) and len(well) >= 2 and well[0].isalpha() and well[1:].isdigit():
        # Plate well input (e.g., 'A1')
        row = well[0].upper()
        col = int(well[1:])

        # Convert row letter to number (A=0, B=1, etc.)
        row_num = ord(row) - ord('A')

        # Adjust column for 0-based indexing
        col_num = col - 1

        # Check if the input is within valid range
        if row_num < 0 or row_num >= 16 or col_num < 0 or col_num >= 24:
            print(f"-Invalid well position: {well}. Please choose a well between A1 and P24.")
            return

        # Move to well location
        if safe_dist:
            G1(z=65, feedrate=feedrate)  # Move to a safe height first

        if direct:
            G1(x=module['X'][row_num, col_num], y=module['Y'][row_num, col_num],
               feedrate=feedrate)  # Move directly to the well location
            G1(z=module['top'])
        else:
            G1(x=module['X'][row_num, col_num], feedrate=feedrate)  # Move to the well's X coordinate
            G1(y=module['Y'][row_num, col_num], feedrate=feedrate)  # Move to the well's Y coordinate
            G1(z=module['top'], feedrate=feedrate)  # Move down to the top of the well


    elif isinstance(well, str) and well.isdigit():
        # Tube well input (e.g., '1')
        tube_number = int(well)

        # Check if the tube number is within valid range
        if tube_number < 1 or tube_number > len(module['X']):
            print(f"-Invalid tube number: {well}. Please choose a number between 1 and {len(module['X'])}.")
            return

        # Adjust for 0-based indexing
        index = tube_number - 1

        # Move to well location
        if safe_dist:
            G1(z=65, feedrate=feedrate)  # Move to a safe height first
        if direct:
            G1(x=module['X'][index], y=module['Y'][index],
               feedrate=feedrate)  # Move down to the top of the tube
            G1(z=module['top'])
        else:
            G1(x=module['X'][index], feedrate=feedrate)  # Move to the tube's X coordinate
            G1(y=module['Y'][index], feedrate=feedrate)  # Move to the tube's Y coordinate
            G1(z=module['top'], feedrate=feedrate)  # Move down to the top of the tube
    else:
        print(f"-Invalid input format: {well}. Please use format like 'A1' for plate wells or '1' for tube wells.")


def move_to_liquid_height(module, volume, feedrate=3000):
    """
    Move the pipette to the correct height based on the liquid volume in the specified well.

    :param module: The module being used (e.g., plate_384_biorad)
    :param volume: The current volume in the well (in μL)
    :param feedrate: Velocity of the motors when moving to the new liquid height (default is 3000)
    """
    if 'height' in module:
        z_height = module['height'](volume)
    else:
        print(f"Error: No height correlation defined for module {module}")
        return
    # Move to the calculated z-height
    G1(z=z_height, feedrate=feedrate)


def preload_volume(module, well_location, volume, custom_name=None):
    """
    Preload a volume into a specific module and well location.

    :param module: The module object (e.g., tube1, tube2, plate_384_biorad)
    :param well_location: Well location as a string (e.g., '1', 'A1')
    :param volume: Volume to preload in µL
    :param custom_name: Optional custom name for the preloaded volume
    """
    if 'V' not in module:
        raise ValueError(f"-Invalid module: {module}. Module must have a 'V' attribute.")

    if isinstance(module['V'], np.ndarray):
        if module['V'].ndim == 1:  # Tube rack
            index = int(well_location) - 1
            if index < 0 or index >= len(module['V']):
                raise ValueError(f"-Invalid well location for tube rack: {well_location}")
            module['V'][index] = volume
        elif module['V'].ndim == 2:  # Plate
            row = ord(well_location[0].upper()) - ord('A')
            col = int(well_location[1:]) - 1
            if row < 0 or row >= module['V'].shape[0] or col < 0 or col >= module['V'].shape[1]:
                raise ValueError(f"-Invalid well location for plate: {well_location}")
            module['V'][row, col] = volume
    else:
        raise ValueError(f"-Unexpected volume array structure for module")

    if custom_name:
        custom_preloads[custom_name] = {
            'module': module,
            'well_location': well_location,
            'volume': volume
        }

    module_name = module.get('name', 'Unknown module')
    print(f"-Preloaded {volume} µL in {module_name} at well location {well_location}")
    if custom_name:
        print(f"-Custom name: {custom_name}\n")


def dead_pump(deadpump_volume=10):
    """
    Aspirate air volume before aspirate liquid

    :param deadpump_volume: Volume of the deadpump (default is 10 cm3)
    """
    global current_deadpump_volume

    # Set default deadpump volume
    G1(z=65, feedrate=3000)
    # Aspirate deadpump
    G1(p=0, feedrate=1000)
    G1(p=deadpump_volume, feedrate=1000)
    current_deadpump_volume = deadpump_volume


def aspirate_volume(aspirated_volume, custom_name=None, aspiration_module=None, well_location=None,
                    aspiration_height='Z0', height_unit='uL', aspirate_feedrate=500, safe_dist=True, direct=False,
                    deadpump=True, deadpump_vol=15, air_gap=False, air_gap_vol=5):
    """
    Aspirate a specified volume from a well location or current position.

    :param aspirated_volume: The volume to aspirate in μL.
    :param custom_name: Optional custom name for preloaded volume.
    :param aspiration_module: The module being used (e.g., plate_384_biorad, tube1, tube2).
    :param well_location: The well location (e.g., 'A1', '1').
    :param aspiration_height: The height to aspirate from (default is 'Z0').
    :param height_unit: The unit of aspiration height ('mm' or 'uL', default is 'uL').
    :param aspirate_feedrate: Velocity of aspiration (default is 500).
    :param safe_dist: Boolean to make the Z-axis height safe before moving to the well location (default is True).
    :param direct: Boolean to move pipette tips directly to the well location without intermediate steps (default is False).
    :param deadpump: Boolean to determine if deadpump should be used (default is True).
    :param deadpump_vol: Volume for the dead pump operation in μL (default is 15).
    :param air_gap: Boolean to determine if an air gap should be added after aspiration (default is False).
    :param air_gap_vol: Volume of the air gap in μL (default is 5).
    """
    global current_aspirated_volume, current_deadpump_volume, current_air_gap_volume

    # Check if a custom-named preloaded volume is being used
    if custom_name and custom_name in custom_preloads:
        preload = custom_preloads[custom_name]
        aspiration_module = preload['module']
        well_location = preload['well_location']

    # Set default deadpump volume
    deadpump_volume = deadpump_vol if deadpump else 0

    # Set air gap volume
    air_gap_volume = air_gap_vol if air_gap else 0

    aspirated_volume = round(aspirated_volume, 3)

    # If no module or location is specified, aspirate at the current position
    if aspiration_module is None and well_location is None:
        total_aspirated_volume = aspirated_volume + current_deadpump_volume
        G1(p=total_aspirated_volume, feedrate=aspirate_feedrate)
        if air_gap:
            G1(z=aspiration_module['top'], feedrate=3000)  # Move up to create air gap
            G1(p=air_gap_volume, feedrate=aspirate_feedrate)
        print(f'G4 P500\n')  # Pause for 500ms
        current_aspirated_volume += aspirated_volume
        current_deadpump_volume = deadpump_volume
        current_air_gap_volume = air_gap_volume
        return

    # Move to the well location
    move_to_well_location(aspiration_module, well_location, safe_dist=safe_dist, direct=direct, feedrate=3000)

    # Get the current volume in the well
    if isinstance(well_location, str) and well_location[0].isalpha():
        # For plate wells (e.g., 'A1')
        row = ord(well_location[0].upper()) - ord('A')
        col = int(well_location[1:]) - 1
        current_volume = aspiration_module['V'][row, col]
    else:
        # For tube wells (e.g., '1')
        index = int(well_location) - 1
        current_volume = aspiration_module['V'][index]

    # Check if aspirated volume is higher than current volume
    if aspirated_volume > current_volume:
        print(
            f"-Note! Cannot aspirate {aspirated_volume} μL from {well_location}. Current volume is only {current_volume} μL.\n")

    # Calculate aspiration height
    if height_unit == 'mm':
        adj_aspiration_height = aspiration_height if aspiration_height != 'Z0' else aspiration_module['Z0']
    elif height_unit == 'uL':
        adj_aspiration_height = aspiration_module['height'](aspiration_height) if aspiration_height != 'Z0' else \
            aspiration_module['Z0']
    else:
        raise ValueError("-Invalid height unit. Use 'uL' or 'mm'.")

    # Aspirate deadpump
    G1(p=0, feedrate=1000)
    G1(p=deadpump_volume, feedrate=500)
    print(f'G4 P500\n')  # Pause for 500ms

    # Move to aspiration height
    G1(z=adj_aspiration_height, feedrate=3000)

    # Aspirate the volume
    total_aspirated_volume = round(aspirated_volume + deadpump_volume, 3)
    G1(p=total_aspirated_volume, feedrate=aspirate_feedrate)
    print(f'G4 P500\n')  # Pause for 500ms

    # Update the volume in the well
    if isinstance(well_location, str) and well_location[0].isalpha():
        aspiration_module['V'][row, col] -= aspirated_volume
        current_volume = aspiration_module['V'][row, col]
    else:
        aspiration_module['V'][index] -= aspirated_volume
        current_volume = aspiration_module['V'][index]

    # Update the custom_preloads dictionary if a custom name was used
    if custom_name and custom_name in custom_preloads:
        custom_preloads[custom_name]['volume'] = current_volume

    # Move to a safe height if module is specified
    if aspiration_module is not None:
        G1(z=aspiration_module['top'], feedrate=3000)

    # Aspirate air gap if enabled
    if air_gap:
        total_aspirated_volume += air_gap_volume
        G1(p=total_aspirated_volume, feedrate=300)
        print(f'G4 P100\n')  # Pause for 100ms

    # Update the current aspirated volume
    current_aspirated_volume = aspirated_volume
    current_deadpump_volume = deadpump_volume
    current_air_gap_volume = air_gap_volume

    # Update the current aspirated volume
    current_aspirated_volume = aspirated_volume
    current_deadpump_volume = deadpump_volume

    module_name = aspiration_module.get('name')
    if deadpump:
        print(f'-Added {deadpump_volume} μL dead pump')
    print(f'-Aspirated {aspirated_volume} μL from {module_name} location {well_location}')
    if air_gap:
        print(f'-Added {air_gap_volume} μL air gap')


def dispense_volume(dispensed_volumes=None, custom_name=None, dispense_modules=None,
                    well_locations=None, safe_dist=True, direct=False, dispense_feedrate=500, blowout=None,
                    touch_tip=False, dispense_height=None):
    """
    Dispense specified volumes to a list of well locations across multiple modules, adjusting the height as needed.
    If no module or location is specified, dispense at the current position.
    :param dispense_height:
    :param touch_tip: Option to touch tip by the rim of the module to make sure all liquid is dispensed
    :param dispensed_volumes: A list of volumes to dispense in μL corresponding to each well location
    :param dispense_modules: A list of modules being used (e.g., [tube1, tube2, plate_384_biorad])
    :param well_locations: A list of well locations corresponding to each module (e.g., [['1', 'A1'], ['2', 'B1']])
    :param safe_dist: Boolean to make the Z-axis height safe (Z65)
    :param direct: Boolean to move pipette tips directly to the well location
    :param dispense_feedrate: Velocity of dispense
    :param blowout: Blowing out remaining liquid at the tip of the pipette
    :param custom_name: Optional custom name for preloaded volume
    """
    global current_aspirated_volume, current_deadpump_volume, current_air_gap_volume

    # Convert single values to lists
    if not isinstance(dispensed_volumes, (list, tuple)):
        dispensed_volumes = [dispensed_volumes]
    if not isinstance(well_locations, (list, tuple)):
        well_locations = [well_locations]

    # Check if a custom-named preloaded volume is being used
    if custom_name and custom_name in custom_preloads:
        preload = custom_preloads[custom_name]
        dispense_modules = [preload['module']]
        well_locations = [[preload['well_location']]]
        current_volume = [[preload['volume']]]

    if not isinstance(dispense_modules, list):
        dispense_modules = [dispense_modules]
    if not isinstance(well_locations, list):
        well_locations = [well_locations]
    if not isinstance(dispensed_volumes, list):
        dispensed_volumes = [dispensed_volumes]

    first_move = safe_dist  # Flag to track the first move

    total_volume = current_air_gap_volume + current_aspirated_volume + current_deadpump_volume

    for module, locations, volumes in zip(dispense_modules, well_locations, dispensed_volumes):
        # Ensure locations and volumes are lists
        if not isinstance(locations, list):
            locations = [locations]
        if not isinstance(volumes, list):
            volumes = [volumes]

        for well_location, dispensed_volume in zip(locations, volumes):
            # If no dispensed volume is specified, use the current aspirated volume
            if dispensed_volume == current_aspirated_volume:
                dispensed_volume = current_aspirated_volume
            elif dispensed_volume is None:
                dispensed_volume = current_aspirated_volume
            elif dispensed_volume > current_aspirated_volume:
                print(
                    f"Warning: Attempting to dispense {dispensed_volume} μL, but only {current_aspirated_volume} μL is available.")
                dispensed_volume = current_aspirated_volume

            if module is None or well_location is None:
                # Dispense air gap first if present
                if current_air_gap_volume > 0:
                    volume_to_dispense = total_volume - current_air_gap_volume
                    G1(p=volume_to_dispense, feedrate=dispense_feedrate)
                    total_volume -= current_air_gap_volume
                    current_air_gap_volume = 0
                # Dispense the volume
                volume_to_dispense = total_volume - dispensed_volume
                G1(p=volume_to_dispense, feedrate=dispense_feedrate)
                total_volume -= dispensed_volume
            else:
                # Move to the well location
                if first_move:
                    move_to_well_location(module, well_location, safe_dist=first_move, direct=direct)
                    first_move = False
                else:
                    move_to_well_location(module, well_location, safe_dist=first_move, direct=True)

                # Get the current volume in the well
                if isinstance(well_location, str) and well_location[0].isalpha():
                    # For plate wells (e.g., 'A1')
                    row = ord(well_location[0].upper()) - ord('A')
                    col = int(well_location[1:]) - 1
                    current_volume = module['V'][row, col]
                else:
                    # For tube wells (e.g., '1')
                    index = int(well_location) - 1
                    current_volume = module['V'][index]

                # Calculate the dispensing height
                if dispense_height is None:
                    if isinstance(module, dict) and module.get('name') == '384-well plate (BioRad)':
                        # For 384-well plate, set dispensing height 0.5 mm above liquid surface
                        if current_volume > 0:
                            dispensing_height = module['height'](current_volume) + 0.5
                        else:
                            dispensing_height = module['Z0'] + 1
                    else:
                        # For other modules, keep the existing logic
                        if current_volume > 0:
                            dispensing_height = module['height'](current_volume) + 1.5  # 1.5mm above the liquid surface
                        else:
                            dispensing_height = module['Z0'] + 1  # 1mm above the Z0 of the empty well
                else:
                    dispensing_height = module['height'](dispense_height)
                # Move to the initial dispensing height
                G1(z=dispensing_height, feedrate=3000)

                # Dispense air gap first if present
                if current_air_gap_volume > 0:
                    volume_to_dispense = total_volume - current_air_gap_volume
                    G1(p=volume_to_dispense, feedrate=dispense_feedrate)
                    total_volume -= current_air_gap_volume
                    current_air_gap_volume = 0
                # Dispense the volume
                volume_to_dispense = total_volume - dispensed_volume
                G1(p=volume_to_dispense, feedrate=dispense_feedrate)
                total_volume -= dispensed_volume

                # Update the volume in the well
                if isinstance(well_location, str) and well_location[0].isalpha():
                    module['V'][row, col] += dispensed_volume
                    current_volume = module['V'][row, col]
                else:
                    module['V'][index] += dispensed_volume
                    current_volume = module['V'][index]

                if custom_name and custom_name in custom_preloads:
                    custom_preloads[custom_name]['volume'] = current_volume

            # Update the current aspirated volume
            current_aspirated_volume -= dispensed_volume

            # Perform blowout with the deadpump volume if specified
            if blowout and current_deadpump_volume > 0:
                if isinstance(module, dict) and module.get('name') == '384-well plate (BioRad)':
                    # For 384-well plate, set dispensing height 1 mm above liquid surface
                    if current_volume > 0:
                        blowout_height = module['height'](current_volume) + 0.5
                    else:
                        blowout_height = module['Z0'] + 1
                else:
                    # For other modules, keep the existing logic
                    if current_volume > 0:
                        blowout_height = module['height'](current_volume) + 1.5  # 1.5mm above the liquid surface
                    else:
                        blowout_height = module['Z0'] + 1  # 1mm above the Z0 of the empty well
                G1(z=blowout_height, feedrate=3000)
                G1(p=0, feedrate=1000)  # Dispense the remaining liquid
                current_deadpump_volume = 0

            if touch_tip:
                # Perform touch tip by moving in a circular path around the inner radius of the module
                x_start = module['X'][row, col] if isinstance(well_location, str) and well_location[0].isalpha() else \
                    module['X'][index]
                radius = module['radius']
                x_start -= radius
                y_start = module['Y'][row, col] if isinstance(well_location, str) and well_location[0].isalpha() else \
                    module['Y'][index]
                touch_tip_height = module['top'] - 2  # 2mm below the top

                # Move to specified Z height
                G1(z=touch_tip_height, feedrate=3000)

                # Start clockwise circular movement
                G1(x=x_start, feedrate=3000)
                G2(x=x_start, y=y_start, i=-radius, j=0, feedrate=1000)
                x_center = x_start + radius
                G1(x=x_center, feedrate=3000)

            # Move to a safe height if module is specified
            if module is not None:
                G1(z=module['top'], feedrate=3000)
                module_name = module['name']
                print(f'-Dispensed {dispensed_volume} μL to {module_name} location {well_location}')


def mix(num_cycles, mix_volume=None, custom_name=None, module=None, well_location=None, mix_height=None, deadpump=True,
        blowout=True,
        aspirate_feedrate=2500, dispense_feedrate=2500, safe_dist=True, direct=False, deadpump_vol=10):
    """
    Perform mixing operation in a specified plate well or tube.

    :param num_cycles: Number of mix cycles to perform.
    :param mix_volume: The volume to aspirate and dispense for mixing in μL.
    :param custom_name: Optional custom name for preloaded volume.
    :param module: The module being used (e.g., plate_384_biorad, tube1, tube2).
    :param well_location: The well location (e.g., 'A1', '1').
    :param mix_height: Height to perform mixing at (if None, uses default liquid height).
    :param deadpump: Boolean indicating whether to perform a dead pump operation before aspirating (default is True).
    :param blowout: Boolean indicating whether to perform a blowout operation after mixing (default is True).
    :param aspirate_feedrate: Velocity of aspiration (default is 2500).
    :param dispense_feedrate: Velocity of dispense (default is 2500).
    :param safe_dist: Boolean to make the Z-axis height safe before moving to the well location (default is True).
    :param direct: Boolean to move pipette tips directly to the well location without intermediate steps (default is False).
    :param deadpump_vol: Volume for the dead pump operation in μL (default is 10).
    """
    global custom_preloads

    # Check if a custom-named preloaded volume is being used
    if custom_name and custom_name in custom_preloads:
        preload = custom_preloads[custom_name]
        module = preload['module']
        well_location = preload['well_location']
        well_vol = preload['volume']
        if mix_volume is None:
            mix_volume = preload['volume']

    # Set default deadpump volume
    deadpump_volume = deadpump_vol if deadpump else 0

    # Ensure required parameters are provided
    if module is None or well_location is None or mix_volume is None:
        raise ValueError("-Module, well location, and mix volume must be provided or specified via custom name.")

    # Move to the well location
    move_to_well_location(module, well_location, safe_dist=safe_dist, direct=direct)

    # Aspirate deadpump
    G1(p=0, feedrate=1000)
    G1(p=deadpump_volume, feedrate=500)

    # Calculate mixing height
    if mix_height is None:
        adj_mix_height = module['Z0'] + 0.5  # 0.5 mm above bottom of the well/tube
    else:
        adj_mix_height = module['height'](mix_height)

    # Perform mixing cycles
    for i in range(num_cycles):
        # Move to mixing height
        G1(z=adj_mix_height, feedrate=3000)
        # Aspirate
        if mix_volume > 95:
            adj_mix_volume = 95
        else:
            adj_mix_volume = mix_volume
        adj_mix_volume += deadpump_volume
        G1(p=adj_mix_volume, feedrate=aspirate_feedrate)
        lag = 1
        print(f'G4 P{lag * 1000}\n')  # G4 P<duration in milliseconds>
        adj_mix_volume -= deadpump_volume
        dispense_height = well_vol - adj_mix_volume
        adj_dispense_height = module['height'](dispense_height)
        G1(z=adj_dispense_height, feedrate=3000)
        # Dispense
        G1(p=deadpump_volume, feedrate=dispense_feedrate)
        lag = 1
        print(f'G4 P{lag * 1000}\n')  # G4 P<duration in milliseconds>

    if blowout and deadpump_volume > 0:
        if isinstance(module, dict) and module.get('name') == '384-well plate (BioRad)':
            # For 384-well plate, set dispensing height 1 mm above liquid surface
            blowout_height = module['height'](mix_volume) + 1
        else:
            # For tubes, set dispensing height 2 mm above liquid surface
            blowout_height = module['height'](mix_volume) + 2
        G1(z=blowout_height, feedrate=3000)
        G1(p=0, feedrate=1000)  # Dispense the remaining liquid
    # Move to a safe height
    G1(z=module['top'], feedrate=3000)

    adj_mix_volume -= deadpump_volume
    module_name = module.get('name')
    print(f"-Mixed {adj_mix_volume} μL in {module_name} location {well_location} for {num_cycles} cycles")


def heat(temperature, duration, height_adj=0, safe_dist=True, direct=False):
    """
    Heats pipette tips to a specified temperature and incubates for a given duration.

    :param temperature: Set temperature in Celsius.
    :param duration: Duration of heating in seconds.
    :param height_adj: Height adjustment for the Z-axis when moving to the heating location (default is 0).
    :param safe_dist: Boolean to make the Z-axis height safe before moving to the heater location (default is True).
    :param direct: Boolean to move pipette tips directly to the heater location without intermediate steps (default is False).
    """
    # Move to the pipette heater location
    if safe_dist:
        G1(z=65, feedrate=3000)  # Move to a safe height first

    if direct:
        G1(x=pipette_heater['X'], y=pipette_heater['Y'], z=pipette_heater['top'], feedrate=3000)
    else:
        G1(x=pipette_heater['X'], feedrate=3000)  # Move to the heater's X coordinate
        G1(y=pipette_heater['Y'])  # Move to the heater's Y coordinate
        G1(z=pipette_heater['top'])  # Move down to the top of the heater

    # Heat to the specified temperature and wait until it reaches the temperature
    print(f'M190 S{temperature}\n')

    # Pipette heating location
    G1(z=pipette_heater['bottom'] + height_adj)

    # Incubate for the specified duration
    print(f'G4 P{duration * 1000}\n')  # G4 P<duration in milliseconds>

    # Set the temperature to room temperature (assuming room temperature is 25°C)
    print('M140 S22\n')

    # Move to a safe height after heating
    G1(z=65, feedrate=3000)


def pipette_pellet(feedrate=100, pellet_duration=60,  # Duration in seconds
                   custom_name=None, module=None, location=None, safe_dist=True, direct=False, touch_tip=False,
                   pellet_height='Z0',  # 12.2 suggested pellet height
                   action=None, action_feedrate=100, deadpump=True, volume=None,
                   double_pellet=False, double_pellet_height='Z0', double_pellet_duration=60,
                   initial_dispense_vol=50):
    """
    Move the pipette to the specified locations in 0.2mL tube, and handle Z-axis movement from Z35.2 to Z0 at given feedrate

    :param feedrate: The speed at which the pipette should move (default is 100).
    :param pellet_duration: Duration in seconds for which the beads are pelleted (default is 60 seconds).
    :param custom_name: Optional custom name for preloaded volume. If provided, it overrides the module and location parameters.
    :param module: The module being used (e.g., tube3). Required if custom_name is not provided.
    :param location: The well location (e.g., '13'). Required if custom_name is not provided. Must be between 13 and 24.
    :param safe_dist: Boolean to make the Z-axis height safe before moving to the well location (default is True).
    :param direct: Boolean to move pipette tips directly to the well location without intermediate steps (default is False).
    :param touch_tip: If True, the pipette will perform a touch tip operation after dispensing (default is False).
    :param pellet_height: The height to which the pipette should move for pelleting (default is 'Z0'). Ideal pellet height is 12.2
    :param action: The action to perform, either 'aspirate' or 'dispense'. If 'aspirate', the pipette will aspirate the specified volume. If 'dispense' the pipette will dispense the aspirate volume
    :param action_feedrate: The feedrate for the action (default is 100).
    :param deadpump: If True, a dead pump operation is performed before aspirating (default is True).
    :param volume: The volume to aspirate or dispense. Required if action is specified.
    :param double_pellet: If True, a second pelleting operation is performed (default is False).
    :param double_pellet_height: The height for the second pelleting operation (default is 'Z0').
    :param double_pellet_duration: Duration in seconds for the second pelleting operation (default is 60 seconds).
    :param initial_dispense_vol: Initial volume to dispense before the main dispense operation (default is 50).
    """

    # Check if a custom-named preloaded volume is being used
    if custom_name and custom_name in custom_preloads:
        preload = custom_preloads[custom_name]
        module = preload['module']
        location = preload['well_location']

    # Validate the provided module and location
    if module is None or location is None:
        raise ValueError("-Module and location must be specified if custom_name is not provided.")

    # Ensure the location is between 13 and 24
    if not (13 <= int(location) <= 24):
        raise ValueError("-Invalid location. Please choose a location between 13 and 24.")

    # Move to well location
    if safe_dist:
        G1(z=65, feedrate=3000)  # Move to a safe height first
        if action == 'aspirate' and deadpump:
            dead_pump()
    x_coord = module['X'][int(location) - 1]
    y_coord = module['Y'][int(location) - 1]
    if direct:
        G1(x=x_coord, y=y_coord, feedrate=3000)
    else:
        G1(x=x_coord, feedrate=3000)
        G1(y=y_coord)

    # Move to the Z location of 35.2
    G1(z=35.2, feedrate=3000)

    # Move to the bottom of the well
    if pellet_height == 'Z0':
        pellet_height = module['Z0'] + 2
    G1(z=pellet_height, feedrate=feedrate)

    # Pellet beads for specified duration
    print(f'G4 P{pellet_duration * 1000}\n')  # G4 P<duration in milliseconds>

    if double_pellet:
        G1(z=double_pellet_height, feedrate=3000)
        # Pellet beads for specified duration
        print(f'G4 P{double_pellet_duration * 1000}\n')  # G4 P<duration in milliseconds>

    if action == 'aspirate':
        G1(z=module['Z0'], feedrate=3000)
        aspirate_volume(volume, aspirate_feedrate=action_feedrate)
        G1(z=12.2, feedrate=100)

    elif action == 'dispense':
        if double_pellet:
            G1(p=initial_dispense_vol, feedrate=500)
            G1(p=10, feedrate=50)
            G1(z=module['top'] - 5)
            G1(p=0, feedrate=1000)
        else:
            G1(p=initial_dispense_vol, feedrate=50)
            G1(p=10, feedrate=500)
            G1(z=module['top'] - 5)
            G1(p=0, feedrate=1000)
        if touch_tip:
            # Perform touch tip by moving in a circular path around the inner radius of the module
            x_start = module['X'][int(location) - 1]
            radius = module['radius']
            x_start -= radius
            y_start = module['Y'][int(location) - 1]
            touch_tip_height = module['top'] - 2  # 2mm below the top

            # Move to specified Z height
            G1(z=touch_tip_height, feedrate=3000)

            # Start clockwise circular movement
            G1(x=x_start, feedrate=3000)
            G2(x=x_start, y=y_start, i=-radius, j=0, feedrate=1000)
            x_center = x_start + radius
            G1(x=x_center, feedrate=3000)

    G1(z=module['top'], feedrate=3000)

    print(f"-Pipette pelletted module {module['name']} at location {location} with feedrate {feedrate}.")


def pipette_mix(num_cycles, lower_limit=50, upper_limit=100, mix_feedrate=1000):
    """
    Perform a mixing operation inside of the pipette (to dislodge beads) between specified limits for a given number of cycles.

    :param num_cycles: Number of mixing cycles to perform.
    :param lower_limit: The lower limit of the pipette movement during mixing (default is 50).
    :param upper_limit: The upper limit of the pipette movement during mixing (default is 100).
    :param mix_feedrate: The speed at which the pipette should move during mixing (default is 1000).
    """

    for i in range(num_cycles):
        G1(p=lower_limit, feedrate=mix_feedrate)
        print(f'G4 P500\n')  # lag
        G1(p=upper_limit, feedrate=mix_feedrate)
        print(f'G4 P500\n')  # lag


def end():
    G1(z=65, feedrate=3000)
    G1(x=10)
    G1(y=100)
    G1(z=40)
