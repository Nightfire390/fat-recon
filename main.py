import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# TEST CLI START
import sys
import subprocess

from misc.reading_sectors import *
from misc.printing_banners import *
from analyses.analysing_boot_sector import *
from analyses.analysing_directory import *
from analyses.analysing_subfolders import *

def get_root(path):

    global partition_path 
    partition_path = path

    # Reading Boot Sector (Sector 0)
    boot_sector = read_sector(partition_path, start_sector = 0, end_sector = 1)

    # Analysing Boot Sector
    boot_sector_analysis = analyse_boot_sector(boot_sector)

    global sectors_per_cluster

    root_directory_sector = boot_sector_analysis["root_directory_sector"]
    sectors_per_cluster = boot_sector_analysis["sectors_per_cluster"]
    data_region_sector = boot_sector_analysis["data_region_sector"]

    # Reading Root Directory Sector
    root_directory = read_sector(partition_path, start_sector = root_directory_sector, end_sector = data_region_sector)

    # Creating Root Entries
    root_entries = create_directory_entries(root_directory)

    # Analying Root Directory
    path = "root"
    
    global sfn_existing_files_analysis, sfn_deleted_files_analysis, sfn_existing_folders_analysis, sfn_deleted_folders_analysis

    sfn_existing_files_analysis, sfn_deleted_files_analysis, sfn_existing_folders_analysis, sfn_deleted_folders_analysis = analyse_directory(root_entries, sectors_per_cluster, data_region_sector, path)
   
    global existing_files_in_existing_folders, deleted_files_in_existing_folders, existing_folders_in_existing_folders, deleted_folders_in_existing_folders 
    
    existing_files_in_existing_folders, deleted_files_in_existing_folders, existing_folders_in_existing_folders, deleted_folders_in_existing_folders = analyse_existing_sub_folders(partition_path, sectors_per_cluster, data_region_sector, sfn_existing_folders_analysis)

    global existing_files_in_deleted_folders, deleted_files_in_deleted_folders, existing_folders_in_deleted_folders, deleted_folders_in_deleted_folders
    existing_files_in_deleted_folders, deleted_files_in_deleted_folders, existing_folders_in_deleted_folders, deleted_folders_in_deleted_folders = analyse_deleted_sub_folders(partition_path, sectors_per_cluster, data_region_sector, sfn_deleted_folders_analysis)

    for x in range(len(sfn_existing_folders_analysis)):
        sfn_existing_folders_analysis[x]['deleted'] = False

    for x in range(len(existing_folders_in_existing_folders)):
        existing_folders_in_existing_folders[x]['deleted'] = False

    for x in range(len(sfn_deleted_folders_analysis)):
        sfn_deleted_folders_analysis[x]['deleted'] = True

    for x in range(len(deleted_folders_in_deleted_folders)):
        deleted_folders_in_deleted_folders[x]['deleted'] = True
    
    for x in range(len(deleted_folders_in_existing_folders)):
        deleted_folders_in_existing_folders[x]['deleted'] = True
    
    for x in range(len(existing_folders_in_deleted_folders)):
        existing_folders_in_deleted_folders[x]['deleted'] = True

    return { "folders": [ sfn_existing_folders_analysis, existing_folders_in_existing_folders, sfn_deleted_folders_analysis, deleted_folders_in_existing_folders, existing_folders_in_deleted_folders, deleted_folders_in_deleted_folders], "files": [ sfn_existing_files_analysis, existing_files_in_existing_folders, sfn_deleted_files_analysis, deleted_files_in_existing_folders, existing_files_in_deleted_folders, deleted_files_in_deleted_folders]}


def recursive_folders(item, root, folder_name, labels):
    for i in range(6):
        for x in labels[i]:
            if x['path'] == root + folder_name + '/' + x['folder_name'] and x['deleted'] == False:
                it = treeview.insert(item, tk.END, text=x['folder_name'], tags=("show_files",))
                recursive_folders(it, root + folder_name + '/', x['folder_name'], labels)

