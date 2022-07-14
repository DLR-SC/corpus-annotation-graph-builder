import hashlib
import json
import urllib
from re import sub

def get_hash_from_str(str):
    hashing_func = hashlib.sha256
    str2int = lambda s : int(hashing_func(s.encode()).hexdigest(), 16)
    return str2int(str)

def encode_name(name):
    """ Encodes any string into a string consisting only of characters valid in ArangoDB _keys.

    Args:
        name (string): The string to be encoded

    Returns:
        (string) Encoded result

    """
    enc_n = urllib.parse.quote_plus(name)
    enc_n = enc_n.replace("~", "%7E")
    return enc_n.replace("%", ")@(")

def to_dictionary(obj):
    return json.loads(json.dumps(obj, default=lambda o: vars(o)))

def camel_case(s):
  s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
  return ''.join([s[0].lower(), s[1:]])

def filter_dic(obj, fields):
    dict_ = to_dictionary(obj)
    dict_ = {k: v for k, v in dict_.items() if k in fields and v is not None}
    return dict_

def camel_nest_dic(dict_):
    res = {}
    for k, v in dict_.items():
        # Check if value is of dict type
        if isinstance(v, dict):
            res[camel_case(k)] = camel_nest_dic(v)
        else:
            # If value is not dict type then yield the value
            if v is not None:
                res[camel_case(k)] =v
    return res

