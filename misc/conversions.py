# Importing 'datetime' module to convert '2024.1.1' to '1 January 2024'
from datetime import datetime

# Converting Hexadecimal Values to ASCII Values
def hex_to_ascii(hex_str):
    try:
        ascii_string = bytes.fromhex(hex_str).decode('ascii')
    except UnicodeDecodeError:
        ascii_string = bytes.fromhex(hex_str).decode('latin1')
    return ascii_string

# Converting Hexadecimal Values to Decimal Values
def hex_to_dec(hex_str):
    return int(hex_str, 16)

# Converting Hexadecimal Values to Binary Values
def hex_to_bin(hex_str):
    return bin(int(hex_str, 16))[2:].zfill(len(hex_str) * 4)

# Converting Binary Values to Decimal Values
def bin_to_dec(bin_str):
    return int(bin_str, 2)

# Switching Hexadecimal Values from Little Endian Format
def little_endian(hex_str):
    # Split the string into bytes
    bytes_list = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    # Reverse the byte order and concatenate them back into a string
    big_endian_hex_str = ''.join(bytes_list[::-1])
    return big_endian_hex_str

# Convert Hexadecimal Values to Time
def convert_time(hex_str):
    # Convert Time from Hexadecimal Values to 24 Hour Format
    hex_str = little_endian(hex_str)
    bin_str = hex_to_bin(hex_str)
    hour = bin_to_dec(bin_str[:5])
    minute = bin_to_dec(bin_str[5:11])
    second = (bin_to_dec(bin_str[11:]) * 2)
    time = f"{hour}:{minute}:{second}"
    # Convert Time from 24 Hour Format to 12 Hour Format (AM/PM)
    hours, minutes, seconds = map(int, time.split(':'))
    if hours == 0:
        period = "AM"
        hours = 12
    elif hours < 12:
        period = "AM"
    elif hours == 12:
        period = "PM"
    else:
        period = "PM"
        hours -= 12 
    return f"{hours:01}:{minutes:02}:{seconds:02} {period}"

# Convert Hexadecimal Values to Date
def convert_date(hex_str):
    # Convert date from hexadecimal to (Year.Month.Date) Format
    hex_str = little_endian(hex_str)
    bin_str = hex_to_bin(hex_str)
    year = (bin_to_dec(bin_str[:7]) + 1980)
    month = bin_to_dec(bin_str[7:11])
    day = bin_to_dec(bin_str[11:])
    date = f"{day}.{month}.{year}"
    # Convert date from (Year.Month.Date) Format to (Date Month Year) Format
    try:
        # Check if the date string is valid
        if date == '0.0.1980':
            return 'Invalid date format'
        # Parse the input date string
        date_obj = datetime.strptime(date, "%d.%m.%Y")
        # Format the date into the desired format
        return date_obj.strftime("%d %B %Y")
    except ValueError as e:
        return f"Error: {e}"
