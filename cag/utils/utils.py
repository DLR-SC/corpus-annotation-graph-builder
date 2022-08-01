import hashlib
import importlib
import json
import urllib
from re import sub

def get_hash_from_str(str):
    """generate a sha256-16 byte int from your string to use as a key

    :param str: _description_
    :type str: _type_
    :return: _description_
    :rtype: _type_
    """
    hashing_func = hashlib.sha256
    str2int = lambda s : int(hashing_func(s.encode()).hexdigest(), 16)
    return str2int(str)

def encode_name(name):
    """Encodes any string in a readable key (length may be of an issue)

    :param name: _description_
    :type name: _type_
    :return: _description_
    :rtype: _type_
    """
    enc_n = urllib.parse.quote_plus(name)
    enc_n = enc_n.replace("~", "%7E")
    return enc_n.replace("%", ")@(")


def to_dictionary(obj: object) -> dict:
    """Deep-clone an object by jsonifying it
    
    :param obj: _description_
    :type obj: object
    :return: _description_
    :rtype: dict
    """
    return json.loads(json.dumps(obj, default=lambda o: vars(o)))


def camel_case(s) -> str:
    # source: https://www.w3resource.com/python-exercises/string/python-data-type-string-exercise-96.php
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


def filter_dic(obj, fields=None) -> dict:
    dict_ = to_dictionary(obj)
    dict_ = {k: v for k, v in dict_.items() if ((fields is None or k in fields) and v is not None)}
    return dict_


def camel_nest_dict(dict_) -> dict:
    res = {}
    for k, v in dict_.items():
        # Check if value is of dict type
        if isinstance(v, dict):
            res[camel_case(k)] = camel_nest_dict(v)
        else:
            # If value is not dict type then yield the value
            if v is not None:
                res[camel_case(k)] =v
    return res

def get_cls_from_path(path):
    module_name, class_name = path.rsplit(".", 1)

    cls = getattr(importlib.import_module(module_name), class_name)

    return cls, class_name