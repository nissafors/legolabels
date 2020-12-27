import argparse
import sys

genfile_info = """The generator file contains part numbers and/or text and settings for pages and labels in JSON format. Valid keys are:

Required:
    labels: {parts, parts, ...}             Definitions of part info for each label.
    parts: [string, string, ...]            List of Lego(TM) part numbers for a label.
    ...and/or:
    text: string                            Text to print on label.

Optional:
    page_size: [int, int]                   Width and height of page in mm.
                                            (Default: 210, 297)
    page_margins: [int, int, int, int]      Top, right, bottom and left page margins in mm.
                                            (Default: 15, 15, 15, 15)
    label_size: [int, int]                  Width an height of each label in mm.
                                            (Default: 60, 25)
    label_margins: [int, int, int, int]     Top, right, bottom and left label margins in mm.
                                            (Default: 2, 4, 2, 4)
    spacing: int                            Spacing between images in labels.
                                            (Default: 2)
    dpi: int                                Resolution.
                                            (Default: 300)
    dot_size: float                         Size of ... dots printed when not all images defined for a label fits.
                                            (Default: 1.5)

Example:
    {
        "labels": {
            "parts": ["3005"],
            "parts": ["3007", "4202"],
            "text": "Mini figures"
        }
        "page_margins": [10, 10, 10, 10],
        "label_size": [80, 35],
        "label_margins": [5, 8, 5, 8],
        "spacing": 5,
        "dpi": 600
    }
"""

# Parse arguments
arg_parser = argparse.ArgumentParser("Create labels for Lego storage boxes.")
arg_parser.add_argument('-f', '--file', nargs=1, help='Generator file.', type=str)
arg_parser.add_argument('-i', '--info', action='store_true', help='Print info about the generator file format.')
if len(sys.argv) < 2:
    arg_parser.print_help()
    exit()
parse_result = arg_parser.parse_args()

# Print info
if parse_result.info:
    print(genfile_info, end='')
    exit()

