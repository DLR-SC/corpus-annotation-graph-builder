import hashlib
import importlib
import json
import urllib
from re import sub


def get_hash_from_str(str: str) -> str:
    """generate a sha256-16 byte int from your string to use as a key

    :param str: the string to hash
    :type str: str
    :return: the hasehed string
    :rtype: str
    """
    hashing_func = hashlib.sha256
    def str2int(s): return int(hashing_func(s.encode()).hexdigest(), 16)
    return str2int(str)


def encode_name(name: str) -> str:
    """Encodes any string in a readable key (length may be of an issue)

    :param name: the string to encode
    :type name: str
    :return: the encoded name
    :rtype: str
    """
    enc_n = urllib.parse.quote_plus(name)
    enc_n = enc_n.replace("~", "%7E")
    return enc_n.replace("%", ")@(")


def to_dictionary(obj: object) -> dict:
    """Deep-clone an object by jsonifying it

    :param obj: the object to deep-clone
    :type obj: object
    :return: the nested dicts
    :rtype: dict
    """
    return json.loads(json.dumps(obj, default=lambda o: vars(o)))


def camel_case(s) -> str:
    # source: https://www.w3resource.com/python-exercises/string/python-data-type-string-exercise-96.php
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


def filter_dic(obj, fields=None) -> dict:
    dict_ = to_dictionary(obj)
    dict_ = {k: v for k, v in dict_.items() if (
        (fields is None or k in fields) and v is not None)}
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
                res[camel_case(k)] = v
    return res

def load_module(module_name:str):
    return importlib.import_module(module_name)

def get_cls_from_path(path: str):
    module_name, class_name = path.rsplit(".", 1)

    cls = getattr(importlib.import_module(module_name), class_name)
    return cls, class_name
