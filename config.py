import datetime
_origin_time_ = datetime.datetime(2020, 6, 7, 23, 45, 39)
_time_since_origin_ = datetime.datetime.now() - _origin_time_
_seconds_since_origin_ = _time_since_origin_.days * 3600*24 + _time_since_origin_.seconds

BRUTE_SLOT_SIZE = 10**8
CACHE_PATH = './commissions.json'
DEFAULT_SLOT = 73500891 # Default to Oct '22
VERBOSITY = 10**6

MAX_AFTER = int(_seconds_since_origin_ * 0.95) # Bruting mustn't exceed the current time
