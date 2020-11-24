#  Copyright (c) 2020 Robert Lieck
from pathlib import Path
import os
import re


class Data:
    """An abstract base class for data items, such as corpora or documents."""
    def metadata(self):
        raise NotImplementedError

    def data(self):
        raise NotImplementedError


class FileCorpus(Data):
    """A collection of files in a directory"""

    @classmethod
    def init(cls, **kwargs):
        if 'path' not in kwargs:
            raise TypeError("Missing required keyword argument 'path'")
        kwargs = {**dict(reader=None,
                         meta_reader=None,
                         file_regex=None,
                         path_regex=None,
                         file_exclude_regex=None,
                         path_exclude_regex=None),
                  **kwargs}
        return FileCorpus(**kwargs)

    def __init__(self,
                 path,
                 reader=None,
                 meta_reader=None,
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
        # set readers
        self.reader = reader
        self.meta_reader = meta_reader
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

    def metadata(self):
        if self.meta_reader is None:
            return self.path
        else:
            return self.meta_reader(self.path, **self.kwargs)

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

    def data(self):
        for path in self.files():
            if self.reader is None:
                yield path
            else:
                yield self.reader(path, **self.kwargs)
