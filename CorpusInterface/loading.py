#  Copyright (c) 2020 Robert Lieck
from pathlib import Path
import urllib.request
import tarfile
import zipfile
import logging
from shutil import rmtree

import git

from CorpusInterface import config
from CorpusInterface.corpora import FileCorpus


# dictionary with reader functions
readers = {
    "FileCorpus": FileCorpus.init
}


# standard keyword arguments
__DOWNLOAD__ = "download"
__READER__ = "reader"


# custom exceptions
class CorpusNotFoundError(Exception):
    pass


class DownloadFailedError(Exception):
    pass


class LoadingError(Exception):
    pass


def populate_kwargs(corpus, kwargs_dict):
    try:
        iter = config.get(corpus)
    except KeyError:
        # corpus is not in config: no keyword arguments to populate (pass)
        pass
    else:
        for key, val in iter:
            if key not in kwargs_dict:
                kwargs_dict[key] = val
    return kwargs_dict


def in_kwargs_and_true(key, kwarg_dict):
    return key in kwarg_dict and config.getboolean(kwarg_dict[key])


def remove(corpus, silent=False, not_exists_ok=False, not_dir_ok=False, **kwargs):
    # populate keyword arguments
    kwargs = populate_kwargs(corpus, kwargs)
    # get path to remove
    path = Path(kwargs[config.__PATH__])
    # check path
    if path.exists():
        if not path.is_dir() and not not_dir_ok:
            raise NotADirectoryError(f"Path {path} for corpus '{corpus}' is not a directory.")
    else:
        if not not_exists_ok:
            raise FileNotFoundError(f"Path {path} for corpus '{corpus}' does not exist.")
        else:
            return
    # get confirmation
    if not silent:
        while True:
            rm = input(f"Remove corpus '{corpus}' ({path}) [y/N]: ").strip().lower()
            if rm in ['y', 'yes']:
                rm = True
                break
            elif rm in ['', 'n', 'no']:
                rm = False
                break
    else:
        rm = True
    # remove
    if rm:
        rmtree(path)
    else:
        print(f"Canceled. Corpus '{corpus}' ({path}) not removed.")


def load(corpus, **kwargs):
    """
    Load a corpus.
    :param corpus: Name of the corpus to load.
    :param kwargs: Keyword arguments that are populated from config (if the corpus is registered); specified values
    for keyword arguments take precedence over the values from config.
    :return:
    """
    # populate keyword arguments from config
    kwargs = populate_kwargs(corpus, kwargs)
    # check if corpus exists
    if Path.exists(kwargs[config.__PATH__]):
        return kwargs[__READER__](**kwargs)
    else:
        # if it does not exist, try downloading (if requested) and then retry
        if in_kwargs_and_true(__DOWNLOAD__, kwargs):
            # prevent second attempt in reload
            kwargs[__DOWNLOAD__] = False
            # download
            download(corpus, **kwargs)
            # reload
            return load(corpus, **kwargs)
        else:
            raise CorpusNotFoundError(f"Corpus '{corpus}' does not exist (specify download=True to try downloading).")


def download(corpus, **kwargs):
    parent = config.get(corpus, config.__PARENT__)
    if parent is not None:
        # for sub-corpora delegate downloading to parent
        download(parent, **kwargs)
    else:
        # populate keyword arguments from config
        kwargs = populate_kwargs(corpus, kwargs)
        # get access method
        access = kwargs[config.__ACCESS__]
        # check if path already exists
        path = Path(kwargs[config.__PATH__])
        if path.exists():
            # directory is not empty
            if path.is_file() or list(path.iterdir()):
                raise DownloadFailedError(f"Cannot download corpus '{corpus}': "
                                          f"target path {path} exists and is non-empty. "
                                          f"Use remove('{corpus}') to remove.")
        else:
            path.mkdir(parents=True)
        logging.info(f"Downloading corpus '{corpus}' to {path}")
        # use known access method or provided callable
        if access in ["git", "zip", "tar.gz"]:
            # known access method
            if access == 'git':
                # clone directly into the target directory
                git.Repo.clone_from(url=kwargs['url'], to_path=path)
            else:
                # download to temporary file
                tmp_file_name, _ = urllib.request.urlretrieve(url=kwargs['url'])
                # open with custom method
                if access == 'tar.gz':
                    tmp_file = tarfile.open(tmp_file_name, "r:gz")
                else:
                    assert access == 'zip'
                    tmp_file = zipfile.ZipFile(tmp_file_name)
                # unpack to target directory
                tmp_file.extractall(path)
                tmp_file.close()
        elif callable(access):
            # access is a callable
            return access(corpus, **kwargs)
        else:
            # unknown access method
            raise DownloadFailedError(f"Unknown access method '{kwargs['access']}'")
