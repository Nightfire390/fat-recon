from misc.conversions import *

def analyse_boot_sector(boot_sector):
    
    boot_sector_analysis = {
    "jmp_instruction": boot_sector[:6],
    "oem_id": hex_to_ascii(boot_sector[6:22]),
    "bytes_per_sector": hex_to_dec(little_endian(boot_sector[22:26])),
    "sectors_per_cluster": hex_to_dec(little_endian(boot_sector[26:28])),
    "reserved_sectors": hex_to_dec(little_endian(boot_sector[28:32])),
    "number_of_FATs": hex_to_dec(little_endian(boot_sector[32:34])),
    "root_entries": hex_to_dec(little_endian(boot_sector[34:38])),
    "total_sectors_small": hex_to_dec(little_endian(boot_sector[38:42])),
    "media_descriptor": boot_sector[42:44],
    "sectors_per_FAT": hex_to_dec(little_endian(boot_sector[44:48])),
    "sectors_per_track": hex_to_dec(little_endian(boot_sector[48:52])),
    "number_of_heads": hex_to_dec(little_endian(boot_sector[52:56])),
    "hidden_sectors": hex_to_dec(little_endian(boot_sector[56:64])),
    "total_sectors_large": hex_to_dec(little_endian(boot_sector[64:72])),
    "physical_drive": hex_to_dec(boot_sector[72:74]),
    "reserved": hex_to_dec(boot_sector[74:76]),
    "extended_signature": hex_to_dec(boot_sector[76:78]),
    "serial_number": boot_sector[78:86],
    "volume_label": hex_to_ascii(boot_sector[86:108]),
    "file_system": hex_to_ascii(boot_sector[108:124]),
    "bootstrap_code": boot_sector[124:1020],
    "signature": boot_sector[1020:1024],
}
    boot_sector_analysis.update({
        "first_FAT_sector": boot_sector_analysis["reserved_sectors"],
        "second_FAT_sector": boot_sector_analysis["reserved_sectors"] + boot_sector_analysis["sectors_per_FAT"],
        "root_directory_sector": boot_sector_analysis["reserved_sectors"] + (boot_sector_analysis["number_of_FATs"] * boot_sector_analysis["sectors_per_FAT"]),
        "sectors_in_root_directory": (boot_sector_analysis["root_entries"] * 32 + boot_sector_analysis["bytes_per_sector"] - 1) // boot_sector_analysis["bytes_per_sector"],
        "data_region_sector": boot_sector_analysis["reserved_sectors"] + (boot_sector_analysis["number_of_FATs"] * boot_sector_analysis["sectors_per_FAT"]) + (boot_sector_analysis["root_entries"] * 32 + boot_sector_analysis["bytes_per_sector"] - 1) // boot_sector_analysis["bytes_per_sector"]
    })

    return boot_sector_analysis