import os
import re
from CorpusInterface import readers

# A Document is a collection of musical events, and some metadata
class Document:

    def metadata(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

# A Corpus is a collection of Documents, and some metadata
class Corpus:

    def metadata(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

# A FileDocument is a concrete file on disk.
class FileDocument(Document):

    def __init__(self, path, reader,**kwargs):
        self.path = path
        self.kwargs = kwargs
        self.reader = reader

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path})"

    def metadata(self):
        return self.path

    def __iter__(self):
        yield from self.reader(self.path,**self.kwargs)

# A FileCorpus is a concrete directory containing files (possibly in
# subdirectories), where each file as identified by the regex is a Document
# in its own right
class FileCorpus(Corpus):

    # We allow for various ways to read metadata
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
    
    # As well as various ways to read the files themselves
    @staticmethod
    def choose_file_reader(file_specification):
        # The file type is the part before the first slash
        file_type = file_specification.split("/")[0]
        # After which optional arguments are given between further slashes,
        # with equals signs delineating between key and value
        # TODO allow key-only arguments
        file_args = dict([x.split("=") for x in file_specification.split("/")[1:]])



        if file_type == "txt":
            return [readers.read_txt, file_args]
        elif file_type == "csv":
            return [readers.read_csv, file_args]
        elif file_type == "tsv":
            return [readers.read_tsv, file_args]
        elif file_type == "midi":
            return [readers.read_midi, file_args]
        else:
            raise TypeError(f"Unsupported file format '{file_type}'")

    # The user can provide their own readers (e.g. wrappers around Music21
    # stuff or similar) if they wish.
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
        [self.file_reader, self.file_args] = FileCorpus.choose_file_reader(file_type) if file_reader is None else [file_reader, None]
        # compile regex if provided
        if file_regex is not None:
            file_regex = re.compile(file_regex)
        # walk through tree
        for root, dirs, files in os.walk(path):
            for file in files:
                # only take matching files
                if file_regex is None or file_regex.match(file):
                    self.document_list.append(FileDocument(os.path.join(root, file), self.file_reader, **self.file_args))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path})"

    def __iter__(self):
        yield from self.document_list

    def metadata(self):
        return self.metadata_reader(self.metadata_path)

#TODO: class JSONCorpus/JSONDocument

#TODO: class APICorpus/APIDocument


