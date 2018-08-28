import re
from collections import namedtuple

# array regex 
_regex = r'\[\d\]'
_pattern = re.compile(_regex)


# define parse result struct for var
ParseVar = namedtuple('ParseVar', ('value', 'start', 'end', 'default_value'))


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
    return parsed key
    """
    _config = {}
    for key, value in config.items():
        keys = key.split('.')
        _parse(keys, value, _config)
    return _config

def _parse_value(text: str):
    """
    parse var in text
    """
    start = -1
    end = -1
    flag = False
    default_value = -1

    var = []
    i = 0
    
    while i < len(text):
        if text[i: i+2] == '${':
            start = i # + 2
            if flag == True:
                raise Exception("match error [idx= {}/text= {}".format(i, text))
            flag = True
            i += 1
            default_value = -1
        elif text[i] == ':':
            if flag :
                default_value = i
        elif text[i] == '}':
            end = i
            if flag == True and start < end and start != -1:
                if default_value == -1:
                    v = text[start+2: end]
                    dv = None
                else:
                    v = text[start+2: default_value]
                    dv = text[default_value + 1: end].strip()
                _var = ParseVar(v, start, end, dv)
                var.append(_var)
            else:
                raise Exception("match error [idx= {}/text= {}".format(i, text))
                
            flag = False
        i += 1
    return var


def _parse_var(value: str, environs: dict):
    if not ('${' in value and '}' in value):
        return None
    _ret_value = _parse_value(value)
    if len(_ret_value) < 1:
        return None

    var = []
    pre = 0
    for item in _ret_value:
        _rep_value = environs.get(item.value, item.default_value)
        if not _rep_value:
            raise ValueError("var[{}] not have value".format(item))
        var.append(value[pre: item.start])
        var.append(str(_rep_value))
        pre = item.end + 1
    return ''.join(var)


def parse_var(config, environs):
    for key, value in config.items():
        if isinstance(value, dict):
            parse_var(value, environs)
        elif isinstance(value, list):
            for i, _v in enumerate(value):
                if isinstance(_v, str):
                    pv = _parse_var(_v, environs)
                    if pv:
                        value[i] = pv
                else:
                    parse_var(_v, environs)
        elif isinstance(value, str):
            pv = _parse_var(value, environs)
            if pv:
                config[key] = pv


if __name__ == "__main__":
    s = 'just test{varhaa${var2:default}dfd${var3}'
    dic = {
            "FIND[0].pattern": s,
            "FIND[1].pattern": 2,
            "REDIS_CONFIG.config[0].k1.a[0]":'v1',
            "REDIS_CONFIG.config[0].k1.a[1]":'v2',
            "REDIS_CONFIG.config[1].k2":'v2',
            }
    config = parse_key(dic)
    print(config)
    

    _ret_value = _parse_value(s)
    print(_ret_value)

    parse_var(config, {})
    print(config)
    

