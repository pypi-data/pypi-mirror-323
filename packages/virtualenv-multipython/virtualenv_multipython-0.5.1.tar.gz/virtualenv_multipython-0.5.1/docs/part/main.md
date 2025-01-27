<!-- docsub: begin #noinstall -->
<!-- docsub: include ../../docs/part/plugin-noinstall.md -->
This plugin is intended to be installed under [multipython](https://github.com/makukha/multipython) docker image. This is done automatically during multipython release, and there seems to be no reason to install this plugin manually by anyone.
<!-- docsub: end #noinstall -->

Environment names supported are all [multipython](https://github.com/makukha/multipython) tags.

This plugin allows to use multipython tags in virtualenv:

```shell
$ virtualenv --python py314t /tmp/venv
```

## Behaviour

* Loosely follow behaviour of builtin virtualenv discovery, with some important differences:
* Try requests one by one, starting with [`--try-first-with`](https://virtualenv.pypa.io/en/latest/cli_interface.html#try-first-with); if one matches multipython tag or is an absolute path, return it to virtualenv.
* If no version was requested at all, use `sys.executable`
* If no request matched conditions above, fail to discover interpreter.
* In particular, command names on `PATH` are not discovered.

## Installation

```shell
$ pip install virtualenv-multipython
```

## Configuration

Set `multipython` to be the default discovery method for virtualenv:

### Option 1. Environment variable

```shell
VIRTUALENV_DISCOVERY=multipython
````

### Option 2. Configuration file

```ini
[virtualenv]
discovery = multipython
```

Add these lines to one of [virtualenv configuration files](https://virtualenv.pypa.io/en/latest/cli_interface.html#conf-file). Under e.g. Debian `root`, the file is `/root/.config/virtualenv/virtualenv.ini`
