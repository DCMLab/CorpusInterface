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
_config = configparser.ConfigParser(allow_no_value=True,
                                    interpolation=configparser.ExtendedInterpolation(),
                                    default_section=_DEFAULT)


def load_config(*args, **kwargs):
    _config.read(*args, **kwargs)


def get(corpus, field):
    return _config[corpus][field]


def set(corpus, key=None, value=None):
    if key is None and value is not None:
        raise ValueError("Cannot set value without key")
    if key is None:
        _config[corpus] = {}
    else:
        _config[corpus][key] = value


def set_default(key, value=None):
    set(_DEFAULT, key=key, value=value)


def get_info(corpus):
    info = _config[corpus]["info"]
    if info is None:
        info = corpus
        for key, val in _config[corpus].items():
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
