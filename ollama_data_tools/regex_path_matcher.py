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
    :param elemwise: Whether to apply the regex matcher to each element
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
    
