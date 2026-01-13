from marshmallow import Schema, post_dump
import re

def snake_to_camel(s: str) -> str:
    parts = s.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])

def _convert(obj):
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            nk = snake_to_camel(k)
            new[nk] = _convert(v)
        return new
    elif isinstance(obj, list):
        return [_convert(x) for x in obj]
    else:
        return obj

class BaseSchema(Schema):
    @post_dump
    def to_camel(self, data, many=False, **kwargs):
        # marshmallow may or may not pass `many`; accept it optionally
        if many and isinstance(data, list):
            return [_convert(x) for x in data]
        return _convert(data)
