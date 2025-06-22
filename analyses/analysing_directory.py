from misc.conversions import *
from analyses.analysing_lfn_entries import *
from analyses.analysing_sfn_entries import *

def create_directory_entries(sector_data):    
    
    # Length of each entry in characters (2 X 32 bytes)
    entry_size_chars = 64
    
    # Creating a List of Entries
    entries = [sector_data[i:i + entry_size_chars] for i in range(0, len(sector_data), entry_size_chars)]
    
    # Removing Null Entries
    directory_entries = [entry for entry in entries if entry != '0000000000000000000000000000000000000000000000000000000000000000']

    return directory_entries

def sfn_or_lfn(directory_entries):

    sfn_entries = []
    lfn_entries = []

    for entry in directory_entries:
        attribute_byte = entry[22:24]
        if attribute_byte == "0F":
            lfn_entries.append(entry)
        else:
            sfn_entries.append(entry)    
    
    return sfn_entries, lfn_entries

def process_file_name(analysis):
    for entry in analysis:
        file_name = entry["file_name"].strip()
        if file_name.endswith(f'.{entry["file_extension"]}'):
            file_name = file_name[:-len(entry["file_extension"]) - 1]
        entry["file_name"] = file_name
    
    return analysis

def process_folder_name(analysis):
    for entry in analysis:
        folder_name = entry["folder_name"].strip()
        if folder_name.endswith(f'.{entry["folder_name"]}'):
            folder_name = folder_name[:-len(entry["folder_name"]) - 1]
        entry["folder_name"] = folder_name
    
    return analysis

def add_file_path(path, analysis):
    for files in analysis:
        full_path = f"{path}/{files['file_name'].strip()}.{files['file_extension'].strip()}"
        files["path"] = full_path
    return analysis

def add_folder_path(path, analysis):
    for folders in analysis:
        full_path = f"{path}/{folders['folder_name'].strip()}"
        folders["path"] = full_path
    return analysis

def analyse_directory(directory_entries, sectors_per_cluster, data_region_sector, path):
    
    # STEP 1: Filtering Out Directory Entries as Short File Name (SFN) or Long File Name (LFN)
    sfn_entries, lfn_entries = sfn_or_lfn(directory_entries)

    # STEP 2: Analysing LFN Entries
    lfn_entries_analysis = analysing_long_file_names(lfn_entries)
        
    # STEP 3: Analysing SFN Entries

    # Filtering Out SFN Entries as a File or a Folder
    existing_files, deleted_files, existing_folders, deleted_folders = filter_sfn_entries(sfn_entries)

    # STEP 3.2. Analysing SFN Existing Files
    sfn_existing_files_analysis = []
    for entry in existing_files:
        analysed_sfn_existing_file = analyse_sfn_file(entry, sectors_per_cluster, data_region_sector)
        sfn_existing_files_analysis.append(analysed_sfn_existing_file)

    # STEP 3.3. Analysing SFN Deleted Files
    sfn_deleted_files_analysis = []
    for entry in deleted_files:
        analysed_sfn_deleted_file = analyse_sfn_file(entry, sectors_per_cluster, data_region_sector)
        sfn_deleted_files_analysis.append(analysed_sfn_deleted_file)

    # STEP 3.4. Analysing SFN Existing Folders
    sfn_existing_folders_analysis = []
    for entry in existing_folders:
        analysed_sfn_existing_folder = analyse_sfn_folder(entry, sectors_per_cluster, data_region_sector)
        sfn_existing_folders_analysis.append(analysed_sfn_existing_folder)

    # STEP 3.5. Analysing SFN Deleted Folders
    sfn_deleted_folders_analysis = []
    for entry in deleted_folders:
        analysed_sfn_deleted_folder = analyse_sfn_folder(entry, sectors_per_cluster, data_region_sector)
        sfn_deleted_folders_analysis.append(analysed_sfn_deleted_folder)

    # STEP 4: Mapping LFN Entries to SFN Entries
    sfn_existing_files_analysis = map_lfn_to_sfn(sfn_existing_files_analysis, lfn_entries_analysis)
    sfn_deleted_files_analysis = map_lfn_to_sfn(sfn_deleted_files_analysis, lfn_entries_analysis)
    sfn_existing_folders_analysis = map_lfn_to_sfn(sfn_existing_folders_analysis, lfn_entries_analysis)
    sfn_deleted_folders_analysis = map_lfn_to_sfn(sfn_deleted_folders_analysis, lfn_entries_analysis)

    # STEP 5: Process Filenames & Foldernames
    sfn_existing_files_analysis = process_file_name(sfn_existing_files_analysis)
    sfn_deleted_files_analysis = process_file_name(sfn_deleted_files_analysis)
    sfn_existing_folders_analysis = process_folder_name(sfn_existing_folders_analysis)
    sfn_deleted_folders_analysis = process_folder_name(sfn_deleted_folders_analysis)

    # STEP 6: Add Path to Analysis
    sfn_existing_files_analysis = add_file_path(path, sfn_existing_files_analysis)
    sfn_deleted_files_analysis = add_file_path(path, sfn_deleted_files_analysis)
    sfn_existing_folders_analysis = add_folder_path(path, sfn_existing_folders_analysis)
    sfn_deleted_folders_analysis = add_folder_path(path, sfn_deleted_folders_analysis)

    return sfn_existing_files_analysis, sfn_deleted_files_analysis, sfn_existing_folders_analysis, sfn_deleted_folders_analysis
