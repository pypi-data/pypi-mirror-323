# U-Phy Device Generator

U-Phy device generator.

## Developing

Python Poetry is recommended. See
https://python-poetry.org/docs/#installation for installation
instructions.

    $ cd /path/to/upgen
    $ poetry install
    $ poetry shell

## Build distributable binary using Nuitka

Install dependencies on Ubuntu::

    apt install patchelf python3-dev build-essential

The Nuitka compiler can be used to build a distributable binary. Note
that it should be possible to run the binary on the currently used and
all later Linux GLIBC versions, but not versions earlier than the one
in the build platform.

    $ poetry run nuitka \
        --include-package-data=upgen \
        --onefile \
        upgen/cli.py
    $ mkdir -p bin
    $ mv cli.bin bin/upgen
