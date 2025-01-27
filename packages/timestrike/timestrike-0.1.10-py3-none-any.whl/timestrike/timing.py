import time
from string import punctuation, ascii_letters, digits

def get_length(measure_time, chars=punctuation + ascii_letters + digits, sample=1, selector=min, max_len=64):
    '''
    Performs a timing attack to get the length of the key, by testing messages of lengths from 0 to max_length-1.

    Parameters
    ----------
    measure_time: the user-defined function that takes a message and returns the time it takes to test if it is the correct key
    chars: the character set of the key (default is punctuation, letters and digits)
    sample: the number of times each possibility is tested (default is 1)
    selector: the function giving a single time for a possibility based on all its measured times (default is min)
    max_length: the maximum length of the key to be tested (default is 64)
    '''
    times = [[] for _ in range(max_len)]
    for _ in range(sample):
        for l in range(max_len):
            message = chars[0] * l
            times[l].append(measure_time(message))
    return max(range(max_len), key=lambda l: selector(times[l]))

def get_key(measure_time, length=None, chars=punctuation + ascii_letters + digits, sample=1, selector=min, initial_key="", print_keys=False):
    '''
    Performs a timing attack to get the content of the key, by iteratively testing each character.

    Parameters
    ----------
    measure_time: the user-defined function that takes a message and returns the time it takes to test if it is the correct key
    length: the length of the key if you already know it (default is automatically calculated with get_length)
    chars: the character set of the key (default is punctuation, letters and digits)
    sample: the number of times each possibility is tested (default is 1)
    selector: the function giving a single time for a possibility based on all its measured times (defailt is min)
    initial_key: the first characters of the key if you already know it (default it '')
    print_keys: the option to print the partial keys each time a character is found (default is False)
    '''
    if length is None:
        length = get_length(measure_time, chars=chars, sample=sample, selector=selector, max_len=64)
    for _ in range(length - len(initial_key)):
        times = {c:[] for c in chars}
        for _ in range(sample):
            for char in chars:
                message = initial_key + char + chars[0] * (length - len(initial_key) - 1)
                response_time = measure_time(message)
                times[char].append(response_time)
        selected = max(times, key=lambda c: selector(times[c]))
        initial_key += selected
        if print_keys:
            print(initial_key)
    return initial_key
