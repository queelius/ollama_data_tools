import subprocess
from pathlib import Path
import re
from datetime import datetime
from typing import Dict, List, Any
from ollama_data_tools import conversion_tools as ct

def get_schema() -> List[Dict[str, Any]]:
    """
    Returns the schema for the model information.
    
    :return: A list of dictionaries representing the schema.
    """
    return [{
        'name': '<str>',
        'model_params': '<dict>',
        'system_message': '<list[str]>',
        'total_weights_size': '<float>',
        'total_weights_size_units': '<str>',
        'template': '<list[str]>',
        'modelfile': '<str|None>',
        'last_modified': '<str>',
        'age': {
            'days': '<int>',
            'years': '<int>',
            'months': '<int>',
            'weeks': '<int>',
            'seconds': '<int>'
        },
        'weights': [{
            'hash': '<str>',
            'path': '<str>',
            'file_name': '<str>',
            'dir': '<str>',
            'file_size': '<float>',
            'file_size_units': '<str>',
            'last_modified': '<str>',
            'metadata_modified': '<str>'
        }]
    }]

def run_ollama(args: List[str]) -> str:
    """
    Execute `ollama` command with arguments and returns the output.
    
    :param args: The arguments to use.
    :return: The output of the command.
    :raises RuntimeError: If the command fails.
    """
    
    result = subprocess.run(['ollama'] + args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ollama with args [{ ''.join(args) }] failed with error: {result.stderr}")
    return result.stdout

def get_models(exclude_keys = None) -> List[Dict[str, Any]]:
    """
    Generates a list of dictionaries containing information about all models in Ollama.

    :param exclude_keys: A list of keys to exclude from the output.
    
    :return: A list of dictionaries with model information.
    """
    output = run_ollama(['list'])
    lines = output.splitlines()
    lines = [line for line in lines if line.strip()]
    if lines and lines[0].startswith('NAME'):
        lines.pop(0)

    models = []
    for line in lines:
        parts = line.split()
        model_name = parts[0]
        #weights_size_gb = convert_bytes(float(parts[2]), parts[3], 'GB')
        dur, delta = ct.parse_duration(parts[4] + ' ' + parts[5])
        
        #weight_info['size_units'] = 'GB'

        weight_infos = []
        weight_paths = get_weights_path(model_name)
        for weight_path in weight_paths:
            weight_info = ct.get_file_info(weight_path)
            match = re.search(r'.*/sha256-([a-f0-9]{64})',
                      str(weight_path), re.IGNORECASE)
            weight_info['hash'] = match.group(1) if match else None
            weight_info['dir'] = str(weight_path.parent)
            weight_infos.append(weight_info)

        total_weights_size = sum([info['file_size'] if 'file_size' in info else 0
                                  for info in weight_infos])        
        models.append({
            'name': model_name,
            'last_modified': (datetime.now() - delta).isoformat(),
            'age': {
                "days": dur.days,
                "seconds": dur.seconds,
                "years": dur.years,
                "months": dur.months,
                "weeks": dur.weeks,
                "hours": dur.hours,
                "minutes": dur.minutes,
            },
            'model_params': get_model_params(model_name),
            'system_message': get_model_system(model_name),
            'template': get_model_template(model_name),
            'modelfile': get_modelfile(model_name),
            'total_weights_size': ct.convert_bytes(total_weights_size, 'B', 'GB'),
            'total_weights_size_units': 'GB',
            #'total_weights_size_alternate': weights_size_gb,
            'weights': weight_infos
        })
    return models

def get_model_weights_license(model_name: str) -> str:
    """
    Fetches the license type of a model's weights using `ollama show --license`.

    :param model_name: The name of the model.
    :return: The license type of the model's weights, or None if the command fails.
    """
    return run_ollama(['show', model_name, '--license'])

def get_modelfile(model_name: str) -> str:
    """
    Fetches the model's modelfile using `ollama show --modelfile`.

    :param model_name: The name of the model.
    :return: The modelfile contents, or None if the command fails.
    """
    return run_ollama(['show', model_name, '--modelfile'])

def get_weights_hash(model_name: str) -> str:
    """
    Retrieves the SHA256 hashes of a model's weights.

    :param model_name: The name of the model.
    :return: A list of SHA256 hashes.
    """
    modelfile = get_modelfile(model_name)
    return re.findall(r'\s*FROM .*/sha256-([a-f0-9]{64})',
                      modelfile, re.IGNORECASE | re.MULTILINE)

def get_weights_path(model_name: str) -> Dict[str, str]:
    """
    Fetches the path and filename of a model's weights.

    :param model_name: The name of the model.
    :return: A dictionary containing the path and filename, or None if not found.
    """
    modelfile = get_modelfile(model_name)
    match = re.findall(r'^\s*FROM (.+)', modelfile, re.IGNORECASE | re.MULTILINE)
    return [Path(filename) for filename in match]
    
def get_model_system(model_name: str) -> str:
    """
    Fetches the system message of a model using `ollama show --system`.

    :param model_name: The name of the model.
    :return: The system message, or None if the command fails.
    """
    return run_ollama(['show', model_name, '--system'])

def get_model_template(model_name: str) -> List[str]:
    """
    Fetches the template of a model using `ollama show --template`.

    :param model_name: The name of the model.
    :return: A list of template lines, or None if the command fails.
    """
    output = run_ollama(['show', model_name, '--template'])
    return [line.strip() for line in output.splitlines() if line.strip()]

def get_model_params(model_name: str) -> Dict[str, str]:
    """
    Fetches the parameters of a model using `ollama show --parameters`.

    :param model_name: The name of the model.
    :return: A dictionary of model parameters, or None if the command fails.
    """
    output = run_ollama(['show', model_name, '--parameters'])
    lines = output.splitlines()
    params = {}

    regex = r'(?:"[^"]*"|[^"\s]+)+'
    for line in lines:
        if line.strip():
            key, value = re.findall(regex, line)
            params[key.strip()] = value.strip()
    return params
