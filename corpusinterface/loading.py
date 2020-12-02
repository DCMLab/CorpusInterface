#  Copyright (c) 2020 Robert Lieck
from pathlib import Path
from urllib.request import urlretrieve
from urllib.error import URLError, HTTPError
import tarfile
import zipfile
from shutil import rmtree

import git

from . import config
from .corpora import FileCorpus
from .util import __DOWNLOAD__, __ACCESS__, __LOADER__, __URL__, \
    CorpusNotFoundError, DownloadFailedError, LoadingFailedError


# dictionary with loader functions
loaders = {
    "FileCorpus": FileCorpus.init
}


def populate_kwargs(corpus, kwargs_dict):
    if corpus is not None:
        for key, val in config.corpus_params(corpus):
            if key not in kwargs_dict:
                kwargs_dict[key] = val
    return kwargs_dict


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


def load(corpus=None, **kwargs):
    """
    Load a corpus.
    :param corpus: Name of the corpus to load or None to only use given keyword arguments.
    :param kwargs: Keyword arguments that are populated from config; specifying parameters as keyword arguments take
    precedence over the values from config.
    :return: output of loader
    """
    # populate keyword arguments from config
    kwargs = populate_kwargs(corpus, kwargs)
    # check if corpus exists
    path = Path(kwargs[config.__PATH__])
    if path.exists():
        if __LOADER__ in kwargs:
            # extract loader from kwargs
            loader = kwargs[__LOADER__]
            # if string was provided, lookup loader function
            if isinstance(loader, str):
                try:
                    loader = loaders[loader]
                except KeyError:
                    raise LoadingFailedError(f"Unknown {__LOADER__} '{loader}'.")
            # make sure loader is callable
            if not callable(loader):
                raise LoadingFailedError(f"{__LOADER__} '{loader}' is not callable.")
            # call loader with remaining kwargs
            return loader(**kwargs)
        else:
            raise LoadingFailedError("No loader specified.")
    else:
        # if it does not exist, try downloading (if requested) and then retry
        if config.getbool(kwargs.get(__DOWNLOAD__, False)):
            # prevent second attempt in reload
            kwargs[__DOWNLOAD__] = False
            # download
            download(corpus, **kwargs)
            # reload
            return load(corpus, **kwargs)
        else:
            raise CorpusNotFoundError(f"Corpus '{corpus}' at path '{path}' does not exist "
                                      f"(specify {__DOWNLOAD__}=True to try downloading).")


def create_download_path(corpus, kwargs):
    path = Path(kwargs[config.__PATH__])
    if path.exists():
        # directory is not empty
        if path.is_file() or list(path.iterdir()):
            raise DownloadFailedError(f"Cannot download corpus '{corpus}': "
                                      f"target path {path} exists and is non-empty.")
    else:
        path.mkdir(parents=True)
    return path


def download(corpus, **kwargs):
    if corpus is not None and config.get(corpus, config.__PARENT__) is not None:
        # for sub-corpora delegate downloading to parent
        download(config.get(corpus, config.__PARENT__), **kwargs)
    else:
        # populate keyword arguments from config
        kwargs = populate_kwargs(corpus, kwargs)
        # get access method
        access = kwargs[__ACCESS__]
        # use known access method or provided callable
        if access in ["git", "zip", "tar.gz"]:
            # known access method
            if access == 'git':
                # clone directly into the target directory
                path = create_download_path(corpus, kwargs)
                git.Repo.clone_from(url=kwargs[__URL__], to_path=path)
            else:
                # download to temporary file
                url = kwargs[__URL__]
                try:
                    # urlopen(url)
                    tmp_file_name, _ = urlretrieve(url=url)
                except (HTTPError, URLError) as e:
                    raise DownloadFailedError(f"Opening url '{url}' failed: {e}")
                # open with custom method
                if access == 'tar.gz':
                    tmp_file = tarfile.open(tmp_file_name, "r:gz")
                else:
                    assert access == 'zip'
                    tmp_file = zipfile.ZipFile(tmp_file_name)
                # unpack to target directory
                path = create_download_path(corpus, kwargs)
                tmp_file.extractall(path)
                tmp_file.close()
        elif callable(access):
            # access is a callable
            create_download_path(corpus, kwargs)
            return access(corpus, **kwargs)
        else:
            # unknown access method
            raise DownloadFailedError(f"Unknown access method '{kwargs[__ACCESS__]}'")
