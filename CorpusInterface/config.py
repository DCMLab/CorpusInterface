#  Copyright (c) 2020 Robert Lieck
import configparser
from pathlib import Path
from warnings import warn

# no imports with 'import config *'
# this is primarily to avoid unintentional overwriting of built-in 'set' with config.set
__all__ = []

# the default section
__DEFAULT__ = "DEFAULT"
# standard keys default section
__INFO__ = "info"
__ROOT__ = "root"
__PATH__ = "path"
__PARENT__ = "parent"
__ACCESS__ = "access"
__URL__ = "url"
__TYPE__ = "type"

# configuration
config = configparser.ConfigParser(allow_no_value=True,
                                   interpolation=configparser.ExtendedInterpolation(),
                                   default_section=__DEFAULT__)


def init():
    # read configurations from default locations when loading module
    config.read([
        # default file that is part of the package, located one level up in the directory tree
        Path(__file__).parents[1] / 'corpora.ini',
        # file in user home corpora directory
        Path("~/corpora/corpora.ini").expanduser(),
        # file in current working directory
        'corpora.ini'
    ])


# actually perform initialisation
init()


def load_config(file):
    with open(file) as file:
        config.read_file(file)


def clear(clear_default=False):
    for sec in config.sections():
        assert config.remove_section(section=sec)
    if clear_default:
        config[__DEFAULT__] = {}


def _corpus_to_str(corpus):
    if not isinstance(corpus, str):
        warn(f"corpus '{corpus}' is not a string and will be converted",
             RuntimeWarning)
        corpus = str(corpus)
    return corpus


def _key_to_str(key):
    if not isinstance(key, str):
        warn(f"key '{key}' is not a string and will be converted (note that keys are case insensitive)",
             RuntimeWarning)
        key = str(key)
    return key


def _value_to_str(value):
    if value is not None and not isinstance(value, str):
        warn(f"value '{value}' is not a string and will be converted",
             RuntimeWarning)
        value = str(value)
    return value


def iterate_corpus(corpus):
    for key, val in config[_corpus_to_str(corpus)].items():
        if key == __INFO__:
            yield key, get_info(corpus)
        elif key == __ROOT__:
            yield key, get_root(corpus)
        elif key == __PATH__:
            yield key, get_path(corpus)
        else:
            yield key, val


def getboolean(value):
    str_value = str(value).lower()
    if str_value in ['1', 'yes', 'true', 'on']:
        return True
    elif str_value in ['0', 'no', 'false', 'off']:
        return False
    else:
        raise ValueError(f"Could not convert value '{value}' to bool.")


def get(corpus, key=None):
    if key is None:
        return iterate_corpus(corpus)
    else:
        return config[_corpus_to_str(corpus)][_key_to_str(key)]


def set(corpus, **kwargs):
    # reset corpus
    if not kwargs:
        set_key_value(corpus)
    # set keys-value arguments
    for key, value in kwargs.items():
        set_key_value(corpus, key=key, value=value)


def set_key_value(corpus, key=None, value=None):
    if key is None and value is not None:
        raise ValueError("Cannot set value without key")
    corpus = _corpus_to_str(corpus)
    if key is None:
        if corpus in config:
            warn(f"Corpus '{corpus}' already exists and will be reset", RuntimeWarning)
        config[corpus] = {}
    else:
        config[corpus][_key_to_str(key)] = _value_to_str(value)


def add_corpus(corpus, **kwargs):
    if corpus in config:
        raise KeyError(f"Corpus '{corpus}' already exists. Use set() to modify values.")
    # add empty corpus
    set_key_value(corpus)
    # add key-value pairs
    if kwargs:
        set(corpus, **kwargs)


def set_default_key_value(key, value=None):
    set_key_value(__DEFAULT__, key=key, value=value)


def set_default(**kwargs):
    set(__DEFAULT__, **kwargs)


def get_info(corpus):
    info = config[corpus][__INFO__]
    if info is None:
        info = corpus
        for key, val in config[corpus].items():
            info += f"\n  {key}: {val}"
    return info


def get_root(corpus):
    # for sub-corpora the root is replaced by the parent's path
    parent = get(corpus, __PARENT__)
    if parent is not None:
        root = get_path(parent)
    else:
        root = get(corpus, __ROOT__)
        try:
            root = Path(root).expanduser()
        except TypeError:
            raise TypeError(f"Could not get root directory. Could not convert {root} to path.")
    if not root.is_absolute():
        warn(f"Root for corpus '{corpus}' is a relative path ('{root}'), which is interpreted relative to the current "
             f"working directory ('{Path.cwd()}')", RuntimeWarning)
    return root


def get_path(corpus):
    # get raw value
    path = get(corpus, __PATH__)
    # if not specified, default to corpus name
    if path is None:
        path = corpus
    # convert to path
    path = Path(path).expanduser()
    # absolut paths overwrite root; relative paths are appended
    if path.is_absolute():
        return path
    else:
        return get_root(corpus).joinpath(path)
