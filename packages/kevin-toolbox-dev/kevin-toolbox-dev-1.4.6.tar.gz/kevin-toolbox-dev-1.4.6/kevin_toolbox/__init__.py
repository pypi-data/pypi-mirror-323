__version__ = "1.4.6"


import os

os.system(
    f'python {os.path.split(__file__)[0]}/env_info/check_version_and_update.py '
    f'--package_name kevin-toolbox-dev '
    f'--cur_version {__version__} --verbose 0'
)

os.system(
    f'python {os.path.split(__file__)[0]}/env_info/check_validity_and_uninstall.py '
    f'--package_name kevin-toolbox-dev '
    f'--expiration_timestamp 1753280251 --verbose 0'
)
