import os
import re
import shutil
from bs4 import BeautifulSoup

def format_html_to_text(input_file):
    """
    Converts an HTML file into a text format by extracting data from tables.

    Args:
        input_file (str): Path to the HTML file to be processed.

    Returns:
        str: A formatted text containing the data extracted from HTML tables. 
             Each row in the table is prefixed with a timestamp and app name.
    """
    with open(input_file, 'r', encoding='utf-8') as file:
        html = file.read()
    soup = BeautifulSoup(html, 'html.parser')
    output = []
    tables = soup.find_all('table')
    
    for table in tables:
        caption = table.find('caption')
        app_name = caption.text if caption else 'Unknown'
        rows = table.find_all('tr')
        current_timestamp = None
        for row in rows:
            header = row.find('th')
            if header:
                current_timestamp = header.get_text(strip=True)
            cells = row.find_all('td')
            for cell in cells:
                text = cell.get_text(strip=True)
                if text and current_timestamp:
                    output.append(f'{current_timestamp} - {app_name} - {text}')
    
    return '\n'.join(output)

def process_html_directory(input_dir, output_dir):
    """
    Processes all HTML files in a directory, converting them to text files.

    Args:
        input_dir (str): Directory containing the HTML files to be processed.
        output_dir (str): Directory where the resulting text files will be saved.

    This function reads each HTML file in the input directory, converts its content
    using `format_html_to_text`, and writes the output to corresponding text files in 
    the specified output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.html'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.txt')
            formatted_output = format_html_to_text(input_path)
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(formatted_output)

def combine_text_files(input_dir, output_file):
    """
    Combines all text files in a directory into a single output file, 
    prepending a date header for each file.

    Args:
        input_dir (str): Directory containing the text files to combine.
        output_file (str): Path to the output file where combined content will be saved.

    This function reads each `.txt` file in the input directory, extracts the date 
    (from the filename) and combines them into a single output file.
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(input_dir):
            if filename.endswith('.txt'):
                # Extract the date from the filename
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
                if date_match:
                    date_str = date_match.group(0)
                else:
                    date_str = 'Unknown Date'
                
                file_path = os.path.join(input_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as infile:
                    # Write the differentiator, date, and file content to the output file
                    outfile.write("=====================\n")
                    outfile.write(f"Date: {date_str}\n")
                    outfile.write("=====================\n")
                    outfile.write(infile.read() + "\n")

def extract(inp_folder='./yay', out_folder='./output_texts', out_file='combined.txt', rmtr=False):
    """
    A high-level function to process HTML files from an input folder, convert them to text files, 
    combine those text files into a single output file, and optionally remove the output folder.

    Args:
        inp_folder (str): Path to the folder containing the HTML files. Default is './yay'.
        out_folder (str): Path to the folder where the converted text files will be saved. Default is './output_texts'.
        out_file (str): Path to the output file where all combined text will be saved. Default is 'combined.txt'.
        rmtr (bool): Flag to determine if the output folder should be removed after processing. Default is False.

    This function calls `process_html_directory` to convert HTML to text, and `combine_text_files` 
    to merge the text files. If `rmtr` is True, the output folder is removed after processing.
    """
    process_html_directory(inp_folder, out_folder)
    combine_text_files(out_folder, out_file)
    if rmtr:
        shutil.rmtree('./output_texts')
