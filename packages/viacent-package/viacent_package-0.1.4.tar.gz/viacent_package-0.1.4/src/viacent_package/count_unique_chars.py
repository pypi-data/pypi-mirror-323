from collections import Counter
from functools import lru_cache

@lru_cache(maxsize = None)                                      #cache for storing results
def counter_unique_chars(input_string: str) -> int:
    if not isinstance(input_string, str):                       #input check
        raise TypeError("Input must be a str")                  #error
    char_count = Counter(input_string)                          #counting character frequency
    return sum(map(lambda x: x == 1, char_count.values()))      #csing map
