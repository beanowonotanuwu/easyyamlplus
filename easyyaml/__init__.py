import os
import yaml

__version__ = '0.0.1'

_yaml_ext = ('.yml', '.yaml')


def _is_valid_key(key:str, invalid_key_list:list=None) -> None:
    if not (isinstance(key, str) and key and key.replace('_', '').isalnum() and not key[0].isdecimal()) \
        or (invalid_key_list and key in invalid_key_list):
        raise ValueError("Invalid Key: %s"%(key))

def _is_valid_value(value):
    if not isinstance(value, (type(None), str, int, float, tuple, list, dict)):
        raise ValueError("Invalid Value: %s"%(str(value)))

def _idx2key(idx):
    return "_%d"%(idx)

def _key2idx(key):
    return int(key[1:])

class YamlDict(dict):
    def __init__(self, d:dict=None, **kwargs):
        d = d or {}
        d.update(**kwargs)
        
        for k, v in d.items():
            setattr(self, k, v)
    
    def __setattr__(self, key:str, value):
        _is_valid_key(key, dict.__dict__.keys())
        _is_valid_value(value)
        if isinstance(value, (tuple, list)):
            value = YamlList([self.__class__(x) 
                                if isinstance(x, dict) else x for x in value])
        elif isinstance(value, dict):
            value = self.__class__(value)
        super(YamlDict, self).__setattr__(key, value)
        super(YamlDict, self).__setitem__(key, value)

    __setitem__ = __setattr__

    def update(self, d:dict=None, **kwargs):
        d = d or {}
        d.update(kwargs)
        for k, v in d:
            setattr(self, k, v)

    def pop(self, k:str, default=None):
        delattr(self, k)
        return super(YamlDict, self).pop(k, default)

    def clear(self):
        for k in self.keys():
            delattr(self, k)
        super(YamlDict, self).clear()

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, list):
                # v = [x.to_dict() if isinstance(x, dict) else x for x in v]
                v = v.to_list()
            elif isinstance(v, dict):
                v = v.to_dict()
            d[k] = v
        return d

class YamlList(list): 
    def __init__(self, it=None):
        it = it or []
        for idx, v in enumerate(it):
            self.append(v)

    def __setitem__(self, idx:int, value):
        _is_valid_value(value)
        key = _idx2key(idx)
        if isinstance(value, (tuple, list)):
            value = self.__class__(value)
        elif isinstance(value, dict):
            value = YamlDict(value)
        super(YamlList, self).__setattr__(key, value)
        super(YamlList, self).__setitem__(idx, value)

    def __setattr__(self, key:str, value):
        _is_valid_value(value)
        idx = _key2idx(key)
        if isinstance(value, (tuple, list)):
            value = self.__class__(value)
        elif isinstance(value, dict):
            value = YamlDict(value)
        super(YamlList, self).__setattr__(key, value)
        super(YamlList, self).__setitem__(idx, value)

    def append(self, v):
        super(YamlList, self).append(v)
        setattr(self, _idx2key(len(self)-1), v)

    def pop(self, index:int=None):
        idx = index or len(self)-1
        delattr(self, _idx2key(idx))
        if index:
            super(YamlList, self).pop(index)
        else:
            super(YamlList, self).pop()

    def to_list(self):
        l = []
        for v in self:
            if isinstance(v, list):
                v = v.to_list()
            elif isinstance(v, dict):
                v = v.to_dict()
            l.append(v)
        return l


def load(yaml_file):
    assert isinstance(yaml_file, str) and os.path.isfile(yaml_file)
    with open(yaml_file, 'r') as foo:
        yaml_data = yaml.load(foo)

    if isinstance(yaml_data, list):
        return YamlList(yaml_data)
    elif isinstance(yaml_data, dict):
        return YamlDict(yaml_data)

def save(yaml_file, yaml_data): 
    assert isinstance(yaml_file, str)
    if isinstance(yaml_data, list):
        yaml_data = yaml_data.to_list()
    elif isinstance(yaml_data, dict):
        yaml_data = yaml_data.to_dict()
    with open(yaml_file, 'w') as foo:
        yaml.dump(yaml_data, foo)


if __name__ == '__main__':
    ydict = YamlDict
    d = {'a': 123, 'b': 234, '_0': 345, '_1000':456, '_1xyz': 567, "test": {'c':[{"e":123}, 0, 1, 2], 'd':222}}
    yd = ydict(d)

    ylist = YamlList
    l = d.keys()
    yl = ylist(l)

    import ipdb; ipdb.set_trace()

    yd = load("./example.yaml")

    save("./temp.yaml", yd)

    