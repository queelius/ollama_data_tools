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

def regex_path_matcher(data, regex, path='@', elemwise=True):
    """
    Match a regular expression to the JSON data on a JMESPath query.
    We apply he regex matcher to the view of the data that the JMESPath
    query returns, or if element-wise, we apply the matcher
    to each sub-element of data, e.g., if we give a list of dictionaries,
    we apply the matcher to each dictionary.

    We serialize the JSON view of the data to a string before applying the
    regex pattern.

    :param data: The JSON data to match the regex pattern against.
    :param regex: The regex pattern.
    :param path: The JMESPath query that creates the view to apply
                 the matcher to.
    :param per_elem: Whether to apply the regex matcher to each element
                     of data as opposed to the entire data object.

    :return: JSON (dict) object representing a filtered view of the top-level
                JSON output.
    """

    validate_json(data)
    regex = re.compile(regex)
    if elemwise:
        if isinstance(data, list):
            return [m for m in data if regex.search(str(jmespath.search(path, m)))]
        elif isinstance(data, dict):
            return {k: v for k, v in data.items() if regex.search(str(jmespath.search(path, {k: v})))}

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
