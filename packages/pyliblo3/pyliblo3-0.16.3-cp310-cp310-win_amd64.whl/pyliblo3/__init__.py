from __future__ import absolute_import


# start delvewheel patch
def _delvewheel_patch_1_10_0():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pyliblo3.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_0()
del _delvewheel_patch_1_10_0
# end delvewheel patch

import platform
import os

if platform.system() == "Windows":
    libspath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pyliblo3.libs'))
    if os.path.exists(libspath) and os.path.isdir(libspath):
        os.add_dll_directory(libspath)
    else:
        possible_paths = ['C:/Program Files/liblo/lib', 'C:/Program Files/liblo/bin']
        for path in ['C:/Program Files/liblo/lib', 'C:/Program Files/liblo/bin']:
            if os.path.exists(path) and os.path.isdir(path):
                os.add_dll_directory(path)
del platform
del os


from ._liblo import *
