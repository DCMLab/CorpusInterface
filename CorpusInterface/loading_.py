import os
from pathlib import Path
import shutil
import subprocess
from contextlib import contextmanager
import pandas as pd
import random
import urllib.request
import tarfile
import zipfile
import logging

from CorpusInterface.corpus_ import FileCorpus, JSONCorpus, CSVCorpus


@contextmanager
def cwd(path):
    cwd = os.getcwd()
    os.chdir(path)
    yield None
    os.chdir(cwd)


# Get the directory for a corpus.
def get_dir(*, name, index_path=None, root_dir=None):
    # use default corpus root dir if not specified
    if root_dir is None:
        root_dir = Path(*Path(os.path.abspath(__file__)).parts[:-2]) / "corpora"
    # get corpus info
    info = get_info(name=name)
    # return or recurse
    if info['Parent'] is None:
        # return
        if info['Root'] is not None:
            return Path(*root_dir.parts, info['Name'], *info['Root'].split("/"))
        else:
            return Path(*root_dir.parts, info['Name'])
    else:
        # recurse
        # TODO: root is None??
        return Path(*get_dir(name=info['Parent'], index_path=index_path, root_dir=root_dir).parts,
                    *info['Root'].split("/"))

# This loads and returns the corpora.csv data
def get_list(index_path=None):
    return pd.read_csv(Path(*Path(os.path.abspath(__file__)).parts[:-2]) / "corpora.csv"
                       if index_path is None else index_path)

# Get the relevant line of corpora.csv for the specified corpus, if it exists
def get_info(*, name, index_path=None):
    corpora = get_list(index_path=index_path)
    hits = corpora[corpora['Name'] == name]
    if len(hits) == 0:
        raise ValueError(f"Could not find corpus with name '{name}', available corpora are:\n{corpora.to_string()}")
    elif len(hits) > 1:
        raise ValueError(f"Found multiple corpora with name '{name}':\n{hits.to_string()}")
    else:
        # construct info as dict with column names as keys
        info = {key: str(val.values[0]) for key, val in hits.items()}
        # replace 'nan' values by proper None
        return {key: None if val == 'nan' else val for key, val in info.items()}

# Download a specified corpus to disk. 
def download(*, name, index_path=None, root_dir=None):
    info = get_info(name=name, index_path=index_path)
    print(f"Attempting to download corpus '{name}'")
    while info['Parent'] is not None:
        logging.info(f"Delegating dowload to parent corpus {info['Parent']}")
        info = get_info(name=info['Parent'], index_path=index_path)
    # use default corpus root dir if not specified
    if root_dir is None:
        root_dir = Path(*Path(os.path.abspath(__file__)).parts[:-2]) / "corpora"
    # The directory target is just the name of the corpus
    corpus_dir = Path(*root_dir.parts, info['Name'])
    if os.path.isdir(corpus_dir):
        raise Warning(f"Corpus directory '{corpus_dir}' exists. Aborting download.")
    # make temprary directory and clone in there
    tmp_dir = str(random.randint(0, 10000000000))
    os.makedirs(tmp_dir)
    with cwd(tmp_dir):
        if info['AccessMethod'] == 'git':
            #TODO: This should be done with a proper git library for better
            #      error messages and tracking etc.
            subprocess.run(["git", "clone", info['URL']])
            subdirs = next(os.walk(os.getcwd()))[1]
            if len(subdirs) > 1:
                raise Warning("More than one subdirectory, something went wrong.")
            # move directory to intended corpus directory
            shutil.move(os.path.join(os.getcwd(), subdirs[0]), corpus_dir)
        elif info['AccessMethod'] == 'tar.gz':
            local_filename, headers = urllib.request.urlretrieve(info['URL'])
            tar = tarfile.open(local_filename, "r:gz")
            tar.extractall(corpus_dir)
            tar.close()
            os.remove(local_filename)
        elif info['AccessMethod'] == 'zip':
            local_filename, headers = urllib.request.urlretrieve(info['URL'])
            zf = zipfile.ZipFile(local_filename)
            zf.extractall(path=corpus_dir)
            zf.close()
            os.remove(local_filename)
        else:
            raise ValueError(f"Unknown access method '{info['AccessMethod']}' specified")
    # remove temporary directory
    os.removedirs(tmp_dir)

# Load a specified, previously downloaded corpus 
def load(*,name, index_path=None, root_dir=None, allow_download=False, **kwargs):
    # We want the info from the child, but need to recurse through the
    # parents until we find the right directory
    temp_info = get_info(name=name, index_path=index_path)
    logging.info(f"Attempting to load corpus '{name}'")
    while temp_info['Parent'] is not None:
        logging.info(f"Looking at parent corpus {temp_info['Parent']} to find root directory")
        temp_info = get_info(name=temp_info['Parent'], index_path=index_path)
    corpus_dir = get_dir(name=temp_info['Name'], index_path=index_path, root_dir=root_dir)
    corpus_info = get_info(name=name, index_path=index_path)
    if not os.path.isdir(corpus_dir) and allow_download:
        download(name=name, index_path=index_path, root_dir=root_dir)
        if not os.path.isdir(corpus_dir):
            raise Warning("Still cannot find corpus...did the download fail?")
    # We want the FileCorpus to look at the proper place inside the parent
    # corpus though
    corpus_dir = get_dir(name=name, index_path=index_path, root_dir=root_dir)
    if corpus_info['CorpusType'] == "files":
        return FileCorpus(path=corpus_dir,parameters=corpus_info['Parameters'], **kwargs)
    elif corpus_info['CorpusType'] == "json":
        return JSONCorpus(path=corpus_dir,parameters=corpus_info['Parameters'], **kwargs)
    elif corpus_info['CorpusType'] == "csv":
        return CSVCorpus(path=corpus_dir,parameters=corpus_info['Parameters'], **kwargs)
    else:
        raise TypeError(f"Unsupported corpus type '{corpus_info['CorpusType']}'")
