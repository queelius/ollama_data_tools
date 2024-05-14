from time import time 
import subprocess
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime

def get_schema():

    return [{
        'name': 'NAME',
        'weights_hash': 'SHA256',
        'weights_path': 'PATH',
        'weights_filename': 'FILENAME',
        'model_params': 'PARAMS',
        'system_message': 'SYSTEM',
        'template': 'TEMPLATE',
        'modelfile': 'MODELFILE',
        'weights_size': 'SIZE ({MB, GB})',
        'weights_license_type': 'LICENSE_TYPE',
        'modified': 'MODIFIED'
    }]

def generate_data():
    """
    Generates a JSON object containing information about all models in Ollama.
    """
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    models = []
    lines = result.stdout.splitlines()

    for line in lines[1:]:
        parts = line.split()
        model_name = parts[0]
        path, filename = get_weights_path(model_name)
        models.append({
            'name': model_name,
            'weights_hash': get_weights_hash(model_name),
            'weights_path': path,
            'weights_filename': filename,
            'modified': get_relative_time(parts[4] + ' ' + parts[5]),
            'model_params': get_model_params(model_name),
            'system_message': get_model_system(model_name),
            'template': get_model_template(model_name),
            'modelfile': get_modelfile(model_name),
            'weights_size': get_weight_size(parts[2] + ' ' + parts[3]), 
            'weights_license_type': get_model_weights_license_type(model_name),
        })
    return models

def get_weight_size(weight_str):
    """
    Returns the weight size in GB.

    Format: "<value> <unit>", e.g., "4.5 GB" or "240 MB"
    """
    parts = weight_str.split()
    weight_size_gb = float(parts[0])
    units = parts[1]
    if units == 'MB':
        weight_size_gb /= 1024
    elif units == 'GB':
        pass
    elif units == 'TB':
        weight_size_gb *= 1024
    elif units == 'KB':
        weight_size_gb /= 1024**2
    elif units == 'B':
        weight_size_gb /= 1024**3
    else:
        raise ValueError(f"Unknown weight unit: {units}")
    
    return weight_size_gb


def get_relative_time(duration):
    """
    Returns a datetime object that is the result of subtracting the given duration from the current time.
    Format: "<value> <unit>", e.g., "1 day" or "2 months ago"
    """
    parts = duration.split()    
    value = int(parts[0])
    unit = parts[1]
    now = datetime.now()
    modified = None
    if unit.startswith('day'):
        modified = now - relativedelta(days=value)
        modified = modified.replace(hour=0, minute=0, second=0, microsecond=0)
    elif unit.startswith('month'):
        modified = now - relativedelta(months=value)
        modified = modified.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif unit.startswith('year'):
        modified = now - relativedelta(years=value)
        modified = modified.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif unit.startswith('hour'):
        modified = now - relativedelta(hours=value)
        modified = modified.replace(minute=0, second=0, microsecond=0)
    elif unit.startswith('minute'):
        modified = now - relativedelta(minutes=value)
        modified = modified.replace(second=0, microsecond=0)
    elif unit.startswith('second'):
        modified = now - relativedelta(seconds=value)
        modified = modified.replace(microsecond=0)
    elif unit.startswith('week'):
        modified = now - relativedelta(weeks=value)
        modified = modified.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError(f"Unknown time unit: {unit}")
    
    return modified.isoformat()

def get_model_weights_license_type(model_name):
    """Fetches the license type of a model's weights using `ollama show --license`."""

    result = subprocess.run(['ollama', 'show', model_name, '--license'], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.splitlines()[0].strip()

def get_modelfile(model_name):
    """Fetches the model's modelfile using `ollama show --modelfile`."""
    result = subprocess.run(['ollama', 'show', model_name, '--modelfile'], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout

def get_weights_hash(model_name):
    """Fetches the SHA256 hash of a model's weights."""
    modelfile = get_modelfile(model_name)
    match = re.search(r'FROM /usr/share/ollama/.ollama/models/blobs/sha256-([a-f0-9]{64})', modelfile)
    if match:
        return match.group(1)
    return None

def get_weights_path(model_name):
    """Fetches the path of a model's weigts"""
    modelfile = get_modelfile(model_name)
    match = re.search(r'^FROM (.+)', modelfile, re.IGNORECASE | re.MULTILINE)
    if match:
        full_path_with_filename = match.group(1)
        filename = full_path_with_filename.split('/')[-1]
        path = '/'.join(full_path_with_filename.split('/')[:-1])
        return path, filename
    return None

def get_model_system(model_name):
    """Fetches the system message of a model using `ollama show --system`."""
    result = subprocess.run(['ollama', 'show', model_name, '--system'], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout

def get_model_template(model_name):
    """Fetches the template of a model using `ollama show --template`."""
    result = subprocess.run(['ollama', 'show', model_name, '--template'], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return [t for t in result.stdout.splitlines() if t.strip()]

def get_model_params(model_name):
    """Fetches the parameters of a model using `ollama show --parameters`."""
    result = subprocess.run(['ollama', 'show', model_name, '--parameters'], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    lines = result.stdout.splitlines()
    params = {}

    # let's split based on regex, where if in quotes it should be considered as one element
    regex = r'(?:"[^"]*"|[^"\s]+)+'
    for line in lines:
        if not line.strip():
            continue
        key, value = re.findall(regex, line)
        params[key.strip()] = value.strip()
    return params
