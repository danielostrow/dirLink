import os
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import json
import subprocess

URL_REGEX_PATTERN = r'(https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[\w./?=#&%~-]*))'

def browse_directory():
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        scan_directory(selected_directory)

def scan_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            scan_file(file_path)

def scan_file(file_path):
    print(f"Scanning file: {file_path}")
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.pdf':
        extract_links_from_pdf(file_path)
    else:
        extract_links_from_file(file_path)

def extract_links_from_pdf(file_path):
    try:
        output = subprocess.check_output(['pdftotext', '-q', '-enc', 'UTF-8', '-nopgbrk', file_path, '-'])
        content = output.decode('utf-8', errors='ignore')
        links = re.findall(URL_REGEX_PATTERN, content)
        visible_links = filter_visible_links(links)
        if visible_links:
            print(f"Links found in {file_path}:")
            for link in visible_links:
                print(f"  - {link}")
            print()
            display_links(file_path, visible_links)
        
        # Extract links from the last page of the PDF panel
        last_page_content = get_last_page_content(file_path)
        links_last_page = re.findall(URL_REGEX_PATTERN, last_page_content)
        visible_links_last_page = filter_visible_links(links_last_page)
        if visible_links_last_page:
            print(f"Links found in the last page of {file_path}:")
            for link in visible_links_last_page:
                print(f"  - {link}")
            print()
            display_links(file_path, visible_links_last_page)
            
    except subprocess.CalledProcessError:
        pass

def get_last_page_content(file_path):
    output = subprocess.check_output(['pdftotext', '-q', '-enc', 'UTF-8', '-f', '-1', '-l', '-1', file_path, '-'])
    content = output.decode('utf-8', errors='ignore')
    return content

def extract_links_from_file(file_path):
    try:
        output = subprocess.check_output(['strings', file_path])
        content = output.decode('utf-8', errors='ignore')
        links = re.findall(URL_REGEX_PATTERN, content)
        visible_links = filter_visible_links(links)
        if visible_links:
            print(f"Links found in {file_path}:")
            for link in visible_links:
                print(f"  - {link}")
            print()
            display_links(file_path, visible_links)
    except subprocess.CalledProcessError:
        pass

def filter_visible_links(links):
    visible_links = []
    for link in links:
        if '.' in link:
            visible_links.append(link)
    return visible_links

def display_links(file_path, links):
    file_name = os.path.basename(file_path)
    item_id = get_tree_item_id(file_name)
    for link in links:
        tree.insert(item_id, 'end', text=link)

def get_tree_item_id(file_name):
    for item in tree.get_children():
        if tree.item(item, 'text') == file_name:
            return item
    return tree.insert('', 'end', text=file_name)

def export_to_json():
    links_data = {}
    items = tree.get_children()
    for item_id in items:
        file_name = tree.item(item_id, 'text')
        links = tree.get_children(item_id)
        links_list = []
        for link_id in links:
            link = tree.item(link_id, 'text')
            links_list.append(link)
        links_data[file_name] = links_list

    json_path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')])
    if json_path:
        with open(json_path, 'w') as f:
            json.dump(links_data, f, indent=4)
        print(f"Links exported to {json_path}")

# Create a GUI window
root = tk.Tk()
root.title("Link Scanner")
root.geometry("600x400")

# Create a TreeView widget to display the links
tree = ttk.Treeview(root)
tree.heading('#0', text='Files')
tree.pack(fill=tk.BOTH, expand=True)

# Add a button to browse the directory
browse_button = tk.Button(root, text="Browse", command=browse_directory)
browse_button.pack(pady=10)

# Add a button to export links to JSON
export_button = tk.Button(root, text="Export to JSON", command=export_to_json)
export_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()