def deleted_recursive_folders(item, root, folder_name, labels):
    for i in range(6):
        for x in labels[i]:
            if x['path'] == root + folder_name + '/' + x['folder_name'] and x['deleted']:
                it = treeview.insert(item, tk.END, text=x['folder_name'], tags=("show_files",), image=x_icon)
                deleted_recursive_folders(it, root + folder_name + '/', x['folder_name'], labels)

# TEST CLI END

# Function to handle label clicks
def on_label_click(label_text):
    result_display.config(text=f"Selected: {label_text}")

# Function to handle file import (using file dialog)
def import_file():
    file_path = filedialog.askopenfilename(title="Select a file to import")
    perform_analysis(file_path)

def perform_analysis(file_path):
    h = read_sector(file_path, 0, 1)[86:96]
    
    fsinfo = "".join([ chr(int(h[x] + h[x+1], 16)) for x in range(0, len(h), 2) ])
    
    if "FAT" not in fsinfo:
        return None

    if file_path:
        labels = get_root(file_path)
        treeview.delete(*treeview.get_children())
        root_dir = treeview.insert("", tk.END, text="root", tags=("show_files"))
        
        # Folders
        for label in labels['folders'][0]:
            item = treeview.insert(root_dir, tk.END, text=label['folder_name'], tags=("show_files",))
            recursive_folders(item, 'root/', label['folder_name'], labels['folders'])
            deleted_recursive_folders(item, 'root/', label['folder_name'], labels['folders'])
            
        for label in labels['folders'][2]:
            item = treeview.insert(root_dir, tk.END, text=label['folder_name'], image=x_icon, tags=("show_files",)) 
            deleted_recursive_folders(item, 'root/', label['folder_name'], labels['folders'])
'''
        # Files
        for label in labels['files'][0]:
            item = fileview.insert("", tk.END, text=label['file_name'], values=(label['file_size'], f"{label['last_write_time']} {label['last_write_date']}"), tags=("read_file",))
        
        for label in labels['files'][2]:
            item = fileview.insert("", tk.END, text=label['file_name'], values=(label['file_size'], f"{label['last_write_time']} {label['last_write_date']}"), image=x_icon, tags=("read_file",))
'''      

