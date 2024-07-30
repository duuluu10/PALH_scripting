# README #

This repository contains all Personal Automated Liquid Handling (PALH) system scripting codes. 

### Calibration ###

List of calibration codes to run before running any protocol:
* Z_tip_calibration - Initial calibration test to make sure the pipette tips are barely touching the bed (use a post-it note to make sure minimum spacing) 
* plate_384_biorad_cal_test - Calibration test for moving the motors to edge wells of a 384-well plate (biorad)
* tube_only_calibration_test - Calibration test for moving the motors to the tube locations (Tube1, Tube2, Tube3)

### Protocol_py / Gcode_protocol_library ###

Use the "gcode_generator_v1_2.py" to reference useful functions for creating a new protocol .gcode file. Use "new_script.py" to write a new protocol. Use the example .py files as a reference.
To test generated codes, use the local terminal to run the "gcode_generator_v1_2.py," which will print out all the terms and generate a new .gcode file. Use a 3D printer controller such as Printrun (https://www.pronterface.com/) to test protocols on the PALH from local machine or transfer the generated .gcode on a microSD card to run protocols directly on the 3D printer.
Gcode_protocol_library: Generated example Gcode protocols from the corresponding .py files.

Example workflows:
* magnetic_extraction_w_heater.py - Magnetic bead-based extraction of nucleic acid from a crude sample
* pUC19_amplification - End-point PCR amplification setup for pUC19 vector
* pUC19_cleanup - Magnetic bead-based cleanup of amplified pUC19 products
* RPLP0_qPCR_protocol - qPCR amplification setup for housekeeping gene RPLP0

---

### Acknowledgement ###

* Tripathi Lab

For questions, issues, or feature requests, please open an issue in this repository or contact duuluu@brown.edu
