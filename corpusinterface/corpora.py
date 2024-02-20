#  Copyright (c) 2020 Robert Lieck
from pathlib import Path
import os
import re
import json
import ast

import pandas


class Data:
    """An abstract base class for data items, such as corpora or documents."""
    def metadata(self, *args, **kwargs):
        raise NotImplementedError

    def data(self, *args, **kwargs):
        raise NotImplementedError


class FileCorpus(Data):
    """A collection of files in a directory"""

    # special keyword arguments
    __META_READER__ = "meta_reader"
    __FILE_READER__ = "file_reader"

    @classmethod
    def init(cls, **kwargs):
        if 'path' not in kwargs:
            raise TypeError("Missing required keyword argument 'path'")
        kwargs = {**dict(file_regex=None,
                         path_regex=None,
                         file_exclude_regex=None,
                         path_exclude_regex=None),
                  **kwargs}
        return FileCorpus(**kwargs)

    def __init__(self,
                 path,
                 file_regex=None,
                 path_regex=None,
                 file_exclude_regex=None,
                 path_exclude_regex=None,
                 **kwargs):
        # set path and check
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Corpus directory {self.path} does not exist")
        elif not self.path.is_dir():
            raise NotADirectoryError(f"{self.path} is not a directory")
        # remember additional keyword arguments
        self.kwargs = kwargs
        # initialise regex for including files
        if file_regex is None:
            self.file_regex = None
        else:
            self.file_regex = re.compile(file_regex)
        # initialise regex for including paths
        if path_regex is None:
            self.path_regex = None
        else:
            self.path_regex = re.compile(path_regex)
        # initialise regex for excluding files
        if file_exclude_regex is None:
            self.file_exclude_regex = None
        else:
            self.file_exclude_regex = re.compile(file_exclude_regex)
        # initialise regex for excluding paths
        if path_exclude_regex is None:
            self.path_exclude_regex = None
        else:
            self.path_exclude_regex = re.compile(path_exclude_regex)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path})"

    def metadata(self, *args, **kwargs):
        kwargs = {**self.kwargs, **kwargs}
        meta_reader = kwargs.get(self.__META_READER__, None)
        if meta_reader is None:
            return self.path
        else:
            return meta_reader(self.path, *args, **kwargs)

    def files(self):
        # recursively traverse directory
        for root, dirs, files in os.walk(self.path):
            root = Path(root)
            for file in files:
                path = root / file
                # check file inclusion regex
                if self.file_regex is not None and not self.file_regex.match(file):
                    continue # skip non-matching files
                # check path inclusion regex
                if self.path_regex is not None and not self.path_regex.match(str(path)):
                    continue  # skip non-matching paths
                # check file exclusion regex
                if self.file_exclude_regex is not None and self.file_exclude_regex.match(file):
                    continue  # skip matching files
                # check path exclusion regex
                if self.path_exclude_regex is not None and self.path_exclude_regex.match(str(path)):
                    continue  # skip matching paths
                # yield absolute path to file
                yield path

    def data(self, *args, **kwargs):
        kwargs = {**self.kwargs, **kwargs}
        file_reader = kwargs.get(self.__FILE_READER__, None)
        for path in self.files():
            if file_reader is None:
                yield path
            else:
                yield file_reader(path, *args, **kwargs)

# single file corpora
# -------------------

class SingleFileCorpus(Data):
    """
    A corpus consisting of a single file, superclass for different file types.
    
    Can be loaded using its constructor, which takes the arguments path, file, and corpus_kwargs.
    path and file refer to the path of corpus directory and the single file containing the data respectively.
    corpus_kwargs contains any keyword arguments that should be used for reading the data,
    e.g. the file_reader and its arguments.
    """

    def __init__(self, path=None, file=None, corpus_kwargs={}, **kwargs):
        # check if path and file are supplied
        if path is None:
            raise TypeError("Missing required key 'path'")
        if file is None:
            raise TypeError("Missing required key 'file'")

        # register path to file and check if exists
        self.path = Path(path).resolve() / Path(file)
        if not self.path.exists():
            raise FileNotFoundError(f"Corpus file {self.path} does not exist")
        elif not self.path.is_file():
            raise IsADirectoryError(f"{self.path} is not a file")

        # remember additional keyword arguments
        self.kwargs = corpus_kwargs

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path})"

    def files(self):
        return [self.path]

    def data(self, *args, **kwargs):
        kwargs = {**self.kwargs, **kwargs}
        file_reader = kwargs.pop('file_reader', None)
        if file_reader is None:
            return self.path
        else:
            return file_reader(self.path, *args, **kwargs)

class JSONFileCorpus(SingleFileCorpus):
    """A corpus consisting of a single JSON file."""

    def data(self, *args, **kwargs):
        kwargs = {**self.kwargs, **kwargs}
        # *args are ignored but catch arguments for convenience
        with open(self.path, 'r') as f:
            return json.load(f, **kwargs)

class JSONLinesFileCorpus(SingleFileCorpus):
    """A corpus consisting of a single JSONL file."""

    def data(self, *args, **kwargs):
        kwargs = {**self.kwargs, **kwargs}
        with open(self.path, 'r') as f:
            return [json.loads(line) for line in f]

class CSVFileCorpus(SingleFileCorpus):
    """A corpus consisting of a single TSV/CSV file."""

    def __init__(self, *args, sep=',', **kwargs):
        # initialize single file corpus normally
        super().__init__(*args, **kwargs)

        # read the separator (this should become unnecessary when switching to JSON/YAML configs)
        if sep[0] == '"' or sep[0] == "'":
            sep = ast.literal_eval(sep)
        # remember the separator
        self.sep = sep

    def data(self, *args, **kwargs):
        kwargs = {**self.kwargs, "sep": self.sep, **kwargs}
        return pandas.read_csv(self.path, **kwargs)
