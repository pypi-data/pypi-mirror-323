import os
import argparse
from el800 import el800
from el800 import el800_window

def main():
    """
    Command-line interface for the file parser using argparse.
    """
    parser = argparse.ArgumentParser(
        description="Utility for extracting reports from a EL800. cite: 10.5281/zenodo.14512335")
    parser.add_argument("--input_file", default= None, help="Path to the input file.")
    parser.add_argument("output_file", help="Path to the output file.")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="serial port specification.")

    args = parser.parse_args()
    
    print(f"citation: 10.5281/zenodo.14512335")
    
    # Validate input file
    if args.input_file is None or not (os.path.isfile(args.input_file)):
        if args.port is None:
            print(f"--port or --input_file must be specified!")
            return
        received_data = el800.communicate_with_serial(args.port)
    else:
        received_data = el800.read_file(args.input_file)
        
    if received_data is not None:
        el800.el800_export(received_data, args.output_file)

def main_gui():
    el800_window.gui()
    