import os
import re
import json
import jsonpath_ng
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

    # The user can provide their own readers (e.g. wrappers around Music21
    # stuff or similar) if they wish.
    def __init__(self, path, parameters, **kwargs):# metadata_reader=None, file_reader=None):
        # Extract the parameters
        self.parameter_dict = dict(map(lambda x : x.split("="), parameters.split("/")))

        if self.parameter_dict.get('metadata') is not None:
            metadata_path = os.path.join(path, metadata)
            if os.path.isfile(metadata_path):
                self.metadata_path = metadata_path
                self.metadata_reader = \
                    FileCorpus.choose_metadata_reader(metadata) if kwargs.get('metadata_reader') is None else kwargs.get('metadata_reader')
            else:
                raise FileNotFoundError(f"Could not find metadata file at '{metadata_path}'")
        else:
            self.metadata_path = None
            self.metadata_reader = lambda *args, **kwargs: None
        self.document_list = []
        self.path = path
        self.file_reader = FileCorpus.choose_file_reader(self.parameter_dict.get('file_type')) if kwargs.get('file_reader') is None else kwargs.get('file_reader')
        # compile regex if provided
        if self.parameter_dict.get('file_regex') is not None:
            self.file_regex = re.compile(self.parameter_dict.get('file_regex'))
        # walk through tree
        for root, dirs, files in os.walk(path):
            for file in files:
                # only take matching files
                if self.file_regex is None or self.file_regex.match(file):
                    self.document_list.append(FileDocument(os.path.join(root, file), self.file_reader, **self.parameter_dict, **kwargs))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path})"

    def __iter__(self):
        yield from self.document_list

    def metadata(self):
        return self.metadata_reader(self.metadata_path)

# A JSONDocument is a slice of a one-file JSON Corpus

class JSONCorpus(Corpus):

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


    def __init__(self, path, parameters, **kwargs ):#json_file = None, metadata_reader = None, json_reader = None, document_reader=None):
        #TODO: Extract this into a superclass?
        self.parameter_dict = dict(map(lambda x : x.split("="), parameters.split("/")))

        if self.parameter_dict.get('metadata') is not None:
            metadata_path = os.path.join(path, metadata)
            if os.path.isfile(metadata_path):
                self.metadata_path = metadata_path
                self.metadata_reader = (lambda x : x) if kwargs.get('metadata_reader') is None else kwargs.get('metadata_reader')#if metadata_reader is None else metadata_reader
            else:
                raise FileNotFoundError(f"Could not find metadata file at '{metadata_path}'")
        else:
            self.metadata_path = None
            self.metadata_reader = lambda *args, **kwargs: None
        self.document_list = []
        self.path = path

        self.json_file = self.parameter_dict.get('json_file') if kwargs.get('json_file') is None else kwargs.get('json_file')

        with open(os.path.join(self.path,self.json_file), 'r') as f:
           self.json_data = json.load(f)
        
        if kwargs.get('json_reader') is not None:
           json_reader = kwargs['json_reader']
           self.document_list = json_reader(json_data=self.json_data, **self.parameter_dict)
           return

        if kwargs.get('document_reader') is not None:
           self.document_reader = kwargs['document_reader']
        else:
           self.document_reader = lambda x : x
        
        if self.parameter_dict.get('json_list_of_documents') is not None:
           self.json_expr = jsonpath_ng.parse(self.parameter_dict.get('json_list_of_documents'))
        else:
           self.json_expr = jsonpath_ng.parse("$[*]")

        self.document_list = map(lambda x : x.value, self.json_expr.find(self.json_data))
        self.document_list = map(self.document_reader, self.document_list)


    def __iter__(self):
      yield from self.document_list

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path})"

    def metadata(self):
        return "JSON"

#TODO: class APICorpus/APIDocument


