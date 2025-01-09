from datetime import datetime
from dateutil.parser import parse

def format_and_validate_date_time(date_time_string):
    try:
        # ISO 8601 ve diğer formatlarla uyumlu bir çözüm
        parsed_date = parse(date_time_string)
        # Tarihi "YYYY-MM-DD HH:MM:SS" formatında döndür
        return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return f"Error parsing date: {e}"
