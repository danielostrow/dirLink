import os
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess
import webbrowser
import requests
from requests.exceptions import MissingSchema


URL_REGEX_PATTERN = r'(https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[\w./?=#&%~-]*))'


def browse_directory():
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        scan_directory(selected_directory)


def scan_directory(directory):
    files = get_all_files(directory)
    total_files = len(files)
    progress_bar['maximum'] = total_files
    status_label.config(text="Scanning...")
    root.update_idletasks()
    for i, file_path in enumerate(files):
        scan_file(file_path)
        progress_bar['value'] = i + 1
        percentage = int((i + 1) / total_files * 100)
        status_label.config(text=f"Scanning... {percentage}%")
        root.update_idletasks()
    status_label.config(text="Scanning complete!")


def get_all_files(directory):
    files = []
    for root, _, file_names in os.walk(directory):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            files.append(file_path)
    return files


def scan_file(file_path):
    print(f"Scanning file: {file_path}")
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.pdf':
        extract_links_from_pdf(file_path)
        extract_links_from_panel(file_path)
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
    except subprocess.CalledProcessError:
        pass


def extract_links_from_panel(file_path):
    try:
        panel_content = extract_panel_content(file_path)
        links_panel = re.findall(URL_REGEX_PATTERN, panel_content)
        visible_links_panel = filter_visible_links(links_panel)
        if visible_links_panel:
            print(f"Links found in the panel object of {file_path}:")
            for link in visible_links_panel:
                print(f"  - {link}")
            print()
            display_links(file_path, visible_links_panel)
    except subprocess.CalledProcessError:
        pass


def extract_panel_content(file_path):
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
    visible_links = set()
    for link in links:
        if '.' in link:
            visible_links.add(link)
    return visible_links


def display_links(file_path, links):
    file_name = os.path.basename(file_path)
    directory = os.path.dirname(file_path)

    # Find the directory item
    directory_item_id = get_tree_item_id('', directory)
    if not directory_item_id:
        directory_item_id = tree.insert('', 'end', text=directory)

    # Find the file item
    file_item_id = get_tree_item_id(directory_item_id, file_name)
    if not file_item_id:
        file_item_id = tree.insert(directory_item_id, 'end', text=file_name)

    # Add links with status codes
    for link in links:
        if not is_link_duplicate(file_item_id, link):
            status_code = get_link_status(link)
            tree.insert(file_item_id, 'end', values=[link, status_code])

    root.update_idletasks()


def is_link_duplicate(file_item_id, link):
    links = tree.get_children(file_item_id)
    for link_id in links:
        if tree.item(link_id, 'values')[0] == link:
            return True
    return False


def get_tree_item_id(parent_id, text):
    for item_id in tree.get_children(parent_id):
        if tree.item(item_id, 'text') == text:
            return item_id
    return None


def get_link_status(link):
    try:
        response = requests.get(link)
        return response.status_code
    except MissingSchema:
        return 0


def open_url(event):
    item_id = tree.focus()
    if item_id:
        values = tree.item(item_id, 'values')
        link = values[0]
        if link:
            webbrowser.open_new(link)


# Create a GUI window
root = tk.Tk()
root.title("Link Scanner")
root.geometry("1000x400")  # Increase the window size

# Create a TreeView widget to display the links
tree = ttk.Treeview(root)
tree.heading('#0', text='Files')
tree.column("#0", width=400)  # Adjust the column width for files

# Add a column for the link
tree['columns'] = ('link', 'status')
tree.heading('link', text='Link')
tree.column('link', width=400)  # Adjust the column width for links

# Add a column for the status
tree.heading('status', text='Status')
tree.column('status', width=100)  # Adjust the column width for status

tree.bind('<Double-1>', open_url)
tree.pack(fill=tk.BOTH, expand=True)

# Add a progress bar
progress_bar = ttk.Progressbar(root, mode='determinate')
progress_bar.pack(pady=10)

# Add a label to display the status
status_label = tk.Label(root, text="Select a directory to scan.")
status_label.pack()

# Add a button to browse the directory
browse_button = tk.Button(root, text="Browse", command=browse_directory)
browse_button.pack(pady=10)

# Start the main event loop
root.mainloop()
