# Corpus Interface

![build](https://github.com/DCMLab/CorpusInterface/workflows/build/badge.svg)
[![PyPI version](https://badge.fury.io/py/corpusinterface.svg)](https://badge.fury.io/py/corpusinterface)

![tests](https://github.com/DCMLab/CorpusInterface/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/DCMLab/CorpusInterface/branch/master/graph/badge.svg?token=BooAiwbcyk)](https://codecov.io/gh/DCMLab/CorpusInterface)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Basic functionality to maintain and load corpora.

## Installation

`pip install corpusinterface`

## Managing Corpora

### Adding your own corpus

#### TL;DR

Provide a config file `your-corpus.ini`

```ini
[Your Corpus]
access: zip
url: http://your-website.com/your-corpus.zip
```

and load it using `init_config("your-corpus.ini")`.

#### More details

Say, you packaged a number of files into a corpus

```
your-corpus
  |- file_1.txt
  |- file_2.txt
  |- dir_1
    |- file_3.txt
    |- file_4.txt
```

and let's assume you made it available as a zip archive at `http://your-website.com/your-corpus.zip` (`git` repos and `tar.gz` files are also supported). Without a config file, this corpus can be added and accessed as follows:

```python
from corpusinterface import config, load

# initialise config
config.init_config()

# add your corpus
config.add_corpus("Your Corpus",
                  access="zip",
                  url="http://your-website.com/your-corpus.zip")

# load the corpus
corpus = load("Your Corpus", download=True)

# access the data (using a file_reader of your choice)
for file in corpus.data(file_reader=lambda file, **kwargs: f"reading: {file}"):
    print(file)
```

This will print

```
reading: ~/corpora/Your Corpus/file_1.txt
reading: ~/corpora/Your Corpus/file_2.txt
reading: ~/corpora/Your Corpus/dir_1/file_3.txt
reading: ~/corpora/Your Corpus/dir_1/file_4.txt
```

with `~` being replaced with your home directory (paths might be displayed differently, depending on your operating system).

Config files allow you to automate the procedure of adding a corpus and are convenient to provide more detailed information, in particular for other people who want to use your corpus.

### Config files

Instead of specifying the necessary information from within Python, you can also put it in a config file:

```ini
[Your Corpus]
access: zip
url: http://your-website.com/your-corpus.zip
```

If you put this file at the default location  `~/corpora/corpora.ini` in your home directory or a file `corpora.ini` in the current working directory, it is automatically loaded when calling `config.init_config()`. Otherwise, you can load any config file by either providing it to `init_config`

```python
config.init_config("your-config-file.ini")
```

or loading it manually later

```python
config.load_config("your-config-file.ini")
```

#### Default config

A default config file is shipped with the `corpusinterface`  package and automatically loaded by `init_config`. It defines some useful defaults that are used for newly added corpora if no corpus-specific values are specified. You can see all the config information associated to your corpus by printing a summary:

```python
print(config.summary(corpus="Your Corpus"))
```

```ini
[Your Corpus]
    access: zip
    url: http://your-website.com/your-corpus.zip
    info: None
    root: ~/corpora
    path: ~/corpora/Your Corpus
    parent: None
    loader: FileCorpus
```

In particular, the default `root` directory `~/corpora` was added and the corpus is stored in a `path` that is a subdirectory `~/corpora/Your Corpus` according to its name (more on `root` and `path` below). Moreover, by default we assume to have a `FileCorpus` consisting of a simple collection of files.

#### Special parameters

The parameters `root`, `path`, `parent`,  `download`, `loader`, `access`, and `url` are special and their values are treated in a particular way.

##### `root`

Root directory to store the corpus in. This should be an absolute path, `~` is expanded to the user home. If a relative path is specified, a warning is issued and it is interpreted relative to the current working directory. If `parent` is non-empty, the value of `root` is ignored and instead the parent's `path` is used. A call to `config.get(Name, 'root')` returns the effective value.

##### `path`

Directory to store the corpus in. This can be

1. an absolute path (`~` is expanded to the user home), in which case `root` is ignored
2. a relative path, in which case it is appended to `root` or
3. be empty, in which case the corpus `[Name]` is appended to `root`.

A call to `config.get(Name, 'path')` returns the effective value. Note that for sub-corpora (with non-empty `parent`) the parent's `path` is used instead of `root`.

##### `parent`

A parent corpus name or empty. If non-emtpy, the parent corpus should be defined separately and the value of `root` is ignored and replaced by the parent's `path`.

Initialisation (e.g. downloading from `url` with `access` method) is delegated to the parent corpus when loading a sub-corpus.

##### `download`

##### `loader`

##### `access`

##### `url`

#### Additional parameters

You can specify additional parameters that are handed over to the loader and (in case of the `FileCorpus` loader) further passed on the your `file_reader` function. For instance, you could specify

```ini
prefix: my prefix
```

in the config file or equivalently

```python
config.add_corpus("Your Corpus",
                  ...,
                  prefix="my prefix")
```

from within Python. Your file reader can then make use of this parameter (provided as a keyword argument, so you have to refer to it by the correct name)

```python
file_reader=lambda file, prefix, **kwargs: f"{prefix}: {file}"
```

```
my prefix: ~/corpora/Your Corpus/file_1.txt
...
```

This is also the reason why we always need  `**kwargs` in a reader function to accept all keyword arguments that are provided, even if we decide to not use them.

The config values can be dynamically overwritten in the `load` function

```python
corpus = load("Your Corpus",
              ...,
              prefix="other prefix")
```

```
other prefix: ~/corpora/Your Corpus/file_1.txt
...
```

or in the `data` function:

```python
for file in corpus.data(..., prefix="still different"):
    ...
```

```
still different: ~/corpora/Your Corpus/file_1.txt
...
```

#### Controlling initialisation

You have full control over how the config is initialised. A call to `config.init_config()` without any arguments will load the default config, look for `corpora.ini` in `~/corpora` and the current working directory and load them, too, if present. This is equivalent to calling

```python
config.init_config(default=None, home=None, local=None)
```

For each of these parameters you may alternatively specify a value of `True` (meaning that you _expect_ the respective config file to be loaded and otherwise an error is raised), or `False` (meaning the the respective config file is _not_ loaded). Additionally, you may specify one or more files that should additionally be loaded

```python
config.init_config("/path/to/file_1.ini", "/path/to/file_2.ini", ...)
```

