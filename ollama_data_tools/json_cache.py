import os
import json
from time import time
from typing import Dict, Any, Union
from ollama_data_tools import conversion_tools as ct

class JsonCache:
    """
    A class to manage a cache file on disk. It uses JSON to store the data.
    It is a very simple cache that operates at the granularity of a
    single JSON or dictionary object. It is an immutable cache, meaning
    that once the data is saved, it cannot be modified. If you need to
    modify the data, you must save a new version of the data.

    Example usage:

        cache = JsonCache('~/.cache/my_cache.json', duration='5 minutes')
        cache.save({'key': 'value'})
        data = cache.load()

    It is designed to allow for slow operations to be cached between runs,
    say for a CLI tool that queries a remote API. The cache file is
    considered invalid if it is older than the specified duration.
    """

    def __init__(self, path: str, duration: Union[int,str] = '1 week'):
        """
        Initialize the CacheManager object.

        :param path: The path to the cache file.
        :param duration: The time duration the cache is valid. It can be a string
                         like "1 day" or an integer representing the number of seconds.
        """
        if not isinstance(duration, str):
            duration = f"{duration} seconds"

        _, duration = ct.parse_duration(duration)
        self.duration = duration
        self.path = os.path.expanduser(path)

        if self.duration.total_seconds() <= 0:
            raise ValueError("Duration must be positive.")

    def get_time_remaining(self) -> float:
        """
        Get the time remaining before the cache expires.

        :return: The time remaining in seconds.
        """
        if not os.path.exists(self.path):
            return 0
        elapsed = time() - os.path.getmtime(self.path)
        return max(0, self.duration.total_seconds() - elapsed)


    def is_valid(self) -> bool:
        """
        Check if the cache file is valid based on the elapsed time since
        it was created.

        :return: True if the cache is valid, False otherwise.
        """
        if not os.path.exists(self.path):
            return False

        elapsed = time() - os.path.getmtime(self.path)
        return elapsed <= self.duration.total_seconds()
    
    def clear(self) -> None:
        """
        Clear the cache file.
        """
        if os.path.exists(self.path):
            os.remove(self.path)

    def load(self) -> Dict[str, Any]:
        """
        Load the cache file from disk.

        :return: The content of the cache file as a dictionary.
        """
        if not self.is_valid():
            raise RuntimeError("Cache is invalid.")
        
        with open(self.path, 'r') as file:
            return json.load(file)

    def save(self, data: Dict[str, Any]) -> None:
        """
        Save data to the cache file.

        :param data: The data to cache.
        """
        dir_name = os.path.dirname(self.path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(self.path, 'w') as file:
            json.dump(data, file, indent=4)
