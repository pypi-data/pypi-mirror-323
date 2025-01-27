"""
This module provides functions for converting HTML files to text format, 
processing HTML files in a directory, and combining the resulting text files.

Functions:
    format_html_to_text(input_file) -> str
    process_html_directory(input_dir, output_dir) -> None
    combine_text_files(input_dir, output_file) -> None
    extract(inp_folder='./yay', out_folder='./output_texts', out_file='combined.txt', rmtr=False) -> None
"""

from .extractor import format_html_to_text, process_html_directory, combine_text_files, extract
