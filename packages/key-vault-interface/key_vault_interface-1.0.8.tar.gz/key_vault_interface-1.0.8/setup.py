from setuptools import setup, find_packages
import os
import re


def get_version():
    version = None
    version_pattern = r'__version__ = ["\']([^"\']+)["\']'

    with open(
        os.path.join(os.path.dirname(__file__), "key_vault_interface", "__init__.py")
    ) as f:
        for line in f:
            match = re.search(version_pattern, line)
            if match:
                version = match.group(1)
                break

    if version is None:
        raise ValueError("Version not found in __init__.py")

    return version


setup(
    name="key-vault-interface",
    version=get_version(),
    packages=find_packages()
)
