
import re
import os
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, Union
from collections import defaultdict

def convert_bytes(quant: float, units_in: str, units_out: str) -> float:
    """
    Converts quantity from one byte unit to another.
    
    :param quant: The quantity to convert.
    :param units_in: The byte unit of the input quantity, e.g., "GB".
    :param units_out: The byte unit of the output quantity, e.g., "MB".
    :return: The converted quantity.
    """

    byte_units = {
        "BIT": 8*1024**3,
        'B': 1024**3,
        'KB': 1024**2,
        'MB': 1024,
        'GB': 1,
        'TB': 1/1024,
        'PB': 1/1024**2,
    }
    return convert_unit(quant, units_in, units_out, byte_units)

def convert_time(quant: float, units_in: str, units_out: str) -> float:
    """
    Converts quantity from one time unit to another.
    
    :param quant: The quantity to convert.
    :param units_in: The time unit of the input quantity, e.g., "days".
    :param units_out: The time unit of the output quantity, e.g., "hours".
    :return: The converted quantity.
    """

    # Let's center it around hours
    time_units = {
        'y': 365*24,
        'month': 30*24,
        'w': 7*24,
        'd': 24,
        'h': 1,
        'm': 1/60,
        's': 1/3600,
        'ms': 1/3600000,
        'us': 1/3600000000,
    }
    return convert_unit(quant, units_in, units_out, time_units)

def convert_unit(quant: float,
                 units_in: str,
                 units_out: str,
                 units: Dict[str, float]) -> float:
    """
    Converts quantity from one byte unit to another.

    The `units` dictionary should all express the same amount of quantity,
    e.g., 1 kg = 1000 g, or 1 km = 1*10^3 m = 1*10^6 mm.
    
    :param quant: The quantity to convert.
    :param units_in: The unit of the input quantity, e.g., "GB".
    :param units_out: The unit of the output quantity, e.g., "MB".
    :param units: A dictionary mapping unit names to conversion factors.
    :return: The converted quantity.
    :raises ValueError: If the specified units are not recognized.
    """

    if units_in not in units:
        raise ValueError(f"Unknown input unit: {units_in}")
    if units_out not in units:
        raise ValueError(f"Unknown output unit: {units_out}")
    return quant / units[units_in] * units[units_out]

def get_file_info(path: Union[Path,str], size_units='B') -> Dict[str, Any]:
    """
    Retrieves detailed information about a file, including creation and modification times.

    :param path: Path to the file.
    :param size_units: The units to use for the file size.
    :return: Dictionary containing file metadata.
    """
    if isinstance(path, str):
        path = Path(path)

    stat = path.stat()   
    info = {
        'file_name': path.name,
        'file_path': str(path),
        'file_size': convert_bytes(stat.st_size, 'B', size_units),
        'file_size_units': size_units,
        'last_modification': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'metadata_change_time': datetime.fromtimestamp(stat.st_ctime).isoformat()
    }
    return info

def parse_duration(duration: str) -> relativedelta:
    """
    Parses a string representing a duration and returns a tuple of a
    relativedelta object and a timedelta object.

    The relativedelta object can be used for precise date arithmetic, while the
    timedelta object can be used to get the total duration in a specific unit.

    Example usage:

        (duration, total_duration) = parse_duration("1 month, 2 weeks, and 3 days")
        occured = datetime.now() - duration
        total_days = total_duration.days

    :param duration: A string representing a duration, e.g., "1 month, 2 weeks, and 3 days".
    :return: A tuple of a relativedelta object and a timedelta object representing the duration.
    :raises ValueError: If the input format is invalid.
    """
    units = ['day', 'week', 'month', 'year', 'hour', 'minute', 'second']
    units_pattern = '|'.join(units)
    pattern = re.compile(rf'(\d+)\s*({units_pattern})s?', re.IGNORECASE)
    matches = pattern.findall(duration)
    
    if not matches:
        raise ValueError("Invalid input format. Expected something like '1 month and 2 weeks'")
    
    relativedelta_kwargs = defaultdict(int)
    for value, unit in matches:
        value = int(value)
        unit = unit.lower().rstrip('s')  # Normalize unit to singular form
        # Accumulate values for each unit
        relativedelta_kwargs[unit] += value

    # add 's' to each unit for relativedelta
    relativedelta_kwargs = {f"{unit}s": value for unit, value in relativedelta_kwargs.items()}
    rd = relativedelta(**relativedelta_kwargs).normalized()
    now = datetime.now()
    future = now + rd
    td = future - now
    return rd, td
