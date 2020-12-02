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

If you put this file at the default location  `~/corpora/corpora.ini` in your home directory or a file `corpora.ini` in the current working directory, it is automatically loaded by `init_config` on package import. Otherwise, you can load any config file by either calling `reset_config`

```python
config.reset_config("your-config-file.ini")
```

which clears the config and reinitialises it, adding `your-config-file.ini` (see `init_config` for more fine-grained control) or by loading it separately

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

##### `download`, `loader`, `access`, `url`

See the section on [loading a corpus](#Loading a corpus).

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

You have full control over how the config is (re)initialised. A call to `config.init_config()` or `config.reset_config()` without any arguments will load the default config, look for `corpora.ini` in `~/corpora` and the current working directory and load them, too, if present. This is equivalent to calling

```python
config.init_config(default=None, home=None, local=None)
```

or

```python
config.reset_config(default=None, home=None, local=None)
```

respectively. For each of these parameters you may alternatively specify a value of `True` (meaning that you _expect_ the respective config file to be loaded and otherwise an error is raised), or `False` (meaning that the respective config file is _not_ loaded, even if it exists). Additionally, you may specify one or more files that should additionally be loaded

```python
config.init_config("/path/to/file_1.ini", "/path/to/file_2.ini", ...)
```

## Loading a corpus

Corpora are loaded with the `load` function

```python
from corpusinterface import load

# load the corpus
corpus = load("Your Corpus", download=True)
```

Specifying `download=True` indicates that the corpus should be downloaded if it cannot be found on disk. The `load` function looks up the given corpus in the config, retrieving any parameters (including default parameters) specified there. If you provide additional keyword arguments, these will overwrite parameters from the config with the same name. So you could, for instance, specify a different URL for downloading

```python
corpus = load("Your Corpus", url="some-other-url.com/corpus.zip" download=True)
```

or a custom path for looking for the corpus on disk and/or downloading it to

```python
corpus = load("Your Corpus", path="/my/custom/path/for/corpus/" download=True)
```

Four parameters are processed by the `load` function itself (`download`, `access`, `url`, `loader`). `download` and `url` play the obvious role described above.

`access` specifies how the content should be accessed and together with `url` is handled by the `download` function (called by `load` if `download=True` is specified). `access` can be a string (`"git"`, `"zip"`, or `"tar.gz"`) resulting in the corpus being downloaded and unpacked accordingly. It can also be a callable provided as a keyword argument to `load`. In that case the corpus `path` is created on disk and the provided method is called with the corpus name and all keyword arguments, including any parameters specified in the config.

The `loader` parameters is handled in a special way. If it is a callable, the `load` function will ensure the corpus exists (potentially downloading it) and then call the specified method with all provided keyword arguments, including any parameters specified in the config. This means that you can simply specify any custom loader function you would like to use

```python
corpus = load("Your Corpus", loader=my_special_loader_function)
```

If `loader` is a string, `load` tries to look up the appropriate function in the `loaders` dictionary. So you can also add it there and request it by providing the corresponding string in the `load` function

```python
from corpusinterface import load, loaders
loaders["my custom loader"] = my_special_loader_function
corpus = load("Your Corpus", loader="my custom loader")
```

The advantage of this approach is that you can specify it in a config file so you don't need to pass it to `load` each time

```ini
loader: my custom loader
```

Adding the loader function can also be automised. For instance, if you have a special corpus type that you provide in a separate python module, you can simply add the loader function there

```python
from corpusinterface import loaders

class MySpecialCorpus:
  ...

loaders["my custom loader"] = MySpecialCorpus
```

Given your custom config file, you corpus can then be loaded simply as

```python
corpus = load("Your Corpus")
```

without having to specify anything manually. Note that any loader function is provided with all keyword arguments, so it might be a good idea to use  `**kwargs` to handle any unforeseen additional parameters, even if they are not used.

## FileCorpus

The default corpus type is defined by the `FileCorpus` class. In a config file, it is specified by

```ini
loader: FileCorpus
```

which is the default if this parameter is not explicitly specified for a corpus. When calling `load`, they keyword argument `loader="FileCorpus"` is looked up in `loaders` and the actual `FileCorpus` constructor is called. In fact, the static `FileCorpus.init` method is called to check for the mandatory `path` argument and provide an interpretable error message if it is missing. The `FileCorpus` class assumes to find a collection of files at `path` and makes them available via the `files` and `data` method. Additionally, accepts four more parameters:

- `file_regex`: a regular expression for file names; if provided, files whose name does _not_ match are ignored
- `path_regex`: a regular expression for paths; if provided, path (including the file name) that do _not_ match are ignored
- `file_exclude_regex`: like `file_regex` but _matches_ are ignores
- `path_exclude_regex`: like `path_regex` but _matches_ are ignores

All additional keyword arguments are stored and passed on to calls of `data` and `metadata`.

### `files`

The `files` function returns an iterator over files (after applying the `*_regex` expressions, if provided). It returns their absolute paths.

### `data`

The `data` function iterates over `files` and attempts to read them. If a `file_reader` function is provided as keyword argument upon initialisation or directly to `data`, it is called with the full path of the respective file as first argument and all keyword arguments. Otherwise (or if `file_reader=None`)  `data` returns the absolute paths just like `files`.

### `metadata`

The `metadata` function looks for metadata in the `path` location of the corpus. If a `meta_reader` function is provided as keyword argument upon initialisation or directly to `metadata`, it is called with the full `path` of the corpus as first argument and all keyword arguments. Otherwise (or if `meta_reader=None`)  the full `path` is returned.

