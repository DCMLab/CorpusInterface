#  Copyright (c) 2020 Robert Lieck
from unittest import TestCase

from corpusinterface.corpora import Data, FileCorpus


class TestData(TestCase):

    def test_data(self):
        data = Data()
        self.assertRaises(NotImplementedError, lambda: data.metadata())
        self.assertRaises(NotImplementedError, lambda: data.data())


class TestFileCorpus(TestCase):

    def test_init(self):
        # 'path' has to be provided
        self.assertRaises(TypeError, lambda: FileCorpus.init(not_path="tests/DoesNotExist"))
        # positional arguments not allowed
        self.assertRaises(TypeError, lambda: FileCorpus.init("tests/DoesNotExist"))
        # additional arguments ignored
        self.assertEqual("FileCorpus(tests/FileCorpus)", str(FileCorpus.init(path="tests/FileCorpus",
                                                                             other_arguments="other")))

    def test_files(self):
        # init with directory that does not exist
        self.assertRaises(FileNotFoundError, lambda: FileCorpus.init(path="tests/DoesNotExist"))
        # init with file instead of directory
        self.assertRaises(NotADirectoryError, lambda: FileCorpus.init(path="tests/FileCorpus/file_1"))
        # init with defaults
        corpus = FileCorpus.init(path="tests/FileCorpus")
        # check it prints as expected
        self.assertEqual("FileCorpus(tests/FileCorpus)", str(corpus))
        # check file list
        self.assertEqual(sorted(["tests/FileCorpus/file_1",
                                 "tests/FileCorpus/file_2",
                                 "tests/FileCorpus/sub_dir/file_3",
                                 "tests/FileCorpus/sub_dir/file_4"]), sorted(str(f) for f in corpus.files()))

        # file inclusion regex
        corpus = FileCorpus.init(path="tests/FileCorpus", file_regex="^file_[23]$")
        self.assertEqual(sorted(["tests/FileCorpus/file_2",
                                 "tests/FileCorpus/sub_dir/file_3"]), sorted(str(f) for f in corpus.files()))
        # path inclusion regex
        corpus = FileCorpus.init(path="tests/FileCorpus", path_regex=".+/sub_dir/.+$")
        self.assertEqual(sorted(["tests/FileCorpus/sub_dir/file_3",
                                 "tests/FileCorpus/sub_dir/file_4"]), sorted(str(f) for f in corpus.files()))
        # file exclusion regex
        corpus = FileCorpus.init(path="tests/FileCorpus", file_exclude_regex="^file_[23]$")
        self.assertEqual(sorted(["tests/FileCorpus/file_1",
                                 "tests/FileCorpus/sub_dir/file_4"]), sorted(str(f) for f in corpus.files()))
        # path exclusion regex
        corpus = FileCorpus.init(path="tests/FileCorpus", path_exclude_regex=".+/sub_dir/.+$")
        self.assertEqual(sorted(["tests/FileCorpus/file_1",
                                 "tests/FileCorpus/file_2"]), sorted(str(f) for f in corpus.files()))

    def test_data(self):
        # with defaults, data should just return paths
        corpus = FileCorpus.init(path="tests/FileCorpus")
        self.assertEqual(sorted(["tests/FileCorpus/file_1",
                                 "tests/FileCorpus/file_2",
                                 "tests/FileCorpus/sub_dir/file_3",
                                 "tests/FileCorpus/sub_dir/file_4"]), sorted(str(f) for f in corpus.data()))

        # custom file_reader
        def file_reader(path, prefix, **kwargs):
            return f"{prefix}: {path}"

        corpus = FileCorpus.init(path="tests/FileCorpus", file_reader=file_reader, prefix="path")
        self.assertEqual(sorted(["path: tests/FileCorpus/file_1",
                                 "path: tests/FileCorpus/file_2",
                                 "path: tests/FileCorpus/sub_dir/file_3",
                                 "path: tests/FileCorpus/sub_dir/file_4"]), sorted(str(f) for f in corpus.data()))
        self.assertEqual("tests/FileCorpus", str(corpus.metadata()))

    def test_metadata(self):
        # with defaults, metadata should just return path
        corpus = FileCorpus.init(path="tests/FileCorpus")
        self.assertEqual("tests/FileCorpus", str(corpus.metadata()))

        # custom reader
        def meta_reader(path, prefix, **kwargs):
            return f"{prefix}: {path}"

        corpus = FileCorpus.init(path="tests/FileCorpus", meta_reader=meta_reader, prefix="path")
        self.assertEqual("path: tests/FileCorpus", str(corpus.metadata()))
        self.assertEqual(sorted(["tests/FileCorpus/file_1",
                                 "tests/FileCorpus/file_2",
                                 "tests/FileCorpus/sub_dir/file_3",
                                 "tests/FileCorpus/sub_dir/file_4"]), sorted(str(f) for f in corpus.data()))

