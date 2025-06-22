from misc.conversions import *

def filter_sfn_entries(sfn_entries):    
    
    existing_files = []
    deleted_files = []
    existing_folders = []
    deleted_folders = []
    
    for entry in sfn_entries:        
        attribute_byte = entry[22:24]
        first_byte = entry[:2]
        if attribute_byte == "10":
            if first_byte == "E5":
                deleted_folders.append(entry)
            else:
                existing_folders.append(entry)
        elif attribute_byte == "20":
            if first_byte == "E5":
                deleted_files.append(entry)
            else:
                existing_files.append(entry)    
    
    return existing_files, deleted_files, existing_folders, deleted_folders

def calculate_checksum(sfn):
    
    checksum = 0
    
    for char in sfn:
        # Rotate right by 1 bit and add the character's ASCII value
        checksum = ((checksum & 1) << 7) + (checksum >> 1) + ord(char)
        # Keep it within 8 bits
        checksum &= 0xFF  # Mask to 8 bits    
    
    return checksum

def analyse_sfn_file(entry, sectors_per_cluster, data_region_sector):
    
    sfn_file_analysis = {
        "file_name": hex_to_ascii(entry[0:16]),
        "file_extension": hex_to_ascii(entry[16:22]),
        "file_attribute": little_endian(entry[22:24]),
        "reserved_nt": little_endian(entry[24:26]),
        "creation_time_ms": hex_to_dec(entry[26:28]),
        "creation_time": convert_time(entry[28:32]),
        "creation_date": convert_date(entry[32:36]),
        "last_accessed_date": convert_date(entry[36:40]),
        "reserved_fat32": little_endian(entry[40:44]),
        "last_write_time": convert_time(entry[44:48]),
        "last_write_date": convert_date(entry[48:52]),
        "starting_cluster": hex_to_dec(little_endian(entry[52:56])),
        "file_size": hex_to_dec(little_endian(entry[56:64])),
    }
    
    # Calculate the first sector of the file
    sfn_file_analysis.update({
        "first_sector": data_region_sector + ((sfn_file_analysis["starting_cluster"] - 2) * sectors_per_cluster)
    })
    
    # Calculate the SFN string for checksum calculation
    sfn_string = sfn_file_analysis["file_name"] + sfn_file_analysis["file_extension"]
    
    # Calculate the checksum and add it to the analysis
    checksum = calculate_checksum(sfn_string)
    
    sfn_file_analysis.update({
        "checksum": f"{checksum:02X}"  # Format as two-digit hexadecimal
    })
    
    return sfn_file_analysis

def analyse_sfn_folder(entry, sectors_per_cluster, data_region_sector):

    sfn_folder_analysis = {
        "folder_name": hex_to_ascii(entry[0:16]),
        "folder_extension": hex_to_ascii(entry[16:22]),
        "folder_attribute": little_endian(entry[22:24]),
        "reserved_nt": little_endian(entry[24:26]),
        "creation_time_ms": hex_to_dec(entry[26:28]),
        "creation_time": convert_time(entry[28:32]),
        "creation_date": convert_date(entry[32:36]),
        "last_accessed_date": convert_date(entry[36:40]),
        "reserved_fat32": little_endian(entry[40:44]),
        "last_write_time": convert_time(entry[44:48]),
        "last_write_date": convert_date(entry[48:52]),
        "starting_cluster": hex_to_dec(little_endian(entry[52:56])),
        "folder_size": hex_to_dec(little_endian(entry[56:64])),
    }
    # Calculate the first sector of the folder
    sfn_folder_analysis.update({
        "first_sector": data_region_sector + ((sfn_folder_analysis["starting_cluster"] - 2) * sectors_per_cluster)
    })
    
    # Calculate the SFN string for checksum calculation
    sfn_string = sfn_folder_analysis["folder_name"] + sfn_folder_analysis["folder_extension"]
    
    # Calculate the checksum and add it to the analysis
    checksum = calculate_checksum(sfn_string)
    
    sfn_folder_analysis.update({
        "checksum": f"{checksum:02X}"  # Format as two-digit hexadecimal
    })
    
    return sfn_folder_analysis

def map_lfn_to_sfn(sfn_analysis, lfn_entries_analysis):
    
    # Iterate through each entry in the SFN list
    for sfn_entry in sfn_analysis:
        # Check if the checksum exists in the LFN dictionary
        checksum = sfn_entry.get("checksum")
        if checksum in lfn_entries_analysis:
            if "file_name" in sfn_entry:
                sfn_entry["file_name"] = lfn_entries_analysis[checksum]
            elif "folder_name" in sfn_entry:
                sfn_entry["folder_name"] = lfn_entries_analysis[checksum]
    
    return sfn_analysis