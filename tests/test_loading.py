#  Copyright (c) 2020 Robert Lieck
from unittest import TestCase
from pathlib import Path
from warnings import warn
import shutil

from CorpusInterface.loading import download, load, CorpusNotFoundError, DownloadFailedError
from CorpusInterface import config


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
                       "testcorpus-zip"]:
            # download corpus
            download(corpus, overwrite=False)
            # assert the directory is there and non-empty
            path = config.get_path(corpus)
            self.assertTrue(list(path.iterdir()))
            # check with custom access function
            self.assertRaises(AccessCheck, lambda: download(corpus, overwrite=True, access=access))

    def test_overwrite(self):
        corpus = "testcorpus-zip"
        path = config.get_path(corpus)
        # first download
        download(corpus, overwrite=False)
        # check folder is there
        self.assertTrue(list(path.iterdir()))
        # re-download fails with overwriting=False
        self.assertRaises(DownloadFailedError, lambda: download(corpus, overwrite=False))
        # re-download succeeds with overwriting=True
        download(corpus, overwrite=True)

    def test_overwrite_from_child(self):
        parent_corpus = "testcorpus-zip"
        corpus = "testcorpus-zip-child"
        parent_path = config.get_path(parent_corpus)
        path = config.get_path(corpus)
        # first download
        download(corpus, overwrite=False)
        # check folder is there
        self.assertTrue(list(path.iterdir()))
        # also for parent
        self.assertTrue(list(parent_path.iterdir()))
        # re-download fails with overwriting=False
        self.assertRaises(DownloadFailedError, lambda: download(corpus, overwrite=False))
        # re-download with overwriting=True triggers warning because parent cannot be overwritten from child
        # as parent exists, download additionally fails
        with self.assertWarns(RuntimeWarning):
            self.assertRaises(DownloadFailedError, lambda: download(corpus, overwrite=True))
        # set overwrite=True for parent in config
        config.set_key_value(parent_corpus, "overwrite", "True")
        # try again: this also warns but download succeeds
        with self.assertWarns(RuntimeWarning):
            download(corpus, overwrite=True)
        # unset overwrite for parent to not mess up other things
        config.set_key_value(parent_corpus, "overwrite")
        self.assertEqual(None, config.get(parent_corpus, "overwrite"))

    def test_load(self):
        corpus = "testcorpus-zip"
        # check load without download (fails)
        self.assertRaises(CorpusNotFoundError, lambda: load(corpus))
        # check load with download; custom reader
        self.assertEqual(1234, load(corpus, download=True, reader=lambda **kwargs: 1234))