def file_selected(event):
    folder_item = treeview.selection()[0]
 
    file_item = fileview.selection()[0]
    file_name = fileview.item(file_item, "text")
    
    path = []
    while folder_item:
        path.insert(0, treeview.item(folder_item, "text"))
        folder_item = treeview.parent(folder_item)
    
    path = "/".join(path) + '/' + file_name

    input_text.config(state = tk.NORMAL)

    for label in sfn_existing_files_analysis:
        if path.strip() == label['path']:
            sector = read_sector(partition_path, start_sector = label['first_sector'], end_sector = label['first_sector'] + sectors_per_cluster)
            data = ''.join([chr(int(sector[i:i+2], 16)) for i in range(0, len(sector), 2)])
            input_text.pack(fill=tk.BOTH)

            input_text.delete(1.0,tk.END)
            input_text.insert(tk.END, data.rstrip('\x00'))

            input_text.config(state = tk.DISABLED)
            return 

        # go to the file cluster and 
        
    for label in sfn_deleted_files_analysis:
        if path.strip() == label['path']:     
            sector = read_sector(partition_path, start_sector = label['first_sector'], end_sector = label['first_sector'] + sectors_per_cluster)
            data = ''.join([chr(int(sector[i:i+2], 16)) for i in range(0, len(sector), 2)])
            input_text.pack(fill=tk.BOTH)
            input_text.delete(1.0,tk.END)
            input_text.insert(tk.END, data.rstrip('\x00'))
            input_text.config(state = tk.DISABLED)
            return

        # go to the file cluster and 
    
    for label in existing_files_in_existing_folders:
        if path.strip() == label['path']: 
            sector = read_sector(partition_path, start_sector = label['first_sector'], end_sector = label['first_sector'] + sectors_per_cluster)
            data = ''.join([chr(int(sector[i:i+2], 16)) for i in range(0, len(sector), 2)])
            
            input_text.pack(fill=tk.BOTH)
            input_text.delete(1.0, tk.END)
            input_text.insert(tk.END, data.rstrip('\x00'))
            input_text.config(state = tk.DISABLED)
            return

        # go to the file cluster and 

    for label in deleted_files_in_existing_folders:
        if path.strip() == label['path']:     
            sector = read_sector(partition_path, start_sector = label['first_sector'], end_sector = label['first_sector'] + sectors_per_cluster)
            data = ''.join([chr(int(sector[i:i+2], 16)) for i in range(0, len(sector), 2)])
            
            input_text.pack(fill=tk.BOTH)
            input_text.delete(1.0,tk.END)
            input_text.insert(tk.END, data.rstrip('\x00'))
            input_text.config(state = tk.DISABLED)
            return

        # go to the file cluster and 
    
    for label in deleted_files_in_deleted_folders:
        if path.strip() == label['path']:     
            sector = read_sector(partition_path, start_sector = label['first_sector'], end_sector = label['first_sector'] + sectors_per_cluster)
            data = ''.join([chr(int(sector[i:i+2], 16)) for i in range(0, len(sector), 2)])
            
            input_text.pack(fill=tk.BOTH)
            input_text.delete(1.0,tk.END)
            input_text.insert(tk.END, data.rstrip('\x00'))
            input_text.config(state = tk.DISABLED)
            return

        # go to the file cluster and 
    
    for label in existing_files_in_deleted_folders:
        if path.strip() == label['path']:     
            sector = read_sector(partition_path, start_sector = label['first_sector'], end_sector = label['first_sector'] + label['file_size'])
            data = ''.join([chr(int(sector[i:i+2], 16)) for i in range(0, len(sector), 2)])
            
            input_text.pack(fill=tk.BOTH)
            input_text.delete(1.0,tk.END)
            input_text.insert(tk.END, data.rstrip('\x00'))
            input_text.config(state = tk.DISABLED)   
            return


def folder_selected(event):
    try:
        # Get the Id of the first selected item.
        item = treeview.selection()[0]
    except IndexError:
        # If the tuple is empty, there is no selected item.
        messagebox.showwarning(
            message="No selected item",
            title="Error"
        )
    else:
        fileview.delete(*fileview.get_children())

        path = []
        while item:
            path.insert(0, treeview.item(item, "text"))  
            item = treeview.parent(item)  
        
        path = "/".join(path) + '/'
        for label in sfn_existing_files_analysis:
            if f"{path}{label['file_name']}.{label['file_extension']}".strip() == label['path']:
                fileview.insert("", tk.END, text=label['file_name'] + '.' + label['file_extension'], values=(label['file_size'], f"{label['last_write_time']} {label['last_write_date']}"), tags=("read_file",))
        
        for label in sfn_deleted_files_analysis:
            if f"{path}{label['file_name']}.{label['file_extension']}".strip() == label['path']:
                fileview.insert("", tk.END, text=label['file_name'] + '.' + label['file_extension'], values=(label['file_size'], f"{label['last_write_time']} {label['last_write_date']}"), image=x_icon, tags=("read_file",))
        
        for label in existing_files_in_existing_folders:
            if f"{path}{label['file_name']}.{label['file_extension']}".strip() == label['path']:
                fileview.insert("", tk.END, text=label['file_name'] + '.' + label['file_extension'], values=(label['file_size'], f"{label['last_write_time']} {label['last_write_date']}"), tags=("read_file",))
    
        for label in deleted_files_in_existing_folders:
            if f"{path}{label['file_name']}.{label['file_extension']}".strip() == label['path']:
                fileview.insert("", tk.END, text=label['file_name'] + '.' + label['file_extension'], values=(label['file_size'], f"{label['last_write_time']} {label['last_write_date']}"), image=x_icon, tags=("read_file",))
        
        for label in deleted_files_in_deleted_folders:
            if f"{path}{label['file_name']}.{label['file_extension']}".strip() == label['path']:
                fileview.insert("", tk.END, text=label['file_name'] + '.' + label['file_extension'], values=(label['file_size'], f"{label['last_write_time']} {label['last_write_date']}"), image=x_icon, tags=("read_file",))
        
        for label in existing_files_in_deleted_folders:
            if f"{path}{label['file_name']}.{label['file_extension']}".strip() == label['path']:
                fileview.insert("", tk.END, text=label['file_name'] + '.' + label['file_extension'], values=(label['file_size'], f"{label['last_write_time']} {label['last_write_date']}"), image=x_icon, tags=("read_file",))

