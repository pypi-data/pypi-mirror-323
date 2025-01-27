"""
Credential Extractor

A Python module designed to extract sensitive credentials such as emails, phone numbers, and passwords 
from HTML files. It offers two key functions for extracting credentials: one for single HTML files, 
and another for processing entire directories of HTML files.

Main Functions:
- extract_credentials: This function extracts credentials (emails, phone numbers, and associated passwords) 
  from a single HTML file.
- extract_credentials_dir: This function extracts credentials from all HTML files within a specified directory.

Usage:
    To extract credentials from a directory of HTML files, simply provide the path to the directory 
    to the `extract_credentials_dir` function. It will process all `.html` files in that directory 
    and print the extracted credentials.

    Example:
        >>> from Credential_Extractor_001 import extract_credentials_dir
        >>> extract_credentials_dir('./path_to_html_files')

Dependencies:
- BeautifulSoup (bs4): Used for parsing HTML content and extracting the relevant data.
- re (Regular Expressions): Used for detecting phone number patterns.

Author:
- a random dude

License:
- MIT License (or specify your preferred license)
"""

from .extractor import extract_credentials, extract_credentials_dir