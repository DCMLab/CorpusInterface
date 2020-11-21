#  Copyright (c) 2020 Robert Lieck
from unittest import TestCase
from pathlib import Path

from CorpusInterface import config
from CorpusInterface.config import init, load_config, clear, \
    get, get_info, get_root, get_path,\
    set, set_key_value, set_default, \
    add_corpus, iterate_corpus, getboolean


class Test(TestCase):

    def test_load_config(self):
        # assert default config was loaded and DEFULT section is there
        self.assertTrue('DEFAULT' in config.config)
        # assert the test config was not yet loaded
        self.assertFalse('a test section' in config.config)
        # load it
        load_config('tests/test_config.ini')
        # assert it's there now
        self.assertTrue('a test section' in config.config)
        # assert the multi-line value is correctly parsed
        self.assertEqual('test values\nover multiple lines', config.config['a test section']['with'])
        # assert empty values are correctly parsed (also check that capitalisation is ignored)
        self.assertEqual(None, config.config['a test section']['A VALUE THAT IS'])
        # assert references are correctly parsed
        self.assertEqual('backref to test values\nover multiple lines', config.config['a test section']['and'])

    def test_get_methods(self):
        load_config('tests/test_corpora.ini')
        # check get method returns the unprocessed values
        self.assertEqual(None, get("Test Corpus", "info"))
        self.assertEqual("~/corpora", get("Test Corpus", "root"))
        self.assertEqual(None, get("Test Corpus", "path"))
        self.assertEqual(None, get("Test Corpus", "parent"))
        self.assertEqual(None, get("Test Corpus", "access"))
        self.assertEqual(None, get("Test Corpus", "url"))
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

        # check omitting key is equivalent to iterate_corpus and returns iterator over processed values
        self.assertEqual(list(get("Test Sub-Corpus")), list(iterate_corpus("Test Sub-Corpus")))
        self.assertEqual(sorted([("info", "Some info"),
                                 ("root", Path("~/corpora").expanduser() / "Test Corpus"),
                                 ("path", Path("~/corpora").expanduser() / "Test Corpus" / "Test Sub-Corpus"),
                                 ("parent", "Test Corpus"),
                                 ("access", None),
                                 ("url", None),
                                 ("type", None)]),
                         sorted(list(get("Test Sub-Corpus"))))

        # check default root
        global_root = Path('~/corpora').expanduser()
        self.assertEqual(global_root, get_root("Test Corpus"))
        # check warning for relative root
        with self.assertWarns(RuntimeWarning):
            relative_root = Path('some/relative/path')
            self.assertFalse(relative_root.is_absolute())
            self.assertEqual(relative_root, get_root("Test Relative Root"))
        # check root for sub- and sub-sub-corpora
        self.assertEqual(global_root / "Test Corpus", get_root("Test Sub-Corpus"))
        self.assertEqual(global_root / "Test Corpus" / "Test Sub-Corpus", get_root("Test Sub-Sub-Corpus"))

        # check path for normal corpus
        self.assertEqual(global_root / "Test Corpus", get_path("Test Corpus"))
        # check relative path
        self.assertEqual(global_root / "some/relative/path", get_path("Test Relative Path"))
        # check absolute path
        self.assertEqual(Path("/some/absolute/path"), get_path("Test Absolute Path"))
        self.assertEqual(Path("~").expanduser() / "some/absolute/path", get_path("Test Absolute Path Home"))
        
        # check path for sub- and sub-sub-corpora
        self.assertEqual(global_root / "Test Corpus" / "Test Sub-Corpus", get_path("Test Sub-Corpus"))
        self.assertEqual(global_root / "Test Corpus" / "Test Sub-Corpus" / "Test Sub-Sub-Corpus",
                         get_path("Test Sub-Sub-Corpus"))

        # check sub-corpora with relative and absolute path
        self.assertEqual(global_root / "some/relative/path", get_path("Test Relative Sub-Path"))
        self.assertEqual(Path("/some/absolute/path"), get_path("Test Absolute Sub-Path"))
        self.assertEqual(Path("~").expanduser() / "some/absolute/path", get_path("Test Absolute Sub-Path Home"))

    def test_set(self):
        # set section
        self.assertFalse("XXX" in config.config)
        set("XXX")
        self.assertTrue("XXX" in config.config)

        # warn when existing corpus is reset
        with self.assertWarns(RuntimeWarning):
            set("XXX")

        # setting non-string section warns
        with self.assertWarns(RuntimeWarning):
            self.assertFalse(1 in config.config)
            set(1)
            self.assertFalse(1 in config.config)
            self.assertTrue("1" in config.config)

        # set value in section to None
        self.assertFalse("YYY" in config.config["XXX"])
        set("XXX", YYY=None)
        self.assertTrue("YYY" in config.config["XXX"])
        self.assertEqual(None, config.config["XXX"]["YYY"])
        self.assertNotEqual('None', config.config["XXX"]["YYY"])

        # error when value is specified but not key
        self.assertRaises(ValueError, lambda: set_key_value("XXX", value="XXX"))
        # warning for non-string keys and values (except None for value)
        with self.assertWarns(RuntimeWarning):
            set_key_value("XXX", key=1)
            self.assertEqual(None, get("XXX", 1))
        with self.assertWarns(RuntimeWarning):
            set_key_value("XXX", "1", 2)
            self.assertNotEqual(2, get("XXX", 1))
            self.assertEqual("2", get("XXX", 1))

        # set value in section
        set("XXX", YYY="ZZZ")
        self.assertEqual("ZZZ", config.config["XXX"]["YYY"])

        # set value in DEFAULT
        set_default(AAA=None)
        self.assertEqual(None, get("XXX", "AAA"))
        set_default(AAA="BBB")
        self.assertEqual("BBB", get("XXX", "AAA"))

        # add corpus
        add_corpus("new corpus", key1="val1", key2="val2")
        self.assertEqual("val1", get("new corpus", "key1"))
        self.assertEqual("val2", get("new corpus", "key2"))
        # add existing corpus raises
        self.assertRaises(KeyError, lambda: add_corpus("new corpus"))

    def test_getboolean(self):
        for val in ['1', 'yes', 'true', 'on', 1, True]:
            self.assertTrue(getboolean(val))
        for val in ['0', 'no', 'false', 'off', 0, False]:
            self.assertFalse(getboolean(val))
        for val in [123, "lkj"]:
            self.assertRaises(ValueError, lambda: getboolean(val))

    def test_clear(self):
        # check that there are sections in config
        self.assertGreater(len(list(config.config)), 1)
        # clear config (don't remove default)
        clear()
        # check only config section is left
        self.assertEqual([config.__DEFAULT__], list(config.config))
        # check its not empty
        self.assertGreater(len(list(config.config[config.__DEFAULT__])), 0)
        # now also clear default
        clear(clear_default=True)
        # check its empty now
        self.assertEqual(len(list(config.config[config.__DEFAULT__])), 0)
        # re-initialise
        init()
        # check that there are sections in config again
        self.assertGreater(len(list(config.config)), 1)
