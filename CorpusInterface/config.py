#  Copyright (c) 2020 Robert Lieck
import configparser
from pathlib import Path
from warnings import warn

# no imports with 'import config *'
# this is primarily to avoid unintentional overwriting of built-in 'set' with config.set
__all__ = []

# the default section
_DEFAULT = "DEFAULT"

# configuration
config = configparser.ConfigParser(allow_no_value=True,
                                   interpolation=configparser.ExtendedInterpolation(),
                                   default_section=_DEFAULT)


def load_config(*args, **kwargs):
    config.read(*args, **kwargs)


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
        if key == "info":
            yield key, get_info(corpus)
        elif key == "root":
            yield key, get_root(corpus)
        elif key == "path":
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


def set(corpus, key=None, value=None):
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
    set(corpus)
    # add key-value pairs
    for key, value in kwargs.items():
        set(corpus, key=key, value=value)


def set_default(key, value=None):
    set(_DEFAULT, key=key, value=value)


def get_info(corpus):
    info = config[corpus]["info"]
    if info is None:
        info = corpus
        for key, val in config[corpus].items():
            info += f"\n  {key}: {val}"
    return info


def get_root(corpus):
    # for sub-corpora the root is replaced by the parent's path
    parent = get(corpus, "parent")
    if parent is not None:
        root = get_path(parent)
    else:
        root = Path(get(corpus, "root")).expanduser()
    if not root.is_absolute():
        warn(f"Root for corpus '{corpus}' is a relative path ('{root}'), which is interpreted relative to the current "
             f"working directory ('{Path.cwd()}')", RuntimeWarning)
    return root


def get_path(corpus):
    # get raw value
    path = get(corpus, "path")
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


# read configurations from default locations when loading module
load_config([
    # default file that is part of the package, located one level up in the directory tree
    Path(__file__).parents[1] / 'corpora.ini',
    # file in user home corpora directory
    Path("~/corpora/corpora.ini").expanduser(),
    # file in current working directory
    'corpora.ini'
])
