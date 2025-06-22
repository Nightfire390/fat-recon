from misc.reading_sectors import *
from analyses.analysing_boot_sector import *
from analyses.analysing_directory import *

def analyse_existing_sub_folders(partition_path, sectors_per_cluster, data_region_sector, sfn_existing_folders_analysis):
    all_existing_files = []
    all_deleted_files = []
    all_existing_folders = []
    all_deleted_folders = []

    def recursive_analyse_existing(folder_list):
        for folder in folder_list:
            first_sector = folder['first_sector']
            last_sector = first_sector + sectors_per_cluster
            folder_path = folder['path']

            # Read the directory entries of the folder
            folder_directory = read_sector(partition_path, start_sector=first_sector, end_sector=last_sector)

            # Create directory entries for the folder
            folder_entries = create_directory_entries(folder_directory)

            # Analyze the directory entries in the folder
            existing_files, deleted_files, existing_folders, deleted_folders = analyse_directory(folder_entries, sectors_per_cluster, data_region_sector, folder_path)

            # Filter out '.' and '..' entries
            existing_folders = [folder for folder in existing_folders if folder['folder_name'] not in ['.', '..']]
            deleted_folders = [folder for folder in deleted_folders if folder['folder_name'] not in ['.', '..']]
            
            # Store the results
            all_existing_files.extend(existing_files)
            all_deleted_files.extend(deleted_files)
            all_existing_folders.extend(existing_folders)
            all_deleted_folders.extend(deleted_folders)

            # Recursively analyze subdirectories
            recursive_analyse_existing(existing_folders)
            recursive_analyse_existing(deleted_folders)

    # Start the recursive analysis from the first level of existing folders
    recursive_analyse_existing(sfn_existing_folders_analysis)

    return all_existing_files, all_deleted_files, all_existing_folders, all_deleted_folders

def analyse_deleted_sub_folders(partition_path, sectors_per_cluster, data_region_sector, sfn_deleted_folders_analysis):
    all_existing_files = []
    all_deleted_files = []
    all_existing_folders = []
    all_deleted_folders = []

    def recursive_analyse_deleted(folder_list):
        for folder in folder_list:
            first_sector = folder['first_sector']
            last_sector = first_sector + sectors_per_cluster
            folder_path = folder['path']

            # Read the directory entries of the folder
            folder_directory = read_sector(partition_path, start_sector=first_sector, end_sector=last_sector)

            # Create directory entries for the folder
            folder_entries = create_directory_entries(folder_directory)

            # Analyze the directory entries in the folder
            existing_files, deleted_files, existing_folders, deleted_folders = analyse_directory(folder_entries, sectors_per_cluster, data_region_sector, folder_path)

            # Filter out '.' and '..' entries
            existing_folders = [folder for folder in existing_folders if folder['folder_name'] not in ['.', '..']]
            deleted_folders = [folder for folder in deleted_folders if folder['folder_name'] not in ['.', '..']]

            # Store the results
            all_existing_files.extend(existing_files)
            all_deleted_files.extend(deleted_files)
            all_existing_folders.extend(existing_folders)
            all_deleted_folders.extend(deleted_folders)

            # Recursively analyze subdirectories
            recursive_analyse_deleted(existing_folders)
            recursive_analyse_deleted(deleted_folders)

    # Start the recursive analysis from the first level of deleted folders
    recursive_analyse_deleted(sfn_deleted_folders_analysis)

    return all_existing_files, all_deleted_files, all_existing_folders, all_deleted_folders