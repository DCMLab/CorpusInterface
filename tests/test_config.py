#  Copyright (c) 2020 Robert Lieck
from unittest import TestCase
from pathlib import Path

from CorpusInterface.config import load_config, _config, get, set, set_default, get_info, get_root, get_path


class Test(TestCase):

    def test_load_config(self):
        # assert default config was loaded and DEFULT section is there
        self.assertTrue('DEFAULT' in _config)
        # assert the test config was not yet loaded
        self.assertFalse('a test section' in _config)
        # load it
        load_config('tests/test_config.ini')
        # assert it's there now
        self.assertTrue('a test section' in _config)
        # assert the multi-line value is correctly parsed
        self.assertEqual('test values\nover multiple lines', _config['a test section']['with'])
        # assert empty values are correctly parsed (also check that capitalisation is ignored)
        self.assertEqual(None, _config['a test section']['A VALUE THAT IS'])
        # assert references are correctly parsed
        self.assertEqual('backref to test values\nover multiple lines', _config['a test section']['and'])

    def test_get_methods(self):
        load_config('tests/test_corpora.ini')
        # for section, content in config.items():
        #     print(section)
        #     for key, val in content.items():
        #         print(f"  {key}: {val}")
        #     print()

        # check get method returns the unprocessed values
        self.assertEqual(None, get("Test Corpus", "info"))
        self.assertEqual(None, get("Test Corpus", "parent"))
        self.assertEqual(None, get("Test Corpus", "access"))
        self.assertEqual(None, get("Test Corpus", "url"))
        self.assertEqual("~/corpora", get("Test Corpus", "root"))
        self.assertEqual(None, get("Test Corpus", "path"))
        self.assertEqual(None, get("Test Corpus", "type"))

        # check info
        self.assertEqual("Test Corpus\n"
                         "  info: None\n"
                         "  root: ~/corpora\n"
                         "  path: None\n"
                         "  parent: None\n"
                         "  access: None\n"
                         "  url: None\n"
                         "  type: None", get_info("Test Corpus"))
        self.assertEqual("Some info", get_info("Test Sub-Corpus"))

        # check default root
        global_root = Path('~/corpora').expanduser()
        self.assertEqual(global_root, get_root("Test Corpus"))
        # check warning for relative root
        with self.assertWarns(RuntimeWarning):
            relative_root = Path('some/relative/path')
            self.assertFalse(relative_root.is_absolute())
            self.assertEqual(relative_root, get_root("Test Relative Root"))
        # check root for sub- and sub-sub-corpora
        self.assertEqual(global_root.joinpath("Test Corpus"),
                         get_root("Test Sub-Corpus"))
        self.assertEqual(global_root.joinpath("Test Corpus").joinpath("Test Sub-Corpus"),
                         get_root("Test Sub-Sub-Corpus"))

        # check path for normal corpus
        self.assertEqual(global_root.joinpath("Test Corpus"), get_path("Test Corpus"))
        # check relative path
        self.assertEqual(global_root.joinpath("some/relative/path"), get_path("Test Relative Path"))
        # check absolute path
        self.assertEqual(Path("/some/absolute/path"), get_path("Test Absolute Path"))
        self.assertEqual(Path("~").expanduser().joinpath("some/absolute/path"), get_path("Test Absolute Path Home"))
        
        # check path for sub- and sub-sub-corpora
        self.assertEqual(global_root.joinpath("Test Corpus").joinpath("Test Sub-Corpus"),
                         get_path("Test Sub-Corpus"))
        self.assertEqual(
            global_root.joinpath("Test Corpus").joinpath("Test Sub-Corpus").joinpath("Test Sub-Sub-Corpus"),
            get_path("Test Sub-Sub-Corpus"))

        # check sub-corpora with relative and absolute path
        self.assertEqual(global_root.joinpath("some/relative/path"),
                         get_path("Test Relative Sub-Path"))
        self.assertEqual(Path("/some/absolute/path"),
                         get_path("Test Absolute Sub-Path"))
        self.assertEqual(Path("~").expanduser().joinpath("some/absolute/path"),
                         get_path("Test Absolute Sub-Path Home"))

    def test_set(self):
        # set section
        self.assertFalse("XXX" in _config)
        set("XXX")
        self.assertTrue("XXX" in _config)
        # set value in section to None
        self.assertFalse("YYY" in _config["XXX"])
        set("XXX", "YYY")
        self.assertTrue("YYY" in _config["XXX"])
        self.assertEqual(None, _config["XXX"]["YYY"])
        self.assertNotEqual('None', _config["XXX"]["YYY"])
        # set value in section
        set("XXX", "YYY", "ZZZ")
        self.assertEqual("ZZZ", _config["XXX"]["YYY"])
        # set value in DEFAULT
        set_default("AAA")
        self.assertEqual(None, get("XXX", "AAA"))
        set_default("AAA", "BBB")
        self.assertEqual("BBB", get("XXX", "AAA"))
