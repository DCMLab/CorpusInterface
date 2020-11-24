#  Copyright (c) 2020 Robert Lieck
from unittest import TestCase, mock
from pathlib import Path
from io import StringIO
import shutil

from CorpusInterface.loading import download, load, remove, CorpusNotFoundError, DownloadFailedError, LoadingError
from CorpusInterface import config
from CorpusInterface.corpora import FileCorpus


class Test(TestCase):

    root_path = Path(__file__).parent / "corpora"

    def setUp(self):
        # set default root to test directory
        config.set_default_key_value(config.__ROOT__, str(self.root_path))
        # load test corpora into config
        config.load_config("./tests/test_corpora.ini")

    def tearDown(self):
        # cleanup: remove root directory with downloaded corpora
        if self.root_path.exists():
            shutil.rmtree(self.root_path)

    def test_download(self):
        # custom Exception to check the provided access function was actually executed
        class AccessCheck(Exception):
            pass

        def access(*args, **kwargs):
            raise AccessCheck

        # check different corpora
        for corpus in ["testcorpus-git-http",
                       # "testcorpus-git-ssh",  # does not work in GitHub action
                       "testcorpus-zip",
                       "testcorpus-tar.gz"]:
            # check with custom access function (raises and leaves directory empty)
            self.assertRaises(AccessCheck, lambda: download(corpus, access=access))
            # check bad access method
            self.assertRaises(DownloadFailedError, lambda: download(corpus, access="bad access method"))
            # download corpus
            download(corpus)
            # assert the directory is there and non-empty
            path = config.get_path(corpus)
            self.assertTrue(list(path.iterdir()))
            # fails because exists
            self.assertRaises(DownloadFailedError, lambda: download(corpus))

    def test_download_from_child(self):
        # child corpus
        corpus = "testcorpus-zip-child"
        # download
        download(corpus)
        # assert the directory is there and non-empty
        path = config.get_path(corpus)
        self.assertTrue(list(path.iterdir()))

    def test_load(self):
        corpus = "testcorpus-zip"
        # check load without download (fails)
        self.assertRaises(CorpusNotFoundError, lambda: load(corpus))
        # check load with download; custom reader
        self.assertEqual(1234, load(corpus, download=True, reader=lambda **kwargs: 1234))
        # check load with only keyword arguments
        self.assertEqual(1234, load(path=Path("tests/corpora/testcorpus-zip"), reader=lambda **kwargs: 1234))
        # test with bad reader
        self.assertRaises(LoadingError, lambda: load(corpus, reader="bad reader"))
        # test with default reader (FileCorpus)
        c = load(corpus)
        self.assertTrue(str(c).startswith("FileCorpus(") and
                        str(c).endswith("/corpora/testcorpus-zip)") and
                        type(c) == FileCorpus)

    def test_errors(self):
        self.assertRaises(LoadingError, lambda: load(path=Path("tests/FileCorpus")))

    def test_remove(self):
        corpus = "testcorpus-zip"

        # download
        download(corpus)
        path = config.get_path(corpus)
        # assert the directory is there and non-empty
        self.assertTrue(list(path.iterdir()))

        # remove without input cancels
        with mock.patch('builtins.input', return_value=''):
            with mock.patch('sys.stdout', new=StringIO()) as out:
                remove(corpus)
                self.assertTrue(out.getvalue().startswith("Canceled. Corpus '"))
        # assert the directory is there and non-empty
        self.assertTrue(list(path.iterdir()))

        # remove with 'no' input cancels
        with mock.patch('builtins.input', return_value='no'):
            with mock.patch('sys.stdout', new=StringIO()) as out:
                remove(corpus)
                self.assertTrue(out.getvalue().startswith("Canceled. Corpus '"))
        # assert the directory is there and non-empty
        self.assertTrue(list(path.iterdir()))

        # remove with 'yes' input removes
        with mock.patch('builtins.input', return_value='yes'):
            remove(corpus)
        # assert the directory is not there anymore
        self.assertFalse(path.exists())

        # re-download
        download(corpus)
        # assert the directory is there and non-empty
        self.assertTrue(list(path.iterdir()))
        # silent remove succeeds
        remove(corpus, silent=True)
        # assert the directory is not there anymore
        self.assertFalse(path.exists())

        # remove non-existent raises
        self.assertRaises(FileNotFoundError, lambda: remove(corpus, silent=True))
        # which can be ignored
        remove(corpus, not_exists_ok=True, silent=True)

        # path pointing to file raises
        self.assertRaises(NotADirectoryError, lambda: remove(corpus, path='tests/FileCorpus/file_1'))
