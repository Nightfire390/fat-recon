import os

def read_sector(partition, start_sector, end_sector, sector_size=512):
    hex_data = ""
    
    with open(partition, 'rb') as file:
        for sector in range(start_sector, end_sector):
            file.seek(sector * sector_size)
            sector_data = file.read(sector_size)
            hex_data += sector_data.hex()
            
    hex_data = hex_data.upper()        
    return hex_data