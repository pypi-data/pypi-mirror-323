import os
import re
import shutil
from bs4 import BeautifulSoup



inp_folder = './yay'
out_folder = './output_texts'
out_file = 'combined.txt'



def format_html_to_text(input_file):
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


def extract(inp, out):
    # Extract the txt file
    input_directory = inp
    output_directory = out
    process_html_directory(input_directory, output_directory)

def combine(inp, out):
    # Combine text into 1 file
    input_directory = inp
    output_filename = out
    combine_text_files(input_directory, output_filename)



extract(inp_folder, out_folder)
combine(out_folder, out_file)

#shutil.rmtree('./output_texts')
