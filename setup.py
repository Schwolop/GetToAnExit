#!/usr/bin/env python

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os","pygame","collections","sys"], "excludes": [], "include_files": ["resources"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "GetToAnExit!",
        version = "0.1",
        description = "A game of skill, chance, and copyright infringement.",
        maintainer="Tom Allen",
        maintainer_email="tom@jugglethis.net",
        url = "https://github.com/Schwolop/GetToAnExit",
        options = {"build_exe": build_exe_options},
        executables = [Executable("main.py", base=base)])