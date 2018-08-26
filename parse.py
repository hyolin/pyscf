import re
from collections import namedtuple

# array regex 
_regex = r'\[\d\]'
_pattern = re.compile(_regex)


# define parse result struct for var
ParseVar = namedtuple('ParseVar', ('value', 'start', 'end'))


def _parse(keys: list, value, config: dict, pattern=_pattern):
    if not isinstance(keys, list):
        raise TypeError("keys must be list")
    if not isinstance(config, dict):
        raise TypeError("config must be dict ")
    last_indx = len(keys) - 1
    _config = config
    for i, key in enumerate(keys):
        match = pattern.search(key)
        if match:
            idx = int(key[match.start()+1: len(key)-1])
            key = key[: match.start()]
            _value = _config.get(key, [])
            if idx >= len(_value):
                _value.extend([None] * (idx - len(_value) + 1))
            if i == last_indx:
                _value[idx] = value
            elif _value[idx] is None:
                _value[idx] = {}
            _config[key] = _value
            _config = _config[key][idx]
        else:
            if i == last_indx:
                _config[key] = value
            elif key not in _config:
                _config[key] = {}
            _config = _config[key]

def parse_key(config: dict):
    """
    parse spring cloud config keys
    """
    _config = {}
    for key, value in config.items():
        keys = key.split('.')
        _parse(keys, value, _config)
    return _config

def _parse_value(text: str):
    start = -1
    end = -1
    flag = False
    
    var = []
    i = 0
    
    import pdb
    pdb.set_trace()
    while i < len(text):
        if text[i: i+2] == '${':
            start = i + 2
            if flag == True:
                raise Exception("match error [idx= {}/text= {}".format(i, text))
            flag = True
            i += 1
        elif text[i] == '}':
            end = i
            if flag == True and start < end and start != -1:
                _var = ParseVar(text[start: end], start, end)
                var.append(_var)
            else:
                raise Exception("match error [idx= {}/text= {}".format(i, text))
                
            flag = False
        i += 1
    return var


def parse_var(config):
    pass

if __name__ == "__main__":
    dic = {
            "FIND[0].pattern": 1,
            "FIND[1].pattern": 2,
            "REDIS_CONFIG.config[0].k1.a[0]":'v1',
            "REDIS_CONFIG.config[0].k1.a[1]":'v2',
            "REDIS_CONFIG.config[1].k2":'v2',
            }
    config = parse_key(dic)
    print(config)
    
    s = 'just test{varhaa${var2}dfd${var3}'
    _ret_value = _parse_value(s)
    print(_ret_value)
