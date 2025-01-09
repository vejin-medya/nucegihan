from datetime import datetime
from dateutil.parser import parse
import pytz

def format_and_validate_date_time(date_time_string):
    date_time = None

    # ISO 8601 formatını kontrol et
    date_time = try_parse_iso8601(date_time_string)

    # Özel tarih formatını kontrol et
    if date_time is None:
        date_time = try_parse_custom_date(date_time_string)

    # Tarih geçerliyse formatla
    if date_time is not None:
        return format_date_time(date_time)

    return str(date_time)  # Hata mesajı

def try_parse_iso8601(date_time_string):
    try:
        return parse(date_time_string)
    except Exception:
        return None

def try_parse_custom_date(date_time_string):
    try:
        # Özel tarih formatını dener: "dd MMM yyyy HH:mm:ss"
        return datetime.strptime(date_time_string, "%d %b %Y %H:%M:%S").replace(tzinfo=pytz.utc).astimezone()
    except Exception:
        return None

def format_date_time(date_time):
    # ISO 8601 formatına uygun hale getir: "YYYY-MM-DD HH:MM:SS"
    return date_time.strftime("%Y-%m-%d %H:%M:%S")