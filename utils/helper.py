import os
import sys
from datetime import datetime

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def format_datetime(datetime_str, 
                   show_time=False,
                   show_timezone=False,
                   show_seconds=False,
                   input_format="%Y-%m-%dT%H:%M:%SZ",
                   default_value=""):
    if not datetime_str:
        return default_value
        
    try:
        dt = datetime.strptime(datetime_str, input_format)
        
        output_format = "%Y-%m-%d"
        
        if show_time:
            if show_seconds:
                output_format += " %H:%M:%S"
            else:
                output_format += " %H:%M"
        
        formatted_dt = dt.strftime(output_format)
        
        if show_timezone and "Z" in input_format:
            formatted_dt += " UTC"
            
        return formatted_dt
        
    except (ValueError, TypeError):
        return default_value
    