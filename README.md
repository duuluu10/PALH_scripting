# README #

This is a repository for all the scripts 

### Calibration ###

List of calibration codes to run before running any protocol:
* Z_tip_calibration - Initial calibration test to make sure the pipette tips are barely touching the bed (use post-it note to make sure minimum spacing) 
* plate_384_biorad_cal_test - Calibration test for moving the motors to edge wells of a 384-well plate (biorad)
* tube_only_calibration_test - Calibration test for moving the motors to the tube locations (Tube1, Tube2, Tube3)

### Protocol_py / Gcode_protocol_library ###

Protocol_py: Example library of Python codes for generating .gcode lines.
Gcode_protocol_library: Generated example Gcode protocols from the corresponding .py files.

Example workflows:
* magnetic_extraction_w_heater.py - Magnetic bead based extraction of nucleic acid from crude sample
* pUC19_amplification - End-point PCR amplification setup for pUC19 vector
* pUC19_cleanup - Magnetic bead based cleanup of amplified pUC19 products
* RPLP0_qPCR_protocol - qPCR amplification setup for housekeeping gene RPLP0

---

### Acknowledgement ###

* Tripathi Lab

For questions, issues, or feature requests, please open an issue in this repository or contact duuluu@brown.edu