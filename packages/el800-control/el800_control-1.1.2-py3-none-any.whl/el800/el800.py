import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.backends.backend_pdf import PdfPages
import serial
import csv

# Function to plot a 96-well plate with OD600 values
def plot_96_well_plate(data, output_pdf):

    # Plate dimensions
    rows = 8
    cols = 12
    well_radius = 0.4

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(cols, rows))
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.axis('off')

    # Row and column labels
    row_labels = [chr(i) for i in range(65, 65 + rows)]  # A-H
    col_labels = list(range(1, cols + 1))

    # Draw wells and add OD600 values
    for i, row_label in enumerate(row_labels):
        for j, col_label in enumerate(col_labels):
            x = j + 0.5
            y = rows - i - 0.5
            # Draw circle for the well
            circle = Circle((x, y), well_radius, edgecolor='black', facecolor='white')
            ax.add_patch(circle)
            # Add OD600 value as text
            od_value = data[i][j]
            ax.text(x, y, f"{od_value:.3f}", ha='center', va='center', fontsize=6)

    # Add row and column labels
    for i, row_label in enumerate(row_labels):
        ax.text(0, rows - i - 0.5, row_label, ha='right', va='center', fontsize=8)
    for j, col_label in enumerate(col_labels):
        ax.text(j + 0.5, rows, str(col_label), ha='center', va='bottom', fontsize=8)

    # Save to PDF
    with PdfPages(output_pdf) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)



def communicate_with_serial(port):
    # Configure the serial port
    baudrate = 9600
    timeout = 1  # Timeout in seconds

    try:
        # Open the serial port
        with serial.Serial(port, baudrate=baudrate, bytesize=serial.EIGHTBITS,
                           stopbits=serial.STOPBITS_TWO, parity=serial.PARITY_NONE, timeout=timeout) as ser:

            # Send the 'D' character
            ser.write(b'D')

            # Read 657 bytes from the port
            data = ser.read(657)
            return data

    except serial.SerialException as e:
        print(f"Error: {e}")
        return None


def extract_string(data):
    try:
        # Ensure data is binary-safe
        start_index = 2
        end_keyword = b'\x1A\x1E'
        
        # Find the position of the keyword 'ASSAY'
        end_index = data.find(end_keyword)
        
        if end_index == -1:
            data_len=len(data)
            raise ValueError(f"Keyword '0x1A0x1E' not found in data len={data_len}.")

        # Extract the substring from position 2 to the keyword
        result = data[start_index:end_index].decode('ascii', errors='ignore')
        return result

    except Exception as e:
        print(f"Error during string extraction: {e}")
        return None
    
def csv_to_matrix(csv_string):
    """
    Converts a string of comma-separated values into a matrix of numbers, ignoring the first value before the first comma on each line.

    Args:
        csv_string (str): The input string containing lines of comma-separated values.

    Returns:
        list[list[float]]: A matrix where each inner list represents a row of numbers.
    """
    try:
        # Split the string into lines
        lines = csv_string.strip().split('\n')

        # Convert each line into a list of floats, ignoring the first value (empty or not)
        matrix = [list(map(float, line.split(',')[1:])) for line in lines if line.strip()]

        return matrix
    except ValueError as e:
        print(f"Error converting string to matrix: {e}")
        return None

def write_matrix_to_csv(matrix, file_path):
    """
    Writes a 2D number array to a tab-separated CSV file.

    Args:
        matrix (list[list[float]]): The 2D number array to write.
        file_path (str): The path to the output CSV file.

    Returns:
        None
    """
    try:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerows(matrix)
    except IOError as e:
        print(f"Error writing to file: {e}")

import os

def convert_pdf_to_csv(filename):
    if filename.endswith('.pdf'):
        new_filename = filename[:-4] + '.csv'
        return new_filename
    else:
        print("The file does not have a .pdf extension.")
        return filename

def read_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()
            print(f"Read {len(data)} bytes from the file.")
            return data
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except IOError as e:
        print(f"Error reading file: {e}")

def el800_export(received_data, out_file):
    
    if received_data is None:
        return

    datamatrix = extract_string(received_data)
    
    valuematrix = csv_to_matrix(datamatrix)
    
    valuematrix = [[value / 1000 for value in row] for row in valuematrix]

    plot_96_well_plate(valuematrix, out_file)
    print(f"96-well plate diagram saved to {out_file}")
    
    csvfile = convert_pdf_to_csv(out_file)
    write_matrix_to_csv(valuematrix, csvfile)
    print(f"96-well plate diagram saved to {csvfile}")
