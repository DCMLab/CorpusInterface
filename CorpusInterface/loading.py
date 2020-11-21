#  Copyright (c) 2020 Robert Lieck
from pathlib import Path
import shutil
import urllib.request
import tarfile
import zipfile
import logging
from warnings import warn

import git

from CorpusInterface import config


# standard keyword arguments
__DOWNLOAD__ = "download"
__OVERWRITE__ = "overwrite"
__READER__ = "reader"


# custom exceptions
class CorpusNotFoundError(Exception):
    pass


class DownloadFailedError(Exception):
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
        # - requesting overwrite of parent not permitted for security reasons
        # - if 'overwrite' is NOT explicitly specified but IS specified in config of parent, that value is used
        if in_kwargs_and_true(__OVERWRITE__, kwargs):
            warn("Requesting overwrite of parent from child is not permitted. The option will be disabled and the "
                 "default from the parent corpus will be used.", RuntimeWarning)
            del kwargs[__OVERWRITE__]
        # download parent
        download(parent, **kwargs)
    else:
        # populate keyword arguments from config
        kwargs = populate_kwargs(corpus, kwargs)
        # get access method
        access = kwargs[config.__ACCESS__]
        # check if path already exists
        path = Path(kwargs[config.__PATH__])
        if path.exists():
            # path exists (overwriting directories may be requested)
            if in_kwargs_and_true(__OVERWRITE__, kwargs):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    raise DownloadFailedError(f"Cannot overwrite target path {path}, because it is not a directory")
            else:
                raise DownloadFailedError(f"Cannot download corpus '{corpus}', target path {path} exists "
                                   f"(use overwrite=True to overwrite existing directories).")
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
            raise ValueError(f"Unknown access method '{kwargs['access']}'")
