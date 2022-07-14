import hashlib
import json
import urllib

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