# Initialize the main window
root = tk.Tk()
root.title("Left Side Clickable Labels with Right Side Display")
root.geometry("900x500")  # Set window size

def open_options_window():
    # Create a new Toplevel window (a new window)
    options_window = tk.Toplevel(root)
    options_window.geometry("350x200");
    options_window.title("Select Option")
    
    # Add a label
    label = ttk.Label(options_window, text="Choose an option:")
    label.pack(pady=10)

    # Variable to store the selected option
    
    disks = [ '/dev/' + x for x in os.listdir('/dev/') if os.stat('/dev/' + x).st_gid == 995 and x != 'loop-control']
    
    selected_option = tk.StringVar(value=disks[0])  # Default selection
    
    for x in disks:
        ttk.Radiobutton(options_window, text=x, variable=selected_option, value=x).pack(anchor="w")
    
    # Function to print the selected option
    def show_selected_option():

        options_window.destroy()  # Close the window after selection
        perform_analysis(selected_option.get())

    # Add a button to confirm selection
    confirm_button = ttk.Button(options_window, text="Confirm", command=show_selected_option)
    confirm_button.pack(pady=10)

x_icon = tk.PhotoImage(file="./icons/deleted.png")

# Create a frame for the left side (clickable labels)
left_frame = tk.Frame(root, bg="lightgrey", width=200)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

# Create a frame for the right side (main display)
right_frame = tk.Frame(root, bg="white")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Add the Import button at the top of the left frame

open_window_button = tk.Button(left_frame, text="Choose Disk", relief=tk.RAISED, padx=10, pady=5, command=open_options_window)
open_window_button.pack(fill=tk.X, pady=4, padx=10)

import_button = tk.Button(left_frame, text="Choose Image", relief=tk.RAISED, padx=10, pady=5, command=import_file)
import_button.pack(fill=tk.X, padx=10, pady=4)

separator = ttk.Separator(left_frame, orient='horizontal')
separator.pack(fill=tk.X, padx=5, pady=5)

treeview = tk.ttk.Treeview(left_frame)
treeview.tag_bind("show_files", "<<TreeviewSelect>>", folder_selected)
treeview.heading("#0", text="Folders")
treeview.insert("", tk.END, text='empty')
treeview.pack()

fileview_heading = tk.Label(right_frame, text="Files")
fileview_heading.pack(fill=tk.X)

fileview = ttk.Treeview(right_frame, columns=("size", "lastmod"))

fileview.tag_bind("read_file", "<<TreeviewSelect>>", file_selected)
fileview.heading("#0", text="File")
fileview.heading("size", text="Size")
fileview.heading("lastmod", text="Last modification")
fileview.pack(fill=tk.X)

# TextBox Creation 

input_heading = tk.Label(right_frame, text="Output:", justify=tk.LEFT)
input_heading.pack(fill=tk.X)

input_text = tk.Text(right_frame) 
input_text.config(state = tk.DISABLED)
input_text.pack(fill=tk.BOTH)

# Run the Tkinter main loop
root.mainloop()
