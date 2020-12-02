#  Copyright (c) 2020 Robert Lieck
import configparser
from pathlib import Path
from warnings import warn

from .util import __DEFAULT__, __ROOT__, __PARENT__, __PATH__, \
    CorpusExistsError, CorpusNotFoundError, DuplicateCorpusError, DuplicateDefaultsError

# remember built-in set
python_set = set

# no imports with 'import config *'
# this is primarily to avoid unintentional overwriting of built-in 'set' with config.set
__all__ = []


##################
# helper functions
##################

def getbool(value):
    str_value = str(value).lower()
    if str_value in ['1', 'yes', 'true', 'on']:
        return True
    elif str_value in ['0', 'no', 'false', 'off']:
        return False
    else:
        raise ValueError(f"Could not convert value '{value}' to bool.")


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


def _get_config_obj():
    return configparser.ConfigParser(allow_no_value=True,
                                     interpolation=configparser.ExtendedInterpolation(),
                                     default_section=__DEFAULT__)


############################################################################
# The configuration data is stored in and accessed via a ConfigParser object
############################################################################

config = _get_config_obj()


##############################################################
# functions for initialising config and adding new information
##############################################################

def init_config(*args, default=None, home=None, local=None):
    # default config that is part of the package (located one level up in the directory tree)
    default_file = Path(__file__).parents[1] / 'default_config.ini'
    if default:
        load_config(default_file)
    elif default is None:
        config.read(default_file)

    # config file in user home/corpora directory
    home_file = Path("~/corpora/corpora.ini").expanduser()
    if home:
        load_config(home_file)
    elif home is None:
        config.read(home_file)

    # config file in current working directory
    local_file = 'corpora.ini'
    if local:
        load_config(local_file)
    elif local is None:
        config.read(local_file)

    # load explicitly provided files
    for file in args:
        load_config(file)


def reset_config(*args, **kwargs):
    clear_config(clear_default=True)
    init_config(*args, **kwargs)


def load_config(file, merge_duplicates=False, merge_defaults=False):
    # if we cannot just merge everything
    if not merge_duplicates or not merge_defaults:
        # first load into separate config
        tmp_config = _get_config_obj()
        with open(file) as f:
            tmp_config.read_file(f)
        # check for duplicate sections/corpora
        if not merge_duplicates:
            # get sections as sets
            old_sections = python_set(config.sections())
            new_sections = python_set(tmp_config.sections())
            # check whether they are disjoints and raise if they are not
            if not old_sections.isdisjoint(new_sections):
                raise DuplicateCorpusError(f"Config file '{file}' contains corpora that are already present "
                                           f"({old_sections.intersection(new_sections)}). "
                                           f"Use merge_duplicates=True to merge them.")
        # check for non-empty defaults on both configs
        if not merge_defaults and config.defaults() and tmp_config.defaults():
            raise DuplicateDefaultsError(f"Existing config and config from file '{file}' both contain non-empty "
                                         f"defaults. Use merge_defaults=True to merge them.")
    with open(file) as f:
        config.read_file(f)


def set_key_value(corpus, key, value):
    corpus = _corpus_to_str(corpus)
    if not corpus in config:
        raise CorpusNotFoundError(f"Corpus '{corpus}' not found in config")
    else:
        config[corpus][_key_to_str(key)] = _value_to_str(value)


def set(corpus, **kwargs):
    for key, value in kwargs.items():
        set_key_value(corpus, key=key, value=value)


def add_corpus(corpus, exists_ok=False, **kwargs):
    corpus = _corpus_to_str(corpus)
    if corpus in config:
        if not exists_ok:
            raise CorpusExistsError(f"Corpus '{corpus}' already exists in config. Use set() to modify values.")
    else:
        # add empty corpus
        config[corpus] = {}
    # add key-value pairs
    set(corpus, **kwargs)


def set_default_key_value(key, value=None):
    set_key_value(__DEFAULT__, key=key, value=value)


def set_default(**kwargs):
    set(__DEFAULT__, **kwargs)


################################################
# functions for deleting information from config
################################################

def delete_corpus(corpus, not_exists_ok=False):
    corpus = _corpus_to_str(corpus)
    if corpus not in config:
        if not_exists_ok:
            return
        else:
            raise CorpusNotFoundError(f"Corpus '{corpus}' not found in config")
    assert config.remove_section(section=corpus)


def clear_config(clear_default=False):
    for sec in config.sections():
        assert config.remove_section(section=sec)
    if clear_default:
        config[__DEFAULT__] = {}


##################################################
# functions for retrieving information from config
##################################################

def get(corpus, key, raw=False):
    if not raw:
        # unless raw values are requested, return processed versions of root and path
        if key == __ROOT__:
            # for sub-corpora the root is replaced by the parent's path
            parent = get(corpus, __PARENT__)
            if parent is not None:
                root = get(parent, __PATH__)
            else:
                root = config[_corpus_to_str(corpus)][__ROOT__]
                root = Path(root).expanduser()
            if not root.is_absolute():
                warn(f"Root for corpus '{corpus}' is a relative path ('{root}'), "
                     f"which is interpreted relative to the current "
                     f"working directory ('{Path.cwd()}')", RuntimeWarning)
            return root
        elif key == __PATH__:
            # get raw value
            path = config[_corpus_to_str(corpus)][__PATH__]
            # if not specified, default to corpus name
            if path is None:
                path = corpus
            # convert to path
            path = Path(path).expanduser()
            # absolut paths overwrite root; relative paths are appended
            if path.is_absolute():
                return path
            else:
                return get(corpus, __ROOT__) / path
    # default (and if raw is requested): return values directly from config
    return config[_corpus_to_str(corpus)][_key_to_str(key)]


def corpora():
    yield from config.sections()


def corpus_params(corpus, raw=False):
    corpus = _corpus_to_str(corpus)
    if corpus not in config:
        raise CorpusNotFoundError(f"Corpus '{corpus}' not found in config")
    for key in config[corpus]:
        yield key, get(corpus, key, raw=raw)


def summary(corpus=None, raw=False):
    if corpus is None:
        # without specific corpus summarise all corpora
        return "\n\n".join(summary(corpus, raw=raw) for corpus in [__DEFAULT__] + list(corpora()))
    else:
        # summarise corpus by providing all parameters
        corpus = _corpus_to_str(corpus)
        s = f"[{corpus}]"
        for key, val in corpus_params(corpus, raw=raw):
            s += f"\n    {key}: {val}"
        return s


####################################
# Initialise config on module import
####################################
init_config()
