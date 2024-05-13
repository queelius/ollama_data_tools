import json
import re
import jmespath

def validate_json(x):
    """
    Validate that an object is JSON-compatible.

    :param x: The object to validate.
    :raises ValueError: If the object is not JSON-compatible.
    """
    try:
        json.dumps(x)
    except (TypeError, OverflowError):
        raise ValueError("Object is not JSON-compatible")

def regex_filter(data, regex, path='@'):
    """
    Filter JSON output using a regex pattern and an optional JMESPath path.

    :param data: The JSON data to filter.
    :param regex: The regex pattern to filter the output.
    :param path: The JMESPath query to extract the view to apply
                 the regex filter to. This works relative to the
                 top-level elements of the output, e.g., if the output
                 is a list of dictionaries, the regex query will be
                 applied to each dictionary and if that dictionary
                 has a path (denoted by the regex path) that matches
                 the regex pattern, the dictionary will be included
                 in the output. We serialize the view of the dictionary
                 to a string before applying the regex pattern. We do
                 something similar for a dictionary of key-value pairs,
                 and likewise for a single value.

    :return: JSON (dict) object representing a filtered view of the top-level
                JSON output.
    """

    validate_json(data)

    regex = re.compile(regex)
    if isinstance(data, list):
        return [m for m in data if regex.search(str(jmespath.search(path, m)))]
    elif isinstance(data, dict):
        return {k: v for k, v in data.items() if regex.search(str(jmespath.search(path, {k: v})))}
    else:
        return data if regex.search(str(jmespath.search(path, data))) else None
    
def filter_paths(data, exclude_paths):
    """
    Filter JSON output by removing objects at the specified paths.

    :param data: The JSON data to filter.
    :param exclude_paths: The paths to exclude from the output.

    :return: JSON (dict) object representing a filtered view of the top-level
                JSON output.
    """

    def _filter(data, path):
        if data is None:
            return
        elif isinstance(data, list):
            _filter_list(data, path)
        elif isinstance(data, dict):
            _filter_dict(data, path)
        else:
            _filter_single(data, path)

    def _filter_list(data, path):
        if len(path) == 0:
            data.pop(path[0], None)
            return
    
        p = re.sub('\s+', '', path[0])
        if not re.match('\[.*\]', p):
            return
        
        # Remove brackets
        p = p[1:-1]

        # pattern for array indexing *, \d+, \d+:\d+
        if re.match('\*', p):
            for d in data:
                _filter(d, path[1:])
        elif re.match('\d+:\d+', p):
            start, end = map(int, p.split(':'))
            for d in data[start:end]:
                _filter(d, path[1:])
        elif re.match('\d+', p):
            index = int(p)
            _filter(data[index], path[1:])        
        
    def _filter_dict(data, path):
        if len(path) == 0:
            data.pop(path[0], None)
            return
    
        p = re.sub('\s+', '', path[0])
        # patterns: .*, .key
        if p == '*':
            for k, v in data.items():
                _filter(v, path[1:])
        else:
            k = p[1:]
            if k in data:
                _filter(data[k], path[1:])

    def _filter_single(data, path):
        if len(path) == 0:
            data.pop(path[0], None)

    for p in exclude_paths:
        _filter(data, p.split('.'))
