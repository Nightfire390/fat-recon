from misc.conversions import *

def analyse_lfn_entry(entry):
    
    lfn_analysis = {
        "sequence_number": entry[0:2],
        "name_1": hex_to_ascii(entry[2:22]),
        "file_attribute": entry[22:24],
        "reserved_byte": entry[24:26],
        "checksum": entry[26:28],
        "name_2": hex_to_ascii(entry[28:52]),
        "starting_cluster": entry[52:56],
        "name_3": hex_to_ascii(entry[56:64])
    }

    # Calculating Partial Long Name
    lfn_analysis.update({
        "partial_name": (lfn_analysis["name_1"] + lfn_analysis["name_2"] + lfn_analysis["name_3"]).upper()
    })

    # Updated LFN Analysis with Sequence Number, Partial Name & Checksum
    lfn_analysis = {
        "sequence_number": lfn_analysis["sequence_number"],
        "partial_name": lfn_analysis["partial_name"],
        "checksum": lfn_analysis["checksum"]
    }

    return lfn_analysis

def process_lfn_entries(lfn_entries_analysis):
    
    for entry in lfn_entries_analysis:
        # Cleaning and Updating Partial Name
        entry['partial_name'] = entry['partial_name'].replace("\x00", '').replace("Ÿ", '')
    
    # Group entries by checksum and sort by sequence_number
    grouped_lfn_entries = {}
    
    for entry in lfn_entries_analysis:
        checksum = entry['checksum']
        if checksum not in grouped_lfn_entries:
            grouped_lfn_entries[checksum] = []
        grouped_lfn_entries[checksum].append(entry)   
    
    # Process each group to concatenate full_name values
    processed_lfn_entries = []
    
    for checksum, items in grouped_lfn_entries.items():
        items_sorted = sorted(items, key=lambda x: x['sequence_number'])
        full_name = ''.join(item['partial_name'] for item in items_sorted)
        processed_lfn_entries.append({'checksum': checksum, 'full_name': full_name})
    processed_lfn_entries = {entry['checksum']: entry['full_name'] for entry in processed_lfn_entries}
    
    return processed_lfn_entries

def analysing_long_file_names(lfn_entries):
    
    lfn_entries_analysis = []
    
    for entry in lfn_entries:
        analysed_lfn_entry = analyse_lfn_entry(entry)
        lfn_entries_analysis.append(analysed_lfn_entry)
    
    return process_lfn_entries(lfn_entries_analysis)