
# How to use this file
#
# 1. create a folder called "hooks" in your repo
# 2. copy this file there
# 3. add the --additional-hooks-dir flag to your pyinstaller command:
#    ex: `pyinstaller --name binary-name --additional-hooks-dir=./hooks entry-point.py`


from PyInstaller.utils.hooks import collect_data_files, get_package_paths, collect_dynamic_libs, collect_submodules
import os, sys

# Get the package path
package_path = get_package_paths('llama_cpp')[0]

# Collect data files
datas = collect_data_files('llama_cpp')
binaries = collect_dynamic_libs('llama_cpp')
hiddenimports = collect_submodules('llama_cpp')

# Append the additional .dll or .so file
if os.name == 'nt':  # Windows
    for fname in os.listdir(package_path):
        if fname.endswith('.dll') or fname.endswith('.pyd'):
            datas.append((os.path.join(package_path, fname), 'llama_cpp'))
elif sys.platform == 'darwin':  # Mac
    lib_dir = os.path.join(package_path, 'lib')
    for fname in os.listdir(lib_dir):
        if fname.endswith('.dylib'):
            datas.append((os.path.join(lib_dir, fname), 'llama_cpp/lib'))
elif os.name == 'posix':  # Linux
    so_path = os.path.join(package_path, 'llama_cpp', 'libllama.so')
    datas.append((so_path, 'llama_cpp'))
