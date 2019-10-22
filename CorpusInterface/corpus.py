import os
import re
from CorpusInterface import readers


class Document:

    def metadata(self):
        raise NotImplementedError

    def data(self):
        raise NotImplementedError


class Corpus:

    def metadata(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


class FileDocument(Document):

    def __init__(self, path, reader):
        self.path = path
        self.reader = reader

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path})"

    def metadata(self):
        return self.path

    def data(self):
        return self.reader(self.path)


class FileCorpus(Corpus):

    @staticmethod
    def choose_metadata_reader(metadata):
        if metadata.endswith(".txt"):
            return readers.read_txt
        elif metadata.endswith(".csv"):
            return readers.read_csv
        elif metadata.endswith(".tsv"):
            return readers.read_tsv
        else:
            raise TypeError(f"Unsupported metadata format of file '{metadata}'")

    @staticmethod
    def choose_file_reader(file_type):
        if file_type == "txt":
            return readers.read_txt
        elif file_type == "csv":
            return readers.read_csv
        elif file_type == "tsv":
            return readers.read_tsv
        elif file_type == "midi":
            return readers.read_midi
        else:
            raise TypeError(f"Unsupported file format '{file_type}'")

    def __init__(self, path, metadata, file_type, file_regex=None, metadata_reader=None, file_reader=None):
        if metadata is not None:
            metadata_path = os.path.join(path, metadata)
            if os.path.isfile(metadata_path):
                self.metadata_path = metadata_path
                self.metadata_reader = \
                    FileCorpus.choose_metadata_reader(metadata) if metadata_reader is None else metadata_reader
            else:
                raise FileNotFoundError(f"Could not find metadata file at '{metadata_path}'")
        else:
            self.metadata_path = None
            self.metadata_reader = lambda *args, **kwargs: None
        self.document_list = []
        self.path = path
        self.file_reader = FileCorpus.choose_file_reader(file_type) if file_reader is None else file_reader
        # compile regex if provided
        if file_regex is not None:
            file_regex = re.compile(file_regex)
        # walk through tree
        for root, dirs, files in os.walk(path):
            for file in files:
                # only take matching files
                if file_regex is None or file_regex.match(file):
                    self.document_list.append(FileDocument(os.path.join(root, file), self.file_reader))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path})"

    def __iter__(self):
        yield from self.document_list

    def metadata(self):
        return self.metadata_reader(self.metadata_path)
